from flask import Blueprint, render_template, request, jsonify, abort
import psycopg2
import psycopg2.extras
import sqlite3
from os import path
from flask import current_app

lab7 = Blueprint('lab7', __name__)


# ФУНКЦИИ РАБОТЫ С БАЗОЙ ДАННЫХ
def db_connect():
    if current_app.config.get('DB_TYPE') == 'postgres':
        # Подключение к PostgreSQL
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='vlad_frank_knowledge_base',
            user='vlad_frank_knowledge_base',
            password='123'
        )
        # RealDictCursor — возвращает строки в виде словарей
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        # Подключение к SQLite (файл хранится рядом с модулем)
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # тоже делает строки похожими на словарь
        cur = conn.cursor()

    return conn, cur


def db_close(conn, cur):
    """
    Корректно закрывает соединение:
    коммит, закрытие курсора, закрытие соединения
    """
    conn.commit()
    cur.close()
    conn.close()


# ИНИЦИАЛИЗАЦИЯ ТАБЛИЦЫ beers (создаётся при первом запуске)
def init_beers_table():
    """
    Создаёт таблицу beers, если её нет.
    Заполняет начальными данными при пустой таблице.
    """
    conn, cur = db_connect()
    try:
        is_postgres = current_app.config.get('DB_TYPE') == 'postgres'

        # Разные SQL-синтаксисы autoincrement для PostgreSQL и SQLite
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

        # Проверяем количество строк
        cur.execute('SELECT COUNT(*) AS cnt FROM beers')
        row = cur.fetchone()
        count = row['cnt'] if isinstance(row, dict) else row[0]

        # Если таблица пустая — добавляем 3 стартовые записи
        if count == 0:
            initial_beers = [
                ("ZATECKY GUS", "Гусь", 3.5,
                 "Пиво Zatecky Gus Cerny — богатый вкус с нотками поджаренного солода, карамели и бархатным ароматом жатецкого хмеля."),
                ("STELLA ARTOIS МРК", "Стелла", 5.0,
                 "Самое популярное в мире бельгийское легкое пиво премиум-класса."),
                ("SPATEN MUNCHEN HELLES", "Шпатен", 5.2,
                 "Пиво умеренной крепости, с мягким пряным вкусом.")
            ]

            # Разные placeholder для SQL
            placeholder = '%s' if is_postgres else '?'

            query = f'''
                INSERT INTO beers (title, title_ru, strength, description)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
            '''

            # executemany добавляет сразу несколько записей
            cur.executemany(query, initial_beers)
            conn.commit()
    finally:
        db_close(conn, cur)


# ВАЛИДАЦИЯ ВХОДНЫХ ДАННЫХ ДЛЯ ПИВА
def validate_beer(data):
    """
    Проверяет корректность данных, присланных с клиента.
    Возвращает кортеж:
    (errors, русский заголовок, английский заголовок, крепость)
    """
    errors = {}

    title_ru = data.get('title_ru', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    strength = data.get('strength')

    # Русское название - обязательно
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно'

    # Хотя бы одно название должно быть заполнено
    if not title and not title_ru:
        errors['title'] = 'Хотя бы одно название должно быть заполнено'

    # strength должен быть числом от 0 до 12
    try:
        strength = float(strength)
        if not (0 <= strength <= 12.0):
            errors['strength'] = 'Крепость должна быть от 0 до 12.0%'
    except (TypeError, ValueError):
        errors['strength'] = 'Крепость должна быть числом'

    # Проверка описания
    if not description:
        errors['description'] = 'Описание обязательно'
    elif len(description) > 2000:
        errors['description'] = 'Описание не может быть длиннее 2000 символов'

    # Если title пуст — backend сам подставляет title_ru
    return errors, title_ru, (title or title_ru), strength


# РОУТЫ FLASK

@lab7.route('/lab7/')
def main():
    """Главная страница. Перед открытием — создаём таблицу."""
    init_beers_table()
    return render_template('lab7/lab7.html')


@lab7.route('/lab7/rest-api/beers/', methods=['GET'])
def get_beers():
    """Возвращает JSON со списком всех сортов пива"""
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
    """Возвращает JSON одной записи по ID"""
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
    """Удаляет запись по ID"""
    conn, cur = db_connect()
    try:
        cur.execute('DELETE FROM beers WHERE id = %s', (id,))
        if cur.rowcount == 0:
            abort(404)
        return '', 204  # Успешное удаление без тела ответа
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/', methods=['POST'])
def add_beer():
    """Добавляет новую запись"""
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

        # Разные способы получения id в postgres и sqlite
        new_id = cur.fetchone()['id'] if current_app.config.get('DB_TYPE') == 'postgres' else cur.fetchone()[0]

        return jsonify(new_id), 201
    finally:
        db_close(conn, cur)


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['PUT'])
def put_beer(id):
    """Редактирует запись"""
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