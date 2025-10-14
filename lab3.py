from flask import Blueprint, render_template, request, make_response,redirect
lab3 = Blueprint('lab3', __name__)

@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    age = request.cookies.get('age')
    name_color = request.cookies.get('name_color')
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Vlad', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'
    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'
    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)


@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')


@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    #Пусть Балтика стоит 70р, Жигуль 80р, Охота 60р
    if drink == 'baltika':
        price = 70
    elif drink == 'zhiguli':
        price = 80
    else:
        price = 60

    #Добавка чипосов стоит 120р, а кальмаров - на 85р
    if request.args.get('chips') == 'on':
        price += 120
    if request.args.get('kalmar') == 'on':
        price += 85
    return render_template('lab3/pay.html', price=price)


@lab3.route('/lab3/success')
def success():
    price = request.args.get('price', 0)
    return render_template('lab3/success.html', price=price)


@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    background = request.args.get('background')
    font_size = request.args.get('font_size')
    padding = request.args.get('padding')

    if color or background or font_size or padding:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if background:
            resp.set_cookie('background', background)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if padding:
            resp.set_cookie('padding', padding)
        return resp

    color = request.cookies.get('color')
    background = request.cookies.get('background')
    font_size = request.cookies.get('font_size')
    padding = request.cookies.get('padding')
    return render_template('lab3/settings.html', color=color, background=background, font_size=font_size, padding=padding)


from datetime import datetime

@lab3.route('/lab3/ticket')
def ticket():
    errors = {}
    fio = request.args.get('fio')
    age = request.args.get('age')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')

    # Проверка полей
    if fio == '':
        errors['fio'] = 'Заполните поле ФИО'
    if age == '':
        errors['age'] = 'Заполните поле возраста'
    elif age:
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            errors['age'] = 'Возраст должен быть от 1 до 120 лет'
    if departure == '':
        errors['departure'] = 'Заполните пункт выезда'
    if destination == '':
        errors['destination'] = 'Заполните пункт назначения'
    if date == '':
        errors['date'] = 'Выберите дату поездки'

    return render_template('lab3/ticket.html', 
                         fio=fio, age=age, shelf=shelf, linen=linen, 
                         baggage=baggage, departure=departure, 
                         destination=destination, date=date, insurance=insurance,
                         errors=errors)

@lab3.route('/lab3/ticket_result')
def ticket_result():
    fio = request.args.get('fio')
    age = int(request.args.get('age'))
    shelf = request.args.get('shelf')
    linen = request.args.get('linen') == 'on'
    baggage = request.args.get('baggage') == 'on'
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance') == 'on'

    # Расчет стоимости
    if age < 18:
        base_price = 700  # детский
    else:
        base_price = 1000  # взрослый

    shelf_surcharge = 0
    if shelf in ['lower', 'side_lower']:
        shelf_surcharge = 100

    total_price = base_price + shelf_surcharge
    if linen:
        total_price += 75
    if baggage:
        total_price += 250
    if insurance:
        total_price += 150

    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    return render_template('lab3/ticket_result.html',
                         fio=fio, age=age, shelf=shelf, linen=linen,
                         baggage=baggage, departure=departure,
                         destination=destination, date=date, insurance=insurance,
                         base_price=base_price, shelf_surcharge=shelf_surcharge,
                         total_price=total_price, timestamp=timestamp)