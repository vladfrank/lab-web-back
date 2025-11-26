from flask import Blueprint, render_template, request, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

def db_connect():
    """
    Универсальная функция для подключения к базе данных
    Работает с PostgreSQL и SQLite3 в зависимости от конфигурации
    """
    if current_app.config.get('DB_TYPE') == 'postgres':
        # Подключение к PostgreSQL
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='vlad_frank_knowledge_base',
            user='vlad_frank_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # Подключение к SQLite3 (по умолчанию)
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur

def db_close(conn, cur):
    """
    Универсальная функция для закрытия соединения с базой данных
    """
    conn.commit()
    cur.close()
    conn.close()

def init_offices_table():
    """
    Инициализация таблицы offices для обеих СУБД
    """
    conn, cur = db_connect()
    
    try:
        # Создаем таблицу offices, если она не существует
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('''
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER
                )
            ''')
        else:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER
                )
            ''')
        
        # Проверяем, есть ли уже данные в таблице
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT COUNT(*) FROM offices')
        else:
            cur.execute('SELECT COUNT(*) FROM offices')
        
        count = cur.fetchone()[0]
        
        # Если таблица пустая, заполняем начальными данными
        if count == 0:
            offices_data = []
            for i in range(1, 11):
                price = 900 + i % 3 * 100  # Стоимость: 900, 1000, 1100
                offices_data.append((i, '', price))
            
            # Вставляем начальные данные
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.executemany(
                    'INSERT INTO offices (number, tenant, price) VALUES (%s, %s, %s)',
                    offices_data
                )
            else:
                cur.executemany(
                    'INSERT INTO offices (number, tenant, price) VALUES (?, ?, ?)',
                    offices_data
                )
            print("Таблица offices инициализирована с начальными данными")
        
    except Exception as e:
        print(f"Ошибка при инициализации таблицы offices: {e}")
    finally:
        db_close(conn, cur)

@lab6.route('/lab6/')
def main():
    """
    Основной маршрут для отображения страницы аренды офисов
    """
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    """
    JSON-RPC API endpoint для обработки операций с офисами
    Поддерживаемые методы: info, booking, cancellation
    Работает с обеими СУБД: PostgreSQL и SQLite3
    """
    # Инициализируем таблицу при первом обращении
    init_offices_table()
    
    data = request.json
    id = data['id']  # ID запроса для соответствия JSON-RPC спецификации
    
    # Метод info - получение информации о всех офисах
    if data['method'] == 'info':
        try:
            conn, cur = db_connect()
            
            # Получаем список всех офисов
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute('SELECT number, tenant, price FROM offices ORDER BY number')
            else:
                cur.execute('SELECT number, tenant, price FROM offices ORDER BY number')
            
            offices = cur.fetchall()

            login = session.get('login')
            
            # Конвертируем результаты в список словарей для JSON
            offices_list = []
            for office in offices:
                offices_list.append({
                    'number': office['number'],
                    'tenant': office['tenant'],
                    'price': office['price']
                })
            
            db_close(conn, cur)
            
            # Возвращаем успешный ответ с данными об офисах
            return {
                'jsonrpc': '2.0',
                'result': {offices_list: offices_list, login: login},
                'id': id,
            }
        except Exception as e:
            # Обработка ошибок базы данных
            if 'conn' in locals():
                db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': f'Database error: {str(e)}'
                },
                'id': id
            }
    
    # Проверка авторизации пользователя для методов, требующих авторизации
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }

    # Метод booking - бронирование офиса
    if data['method'] == 'booking':
        office_number = data['params']  # Номер офиса из параметров запроса
        try:
            conn, cur = db_connect()
            
            # Проверяем, существует ли офис с таким номером
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute('SELECT tenant FROM offices WHERE number = %s', (office_number,))
            else:
                cur.execute('SELECT tenant FROM offices WHERE number = ?', (office_number,))
            
            result = cur.fetchone()
            
            if not result:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 5,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            # Проверяем, свободен ли офис (tenant пустой)
            if result['tenant'] != '':
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 2,
                        'message': 'Already booked'
                    },
                    'id': id
                }
            
            # Бронируем офис за текущим пользователем
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute('UPDATE offices SET tenant = %s WHERE number = %s', (login, office_number))
            else:
                cur.execute('UPDATE offices SET tenant = ? WHERE number = ?', (login, office_number))
            
            db_close(conn, cur)
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            # Обработка ошибок
            if 'conn' in locals():
                db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': f'Database error: {str(e)}'
                },
                'id': id
            }
        
    # Метод cancellation - отмена бронирования офиса
    if data['method'] == 'cancellation':
        office_number = data['params']  # Номер офиса из параметров запроса
        try:
            conn, cur = db_connect()
            
            # Получаем информацию о текущем арендаторе офиса
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute('SELECT tenant FROM offices WHERE number = %s', (office_number,))
            else:
                cur.execute('SELECT tenant FROM offices WHERE number = ?', (office_number,))
            
            result = cur.fetchone()
            
            if not result:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 5,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            tenant = result['tenant']  # Текущий арендатор офиса
            
            # Проверяем, арендован ли офис вообще
            if tenant == '':
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 3,
                        'message': 'Office is not booked'
                    },
                    'id': id
                }
            
            # Проверяем, принадлежит ли бронирование текущему пользователю
            if tenant != login:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 4,
                        'message': 'You can only cancel your own booking'
                    },
                    'id': id
                }
            
            # Освобождаем офис (устанавливаем tenant в пустую строку)
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute('UPDATE offices SET tenant = %s WHERE number = %s', ('', office_number))
            else:
                cur.execute('UPDATE offices SET tenant = ? WHERE number = ?', ('', office_number))
            
            db_close(conn, cur)
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            # Обработка ошибок
            if 'conn' in locals():
                db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': f'Database error: {str(e)}'
                },
                'id': id
            }
        
    # Если метод не распознан, возвращаем ошибку
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }