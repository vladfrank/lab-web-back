from flask import Blueprint, render_template, request, make_response, redirect, session
lab4 = Blueprint('lab4', __name__)

# Глобальный список пользователей (наш аналог БД)
users = [
    {'login': 'vlad', 'password': '123', 'name': 'Владислав Франк', 'gender': 'male'},
    {'login': 'bob', 'password': '555', 'name': 'Губка Боб', 'gender': 'male'},
    {'login': 'vika', 'password': 'lox', 'name': 'Виктория Мальборо', 'gender': 'female'},
    {'login': 'sanya', 'password': 'moshkovo', 'name': 'Александр Мошковский', 'gender': 'male'},
    {'login': 'egor_ivanovich', 'password': 'nstu', 'name': 'Егор Иванович', 'gender': 'male'},
]


@lab4.route('/lab4/')
def lab():
    return render_template('/lab4/lab4.html')


@lab4.route('/lab4/div-form')
def div_form():
    return render_template('/lab4/div-form.html')


@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены!')
    if x2 == '0':
        return render_template('lab4/div.html', error='На ноль делить нельзя!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)    


@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('/lab4/sum-form.html')


@lab4.route('/lab4/sum', methods = ['POST'])
def sum():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    
    # Если поля пустые берем значение 0
    x1 = 0 if x1 == '' else int(x1)
    x2 = 0 if x2 == '' else int(x2)
    
    result = x1 + x2
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/mul-form')
def mul_form():
    return render_template('/lab4/mul-form.html')


@lab4.route('/lab4/mul', methods = ['POST'])
def mul():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    
    # Если поля пустые берем значение 1
    x1 = 1 if x1 == '' else int(x1)
    x2 = 1 if x2 == '' else int(x2)
    
    result = x1 * x2
    return render_template('lab4/mul.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('/lab4/sub-form.html')


@lab4.route('/lab4/sub', methods = ['POST'])
def sub():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    
    # Проверка на пустые поля
    if x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error='Оба поля должны быть заполнены!')
    
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/pow-form')
def pow_form():
    return render_template('/lab4/pow-form.html')


@lab4.route('/lab4/pow', methods = ['POST'])
def pow():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    
    # Проверка на пустые поля
    if x1 == '' or x2 == '':
        return render_template('lab4/pow.html', error='Оба поля должны быть заполнены!')
    
    x1 = int(x1)
    x2 = int(x2)
    
    # Проверка на два нуля
    if x1 == 0 and x2 == 0:
        return render_template('lab4/pow.html', error='Оба числа не могут быть равны нулю!')
    
    result = x1 ** x2
    return render_template('lab4/pow.html', x1=x1, x2=x2, result=result)


tree_count = 0 
MAX_TREES = 10  # Максимальное количество деревьев

@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count, max_trees=MAX_TREES)

    operation = request.form.get('operation')

    if operation == 'cut':
        # проверяем, что деревья не в минусе
        if tree_count > 0:
            tree_count -= 1
    elif operation == 'plant':
        # проверяем количество деревьев, меньше ли 10
        if tree_count < MAX_TREES:
            tree_count += 1

    return redirect('/lab4/tree')


