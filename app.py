from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "Вы кажется не туда попали", 404

@app.route("/")
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