from flask import Blueprint, render_template, request, jsonify, abort
import psycopg2
import psycopg2.extras
import sqlite3
from os import path
from flask import current_app

lab7 = Blueprint('lab7', __name__)

# Подключение к базе данных 

def db_connect():
    """Возвращает (conn, cur) — универсально для обеих СУБД"""
    if current_app.config.get('DB_TYPE') == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='vlad_frank_knowledge_base',
            user='vlad_frank_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur


def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


# Инициализация таблицы beers — один раз при первом запуске
def init_beers_table():
    """Создаёт таблицу beers и заполняет стартовыми данными"""
    conn, cur = db_connect()
    try:
        is_postgres = current_app.config.get('DB_TYPE') == 'postgres'

        # Правильный автоинкремент для каждой СУБД
        if is_postgres:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS beers (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    title_ru TEXT NOT NULL,
                    strength REAL NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
        else:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS beers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    title_ru TEXT NOT NULL,
                    strength REAL NOT NULL,
                    description TEXT NOT NULL
                )
            ''')

        # Универсальное получение количества записей
        cur.execute('SELECT COUNT(*) AS cnt FROM beers')
        row = cur.fetchone()
        count = row['cnt'] if isinstance(row, dict) else row[0]

        if count == 0:
            initial_beers = [
                ("ZATECKY GUS", "Гусь", 3.5,
                 "Пиво Zatecky Gus Cerny — богатый вкус с нотками поджаренного солода, карамели и бархатным ароматом жатецкого хмеля."),
                ("STELLA ARTOIS МРК", "Стелла", 5.0,
                 "Самое популярное в мире бельгийское легкое пиво премиум-класса."),
                ("SPATEN MUNCHEN HELLES", "Шпатен", 5.2,
                 "Пиво умеренной крепости, с мягким пряным вкусом.")
            ]

            placeholder = '%s' if is_postgres else '?'
            query = f'''
                INSERT INTO beers (title, title_ru, strength, description)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
            '''
            cur.executemany(query, initial_beers)
            conn.commit()
    finally:
        db_close(conn, cur)


# Валидация входных данных
def validate_beer(data):
    errors = {}
    title_ru = data.get('title_ru', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    strength = data.get('strength')

    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно'

    if not title and not title_ru:
        errors['title'] = 'Хотя бы одно название должно быть заполнено'

    try:
        strength = float(strength)
        if not (0 <= strength <= 12.0):
            errors['strength'] = 'Крепость должна быть от 0 до 12.0%'
    except (TypeError, ValueError):
        errors['strength'] = 'Крепость должна быть числом'

    if not description:
        errors['description'] = 'Описание обязательно'
    elif len(description) > 2000:
        errors['description'] = 'Описание не может быть длиннее 2000 символов'

    return errors, title_ru, (title or title_ru), strength


@lab7.route('/lab7/')
def main():
    init_beers_table()
    return render_template('lab7/lab7.html')


@lab7.route('/lab7/rest-api/beers/', methods=['GET'])
def get_beers():
    conn, cur = db_connect()
    try:
        cur.execute('SELECT id, title, title_ru, strength, description FROM beers ORDER BY id')
        rows = cur.fetchall()
        beers = [dict(row) for row in rows]
        return jsonify(beers)
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['GET'])
def get_beer(id):
    conn, cur = db_connect()
    try:
        cur.execute('SELECT id, title, title_ru, strength, description FROM beers WHERE id = %s', (id,))
        row = cur.fetchone()
        if not row:
            abort(404)
        return jsonify(dict(row))
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['DELETE'])
def del_beer(id):
    conn, cur = db_connect()
    try:
        cur.execute('DELETE FROM beers WHERE id = %s', (id,))
        if cur.rowcount == 0:
            abort(404)
        return '', 204
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/', methods=['POST'])
def add_beer():
    data = request.get_json() or {}
    errors, title_ru, title, strength = validate_beer(data)
    if errors:
        return jsonify(errors), 400

    description = data.get('description', '').strip()

    conn, cur = db_connect()
    try:
        cur.execute('''
            INSERT INTO beers (title, title_ru, strength, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (title, title_ru, strength, description))
        new_id = cur.fetchone()['id'] if current_app.config.get('DB_TYPE') == 'postgres' else cur.fetchone()[0]
        return jsonify(new_id), 201
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['PUT'])
def put_beer(id):
    data = request.get_json() or {}
    errors, title_ru, title, strength = validate_beer(data)
    if errors:
        return jsonify(errors), 400

    description = data.get('description', '').strip()

    conn, cur = db_connect()
    try:
        cur.execute('''
            UPDATE beers
            SET title = %s, title_ru = %s, strength = %s, description = %s
            WHERE id = %s
            RETURNING id, title, title_ru, strength, description
        ''', (title, title_ru, strength, description, id))

        if cur.rowcount == 0:
            abort(404)

        row = cur.fetchone()
        updated = dict(row)
        return jsonify(updated)
    finally:
        db_close(conn, cur)