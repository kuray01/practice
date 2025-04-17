from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pyodbc
import logging
from database import register_user, check_user, get_user_data, update_user_name, update_user_password, get_user_meals, get_weight_stats, add_meal, add_weight_stat, get_user_history, get_calories_today
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Замените на реальный секретный ключ
app.debug = True

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        weight = request.form.get('weight')
        height = request.form.get('height')
        lifestyle = request.form.get('lifestyle')
        goal = request.form.get('goal')

        try:
            if password != confirm_password:
                return render_template('register.html', error="Пароли не совпадают")

            success, message = register_user(email, password, name, birth_date, weight, height, lifestyle, goal)
            if success:
                return redirect(url_for('login'))
            else:
                return render_template('register.html', error=message)
        except Exception as e:
            logger.error(f"Ошибка при регистрации: {str(e)}")
            return render_template('register.html', error="Произошла ошибка при регистрации")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('main'))
        return redirect(url_for('index'))
    
    try:
        email = request.form['email']
        password = request.form['password']
        
        if check_user(email, password):
            session['user_id'] = email
            return redirect(url_for('main'))
        else:
            flash('Неверный email или пароль', 'error')
    except Exception as e:
        logger.error(f'Ошибка при входе: {str(e)}')
        flash('Произошла ошибка при входе', 'error')
    
    return redirect(url_for('index'))

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_data(session['user_id'])
    if not user_data:
        session.pop('user_id', None)
        return redirect(url_for('login'))
    
    # Получаем историю и калории
    history = get_user_history(session['user_id'])
    calories_today = get_calories_today(session['user_id'])
    
    # Добавляем калории в данные пользователя
    user_data['calories_today'] = calories_today
    
    return render_template('main.html', 
                         user_data=user_data,
                         history=history)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
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
        logger.error(f"Ошибка при проверке email: {e}")
        return jsonify({'exists': False})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/update_name', methods=['POST'])
@login_required
def update_name():
    try:
        data = request.get_json()
        new_name = data.get('new_name')
        
        if not new_name:
            return jsonify({'success': False, 'message': 'Имя не может быть пустым'})
        
        success, message = update_user_name(session['user_id'], new_name)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        logger.error(f'Ошибка при обновлении имени: {str(e)}')
        return jsonify({'success': False, 'message': 'Произошла ошибка при обновлении имени'})

if __name__ == '__main__':
    app.run(debug=True) 