from flask import Flask, url_for, request, redirect, abort, render_template
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed
import datetime
from lab1 import lab1
app = Flask(__name__)
app.register_blueprint(lab1)



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
            <a href="/lab2/">Лабораторная работа 2. Шаблоны в Flask</a>
        </ul>

        <footer>
            <p>Франк Владислав Валерьевич, ФБИ-31, 3 курс</p>
            <p>2025</p>
        </footer>
    </body>
</html>
'''


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


flowers = [
    {"id": 0, "name": "роза", "price": 300},
    {"id": 1, "name": "тюльпан", "price": 310},
    {"id": 2, "name": "незабудка", "price": 320},
    {"id": 3, "name": "ромашка", "price": 330},
    {"id": 4, "name": "георгин", "price": 300},
    {"id": 5, "name": "гладиолус", "price": 310}
]

# Просмотр конкретного цветка
@app.route('/lab2/flowers/<int:flower_id>')
def flower_detail(flower_id):
    if flower_id >= len(flowers):
        abort(404)
    flower = flowers[flower_id]
    return render_template('flower_detail.html', flower=flower)


# Добавление цветка с помощью url
@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    new_id = len(flowers)
    flowers.append({"id": new_id, "name": name, "price": 300})
    return redirect('/lab2/all_flowers')


# Добавление цветка через форму
@app.route('/lab2/add_flower_form', methods=['POST'])
def add_flower_form():
    name = request.form.get('flower_name', '').strip()
    new_id = len(flowers)
    flowers.append({"id": new_id, "name": name, "price": 300})
    return redirect('/lab2/all_flowers')


# Ошибка при добавлении без имени
@app.route('/lab2/add_flower/')
def add_flower_no_name():
    return 'вы не задали имя цветка', 400


# Страница всех цветов
@app.route('/lab2/all_flowers')
def all_flowers():
    return render_template('all_flowers.html', flowers=flowers)


# Удаление конкретного цветка
@app.route('/lab2/del_flower/<int:flower_id>')
def del_flower(flower_id):
    if flower_id >= len(flowers):
        abort(404)
    flowers.pop(flower_id)
    # Обновляем ID
    for i, flower in enumerate(flowers):
        flower['id'] = i
    return redirect('/lab2/all_flowers')


# Очистка всех цветов
@app.route('/lab2/clear_flowers')
def clear_flowers():
    flowers.clear()
    return redirect('/lab2/all_flowers')


@app.route('/lab2/example')
def example():
    name = 'Франк Владислав'
    course = '3 курс'
    group = 'ФБИ-31'
    numlab = '2'
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321},
    ]
    return render_template('example.html', name=name, group=group, course=course, numlab=numlab, fruits=fruits)


@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')


@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)



# калькулятор с двумя числами
@app.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    # математические операции
    sum_result = a + b
    min_result = a - b
    umn_result = a * b
    del_result = a / b if b != 0 else 'деление на ноль'
    step_result = a ** b
    
    # Возвращаем HTML-страницу с результатами вычислений
    return f'''
<!doctype html>
<html>
    <head>
        <title>Калькулятор</title>
    </head>
    <body>
        <h1>Расчёт с параметрами:</h1>
        <p>
            {a} + {b} = {sum_result}<br>
            {a} - {b} = {min_result}<br>
            {a} × {b} = {umn_result}<br>
            {a} / {b} = {del_result}<br>
            {a}^{b} = {step_result}
        </p>
    </body>
