import sqlite3
import json

DB_NAME = "posts.db"
JSON_FILE = "posts.json"

# Conectar a la base de datos
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        cover TEXT,
        id_google TEXT
    )
""")

# Leer el JSON
with open(JSON_FILE, "r", encoding="utf-8") as file:
    posts = json.load(file)

# Insertar posts en la base de datos
for post in posts:
    try:
        cursor.execute("""
            INSERT INTO posts (title, slug, date, cover_google_id, id_google)
            VALUES (?, ?, ?, ?, ?)
        """, (
            post["title"],
            post["slug"],
            post["date"],
            post["cover_google_id"],
            post.get("id_google", None)
            
        ))
        print(f"✅ Post '{post['title']}' insertado correctamente")
    except sqlite3.IntegrityError:
        print(f"⚠ Post '{post['title']}' ya existe en la base de datos, omitiendo...")

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("📌 Carga de datos completada.")
