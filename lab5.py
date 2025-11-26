from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor  
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path 

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def main():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'vlad_frank_knowledge_base',
            user = 'vlad_frank_knowledge_base',
            password = '123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
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

#регистрация
@lab5.route('/lab5/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')
    full_name = request.form.get('full_name')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните логин и пароль')
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT login FROM users WHERE login=?;", (login,))

    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error='Такой пользователь уже существует')

    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (%s, %s, %s);", 
                    (login, password_hash, full_name))
    else:
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (?, ?, ?);", 
                    (login, password_hash, full_name))
    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

#логирование
@lab5.route('/lab5/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/login.html', error='Заполните все поля')
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login, ))

    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    session['login'] = login
    session['user_id'] = user['id']

    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)

#разлог
@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    session.pop('user_id', None)
    return redirect('/lab5')

#создание статьи
@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    is_favorite = request.form.get('is_favorite') == 'on'

    if not title or not article_text:
        return render_template('lab5/create_article.html', 
                              error='Заполните название и текст статьи')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login, ))

    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')
    
    user_id = user["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            INSERT INTO articles(user_id, title, article_text, is_public, is_favorite) 
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, title, article_text, is_public, is_favorite))
    else:
        cur.execute("""
            INSERT INTO articles(user_id, title, article_text, is_public, is_favorite) 
            VALUES (?, ?, ?, ?, ?);
        """, (user_id, title, article_text, is_public, is_favorite))
    
    db_close(conn, cur)
    return redirect('/lab5/list')

#cсписок статей
@lab5.route('/lab5/list')
def list_articles():
    login = session.get('login')
    user_id = session.get('user_id')

    conn, cur = db_connect()

    # Создаем временную таблицу для избранных статей
    if current_app.config['DB_TYPE'] == 'postgres':
        # Получаем все публичные статьи + статьи пользователя (если авторизован)
        # и информацию об избранных статьях
        if login:
            cur.execute("""
                SELECT 
                    a.*, 
                    u.login as author, 
                    u.full_name,
                    EXISTS(
                        SELECT 1 FROM favorite_articles fa 
                        WHERE fa.article_id = a.id AND fa.user_id = %s
                    ) as is_favorite
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE OR a.user_id = %s
                ORDER BY 
                    (EXISTS(SELECT 1 FROM favorite_articles fa WHERE fa.article_id = a.id AND fa.user_id = %s)) DESC,
                    a.id DESC;
            """, (user_id, user_id, user_id))
        else:
            # Для неавторизованных - только публичные статьи
            cur.execute("""
                SELECT 
                    a.*, 
                    u.login as author, 
                    u.full_name,
                    FALSE as is_favorite
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE
                ORDER BY a.id DESC;
            """)
    else:
        # SQLite версия
        if login:
            cur.execute("""
                SELECT 
                    a.*, 
                    u.login as author, 
                    u.full_name,
                    EXISTS(
                        SELECT 1 FROM favorite_articles fa 
                        WHERE fa.article_id = a.id AND fa.user_id = ?
                    ) as is_favorite
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE OR a.user_id = ?
                ORDER BY 
                    (EXISTS(SELECT 1 FROM favorite_articles fa WHERE fa.article_id = a.id AND fa.user_id = ?)) DESC,
                    a.id DESC;
            """, (user_id, user_id, user_id))
        else:
            cur.execute("""
                SELECT 
                    a.*, 
                    u.login as author, 
                    u.full_name,
                    0 as is_favorite
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE
                ORDER BY a.id DESC;
            """)
    
    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('/lab5/articles.html', articles=articles, login=login)

