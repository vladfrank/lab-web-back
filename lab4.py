from flask import Blueprint, render_template, request, make_response, redirect, session
lab4 = Blueprint('lab4', __name__)


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


users = [
    {'login': 'vlad', 'password': '123', 'name': 'Владислав Франк', 'gender': 'male'},
    {'login': 'bob', 'password': '555', 'name': 'Губка Боб', 'gender': 'male'},
    {'login': 'vika', 'password': 'lox', 'name': 'Виктория Мальборо', 'gender': 'female'},
    {'login': 'sanya', 'password': 'moshkovo', 'name': 'Александр Мошковский', 'gender': 'male'},
    {'login': 'egor_ivanovich', 'password': 'nstu', 'name': 'Егор Иванович', 'gender': 'male'},
]


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
    
    # Проверка на слишком низкую температуру
    if temp < -12:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру - слишком низкое значение', temp_value=temperature)
    
    # Проверка на слишком высокую температуру
    if temp > -1:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру - слишком высокое значение', temp_value=temperature)
    
    # Определение количества снежинок в зависимости от диапазона температуры
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
