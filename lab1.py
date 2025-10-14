from flask import Blueprint, url_for, request, redirect
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed, ImATeapot
import datetime
lab1 = Blueprint('lab1', __name__)
from flask import request
import datetime

# хранение лога
access_log = []

@lab1.errorhandler(BadRequest)
def bad_request(err):
    return "Некорректный запрос, попробуй снова", 400


@lab1.errorhandler(Unauthorized)
def unauthorized(err):
    return "Не авторизован, нам нужны твои данные!", 401


@lab1.errorhandler(Forbidden)
def forbidden(err):
    return "Запрещено, вон от сюда", 403


@lab1.errorhandler(MethodNotAllowed)
def method_not_allowed(err):
    return "Метод не поддерживается, разберись уже чего ты хочешь", 405


@lab1.errorhandler(ImATeapot)
def im_a_teapot(err):
    return "Ну ты даёшь, посмотри видео для чайников", 418

# вызов ошибок
@lab1.route('/test400')
def test_400():
    raise BadRequest()


@lab1.route('/test401')
def test_401():
    raise Unauthorized()


@lab1.route('/test403')
def test_403():
    raise Forbidden()


@lab1.route('/test405')
def test_405():
    raise MethodNotAllowed()


@lab1.route('/test418')
def test_418():
    raise ImATeapot()


@lab1.route('/lab1')
def lab():
    style = url_for("static", filename='lab1/lab1.css')
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


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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


@lab1.route('/lab1/image')
def image():
    path = url_for("static", filename='lab1/stantion.jpeg')
    style = url_for("static", filename='lab1/lab1.css')
    
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

@lab1.route('/lab1/counter')
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


@lab1.route('/lab1/reset_counter')
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))


@lab1.route("/lab1/info")
def info():
    return redirect("/lab1/author")


@lab1.route("/lab1/created")
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
@lab1.route('/server_error')
def cause_server_error():
    result = 10 / 0 
    return result

class PaymentRequired(Exception):
    code = 402
    description = 'Payment Required'


class ImATeapot(Exception):
    code = 418
    description = "I'm a teapot"

