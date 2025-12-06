# lab7.py
from flask import Blueprint, render_template, request, jsonify, abort

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')


# Временное хранилище (в реальном проекте — база данных)
beers = [
    {
        "title": "ZATECKY GUS",
        "title_ru": "Гусь",
        "strength": 3.5,
        "description": "Пиво Zatecky Gus Cerny - это богатый вкус с нотками "
                       "поджаренного солода, карамели и бархатным ароматом жатецкого хмеля. "
                       "Рекомендуется употреблять в охлажденном виде",
    },
    {
        "title": "STELLA ARTOIS МРК",
        "title_ru": "Стелла",
        "strength": 5,
        "description": "Самое популярное в мире бельгийское легкое пиво премиум-класса, "
                       "имеет изысканный горьковатый оттенок. Отлично подходит для пикника "
                       "или летнего застолья с друзьями.",
    },
    {
        "title": "SPATEN MUNCHEN HELLES",
        "title_ru": "Шпатен",
        "strength": 5.2,
        "description": "Пиво умеренной крепости, с мягким пряным вкусом, превосходно "
                       "сочетающим в себе горечь хмеля и сладость пивного сусла.",
    }
]


@lab7.route('/lab7/rest-api/beers/', methods=['GET'])
def get_beers():
    return jsonify(beers)


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['GET'])
def get_beer(id):
    if id < 0 or id >= len(beers):
        abort(404)
    return jsonify(beers[id])


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['DELETE'])
def del_beer(id):
    if id < 0 or id >= len(beers):
        abort(404)
    del beers[id]
    return '', 204


@lab7.route('/lab7/rest-api/beers/', methods=['POST'])
def add_beer():
    beer = request.get_json()

    # Извлекаем и очищаем значения
    title_ru = beer.get('title_ru', '').strip()
    title = beer.get('title', '').strip()
    description = beer.get('description', '').strip()
    strength = beer.get('strength', 0)

    # Ключевая логика: если оригинального названия нет или оно пустое — копируем русское
    if not title and title_ru:
        title = title_ru

    # Валидация
    if not title_ru:
        return jsonify({'title_ru': 'Заполните русское название'}), 400

    if not description:
        return jsonify({'description': 'Заполните описание'}), 400

    # Приводим крепость к float
    try:
        strength = float(strength)
    except (ValueError, TypeError):
        strength = 0.0

    new_beer = {
        'title': title,
        'title_ru': title_ru,
        'strength': strength,
        'description': description
    }

    beers.append(new_beer)
    return jsonify(len(beers) - 1), 201


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['PUT'])
def put_beer(id):
    if id < 0 or id >= len(beers):
        abort(404)

    beer = request.get_json()

    title_ru = beer.get('title_ru', '').strip()
    title = beer.get('title', '').strip()
    description = beer.get('description', '').strip()
    strength = beer.get('strength', 0)

    # Ключевая логика: если оригинального названия нет или оно пустое — копируем русское
    if not title and title_ru:
        title = title_ru

    if not title_ru:
        return jsonify({'title_ru': 'Заполните русское название'}), 400

    if not description:
        return jsonify({'description': 'Заполните описание'}), 400

    try:
        strength = float(strength)
    except (ValueError, TypeError):
        strength = 0.0

    updated_beer = {
        'title': title,
        'title_ru': title_ru,
        'strength': strength,
        'description': description
    }

    beers[id] = updated_beer
    return jsonify(updated_beer)