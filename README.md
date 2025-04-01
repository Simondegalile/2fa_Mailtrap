2FA Mailtrap Project 🔐✉️
Bienvenue sur le dépôt 2FA Mailtrap Project !
Ce projet est une application web développée en Flask qui implémente une authentification à double facteur (2FA), la réinitialisation du mot de passe par email et un panneau d'administration pour gérer les utilisateurs et les logs. Les emails sont envoyés via Mailtrap pour tester la fonctionnalité sans envoyer de vrais emails.

🚀 Fonctionnalités
Authentification Sécurisée : Connexion avec username/password et vérification via un code à 6 chiffres envoyé par email.

Réinitialisation du Mot de Passe : Envoi d'un lien de réinitialisation de mot de passe par email.

Panneau Administrateur : Accès réservé pour visualiser la liste des utilisateurs et les logs.

Gestion des Sessions : Utilisation de Flask-Session et d'une clé secrète pour sécuriser les sessions.

Logs d'Activité : Enregistrement des actions importantes dans la base de données et dans un fichier de log.

🔧 Technologies Utilisées
Flask – Framework web Python

Flask-Mail – Envoi d'emails

Flask-Session – Gestion des sessions côté serveur

Flask-SQLAlchemy – ORM pour la base de données (SQLite)

python-dotenv – Gestion des variables d'environnement

⚙️ Installation et Lancement
Prérequis
Python 3.12 (ou une version compatible)

pip (le gestionnaire de packages Python)

Étapes
Cloner le dépôt :

bash
Copier
git clone https://github.com/Simondegalile/2fa_Mailtrap.git
cd 2fa_Mailtrap
Créer un environnement virtuel (recommandé) :

bash
Copier
python -m venv venv
# Sur Windows :
venv\Scripts\activate
# Sur Linux/Mac :
source venv/bin/activate
Installer les dépendances :

bash
Copier
pip install -r requirements.txt
Configurer les variables d'environnement :
Crée un fichier .env à la racine du projet avec le contenu suivant :

dotenv
Copier
SECRET_KEY=8705ce5c93edb54f7e9b83ca1bdb5ba3
MAIL_USERNAME=3016fb5ab06aba
MAIL_PASSWORD=fe40f30e5bab85
Important : Pour des raisons de sécurité, je ne peux pas partager mes identifiants Mailtrap. Vous devez créer un compte gratuit sur Mailtrap et utiliser vos propres identifiants.

Lancer l'application :

bash
Copier
python app.py
L'application sera accessible à http://127.0.0.1:5000.

🛠️ Dépannage
Clé secrète non définie :
Assurez-vous que le fichier .env est bien à la racine et que la variable SECRET_KEY y est définie. Flask lira cette clé pour sécuriser les sessions.

Problème d'envoi d'email :
Pour tester l'envoi d'emails, mettez à jour vos identifiants Mailtrap dans le fichier .env. Si vous souhaitez tester avec un autre SMTP, modifiez la configuration dans config.py.

Sessions indisponibles :
Vérifiez que SESSION_TYPE est bien défini (dans notre cas, "filesystem") et que la clé secrète est correctement chargée dans l'application.

🤝 Contribuer
Les contributions sont les bienvenues !
N'hésitez pas à forker ce dépôt, apporter des améliorations et soumettre vos pull requests.

📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

📫 Contact
Pour toute question ou suggestion, vous pouvez me contacter à simonalmeidadasilva@gmail.com.
