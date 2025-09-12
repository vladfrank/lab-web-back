from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

class PaymentRequired(Exception):
    code = 402
    description = 'Payment Required'

class ImATeapot(Exception):
    code = 418
    description = "I'm a teapot"

@app.errorhandler(404)
def not_found(err):
    style = url_for("static", filename='lab1.css')
    return '''
    <!doctype html>
    <html>
    <head>
        <title>404</title>
        <link rel='stylesheet' href="''' + style + '''">
        <style>
            body {
                background: #f8f9fa;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .error {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 500px;
                width: 100%;
            }
            .error-code {
                font-size: 80px;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="error">
            <div class="error-code">404</div>
            <h1>Страница не найдена</h1>
            <p>
                Иди проверяй, что ты тут мне понавводил!
            </p>
            <a href="/">На главную</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(400)
def bad_request(err):
    return "Некорректный запрос, попробуй снова", 400

@app.errorhandler(401)
def unauthorized(err):
    return "Не авторизован, нам нужны твои данные!", 401

@app.errorhandler(PaymentRequired)
def payment_required(err):
    return "Отдай мне свои деньги", 402

@app.errorhandler(403)
def forbidden(err):
    return "Запрещено, вон от сюда", 403

@app.errorhandler(405)
def method_not_allowed(err):
    return "Метод не поддерживается, разберись уже чего ты хочешь", 405

@app.errorhandler(ImATeapot)
def im_a_teapot(err):
    return "Ну ты даёшь, посмотри видео для чайников", 418

@app.route('/')
@app.route('/index')
def index():
    style = url_for("static", filename='lab1.css')
    return '''
<!doctype html>
<html>
    <head>
        <title>НГТУ, ФБ, Лабораторные работы</title>
        <link rel='stylesheet' href="''' + style + '''">
    </head>
    <body>
        <header>
            <h1>НГТУ, ФБ, WEB-программирование, часть 2</h1>
            <h2>Список лабораторных</h2>
        </header>

        <ul>
            <a href="/lab1">Лабраторная работа 1. Введение во Flask</a>
        </ul>

        <footer>
            <p>Франк Владислав Валерьевич, ФБИ-31, 3 курс</p>
            <p>2025</p>
        </footer>
    </body>
</html>
'''
@app.route('/lab1')
def lab1():
    style = url_for("static", filename='lab1.css')
    return '''
<!doctype html>
<html>
    <head>
        <title>Первая лабораторная</title>
        <link rel='stylesheet' href="''' + style + '''">
        <style>
            .menu {
                text-align: center;
                margin: 30px 0;
            }
            .menu a {
                display: inline-block;
                margin: 10px;
                padding: 15px 25px;
                border-radius: 5px;
                font-weight: bold;
            }
            .back {
                text-align: center;
                margin-top: 30px;
            }
            .back a {
                background: #435a58
            }
            .content { 
                background: white;
                padding: 25px; 
                border-radius: 12px; 
                margin-bottom: 30px; 
                font-size: 20px; 
            } 
            .content p { 
                margin: 0; 
                text-align: justify; 
            }
        </style>
    </head>
    <body>
        <h1>Лабораторная работа 1</h1>
        
        <div class="content">
            <p>Flask — фреймворк для создания веб-приложений на языке
            программирования Python, использующий набор инструментов
            Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
            называемых микрофреймворков — минималистичных каркасов
            веб-приложений, сознательно предоставляющих 
            лишь самые базовые возможности.</p>
        </div>

        <div class="menu">
            <a href="/lab1/web">Web</a>
            <a href="/lab1/author">Author</a>
            <a href="/lab1/image">Image</a>
            <a href="/lab1/counter">Counter</a>
            <a href="/lab1/info">Info</a>
        </div>

        <div class="back">
            <a href="/">← На главную</a>
        </div>
    </body>
</html>
'''

@app.route("/lab1/web")
def web():
    return"""<!doctype html>
        <html>
            <body>
                <h1>web-сервер на flask</h1>
                <a href="/lab1/author">author</a>
                <a href="/lab1/image">image</a>
                <a href="/lab1/counter">counter</a>
            </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'                    
        }

@app.route("/lab1/author")
def author():
    name = "Франк Владислав Валерьевич"
    group = "ФБИ-31"
    faculty = "ФБ"

    return"""<!doctype html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/lab1/web">web</a>
                <a href="/lab1/image">image</a>
                <a href="/lab1/counter">counter</a>
            </body>
        </html>"""

@app.route('/lab1/image')
def image():
    path = url_for("static", filename='stantion.jpeg')
    style = url_for("static", filename='lab1.css')
    return'''
<!doctype html>
<html>
    <head>
        <link rel='stylesheet' href="''' + style + '''">
    </head>
    <body>
        <h1>Станция метро УРА!</h1>
        <img src="''' + path + '''">
        <a href="/lab1/web">web</a>
        <a href="/lab1/author">author</a>
        <a href="/lab1/counter">counter</a>
    </body>
</html>
'''

count = 0

@app.route('/lab1/counter')
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''
        <a href="/lab1/reset_counter">Очистить счётчик</a>
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + url + '''<br>
        Ваш IP адрес: ''' + client_ip + '''<br>
        <a href="/lab1/web">web</a>
        <a href="/lab1/author">author</a>
        <a href="/lab1/image">image</a>
    </body>
</html>
'''

@app.route('/lab1/reset_counter')
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))

@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201