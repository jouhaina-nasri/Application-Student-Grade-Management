# Flask User Management System

A simple Flask web application that includes:

- Authentication (login, logout, register)
- User Management (add, edit, block)
- Role-based access (admin, professor, monitor, student)
- Bootstrap UI + dynamic modals
- Templates using Jinja2
- MySQL/PostgreSQL/SQLite support
  
---

## ▶️ Running the Project

### 1. Create virtual environment
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

### 2. Install dependencies
pip install -r requirements.txt


### 3. Run the app
python run.py

---

## ⚙️ Environment Variables

Create a `.env` file:

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=mysql://user:password@localhost/dbname


---

## 📦 Deployment (Gunicorn)

gunicorn -w 4 run:app


---

## 👤 Author

Jouhaina Nasri  
📧 jouhainanasri50@gmail.com  
