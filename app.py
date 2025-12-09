from flask import Flask, url_for, request
import datetime
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7
from messenger import messenger
app = Flask(__name__)
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно-секретный секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(messenger)


from flask import request
import datetime

# хранение лога
access_log = []

@app.errorhandler(404)
def not_found(err):
    # данные о запросе
    client_ip = request.remote_addr
    access_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    requested_url = request.url
    
    # добавляем запись в список
    access_log.append({
        'ip': client_ip,
        'time': access_time,
        'url': requested_url
    })
    
    style = url_for("static", filename='lab1.css')
    
    # создание html кода записи для сайта
    log_html = ''
    for entry in access_log[-10:]:
        log_html += f'<tr><td>{entry["ip"]}</td><td>{entry["time"]}</td><td>{entry["url"]}</td></tr>'
    
    return '''
    <!doctype html>
    <html>
    <head>
        <title>404</title>
        <link rel='stylesheet' href="''' + style + '''">
        <style>
            .error {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 0 auto;
            }
            .error-code {
                font-size: 80px;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 10px;
            }
            .log {
                margin-top: 30px;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 20px auto;
            }
            table {
                width: 100%;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <div class="error">
            <div class="error-code">404</div>
            <h1>Страница не найдена</h1>
            <p>Твой IP (мы тебя найдем): ''' + client_ip + '''</p>
            <p>Время твоего косяка: ''' + access_time + '''</p>
            <p>Адрес с которым ты напортачил: ''' + requested_url + '''</p>
            <p>А теперь иди проверяй, что ты тут мне понавводил!</p>
            <a href="/">На главную</a>
        </div>
        
        <div class="log">
            <h2>Журнал (последние 10 записей):</h2>
            <table>
                <tr>
                    <th>IP-адрес</th>
                    <th>Время</th>
                    <th>URL</th>
                </tr>
                ''' + log_html + '''
            </table>
        </div>
    </body>
    </html>
    ''', 404

@app.route('/')
@app.route('/index')
def index():
    style = url_for("static", filename='lab1/lab1.css')
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
            <a href="/lab2/">Лабораторная работа 2. Шаблоны в Flask</a>
            <a href="/lab3/">Лабораторная работа 3. Формы, cookie</a>
            <a href="/lab4/">Лабораторная работа 4. Формы (POST)</a>
            <a href="/lab5/">Лабораторная работа 5. Flask и БД</a>
            <a href="/lab6/">Лабораторная работа 6. API JSON-RPC</a>
            <a href="/lab7/">Лабораторная работа 7. API REST</a>
            <a href="/messenger/">РГЗ. Мессенджер</a>
        </ul>

        <footer>
            <p>Франк Владислав Валерьевич, ФБИ-31, 3 курс</p>
            <p>2025</p>
        </footer>
    </body>
</html>
'''


@app.errorhandler(500)
def internal_server_error(err):
    style = url_for("static", filename='lab1.css')
    return '''
    <!doctype html>
    <html>
    <head>
        <title>500</title>
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
            <div class="error-code">500</div>
            <h1>Ошибка на сервере</h1>
            <p>
                Произошла внутренняя ошибка сервера. 
                Наши инженеры уже работают над решением проблемы.
                Пожалуйста, попробуйте позже.
            </p>
            <a href="/">На главную</a>
        </div>
    </body>
    </html>
    ''', 500
