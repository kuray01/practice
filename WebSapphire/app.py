from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pyodbc
import logging
from database import register_user, check_user, get_user_data
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Замените на реальный секретный ключ
app.debug = True

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        birth_date = request.form['birth_date']
        weight = float(request.form['weight'])
        height = int(request.form['height'])
        lifestyle = request.form['lifestyle']
        goal = request.form['goal']
        
        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        # Регистрация пользователя
        success, message = register_user(email, password, name, birth_date, weight, height, lifestyle, goal)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    if check_user(email, password):
        session['user'] = email
        return redirect(url_for('main'))
    else:
        flash('Неверный email или пароль', 'error')
        return redirect(url_for('index'))

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/main')
def main():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    # Получаем данные пользователя
    user_data = get_user_data(session['user'])
    if not user_data:
        session.pop('user', None)
        flash('Ошибка получения данных пользователя', 'error')
        return redirect(url_for('index'))
    
    return render_template('main.html', user=user_data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/check_email')
def check_email():
    email = request.args.get('email')

    if not email:
        return jsonify({'exists': False})

    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE email = ?", (email,))
        result = cursor.fetchone()
        exists = result[0] > 0
        return jsonify({'exists': exists})
    except Exception as e:
        logging.error(f"Ошибка при проверке email: {e}")
        return jsonify({'exists': False})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

