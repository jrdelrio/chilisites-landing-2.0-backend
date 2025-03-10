# 🌶️ Chilisites Blog Backend 🚀

Este es el backend del blog de **Chilisites**, construido con **Flask** y utilizando **SQLite** como base de datos. Permite gestionar y servir los posts del blog de manera eficiente, además de manejar la subida de imágenes y archivos Markdown.

---

## 📌 **Tecnologías utilizadas**

-   **Python 3**
-   **Flask** - Framework para el backend
-   **SQLite3** - Base de datos ligera
-   **SQLAlchemy** - ORM para manejar la base de datos
-   **Flask-CORS** - Para manejar peticiones desde el frontend
-   **Google Drive API** (próximamente) - Para almacenar imágenes y archivos Markdown

---

## 🚀 **Cómo instalar y ejecutar el backend**

### **1️⃣ Clonar el repositorio**

```bash
git clone https://github.com/jrdelrio/chilisites-landing-2.0-backend.git
cd chilisites-landing-2.0-backend
```

### **2️⃣ Crear y activar el entorno virtual**

```bash
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
venv\Scripts\activate      # En Windows
```

### **3️⃣ Instalar dependencias**

```bash
pip install -r requirements.txt
```

### **4️⃣ Crear la base de datos**

```bash
python database.py
```

### **5️⃣ Ejecutar el servidor**

```bash
python app.py
```

### **📂 Estructura del proyecto**

```bash
/chilisites-landing-2.0-backend
│── /static/                 # Carpeta para imágenes y archivos subidos (opcional)
│── /templates/              # Carpeta para templates de Flask (si se usa)
│── /instance/               # Carpeta donde se almacenará SQLite (ignorada en el repo)
│── app.py                   # Archivo principal con las rutas del backend
│── database.py              # Inicialización de la base de datos SQLite
│── models.py                # Definición de modelos de la base de datos con SQLAlchemy
│── requirements.txt         # Lista de dependencias
│── .gitignore               # Ignora archivos innecesarios como la base de datos
│── README.md                # Este archivo 📄
```
