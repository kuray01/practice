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
    
    # Получаем историю и калории за сегодня
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

@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Все поля должны быть заполнены'})
        
        # Проверяем текущий пароль
        if not check_user(session['user_id'], current_password):
            return jsonify({'success': False, 'message': 'Неверный текущий пароль'})
        
        success, message = update_user_password(session['user_id'], new_password)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        logger.error(f'Ошибка при обновлении пароля: {str(e)}')
        return jsonify({'success': False, 'message': 'Произошла ошибка при обновлении пароля'})

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal_route():
    try:
        data = request.get_json()
        message = add_meal(
            session['user_id'],  # email
            data.get('meal_name'),
            data.get('category'),
            int(data.get('calories'))
        )
        
        if "Успешно" in message:
            # Получаем обновленные данные пользователя
            updated_user = get_user_data(session['user_id'])
            return jsonify({
                'success': True,
                'message': message,
                'calories_today': updated_user['calories_today']
            })
        return jsonify({'success': False, 'message': message})
    except Exception as e:
        logger.error(f'Ошибка при добавлении еды: {str(e)}')
        return jsonify({'success': False, 'message': 'Произошла ошибка при добавлении еды'})

@app.route('/add_weight', methods=['POST'])
@login_required
def add_weight_route():
    try:
        data = request.get_json()
        weight = data.get('weight')
        
        if weight is None:
            return jsonify({'success': False, 'message': 'Вес не может быть пустым'})
            
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Вес должен быть числом'})
            
        if weight <= 0:
            return jsonify({'success': False, 'message': 'Вес должен быть положительным числом'})
        
        message = add_weight_stat(
            session['user_id'],  # email
            weight
        )
        
        if "Успешно" in message:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message})
    except Exception as e:
        logger.error(f'Ошибка при добавлении веса: {str(e)}')
        return jsonify({'success': False, 'message': 'Произошла ошибка при добавлении веса'})

@app.route('/get_history')
@login_required
def get_history():
    try:
        history = get_user_history(session['user_id'])  # email
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f'Ошибка при получении истории: {str(e)}')
        return jsonify({'success': False, 'message': 'Произошла ошибка при получении истории'})

@app.route('/add_recipe', methods=['POST'])
def add_recipe_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})
    
    data = request.get_json()
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    
    if not all([title, ingredients, instructions]):
        return jsonify({'success': False, 'message': 'Все поля обязательны для заполнения'})
    
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Добавляем рецепт
        cursor.execute("""
            INSERT INTO Recipes (user_id, title, ingredients, instructions, created_at)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (user_id, title, ingredients, instructions))
        
        conn.commit()
        recipe_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        
        return jsonify({
            'success': True,
            'message': 'Рецепт успешно добавлен',
            'recipe_id': recipe_id
        })
    except Exception as e:
        logger.error(f"Ошибка при добавлении рецепта: {str(e)}")
        return jsonify({'success': False, 'message': 'Произошла ошибка при добавлении рецепта'})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/get_recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_route(recipe_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})
    
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Получаем рецепт
        cursor.execute("""
            SELECT id, title, ingredients, instructions, created_at
            FROM Recipes
            WHERE id = ? AND user_id = ?
        """, (recipe_id, user_id))
        
        recipe = cursor.fetchone()
        if not recipe:
            return jsonify({'success': False, 'message': 'Рецепт не найден'})
        
        return jsonify({
            'success': True,
            'recipe': {
                'id': recipe[0],
                'title': recipe[1],
                'ingredients': recipe[2],
                'instructions': recipe[3],
                'created_at': recipe[4].strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        logger.error(f"Ошибка при получении рецепта: {str(e)}")
        return jsonify({'success': False, 'message': 'Произошла ошибка при получении рецепта'})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/update_recipe', methods=['POST'])
def update_recipe_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})
    
    data = request.get_json()
    recipe_id = data.get('id')
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    
    if not all([recipe_id, title, ingredients, instructions]):
        return jsonify({'success': False, 'message': 'Все поля обязательны для заполнения'})
    
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Обновляем рецепт
        cursor.execute("""
            UPDATE Recipes
            SET title = ?, ingredients = ?, instructions = ?
            WHERE id = ? AND user_id = ?
        """, (title, ingredients, instructions, recipe_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Рецепт не найден или нет прав на редактирование'})
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Рецепт успешно обновлен'})
    except Exception as e:
        logger.error(f"Ошибка при обновлении рецепта: {str(e)}")
        return jsonify({'success': False, 'message': 'Произошла ошибка при обновлении рецепта'})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/delete_recipe/<int:recipe_id>', methods=['DELETE'])
def delete_recipe_route(recipe_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})
    
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Удаляем рецепт
        cursor.execute("""
            DELETE FROM Recipes
            WHERE id = ? AND user_id = ?
        """, (recipe_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Рецепт не найден или нет прав на удаление'})
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Рецепт успешно удален'})
    except Exception as e:
        logger.error(f"Ошибка при удалении рецепта: {str(e)}")
        return jsonify({'success': False, 'message': 'Произошла ошибка при удалении рецепта'})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/get_user_recipes', methods=['GET'])
def get_user_recipes_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})
    
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Получаем все рецепты пользователя
        cursor.execute("""
            SELECT id, title, ingredients, instructions, created_at
            FROM Recipes
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        recipes = []
        for row in cursor.fetchall():
            recipes.append({
                'id': row[0],
                'title': row[1],
                'ingredients': row[2],
                'instructions': row[3],
                'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'recipes': recipes
        })
    except Exception as e:
        logger.error(f"Ошибка при получении рецептов: {str(e)}")
        return jsonify({'success': False, 'message': 'Произошла ошибка при получении рецептов'})
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/get_user_history', methods=['GET'])
@login_required
def get_user_history_route():
    try:
        history = get_user_history(session['user_id'])
        return jsonify(history)
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {str(e)}")
        return jsonify([])

@app.route('/update_meal/<int:meal_id>', methods=['POST'])
@login_required
def update_meal_route(meal_id):
    try:
        data = request.get_json()
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=SapphireSite;'
                              'Trusted_Connection=yes')
        cursor = conn.cursor()
        
        # Получаем user_id из email
        cursor.execute("SELECT id FROM Users WHERE email = ?", (session['user_id'],))
        user_id = cursor.fetchone()[0]
        
        # Обновляем приём пищи
        cursor.execute("""
            UPDATE Meals
            SET name = ?, category = ?, calories = ?
            WHERE id = ? AND user_id = ?
        """, (data.get('name'), data.get('category'), int(data.get('calories')), meal_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Приём пищи не найден или нет прав на его редактирование'})
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Приём пищи успешно обновлен'})
    except Exception as e:
        logger.error(f"Ошибка при обновлении приёма пищи: {str(e)}")
        return jsonify({'success': False, 'message': 'Ошибка при обновлении приёма пищи'})
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)

