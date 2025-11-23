from flask import Blueprint, render_template, request, session
import psycopg2
from psycopg2.extras import RealDictCursor

# Создание Blueprint для лабораторной работы 6
lab6 = Blueprint('lab6', __name__)

def get_db_connection():
    """
    Функция для установления соединения с базой данных PostgreSQL
    """
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='vlad_frank_knowledge_base',
        user='vlad_frank_knowledge_base',  
        password='123'  
    )
    return conn

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
    """
    data = request.json
    id = data['id']  # ID запроса для соответствия JSON-RPC спецификации
    
    # Метод info - получение информации о всех офисах
    if data['method'] == 'info':
        try:
            # Подключаемся к базе данных и получаем список всех офисов
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT number, tenant, price FROM offices ORDER BY number')
            offices = cur.fetchall()
            cur.close()
            conn.close()
            
            # Возвращаем успешный ответ с данными об офисах
            return {
                'jsonrpc': '2.0',
                'result': offices,
                'id': id
            }
        except Exception as e:
            # Обработка ошибок базы данных
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
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Проверяем, существует ли офис с таким номером
            cur.execute('SELECT tenant FROM offices WHERE number = %s', (office_number,))
            result = cur.fetchone()
            
            if not result:
                cur.close()
                conn.close()
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 5,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            # Проверяем, свободен ли офис (tenant пустой)
            if result[0] != '':
                cur.close()
                conn.close()
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 2,
                        'message': 'Already booked'
                    },
                    'id': id
                }
            
            # Бронируем офис за текущим пользователем
            cur.execute('UPDATE offices SET tenant = %s WHERE number = %s', (login, office_number))
            conn.commit()  # Сохраняем изменения в базе данных
            cur.close()
            conn.close()
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            if conn:
                conn.rollback()
                cur.close()
                conn.close()
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
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Получаем информацию о текущем арендаторе офиса
            cur.execute('SELECT tenant FROM offices WHERE number = %s', (office_number,))
            result = cur.fetchone()
            
            if not result:
                cur.close()
                conn.close()
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 5,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            tenant = result[0]  # Текущий арендатор офиса
            
            # Проверяем, арендован ли офис вообще
            if tenant == '':
                cur.close()
                conn.close()
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
                cur.close()
                conn.close()
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 4,
                        'message': 'You can only cancel your own booking'
                    },
                    'id': id
                }
            
            # Освобождаем офис (устанавливаем tenant в пустую строку)
            cur.execute('UPDATE offices SET tenant = %s WHERE number = %s', ('', office_number))
            conn.commit()  # Сохраняем изменения в базе данных
            cur.close()
            conn.close()
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            if conn:
                conn.rollback()
                cur.close()
                conn.close()
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