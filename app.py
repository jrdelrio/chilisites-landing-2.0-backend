from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlite3
import os
import requests
from dotenv import load_dotenv
import resend
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///posts.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Permitir solicitudes de dominios específicos
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:3000/", "https://chilisites.com"]}}, credentials=True)

DB_NAME = "posts.db"

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

db = SQLAlchemy(app)

# Ruta de prueba
@app.route("/test-connection", methods=["GET"])
def test_connection():
    return jsonify({"message": "API de ChiliSites funcionando correctamente 🚀"})

# Endpoint para obtener todos los posts
@app.route("/posts", methods=["GET"])
def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    limit = request.args.get("limit", type=int)
    order = request.args.get("order", type=str, default="desc").lower()
    
    # Validación de orden
    if order not in ["asc", "desc"]:
        order = "desc"
    
    query = f"SELECT * FROM posts ORDER BY date {order}"
    
    if limit:
        query += " LIMIT ?"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)
    
    posts = cursor.fetchall()
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

# Obtener un post por su slug
@app.route("/posts/<slug>", methods=["GET"])
def get_post(slug):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
    conn.close()

    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    return jsonify(dict(post)), 200

# Crear un nuevo post
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

# Actualizar un post
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

# Eliminar un post
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

@app.route("/send-email-thanks-for-contact", methods=["POST"])
def send_email_to_leed():
    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        data = request.json
        
        file_path = os.path.join(os.path.dirname(__file__), "templates", "thanks-email", "thanks-email.html")
        
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(file_path, "r", encoding="utf-8") as file:
            email_template = file.read()
            email_template = email_template.replace("{{from_name}}", data.get("fromName", ""))
            # email_template = email_template.replace("{{from_email}}", data.get("fromEmail", ""))
            # email_template = email_template.replace("{{from_message}}", data.get("fromMessage", ""))
            # email_template = email_template.replace("{{from_phone}}", data.get("fromPhone", ""))
            # email_template = email_template.replace("{{timestamp}}", timestamp)
        
            params = {
                "from": "Equipo 🌶️Chilisites <contacto@chilisites.com>",
                "to": request.json["fromEmail"],
                "subject": "Muchas gracias por el contacto!",
                "html": email_template
            }
        
        email = resend.Emails.send(params)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


    return {"email": email}

@app.route("/send-email-to-chilisites", methods=["POST"])
def send_email_to_chilisites():
    
    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        data = request.json
        
        file_path = os.path.join(os.path.dirname(__file__), "templates", "intern-email", "intern-email.html")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        possible_fields = {
            "{{from_name}}": data["fromName"], 
            "{{from_email}}": data["fromEmail"], 
            "{{from_phone}}": data["fromPhone"], 
            "{{from_type}}": data["fromType"], 
            "{{from_message}}": data["fromMessage"]
        }        
        
        with open(file_path, "r", encoding="utf-8") as file:
            email_template = file.read()
            
            for placeholder, value in possible_fields.items():
                email_template = email_template.replace(placeholder, value)
                
            email_template = email_template.replace("{{timestamp}}", timestamp)
            
            params = {
                "from": "contacto@chilisites.com",
                "to": ["contacto@chilisites.com"],
                "subject": "Contacto Chilisites Web",
                "html": email_template
            }
        
        email = resend.Emails.send(params)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
    return {"email": email}
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

