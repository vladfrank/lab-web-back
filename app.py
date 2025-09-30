from flask import Flask, url_for, request, redirect, abort, render_template
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed
import datetime
app = Flask(__name__)

class PaymentRequired(Exception):
    code = 402
    description = 'Payment Required'

class ImATeapot(Exception):
    code = 418
    description = "I'm a teapot"

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

@app.errorhandler(BadRequest)
def bad_request(err):
    return "Некорректный запрос, попробуй снова", 400

@app.errorhandler(Unauthorized)
def unauthorized(err):
    return "Не авторизован, нам нужны твои данные!", 401

@app.errorhandler(PaymentRequired)
def payment_required(err):
    return "Отдай мне свои деньги", 402

@app.errorhandler(Forbidden)
def forbidden(err):
    return "Запрещено, вон от сюда", 403

@app.errorhandler(MethodNotAllowed)
def method_not_allowed(err):
    return "Метод не поддерживается, разберись уже чего ты хочешь", 405

@app.errorhandler(ImATeapot)
def im_a_teapot(err):
    return "Ну ты даёшь, посмотри видео для чайников", 418

# вызов ошибок
@app.route('/test400')
def test_400():
    raise BadRequest()

@app.route('/test401')
def test_401():
    raise Unauthorized()

@app.route('/test402')
def test_402():
    raise PaymentRequired()

@app.route('/test403')
def test_403():
    raise Forbidden()

@app.route('/test405')
def test_405():
    raise MethodNotAllowed()

@app.route('/test418')
def test_418():
    raise ImATeapot()

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

        <h2>Список роутов</h2>
        <div class="menu">
            <a href="/lab1/web">Web</a>
            <a href="/lab1/author">Author</a>
            <a href="/lab1/image">Image</a>
            <a href="/lab1/counter">Counter</a>
            <a href="/lab1/info">Info</a>
            <a href="/lab1/created">Created</a>
            <a href="/server_error">Server_error</a>
        </div>
        <div>
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
    
    response = '''
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
    
    from flask import Response
    resp = Response(response)
    
    # язык контента
    resp.headers['Content-Language'] = 'ru' 
    
    resp.headers['X-Developer-Name'] = 'Vladislav Frank'  # имя разработчика
    resp.headers['X-Custom-Header'] = 'Lbr1_Image'  # произвольный заголовок
    
    return resp

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

# Маршрут, который вызывает ошибку на сервере (деление на ноль)
@app.route('/server_error')
def cause_server_error():
    result = 10 / 0 
    return result

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

    # ----------------Лабораторная 2-------------------
    
@app.route('/lab2/a')
def a():
        return 'без слэша'

@app.route('/lab2/a/')
def a2():
        return 'со слэшем'

flower_list = ['роза','тюльпан','незабудка','ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        return "цветок: " + flower_list[flower_id]

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлен новый цветок</h1>
    <p>Название нового цветка: {name}</p>
    <p>Всего цветов: {len(flower_list)}</p>
    <p>Полный список: {flower_list}</p>
    </body>
</html>
'''

@app.route('/lab2/example')
def example():
    name = 'Франк Владислав'
    course = '3 курс'
    group = 'ФБИ-31'
    numlab = '2'
    return render_template('example.html', name=name, group=group, course=course, numlab=numlab)
