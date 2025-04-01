import sqlite3

# Ouvrir la base de données (le fichier app.db doit être dans le même dossier)
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Afficher la liste des tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables dans la base de données :")
for table in tables:
    print(table[0])

# Par exemple, pour afficher les utilisateurs dans la table User
print("\nContenu de la table users :")
cursor.execute("SELECT * FROM users;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
