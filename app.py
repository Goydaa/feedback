from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key-123' # Нужно для работы сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Куда перекидывать, если доступа нет

# Модель пользователя для авторизации
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Модель отзывов
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

# Создание базы данных (если её еще нет)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    reviews = Review.query.all()
    return render_template('index.html', reviews=reviews)

@app.route('/leave_review', methods=['GET', 'POST'])
def leave_review():
    if request.method == 'POST':
        author = request.form.get('author')
        text = request.form.get('text')
        if author and text:
            new_review = Review(author=author, text=text)
            db.session.add(new_review)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('leave_review.html')

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Простейшая проверка (замени на свои данные при желании)
        if username == 'admin' and password == 'admin':
            user = User(id=1)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            return "Неверный логин или пароль", 401
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Логин">
            <input type="password" name="password" placeholder="Пароль">
            <button type="submit">Войти</button>
        </form>
    '''

# ЗАЩИЩЕННАЯ АДМИНКА
@app.route('/admin')
@login_required # Тот самый замок!
def admin():
    reviews = Review.query.all()
    return render_template('admin.html', reviews=reviews)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
