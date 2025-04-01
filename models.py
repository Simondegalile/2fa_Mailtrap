# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Modèle représentant un utilisateur."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user", "admin", etc.
    two_factor_code = db.Column(db.String(6), nullable=True)  # 6 chiffres
    two_factor_expiration = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

class LogEntry(db.Model):
    """Modèle représentant une entrée de log."""
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Log {self.id} {self.action} at {self.timestamp}>"

