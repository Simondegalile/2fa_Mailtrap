import os
import random
import string
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from models import db, User, LogEntry
from config import Config
import logging


app = Flask(__name__)
app.config.from_object(Config)

# Initialise SQLAlchemy
db.init_app(app)

# Initialise la session sur le serveur
Session(app)

# Initialise Flask-Mail
mail = Mail(app)

# Configuration du logger pour écrire dans un fichier logs/app.log
if not os.path.exists("logs"):
    os.makedirs("logs")
file_handler = logging.FileHandler("logs/app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# ----------------------------
# CREATION DE LA BDD AU DEMARRAGE
# ----------------------------
@app.before_first_request
def create_tables():
    db.create_all()
    app.logger.info("Base de données initialisée / Vérifiée.")
    log_entry = LogEntry(action="Server started", timestamp=datetime.utcnow())
    db.session.add(log_entry)
    db.session.commit()

# ----------------------------
# FONCTIONS UTILITAIRES
# ----------------------------
def log_action(username, action):
    """Insère une entrée de log dans la BDD et dans le fichier de log."""
    app.logger.info(f"{username} - {action}")
    entry = LogEntry(username=username, action=action)
    db.session.add(entry)
    db.session.commit()

def generate_6_digit_code():
    """Génère un code à 6 chiffres aléatoire pour le 2FA."""
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def is_logged_in():
    """Retourne True si l'utilisateur est connecté et a validé le 2FA."""
    return session.get("user_id") is not None and session.get("two_factor_validated") is True

def is_admin():
    """Retourne True si l'utilisateur a le rôle 'admin'."""
    return session.get("role") == "admin"

# ----------------------------
# ROUTES
# ----------------------------
@app.route("/")
def index():
    """Page d'accueil, accessible uniquement si l'utilisateur est connecté."""
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("welcome.html", username=session.get("username"), role=session.get("role"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Connexion utilisateur (étape 1 : vérification username/mot de passe, puis envoi du code 2FA)."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # Génération du code 2FA (valable 5 minutes)
            code = generate_6_digit_code()
            user.two_factor_code = code
            user.two_factor_expiration = datetime.utcnow() + timedelta(minutes=5)
            db.session.commit()
            # Envoi du code par email (si l'utilisateur a un email)
            if user.email:
                msg = Message("Votre code de connexion à 6 chiffres", recipients=[user.email])
                msg.body = f"Bonjour {user.username},\n\nVoici votre code de connexion : {code}\n\nIl expirera dans 5 minutes."
                mail.send(msg)
            # Sauvegarde de l'ID de l'utilisateur en pré-2FA
            session["pre_2fa_user_id"] = user.id
            log_action(username, "Login attempt (password OK). Code 2FA envoyé.")
            return redirect(url_for("two_factor"))
        else:
            flash("Identifiants invalides.")
            log_action(username, "Login attempt FAILED")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/two_factor", methods=["GET", "POST"])
def two_factor():
    """Vérification du code 2FA envoyé par email."""
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        return redirect(url_for("login"))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("login"))
    if request.method == "POST":
        code = request.form["code"]
        if (user.two_factor_code == code) and (user.two_factor_expiration > datetime.utcnow()):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session["two_factor_validated"] = True
            # Réinitialisation du code 2FA
            user.two_factor_code = None
            user.two_factor_expiration = None
            db.session.commit()
            log_action(user.username, "2FA validated. User logged in.")
            return redirect(url_for("index"))
        else:
            flash("Code invalide ou expiré.")
            log_action(user.username, "2FA FAILED")
            return render_template("two_factor.html")
    return render_template("two_factor.html")

@app.route("/logout")
def logout():
    """Déconnexion de l'utilisateur."""
    if is_logged_in():
        log_action(session["username"], "Logout")
    session.clear()
    flash("Vous êtes déconnecté.")
    return redirect(url_for("login"))

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Envoi d'un lien de réinitialisation de mot de passe par email."""
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
            reset_link = url_for("reset_password", token=token, _external=True)
            session["reset_token"] = token
            session["reset_user_id"] = user.id
            msg = Message("Réinitialisation de mot de passe", recipients=[user.email])
            msg.body = (
                f"Bonjour {user.username},\n\n"
                f"Pour réinitialiser votre mot de passe, cliquez sur ce lien : {reset_link}\n"
                "Ce lien est valable quelques minutes."
            )
            mail.send(msg)
            flash("Un email vous a été envoyé pour réinitialiser votre mot de passe.")
            log_action(user.username, "Password reset requested. Email sent.")
        else:
            flash("Aucun utilisateur n'existe avec cet email.")
    return render_template("forgot_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Réinitialisation du mot de passe via le lien envoyé par email."""
    saved_token = session.get("reset_token")
    user_id = session.get("reset_user_id")
    if not saved_token or token != saved_token or not user_id:
        flash("Lien invalide ou expiré.")
        return redirect(url_for("login"))
    user = User.query.get(user_id)
    if not user:
        flash("Utilisateur introuvable.")
        return redirect(url_for("login"))
    if request.method == "POST":
        new_password = request.form["new_password"]
        if len(new_password) < 4:
            flash("Mot de passe trop court.")
            return render_template("reset_password.html")
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        session.pop("reset_token", None)
        session.pop("reset_user_id", None)
        flash("Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.")
        log_action(user.username, "Password reset successfully.")
        return redirect(url_for("login"))
    return render_template("reset_password.html")

@app.route("/admin_panel")
def admin_panel():
    """Accès réservé à l'administrateur pour visualiser les utilisateurs et logs."""
    if not is_logged_in():
        flash("Vous devez être connecté.")
        return redirect(url_for("login"))
    if not is_admin():
        flash("Accès refusé. Rôle admin requis.")
        log_action(session["username"], "Attempted access to admin_panel - DENIED")
        return redirect(url_for("index"))
    log_action(session["username"], "Accessed admin_panel")
    users = User.query.all()
    logs = LogEntry.query.order_by(LogEntry.timestamp.desc()).limit(50).all()
    return render_template("admin_panel.html", users=users, logs=logs)

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
