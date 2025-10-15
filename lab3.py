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


# настройка стилей
@lab3.route('/lab3/settings')
def settings():
    # параметры стилей из GET-запроса
    color = request.args.get('color')
    background = request.args.get('background')
    font_size = request.args.get('font_size')
    padding = request.args.get('padding')

    # Если хотя бы один параметр передан сохраняем в куки
    if color or background or font_size or padding:
        # ответ с редиректом
        resp = make_response(redirect('/lab3/settings'))
        
        # установка куки для каждого переданного параметра
        if color:
            resp.set_cookie('color', color)
        if background:
            resp.set_cookie('background', background)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if padding:
            resp.set_cookie('padding', padding)
        return resp

    # Если параметров не было, то берем из куки
    color = request.cookies.get('color')
    background = request.cookies.get('background')
    font_size = request.cookies.get('font_size')
    padding = request.cookies.get('padding')
    
    return render_template('lab3/settings.html', color=color, background=background, font_size=font_size, padding=padding)


# удаление сохраненных стилей
@lab3.route('/lab3/del_style')
def del_style():
    resp = make_response(redirect('/lab3/settings'))
    
    # Удаляем все куки со стилями
    resp.delete_cookie('color')
    resp.delete_cookie('background')
    resp.delete_cookie('font_size')
    resp.delete_cookie('padding')
    
    return resp


from datetime import datetime


# страница оформления билета
@lab3.route('/lab3/ticket')
def ticket():
    errors = {}
    
    # Получаем параметры из GET-запроса
    fio = request.args.get('fio')
    age = request.args.get('age')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')

    # Валидация
    if fio == '':
        errors['fio'] = 'Заполните поле ФИО'
    if age == '':
        errors['age'] = 'Заполните поле возраста'
    elif age:  # если возрат указан, проверим корректен ли он
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            errors['age'] = 'Возраст должен быть от 1 до 120 лет'
    if departure == '':
        errors['departure'] = 'Заполните пункт выезда'
    if destination == '':
        errors['destination'] = 'Заполните пункт назначения'
    if date == '':
        errors['date'] = 'Выберите дату поездки'

    # страница билета с переданными данными и ошибками
    return render_template('lab3/ticket.html', 
                         fio=fio, age=age, shelf=shelf, linen=linen, 
                         baggage=baggage, departure=departure, 
                         destination=destination, date=date, insurance=insurance,
                         errors=errors)


# страница с результатом оформления билета
@lab3.route('/lab3/ticket_result')
def ticket_result():
    fio = request.args.get('fio')
    age = int(request.args.get('age'))  # возраст в число
    shelf = request.args.get('shelf')
    linen = request.args.get('linen') == 'on'  # Чекбоксы преобразуем в тру\фолс
    baggage = request.args.get('baggage') == 'on'
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance') == 'on'

    if age < 18:
        base_price = 700  # детский билет
    else:
        base_price = 1000  # взрослый билет

    # Надбавка за тип полки
    shelf_surcharge = 0
    if shelf in ['lower', 'side_lower']: 
        shelf_surcharge = 100

    # Расчет общей стоимости с учетом всех опций
    total_price = base_price + shelf_surcharge
    if linen:       # Постельное
        total_price += 75
    if baggage:     # Багаж
        total_price += 250
    if insurance:   # Страховка
        total_price += 150

    # для отображения времени оформления
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Отображаем страницу с результатом и всеми расчетами
    return render_template('lab3/ticket_result.html',
                         fio=fio, age=age, shelf=shelf, linen=linen,
                         baggage=baggage, departure=departure,
                         destination=destination, date=date, insurance=insurance,
                         base_price=base_price, shelf_surcharge=shelf_surcharge,
                         total_price=total_price, timestamp=timestamp)

