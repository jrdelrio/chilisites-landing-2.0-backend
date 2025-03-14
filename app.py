from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///posts.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3001,https://chilisites.com").split(",")
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

DB_NAME = "posts.db"

def get_db_connection():
    """Crea una conexión a la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


db = SQLAlchemy(app)

# Ruta de prueba
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API de ChiliSites funcionando correctamente 🚀"})

# ✅ Obtener todos los posts
@app.route("/posts", methods=["GET"])
def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    limit = request.args.get("limit", type=int)
    order = request.args.get("order", type=str, default="desc").lower()
    
    # Validar el orden
    if order not in ["asc", "desc"]:
        order = "desc"
    
    query = f"SELECT * FROM posts ORDER BY date {order}"
    
    if limit:
        query += " LIMIT ?"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)
    
    if limit:
        posts = cursor.execute(query, (limit,)).fetchall()
    else:
        posts = cursor.execute(query).fetchall()
    
    conn.close()
    
    post_list = []
    for post in posts:
        post_list.append({
            "id": post[0],
            "title": post[1],
            "slug": post[2],
            "date": post[3],
            "cover_google_id": post[4]
        })

    return jsonify([dict(post) for post in posts]), 200

# ✅ Obtener un post por su slug
@app.route("/posts/<slug>", methods=["GET"])
def get_post(slug):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
    conn.close()

    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    return jsonify(dict(post)), 200


# ✅ Crear un nuevo post
@app.route("/posts", methods=["POST"])
def create_post():
    data = request.json
    required_fields = ["title", "slug", "id_google", "date", "cover_google_id"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO posts (title, slug, date, cover_google_id, id_google) VALUES (?, ?, ?, ?, ?)",
            (data["title"], data["slug"], data["date"], data["cover_google_id"], data["id_google"]),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Registro en DB creado exitosamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El slug o id_google ya existen"}), 400

# ✅ Actualizar un post por su slug - ESTE ENDPOINT NO ESTA REVISADO
@app.route("/posts/<slug>", methods=["PUT"])
def update_post(slug):
    data = request.json
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()

    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    conn.execute(
        "UPDATE posts SET title = ?, date = ?, cover_google_id = ? WHERE slug = ?",
        (data.get("title", post["title"]),
         data.get("date", post["date"]), 
         post["cover_google_id"]),
        slug
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Post actualizado exitosamente"}), 200

# ✅ Eliminar un post por su slug
@app.route("/posts/<slug>", methods=["DELETE"])
def delete_post(slug):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()

    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    conn.execute("DELETE FROM posts WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Post eliminado exitosamente"}), 200

if __name__ == "__main__":
    app.run(debug=False)
