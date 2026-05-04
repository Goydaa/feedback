import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__, instance_path=instance_path)
app.config['SECRET_KEY'] = 'secure-key-v4-priority'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'feedback_v4.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- МОДЕЛИ ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='category', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- ИНИЦИАЛИЗАЦИЯ ---
with app.app_context():
    db.create_all()
    if not Category.query.first():
        cats = ['Общие вопросы', 'Техподдержка', 'Предложения', 'Жалобы', 'Затрудняюсь ответить']
        for c in cats:
            db.session.add(Category(name=c))
        db.session.commit()

class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(user_id): return User(user_id)

# --- МАРШРУТЫ ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        author, email, text, cat_id = request.form.get('author'), request.form.get('email'), request.form.get('text'), request.form.get('category_id')
        if author and email and text and cat_id:
            db.session.add(Review(author=author, email=email, text=text, category_id=int(cat_id)))
            db.session.commit()
            flash('Сообщение отправлено!', 'success')
            return redirect(url_for('index'))
    return render_template('index.html', categories=Category.query.all())

@app.route('/admin')
@login_required
def admin():
    reviews = Review.query.order_by(Review.timestamp.desc()).all()
    
    # Обновленная логика приоритетов
    for r in reviews:
        if r.category.name in ['Техподдержка', 'Жалобы']:
            r.priority_color = 'danger'  # Красный
            r.priority_label = 'Высокий'
        elif r.category.name == 'Предложения':
            r.priority_color = 'warning' # Желтый
            r.priority_label = 'Средний'
        else:
            r.priority_color = 'success' # Зеленый 
            r.priority_label = 'Низкий'
            
    return render_template('admin.html', reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin':
            login_user(User(1)); return redirect(url_for('admin'))
        flash('Ошибка входа', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