# Список пива
all_products = [
        {'name': 'Балтика 0', 'price': 85, 'brand': 'Балтика', 'type': 'Безалкогольное', 'alcohol': 0.5, 'volume': 0.5},
        {'name': 'Балтика 6', 'price': 95, 'brand': 'Балтика', 'type': 'Портер', 'alcohol': 7.0, 'volume': 0.5},
        {'name': 'Балтика 7', 'price': 90, 'brand': 'Балтика', 'type': 'Экспортное', 'alcohol': 5.4, 'volume': 0.5},
        {'name': 'Балтика 9', 'price': 110, 'brand': 'Балтика', 'type': 'Крепкое', 'alcohol': 8.0, 'volume': 0.5},
        {'name': 'Жигулевское Барное', 'price': 80, 'brand': 'Жигулевское', 'type': 'Светлое', 'alcohol': 4.5, 'volume': 0.5},
        {'name': 'Корона', 'price': 150, 'brand': 'Corona', 'type': 'Лагер', 'alcohol': 4.5, 'volume': 0.33},
        {'name': 'Бад', 'price': 120, 'brand': 'BUD', 'type': 'Лагер', 'alcohol': 4.7, 'volume': 0.5},
        {'name': 'Охота Крепкое', 'price': 75, 'brand': 'Охота', 'type': 'Крепкое', 'alcohol': 7.2, 'volume': 0.5},
        {'name': 'Охота Классическое', 'price': 70, 'brand': 'Охота', 'type': 'Светлое', 'alcohol': 4.7, 'volume': 0.5},
        {'name': 'Туборг', 'price': 95, 'brand': 'Tuborg', 'type': 'Светлое', 'alcohol': 4.6, 'volume': 0.5},
        {'name': 'Сибирская Корона', 'price': 85, 'brand': 'Сибирская Корона', 'type': 'Классическое', 'alcohol': 4.7, 'volume': 0.5},
        {'name': 'Клинское Светлое', 'price': 65, 'brand': 'Клинское', 'type': 'Светлое', 'alcohol': 4.5, 'volume': 0.5},
        {'name': 'Клинское Безалкогольное', 'price': 75, 'brand': 'Клинское', 'type': 'Безалкогольное', 'alcohol': 0.5, 'volume': 0.5},
        {'name': 'Старый Мельник', 'price': 88, 'brand': 'Старый Мельник', 'type': 'Пшеничное', 'alcohol': 4.9, 'volume': 0.5},
        {'name': 'Золотая Бочка', 'price': 60, 'brand': 'Золотая Бочка', 'type': 'Светлое', 'alcohol': 4.3, 'volume': 0.5},
        {'name': 'Бочкарев Светлое', 'price': 78, 'brand': 'Бочкарев', 'type': 'Светлое', 'alcohol': 4.6, 'volume': 0.5},
        {'name': 'Бочкарев Темное', 'price': 82, 'brand': 'Бочкарев', 'type': 'Темное', 'alcohol': 4.8, 'volume': 0.5},
        {'name': 'Хайнекен', 'price': 140, 'brand': 'Heineken', 'type': 'Лагер', 'alcohol': 5.0, 'volume': 0.5},
        {'name': 'Гиннесс', 'price': 180, 'brand': 'Guinness', 'type': 'Стаут', 'alcohol': 4.2, 'volume': 0.44},
        {'name': 'Хугарден', 'price': 160, 'brand': 'Hoegaarden', 'type': 'Пшеничное', 'alcohol': 4.9, 'volume': 0.33},
        {'name': 'Ставропольское', 'price': 72, 'brand': 'Ставропольское', 'type': 'Светлое', 'alcohol': 4.5, 'volume': 0.5},
        {'name': 'Афанасий', 'price': 130, 'brand': 'Афанасий', 'type': 'Премиум', 'alcohol': 5.0, 'volume': 0.5},
        {'name': 'Велкопоповицкий Козел', 'price': 125, 'brand': 'Velkopopovicky', 'type': 'Лагер', 'alcohol': 4.6, 'volume': 0.5},
        {'name': 'Эфес', 'price': 95, 'brand': 'EFES', 'type': 'Пилснер', 'alcohol': 5.0, 'volume': 0.5},
        {'name': 'Карлсберг', 'price': 110, 'brand': 'Carlsberg', 'type': 'Лагер', 'alcohol': 5.0, 'volume': 0.5}
]

    # Находим мин и макс цены для плейсхолдеров
min_product_price = min(product['price'] for product in all_products)
max_product_price = max(product['price'] for product in all_products)


@lab3.route('/lab3/products')
def products():

    action = request.args.get('action')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # сброс
    if action == 'reset':
        resp = make_response(redirect('/lab3/products'))
        resp.delete_cookie('min_price')
        resp.delete_cookie('max_price')
        return resp

    # Получаем значения из куки если они есть
    if not min_price:
        min_price = request.cookies.get('min_price')
    if not max_price:
        max_price = request.cookies.get('max_price')

    filtered_products = all_products
    searched = False

    # Фильтрация товаров
    if min_price or max_price:
        searched = True
        
        # Преобразуем в числа, если не пустые
        min_val = int(min_price) if min_price else None
        max_val = int(max_price) if max_price else None
        
        # Если пользователь перепутал мин и макс - меняем местами
        if min_val and max_val and min_val > max_val:
            min_val, max_val = max_val, min_val
        
        # Фильтруем товары
        filtered_products = []
        for product in all_products:
            price = product['price']
            if min_val and max_val:
                if min_val <= price <= max_val:
                    filtered_products.append(product)
            elif min_val and not max_val:
                if price >= min_val:
                    filtered_products.append(product)
            elif max_val and not min_val:
                if price <= max_val:
                    filtered_products.append(product)
        
        # Сохраняем в cookies
        resp = make_response(render_template('lab3/products.html',
                           products=filtered_products,
                           min_price=min_price,
                           max_price=max_price,
                           min_product_price=min_product_price,
                           max_product_price=max_product_price,
                           searched=searched))
        
        if min_price:
            resp.set_cookie('min_price', min_price)
        if max_price:
            resp.set_cookie('max_price', max_price)
            
        return resp

    # Если нет фильтра - показываем все товары
    return render_template('lab3/products.html',
                         products=filtered_products,
                         min_price=min_price,
                         max_price=max_price,
                         min_product_price=min_product_price,
                         max_product_price=max_product_price,
                         searched=searched)