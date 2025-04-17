import pyodbc
import hashlib
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

logger = logging.getLogger(__name__)

def get_connection():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=localhost;'
                            'DATABASE=SapphireSite;'
                            'Trusted_Connection=yes')
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise

def register_user(email, password, name, birth_date, weight, height, lifestyle, goal):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование email
        cursor.execute("SELECT COUNT(*) FROM Users WHERE email = ?", (email,))
        if cursor.fetchone()[0] > 0:
            return False, "Пользователь с таким email уже существует"
        
        # Проверяем ограничения
        if not (120 <= height <= 220):
            return False, "Рост должен быть от 120 до 220 см"
        if not (12 <= weight <= 90):
            return False, "Вес должен быть от 12 до 90 кг"
        
        # Хешируем пароль
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
        return True, "Регистрация успешно завершена"
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        return False, "Произошла ошибка при регистрации"
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")

def check_user(email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM Users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result and check_password_hash(result[0], password):
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке пользователя: {e}")
        return False
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")

def get_calories_today(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        user_id_row = cursor.fetchone()
        if not user_id_row:
            return 0
        
        user_id = user_id_row[0]
        
        # Получаем сумму калорий за сегодня
        cursor.execute("""
            SELECT ISNULL(SUM(calories), 0) as total_calories
            FROM Meals
            WHERE user_id = ? AND CAST(meal_date AS DATE) = CAST(GETDATE() AS DATE)
        """, (user_id,))
        
        result = cursor.fetchone()
        return result.total_calories if result else 0
    except Exception as e:
        logger.error(f"Ошибка при получении калорий за сегодня: {str(e)}")
        return 0
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_data(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        user_id_row = cursor.fetchone()
        if not user_id_row:
            return None
        
        user_id = user_id_row[0]
        
        # Получаем основные данные пользователя
        cursor.execute("""
            SELECT email, name, birth_date, weight, height, Lifestyle, Goal, 
                   IMT, DailyCalorieTarget
            FROM Users WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        if row:
            # Получаем калории за сегодня
            calories_today = get_calories_today(email)
            
            return {
                'email': row[0],
                'name': row[1],
                'birth_date': row[2],
                'weight': row[3],
                'height': row[4],
                'lifestyle': row[5],
                'goal': row[6],
                'imt': row[7],
                'daily_calorie_target': row[8],
                'calories_today': calories_today
            }
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя: {e}")
        return None
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")

def update_user_name(email, new_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE Users SET name = ? WHERE email = ?", (new_name, email))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Имя успешно обновлено"
        return False, "Пользователь не найден"
    except Exception as e:
        logger.error(f"Ошибка при обновлении имени: {e}")
        return False, "Произошла ошибка при обновлении имени"
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")

def update_user_password(email, new_password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE Users SET password_hash = ? WHERE email = ?", 
                      (hashed_password, email))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Пароль успешно обновлен"
        return False, "Пользователь не найден"
    except Exception as e:
        logger.error(f"Ошибка при обновлении пароля: {e}")
        return False, "Произошла ошибка при обновлении пароля"
    finally:
        if 'conn' in locals():
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")

def get_user_meals(user_id, date=None):
    """Получить приёмы пищи пользователя за определенную дату"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if date:
            cursor.execute("""
                SELECT id, name, category, calories, meal_date 
                FROM Meals 
                WHERE user_id = ? AND CAST(meal_date AS DATE) = CAST(? AS DATE)
                ORDER BY meal_date DESC
            """, (user_id, date))
        else:
            cursor.execute("""
                SELECT id, name, category, calories, meal_date 
                FROM Meals 
                WHERE user_id = ? AND CAST(meal_date AS DATE) = CAST(GETDATE() AS DATE)
                ORDER BY meal_date DESC
            """, (user_id,))
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'calories': row[3],
                'meal_date': row[4]
            })
        return meals
    except Exception as e:
        logger.error(f"Ошибка при получении приёмов пищи: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_meal(email, name, category, calories):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        user_id_row = cursor.fetchone()
        if not user_id_row:
            return "Пользователь не найден"
        
        user_id = user_id_row[0]
        
        # Добавляем прием пищи
        cursor.execute("""
            INSERT INTO Meals (user_id, name, category, calories, meal_date)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (user_id, name, category, calories))
        
        conn.commit()
        return "Прием пищи успешно добавлен"
    except Exception as e:
        logger.error(f"Ошибка при добавлении приема пищи: {str(e)}")
        return "Произошла ошибка при добавлении приема пищи"
    finally:
        if 'conn' in locals():
            conn.close()

def get_weight_stats(user_id, limit=10):
    """Получить статистику веса пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT weight, weigh_date 
            FROM WeightStats 
            WHERE user_id = ?
            ORDER BY weigh_date DESC
            OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
        """, (user_id, limit))
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                'weight': row[0],
                'date': row[1]
            })
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении статистики веса: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_weight_stat(email, weight):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        user_id_row = cursor.fetchone()
        if not user_id_row:
            return "Пользователь не найден"
        
        user_id = user_id_row[0]
        
        # Проверяем ограничения
        if not (12 <= weight <= 90):
            return "Вес должен быть от 12 до 90 кг"
        
        # Добавляем запись о весе
        cursor.execute("""
            INSERT INTO WeightStats (user_id, weight, weigh_date)
            VALUES (?, ?, GETDATE())
        """, (user_id, weight))
        
        conn.commit()
        return "Вес успешно добавлен"
    except Exception as e:
        logger.error(f"Ошибка при добавлении веса: {str(e)}")
        return "Произошла ошибка при добавлении веса"
    finally:
        if 'conn' in locals():
            conn.close()

def init_db():
    """Инициализация базы данных"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Создаем таблицу пользователей
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' and xtype='U')
        CREATE TABLE Users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL,
            birth_date DATE,
            weight FLOAT,
            height FLOAT,
            lifestyle VARCHAR(50),
            goal VARCHAR(50),
            IMT FLOAT,
            DailyCalorieTarget INT
        )
        """)
        
        # Создаем таблицу приёмов пищи
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Meals' and xtype='U')
        CREATE TABLE Meals (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            calories INT NOT NULL,
            meal_date DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        """)
        
        # Создаем таблицу статистики веса
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='WeightStats' and xtype='U')
        CREATE TABLE WeightStats (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT NOT NULL,
            weight FLOAT NOT NULL,
            weigh_date DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        """)
        
        conn.commit()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_user_history(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
        user_id_row = cursor.fetchone()
        if not user_id_row:
            return []
        
        user_id = user_id_row[0]
        
        # Получаем историю приемов пищи
        cursor.execute("""
            SELECT TOP 10 id, name, category, calories, meal_date
            FROM Meals
            WHERE user_id = ?
            ORDER BY meal_date DESC
        """, (user_id,))
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'calories': row[3],
                'date': row[4].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Получаем историю веса
        cursor.execute("""
            SELECT TOP 10 weight, weigh_date
            FROM WeightStats
            WHERE user_id = ?
            ORDER BY weigh_date DESC
        """, (user_id,))
        
        weights = []
        for row in cursor.fetchall():
            weights.append({
                'weight': row[0],
                'date': row[1].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Объединяем и сортируем историю
        history = meals + weights
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return history
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# Инициализируем базу данных при импорте модуля
init_db() 