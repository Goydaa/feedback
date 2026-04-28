import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists('database.db'):
        os.remove('database.db') # Гарантируем чистую базу при запуске скрипта
    conn = get_db_connection()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    
    if request.method == 'POST':
        category_id = request.form.get('category')
        email = request.form.get('email')
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not all([category_id, email, title, content]):
            return "<h3>Ошибка: Заполните все поля!</h3><a href='/'>Назад</a>"

        if len(content) < 10:
            return "<h3>Ошибка: Сообщение слишком короткое (мин. 10 симв).</h3><a href='/'>Назад</a>"
            
        # Приоритет 'Высокий' для категории 'Хозяйственные и тех. вопросы' (ID 2)
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
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True)