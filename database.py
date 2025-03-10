import sqlite3

DB_NAME = "posts.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            id_google TEXT,
            date TEXT NOT NULL,
            cover_google_id TEXT NOT NULL
            
        )
    """)

    conn.commit()
    conn.close()
    
    return print("✅ Tabla 'posts' creada exitosamente.")

def add_column(new_column):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
                   ALTER TABLE posts ADD COLUMN cover {} TEXT""".format(new_column)
                   )

    conn.commit()
    conn.close()
    
    return print("✅ Columna '{}' agregada exitosamente a la tabla 'posts'.".format(new_column))
    
if __name__ == "__main__":
    create_database()
    # add_column("cover_google_id")
    print("📦 Base de datos creada exitosamente.")