@lab4.route('/lab4/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            login = session['login']
            # Находим имя пользователя
            user_data = next((user for user in users if user['login'] == login), None)
            name = user_data['name'] if user_data else login
        else:
            authorized = False
            login = ''
            name = ''
        return render_template("lab4/login.html", authorized=authorized, login=login, name=name)

    login = request.form.get('login')
    password = request.form.get('password')
    
    # Проверка на пустые поля
    if not login:
        return render_template('lab4/login.html', error='Не введён логин', login_value=login, authorized=False)
    if not password:
        return render_template('lab4/login.html', error='Не введён пароль', login_value=login, authorized=False)
    
    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            session['name'] = user['name']
            return redirect('/lab4/login')
    
    error = 'Неверный логин и/или пароль'
    return render_template('lab4/login.html', error=error, login_value=login, authorized=False)


@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    session.pop('name', None)
    return redirect('/lab4/login')


@lab4.route('/lab4/fridge')
def fridge():
    return render_template('/lab4/fridge.html')


@lab4.route('/lab4/fridge-set', methods = ['POST'])
def fridge_set():
    temperature = request.form.get('temperature')
    
    # Проверка на пустое значение
    if not temperature:
        return render_template('lab4/fridge.html', error='Ошибка: не задана температура', temp_value=temperature)
    
    temp = int(temperature)
    
    # Проверка на низкую температуру
    if temp < -12:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру - слишком низкое значение', temp_value=temperature)
    
    # Проверка на высокую температуру
    if temp > -1:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру - слишком высокое значение', temp_value=temperature)
    
    # Определение количества снежинок в зависимости от температуры
    if -12 <= temp <= -9:
        snowflakes = 3
    elif -8 <= temp <= -5:
        snowflakes = 2
    elif -4 <= temp <= -1:
        snowflakes = 1
    else:
        snowflakes = 0
    
    message = f'Установлена температура: {temp}°С'
    return render_template('lab4/fridge.html', message=message, snowflakes=snowflakes)


@lab4.route('/lab4/beer-order')
def beer_order():
    return render_template('/lab4/beer-order.html')


@lab4.route('/lab4/beer-order-process', methods = ['POST'])
def beer_order_process():
    beer_type = request.form.get('beer_type')
    volume = request.form.get('volume')
    
    # Проверка на пустое значение объема
    if not volume:
        return render_template('lab4/beer-order.html', error='Не указан объем заказа', beer_type=beer_type)
    
    volume_float = float(volume)
    
    # Проверка на отрицательный или нулевой объем
    if volume_float <= 0:
        return render_template('lab4/beer-order.html', error='Объем должен быть больше 0', beer_type=beer_type, volume=volume)
    
    # Проверка на слишком большой объем
    if volume_float > 50:
        return render_template('lab4/beer-order.html', error='Такого объема сейчас нет в наличии', beer_type=beer_type, volume=volume)
    
    # Цены за литр
    prices = {
        'lager': 150,
        'ale': 180,
        'stout': 200,
        'wheat': 170
    }
    
    # Названия сортов пива
    beer_names = {
        'lager': 'Lager',
        'ale': 'Ale',
        'stout': 'Stout',
        'wheat': 'Пшеничное'
    }
    
    price_per_liter = prices[beer_type]
    beer_name = beer_names[beer_type]
    
    # Расчет стоимости
    total_cost = volume_float * price_per_liter
    
    # Применение скидки 10% за заказ более 10 литров
    discount_applied = False
    discount_amount = 0
    
    if volume_float > 10:
        discount_amount = total_cost * 0.1
        total_cost -= discount_amount
        discount_applied = True
    
    message = f'Заказ успешно сформирован. Вы заказали {beer_name}. Объем: {volume_float} л. Сумма к оплате: {total_cost:.0f} руб.'
    
    return render_template('lab4/beer-order.html', 
                         message=message, 
                         discount_applied=discount_applied,
                         discount_amount=discount_amount,
                         beer_type=beer_type,
                         volume=volume)


@lab4.route('/lab4/register')
def register():
    return render_template('/lab4/register.html')


@lab4.route('/lab4/register-process', methods = ['POST'])
def register_process():
    login = request.form.get('login')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    gender = request.form.get('gender')
    
    # Проверка на пустые поля
    if not login or not name or not password or not confirm_password:
        return render_template('lab4/register.html', error='Все поля должны быть заполнены', 
                             login_value=login, name_value=name, gender=gender)
    
    # Проверка совпадения паролей
    if password != confirm_password:
        return render_template('lab4/register.html', error='Пароли не совпадают', 
                             login_value=login, name_value=name, gender=gender)
    
    # Проверка на существующий логин
    for user in users:
        if user['login'] == login:
            return render_template('lab4/register.html', error='Пользователь с таким логином уже существует', 
                                 login_value=login, name_value=name, gender=gender)
    
    # Добавление нового пользователя
    new_user = {
        'login': login,
        'name': name,
        'password': password,
        'gender': gender
    }
    users.append(new_user)
    
    # Автоматический вход после регистрации
    session['login'] = login
    session['name'] = name
    
    return redirect('/lab4/login')


@lab4.route('/lab4/users')
def users_list():
    # Проверка авторизации
    if 'login' not in session:
        return redirect('/lab4/login')
    
    current_user_login = session['login']
    return render_template('/lab4/users.html', users=users, current_user=current_user_login)


@lab4.route('/lab4/edit-user', methods = ['POST'])
def edit_user():
    # Проверка авторизации
    if 'login' not in session:
        return redirect('/lab4/login')
    
    login = request.form.get('login')
    
    # Проверка, что пользователь редактирует только свой аккаунт
    if login != session['login']:
        return redirect('/lab4/users')
    
    user = next((u for u in users if u['login'] == login), None)
    if user:
        # Создаем копию без пароля для безопасности
        user_safe = user.copy()
        user_safe.pop('password', None)
        return render_template('/lab4/edit-user.html', user=user_safe)
    
    return redirect('/lab4/users')


@lab4.route('/lab4/update-user', methods = ['POST'])
def update_user():
    # Проверка авторизации
    if 'login' not in session:
        return redirect('/lab4/login')
    
    old_login = request.form.get('old_login')
    new_login = request.form.get('login')
    name = request.form.get('name')
    gender = request.form.get('gender')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Проверка, что пользователь редактирует только свой аккаунт
    if old_login != session['login']:
        return redirect('/lab4/users')
    
    # Проверка на существующий логин (если логин меняется)
    if new_login != old_login:
        for user in users:
            if user['login'] == new_login:
                user_safe = {'login': old_login, 'name': name, 'gender': gender}
                return render_template('/lab4/edit-user.html', user=user_safe, error='Пользователь с таким логином уже существует')
    
    # Находим пользователя
    user_index = next((i for i, u in enumerate(users) if u['login'] == old_login), None)
    if user_index is not None:
        # Обновляем данные
        users[user_index]['login'] = new_login
        users[user_index]['name'] = name
        users[user_index]['gender'] = gender
        
        # Обновляем пароль только если он указан
        if password and confirm_password:
            if password != confirm_password:
                user_safe = {'login': new_login, 'name': name, 'gender': gender}
                return render_template('/lab4/edit-user.html', user=user_safe, error='Пароли не совпадают')
            users[user_index]['password'] = password
        
        # Обновляем сессию
        session['login'] = new_login
        session['name'] = name
    
    return redirect('/lab4/users')


@lab4.route('/lab4/delete-user', methods = ['POST'])
def delete_user():
    # Проверка авторизации
    if 'login' not in session:
        return redirect('/lab4/login')
    
    login = request.form.get('login')
    
    # Проверка, что пользователь удаляет только свой аккаунт
    if login != session['login']:
        return redirect('/lab4/users')
    
    # Удаляем пользователя
    global users
    users = [user for user in users if user['login'] != login]
    
    # Выход из системы
    session.pop('login', None)
    session.pop('name', None)
    
    return redirect('/lab4/login')