</html>
'''


# перенаправления с calc/ на calc/1/1
@app.route('/lab2/calc/')
def calc_default():
    # по умолчанию 1 и 1
    return redirect('/lab2/calc/1/1')


# перенаправления с <int:a> на <int:a>/1
@app.route('/lab2/calc/<int:a>')
def calc_single(a):
    # калькулятор с первым числом a и вторым числом 1
    return redirect(f'/lab2/calc/{a}/1')


books = [
    {"author": "ХЗ Кто", "title": "Как я стал программистом, не зная питон", "genre": "Фантастика", "pages": 1488},
    {"author": "Олег Kizaru", "title": "Мои мемуары", "genre": "Триллер", "pages": 999},
    {"author": "Капитан Очевидность", "title": "Вода мокрая: руководство для начинающих", "genre": "Научпоп", "pages": 42},
    {"author": "Бабушка", "title": "Пирожки с капустой", "genre": "Кулинария", "pages": 777},
    {"author": "Дед Максим", "title": "Вот и помер", "genre": "Ностальгия", "pages": 1984},
    {"author": "Кот", "title": "МЯУ", "genre": "Руководство", "pages": 1337},
    {"author": "Студент ФБИ-31", "title": "Сон на паре: искусство маскировки", "genre": "Учебное пособие", "pages": 666},
    {"author": "Егор Крид", "title": "Мне тебя мало, ты мои деньги, деньги, всегда мало", "genre": "Автобиография", "pages": 228},
    {"author": "Лаг Багович", "title": "Я живу в вашем коде", "genre": "Хоррор", "pages": 404},
    {"author": "Гит Хабович", "title": "Commit'ы моей души", "genre": "Поэзия", "pages": 322},
    {"author": "Влад Креатив", "title": "Устал", "genre": "Хоррор", "pages": 500},
    {"author": "Настя tequilka В***ева", "title": "Тайны казахов на Чемасе", "genre": "Мистика", "pages": 1000}
]

# вывод списка книг с использованием шаблона
@app.route('/lab2/books')
def books_list():
    return render_template('books.html', books=books)


# солярисы разных поколений и рестайлингов
solaris_cars = [
    {
        "id": 1,
        "name": "Hyundai Solaris I (2010-2014)",
        "generation": "Первое поколение",
        "years": "2010-2014",
        "description": "Первое поколение Solaris для российского рынка. Седан на платформе Hyundai RB.",
        "image": "solaris_2010.jpg",
        "engine": "1.4L / 1.6L",
        "features": "Начало эпохи Solaris в России"
    },
    {
        "id": 2,
        "name": "Hyundai Solaris I Рестайлинг (2014-2017)",
        "generation": "Первое поколение (рестайлинг)",
        "years": "2014-2017", 
        "description": "Рестайлинг первой генерации. Изменена передняя оптика, бампер, решётка радиатора.",
        "image": "solaris_2014.jpg",
        "engine": "1.4L / 1.6L",
        "features": "Обновлённый дизайн, новые опции"
    },
    {
        "id": 3,
        "name": "Hyundai Solaris II (2017-2020)",
        "generation": "Второе поколение",
        "years": "2017-2020",
        "description": "Полностью новая платформа K2. Современный дизайн в стиле Fluidic Sculpture 2.0.",
        "image": "solaris_2017.jpg",
        "engine": "1.4L / 1.6L",
        "features": "Новая платформа, мультимедийная система"
    },
    {
        "id": 4, 
        "name": "Hyundai Solaris II Рестайлинг (2020-2023)",
        "generation": "Второе поколение (рестайлинг)",
        "years": "2020-2023",
        "description": "Рестайлинг второго поколения. Полностью переработанная передняя часть, новая оптика.",
        "image": "solaris_2020.jpg",
        "engine": "1.4L / 1.6L",
        "features": "LED-оптика, обновлённая решётка"
    },
    {
        "id": 5,
        "name": "Hyundai Solaris III (2023-н.в.)",
        "generation": "Третье поколение", 
        "years": "2023-настоящее время",
        "description": "Современный дизайн в духе новых Hyundai. Увеличенные габариты, премиальная отделка.",
        "image": "solaris_2023.jpeg",
        "engine": "1.5L / 1.6L",
        "features": "Цифровая приборная панель, ADAS"
    },
    {
        "id": 6,
        "name": "Hyundai Solaris хетчбэк (2011-2014) ЛУЧШИЙ",
        "generation": "Первое поколение (хетчбэк)",
        "years": "2011-2014",
        "description": "Хетчбэк версия первого поколения Solaris. Компактный и практичный.",
        "image": "solaris_hatch_2011.jpeg",
        "engine": "1.4L / 1.6L", 
        "features": "Практичный хетчбэк, маневренность"
    },
    {
        "id": 7,
        "name": "Hyundai Solaris седан (2010-2017)",
        "generation": "Классический седан",
        "years": "2010-2017",
        "description": "Классический седан - самый популярный кузов Solaris в России.",
        "image": "solaris_sedan_classic.jpeg",
        "engine": "1.4L / 1.6L",
        "features": "Просторный багажник, комфорт"
    },
    {
        "id": 8,
        "name": "Hyundai Solaris Active (2018)",
        "generation": "Специальная версия",
        "years": "2018",
        "description": "Версия с увеличенным клиренсом и защитой кузова для плохих дорог.",
        "image": "solaris_active.jpeg",
        "engine": "1.6L",
        "features": "Увеличенный клиренс, защита"
    },
    {
        "id": 9,
        "name": "Hyundai Solaris Business (2015)",
        "generation": "Бизнес-версия",
        "years": "2015", 
        "description": "Комплектация для корпоративных клиентов с улучшенной отделкой.",
        "image": "solaris_business.png",
        "engine": "1.6L",
        "features": "Кожаный салон, климат-контроль"
    },
    {
        "id": 10,
        "name": "Hyundai Solaris Limited (2021)",
        "generation": "Лимитированная версия",
        "years": "2021",
        "description": "Лимитированная версия с эксклюзивной отделкой и дополнительным оборудованием.",
        "image": "solaris_limited.jpg",
        "engine": "1.6L",
        "features": "Эксклюзивный дизайн, полный пакет опций"
    },
    {
        "id": 11,
        "name": "Hyundai Solaris I Базовая (2010)",
        "generation": "Базовая комплектация",
        "years": "2010",
        "description": "Самая доступная комплектация первого поколения. Минимум опций, максимум надежности.",
        "image": "solaris_base_2010.jpeg",
        "engine": "1.4L",
        "features": "Экономичность, надежность"
    },
    {
        "id": 12,
        "name": "Hyundai Solaris II Premium (2018)",
        "generation": "Премиум комплектация", 
        "years": "2018",
        "description": "Максимальная комплектация второго поколения с полным пакетом опций.",
        "image": "solaris_premium_2018.jpeg",
        "engine": "1.6L",
        "features": "Кожа, подогревы, мультимедиа"
    },
    {
        "id": 13,
        "name": "Hyundai Solaris Sport (2016)",
        "generation": "Спортивная версия",
        "years": "2016",
        "description": "Спортивный обвес, улучшенная подвеска, спортивные сиденья.",
        "image": "solaris_sport.jpeg",
        "engine": "1.6L",
        "features": "Спортивный дизайн, улучшенная динамика"
    },
    {
        "id": 14,
        "name": "Hyundai Solaris Urban (2019)",
        "generation": "Городская версия",
        "years": "2019",
        "description": "Специальная версия для городской эксплуатации с улучшенной маневренностью.",
        "image": "solaris_urban.jpeg", 
        "engine": "1.6L",
        "features": "Парктроники, камера, компактность"
    },
    {
        "id": 15,
        "name": "Hyundai Solaris Family (2015)",
        "generation": "Семейная версия",
        "years": "2015",
        "description": "Версия с усиленной безопасностью и дополнительными детскими опциями.",
        "image": "solaris_family.jpeg",
        "engine": "1.6L",
        "features": "Детские кресла, защита"
    },
    {
        "id": 16,
        "name": "Hyundai Solaris Taxi (2013)",
        "generation": "Такси-версия",
        "years": "2013", 
        "description": "Специальная подготовка для работы в такси. Усиленная подвеска, экономичный двигатель.",
        "image": "solaris_taxi.jpeg",
        "engine": "1.6L",
        "features": "Таксомоторный пакет, экономичность"
    },
    {
        "id": 17,
        "name": "Hyundai Solaris Winter (2017)",
        "generation": "Зимний пакет",
        "years": "2017",
        "description": "Комплектация с дополнительной подготовкой для зимней эксплуатации.",
        "image": "solaris_winter.jpg",
        "engine": "1.6L",
        "features": "Подогревы, зимняя резина"
    },
    {
        "id": 18,
        "name": "Hyundai Solaris Comfort (2022)",
        "generation": "Комфорт-версия",
        "years": "2022",
        "description": "Улучшенная шумоизоляция, комфортная подвеска, премиальная отделка салона.",
        "image": "solaris_comfort.jpeg",
        "engine": "1.6L", 
        "features": "Комфорт, тишина в салоне"
    },
    {
        "id": 19,
        "name": "Hyundai Solaris Eco (2020)",
        "generation": "Эко-версия",
        "years": "2020",
        "description": "Версия с системой старт-стоп и улучшенной аэродинамикой для снижения расхода.",
        "image": "solaris_eco.jpg",
        "engine": "1.6L",
        "features": "Эко-режим, низкий расход"
    },
    {
        "id": 20,
        "name": "Hyundai Solaris Anniversary (2021)",
        "generation": "Юбилейная версия",
        "years": "2021",
        "description": "Специальная версия к 10-летию Solaris в России с эксклюзивным дизайном.",
        "image": "solaris_anniversary.jpg",
        "engine": "1.6L",
        "features": "Эксклюзив, памятная отделка"
    }
]

@app.route('/lab2/solaris')
def solaris_gallery():
    return render_template('solaris.html', cars=solaris_cars)
