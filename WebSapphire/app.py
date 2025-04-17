from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pyodbc
import logging

app = Flask(__name__)
app.debug = True

try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=localhost;'
                          'DATABASE=SapphireSite;'
                          'Trusted_Connection=yes')
    print("Подключение к базе данных успешно.")
except Exception as e:
    print(f"Ошибка при подключении к базе данных: {e}")


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=localhost;'
                      'DATABASE=SapphireSite;'
                      'Trusted_Connection=yes')

cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Сохраняем все значения в сессию
        session['register_form'] = {
            'name': request.form.get('name'),
            'birth_date': request.form.get('birth_date'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'lifestyle': request.form.get('lifestyle'),
            'goal': request.form.get('goal'),
            'email': request.form.get('email')
        }

        # Дальше можешь проверить пароли и выполнить регистрацию
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            error = "Пароли не совпадают"
            return render_template('register.html', **session['register_form'], error=error)

        # ... регистрация в БД

        session.pop('register_form', None)  # очищаем данные из сессии
        return redirect(url_for('main'))

    # При GET — получаем данные из сессии
    form_data = session.get('register_form', {})

    return render_template('register.html', **form_data)

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/check_email')
def check_email():
    email = request.args.get('email')

    if not email:
        return jsonify({'exists': False})

    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    exists = result[0] > 0
    return jsonify({'exists': exists})

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(debug=True)

