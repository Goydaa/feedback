import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-12345'

# Исправленная настройка путей для Render
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- МОДЕЛИ ДАННЫХ ---

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    reviews = db.relationship('Review', backref='category', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- СИСТЕМА ВХОДА ---

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- МАРШРУТЫ ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        author = request.form.get('author')
        text = request.form.get('text')
        cat_id = request.form.get('category_id')
        
        if author and text and cat_id:
            new_review = Review(author=author, text=text, category_id=int(cat_id))
            db.session.add(new_review)
            db.session.commit()
            flash('Отзыв успешно отправлен!', 'success')
            return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/admin')
@login_required
def admin():
    reviews = Review.query.order_by(Review.timestamp.desc()).all()
    return render_template('admin.html', reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin':
            login_user(User(id=1))
            return redirect(url_for('admin'))
        flash('Неверные данные!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ЗАПУСК И ИНИЦИАЛИЗАЦИЯ
if __name__ == '__main__':
    with app.app_context():
        # Создаем папку instance вручную, если её нет (решает ошибку 500 на Render)
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        db.create_all()
        
        # Наполняем категории, если база пуста
        if not Category.query.first():
            db.session.add_all([
                Category(name='Учебный процесс'),
                Category(name='Инфраструктура'),
                Category(name='Преподаватели')
            ])
            db.session.commit()
            
    app.run(debug=True)