#изменение статьи
@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    # авторизован ли пользователь
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    # Подключаемся к бд
    conn, cur = db_connect()

    # получаем данные статьи вместе с информацией об авторе
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            SELECT articles.*, users.login as author 
            FROM articles 
            JOIN users ON articles.user_id = users.id 
            WHERE articles.id=%s;
        """, (article_id,))
    else:
        cur.execute("""
            SELECT articles.*, users.login as author 
            FROM articles 
            JOIN users ON articles.user_id = users.id 
            WHERE articles.id=?;
        """, (article_id,))
    
    article = cur.fetchone()
    
    # существует ли статья и принадлежит ли она текущему пользователю
    if not article or article['author'] != login:
        db_close(conn, cur)
        return redirect('/lab5/list')

    # отображение формы редактирования
    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article)

    # сохранение изменений
    # Получаем данные из формы
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'  # чекбокс в boolean

    # Валидация (название и текст не пустые)
    if not title or not article_text:
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', 
                              article=article, 
                              error='Заполните название и текст статьи')

    # подключаемся к базе данных для обновления
    conn, cur = db_connect()
    
    # обновляем статью в базе данных
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE articles 
            SET title=%s, article_text=%s, is_public=%s
            WHERE id=%s AND user_id=(SELECT id FROM users WHERE login=%s);
        """, (title, article_text, is_public, article_id, login))
    else:
        cur.execute("""
            UPDATE articles 
            SET title=?, article_text=?, is_public=?
            WHERE id=? AND user_id=(SELECT id FROM users WHERE login=?);
        """, (title, article_text, is_public, article_id, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5/list')


@lab5.route('/lab5/delete/<int:article_id>')
def delete_article(article_id):
    # авторизован ли пользователь
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    # Подключаемся к бд
    conn, cur = db_connect()

    # удаление статьи из базы данных
    if current_app.config['DB_TYPE'] == 'postgres':
        # удаляем статью только если она принадлежит текущему пользователю
        cur.execute("""
            DELETE FROM articles 
            WHERE id=%s AND user_id=(SELECT id FROM users WHERE login=%s);
        """, (article_id, login))
    else:
        cur.execute("""
            DELETE FROM articles 
            WHERE id=? AND user_id=(SELECT id FROM users WHERE login=?);
        """, (article_id, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5/list')

# функции для избранных статей

@lab5.route('/lab5/favorite/<int:article_id>')
def add_to_favorite(article_id):
    # авторизован ли пользователь
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # существует ли статья с указанным ID
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM articles WHERE id=%s;", (article_id,))
    else:
        cur.execute("SELECT id FROM articles WHERE id=?;", (article_id,))
    
    # Если статья не найдена, перенаправляем на список статей
    if not cur.fetchone():
        db_close(conn, cur)
        return redirect('/lab5/list')

    # Добавляем статью в избранное для текущего пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        # в постгрес используем ON CONFLICT для избежания дубликатов
        cur.execute("""
            INSERT INTO favorite_articles (user_id, article_id) 
            SELECT id, %s FROM users WHERE login=%s
            ON CONFLICT (user_id, article_id) DO NOTHING;
        """, (article_id, login))
    else:
        # в лайте используем INSERT OR IGNORE для избежания дубликатов
        cur.execute("""
            INSERT OR IGNORE INTO favorite_articles (user_id, article_id) 
            SELECT id, ? FROM users WHERE login=?;
        """, (article_id, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5/list')

@lab5.route('/lab5/unfavorite/<int:article_id>')
def remove_from_favorite(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # Удаляем статью из избранного для текущего пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            DELETE FROM favorite_articles 
            WHERE article_id=%s AND user_id=(SELECT id FROM users WHERE login=%s);
        """, (article_id, login))
    else:
        cur.execute("""
            DELETE FROM favorite_articles 
            WHERE article_id=? AND user_id=(SELECT id FROM users WHERE login=?);
        """, (article_id, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5/list')

# Функции для работы с пользователями и профилем

@lab5.route('/lab5/users')
def users_list():
    # авторизован ли пользователь
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # список всех пользователей (только логины и имена, без паролей)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login, full_name FROM users ORDER BY login;")
    else:
        cur.execute("SELECT login, full_name FROM users ORDER BY login;")
    
    users = cur.fetchall()

    db_close(conn, cur)
    
    return render_template('/lab5/users.html', users=users, login=login)

@lab5.route('/lab5/change_password', methods=['GET', 'POST'])
def change_password():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    # GET запрос отображение формы смены пароля
    if request.method == 'GET':
        return render_template('lab5/change_password.html', login=login)

    # POST запрос смена пароля
    # Получаем данные из формы
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Валидация
    if not current_password or not new_password or not confirm_password:
        return render_template('lab5/change_password.html', 
                              error='Заполните все поля')

    if new_password != confirm_password:
        return render_template('lab5/change_password.html', 
                              error='Новые пароли не совпадают')

    conn, cur = db_connect()

    # Проверяем текущий пароль пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT password FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT password FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    
    # Если текущий пароль неверен, показываем ошибку
    if not user or not check_password_hash(user['password'], current_password):
        db_close(conn, cur)
        return render_template('lab5/change_password.html', 
                              error='Текущий пароль неверен')

    # Хэшируем новый пароль и обновляем его в базе данных
    new_password_hash = generate_password_hash(new_password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE users SET password=%s WHERE login=%s;", 
                    (new_password_hash, login))
    else:
        cur.execute("UPDATE users SET password=? WHERE login=?;", 
                    (new_password_hash, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5/profile')

@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    # GET запрос отображение формы профиля
    if request.method == 'GET':
        # Получаем текущее имя пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT full_name FROM users WHERE login=%s;", (login,))
        else:
            cur.execute("SELECT full_name FROM users WHERE login=?;", (login,))
        
        user = cur.fetchone()
        
        # Закрываем соединение и отображаем форму
        db_close(conn, cur)
        return render_template('lab5/profile.html', user=user, login=login)

    # POST запрос обновление имени пользователя
    # Получаем новое имя из формы
    full_name = request.form.get('full_name')

    # Обновляем имя пользователя в базе данных
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE users SET full_name=%s WHERE login=%s;", 
                    (full_name, login))
    else:
        cur.execute("UPDATE users SET full_name=? WHERE login=?;", 
                    (full_name, login))
    
    db_close(conn, cur)
    
    return redirect('/lab5')