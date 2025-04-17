import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

def get_connection():
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=localhost;'
                          'DATABASE=SapphireSite;'
                          'Trusted_Connection=yes')

def register_user(email, password, name, birth_date, weight, height, lifestyle, goal):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь с таким email
        cursor.execute("SELECT COUNT(*) FROM Users WHERE email = ?", (email,))
        if cursor.fetchone()[0] > 0:
            return False, "Пользователь с таким email уже существует"
        
        # Хэшируем пароль
        hashed_password = generate_password_hash(password)
        
        # Вычисляем ИМТ
        imt = weight / ((height / 100) ** 2)
        
        # Вычисляем целевые калории (примерный расчет)
        daily_calorie_target = 0
        if goal == 'lose':
            daily_calorie_target = int(weight * 30 - 500)  # Для похудения
        elif goal == 'gain':
            daily_calorie_target = int(weight * 30 + 500)  # Для набора веса
        else:
            daily_calorie_target = int(weight * 30)  # Для поддержания веса
        
        # Добавляем пользователя
        cursor.execute("""
            INSERT INTO Users (email, password_hash, name, birth_date, weight, height, 
                              Lifestyle, Goal, DailyCalorieTarget, IMT, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (email, hashed_password, name, birth_date, weight, height, 
              lifestyle, goal, daily_calorie_target, imt))
        
        conn.commit()
        return True, "Регистрация успешна"
    except Exception as e:
        return False, f"Ошибка при регистрации: {str(e)}"
    finally:
        conn.close()

def check_user(email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM Users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result and check_password_hash(result[0], password):
            return True
        return False
    except Exception:
        return False
    finally:
        conn.close()

def get_user_data(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, birth_date, weight, height, Lifestyle, Goal, 
                   DailyCalorieTarget, IMT
            FROM Users 
            WHERE email = ?
        """, (email,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'birth_date': result[2],
                'weight': result[3],
                'height': result[4],
                'lifestyle': result[5],
                'goal': result[6],
                'daily_calorie_target': result[7],
                'imt': result[8]
            }
        return None
    except Exception:
        return None
    finally:
        conn.close() 