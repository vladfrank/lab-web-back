from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.route("/")
@app.route("/web")
def web():
    return"""<!doctype html>
        <html>
            <body>
                <h1>web-сервер на flask</h1>
                <a href="/author">author</a>
                <a href="/image">image</a>
                <a href="/counter">counter</a>
            </body>
        </html>"""

@app.route("/author")
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
                <a href="/web">web</a>
                <a href="/image">image</a>
                <a href="/counter">counter</a>
            </body>
        </html>"""

@app.route('/image')
def image():
    path = url_for("static", filename='stantion.jpeg')
    return'''
<!doctype html>
<html>
    <body>
        <h1>Станция метро УРА!</h1>
        <img src="''' + path + '''">
        <a href="/web">web</a>
        <a href="/author">author</a>
        <a href="/counter">counter</a>
    </body>
</html>
'''

count = 0

@app.route('/counter')
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
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + url + '''<br>
        Ваш IP адрес: ''' + client_ip + '''<br>
        <a href="/web">web</a>
        <a href="/author">author</a>
        <a href="/image">image</a>
    </body>
</html>
'''

@app.route("/info")
def info():
    return redirect("/author")
