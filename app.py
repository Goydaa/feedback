import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Определяем пути
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("Инициализация базы данных...")
    conn = get_db_connection()
    with open(os.path.join(basedir, 'schema.sql'), 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()
    print("База данных успешно создана.")

# --- ВАЖНЫЙ БЛОК ДЛЯ ОБЛАКА ---
# Этот код сработает ПРИ КАЖДОМ запуске сервера (даже на Railway)
with app.app_context():
    if not os.path.exists(db_path):
        init_db()
# ------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    # Проверка: если таблиц нет (на всякий случай), пробуем создать
    try:
        categories = conn.execute('SELECT * FROM categories').fetchall()
    except sqlite3.OperationalError:
        conn.close()
        init_db()
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories').fetchall()
    
    if request.method == 'POST':
        category_id = request.form.get('category')
        email = request.form.get('email')
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not all([category_id, email, title, content]):
            conn.close()
            return "<h3>Ошибка: Заполните все поля!</h3><a href='/'>Назад</a>"

        if len(content) < 10:
            conn.close()
            return "<h3>Ошибка: Сообщение слишком короткое.</h3><a href='/'>Назад</a>"
            
        priority = 'Высокий' if category_id == '2' else 'Средний'
        
        conn.execute('INSERT INTO feedback (category_id, email, title, content, priority) VALUES (?, ?, ?, ?, ?)',
                     (category_id, email, title, content, priority))
        conn.commit()
        conn.close()
        return f"<h3>Успех! Ответ придет на {email}</h3><a href='/'>Вернуться</a>"

    conn.close()
    return render_template('index.html', categories=categories)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    feedbacks = conn.execute('''
        SELECT f.*, c.name as cat_name 
        FROM feedback f 
        JOIN categories c ON f.category_id = c.id
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
