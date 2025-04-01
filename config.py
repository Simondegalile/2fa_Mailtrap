# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ma_cle_secrete_de_dev")
    SESSION_TYPE = "filesystem"

    # Base de données
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration Mailtrap
    MAIL_SERVER = "sandbox.smtp.mailtrap.io"   # Hôte fourni par Mailtrap
    MAIL_PORT = 2525                           # Port recommandé (TLS)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "3016fb5ab06aba")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "fe40f30e5bab85")
    MAIL_DEFAULT_SENDER = "from@example.com"   # L'adresse 'From' par défaut
