from flask import Blueprint, render_template, request, jsonify, abort

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')

beers = [
    {
        "title": "ZATECKY GUS",
        "title_ru": "Гусь",
        "strength": 3.5,
        "description": "Пиво Zatecky Gus Cerny - это богатый вкус с нотками \
        поджаренного солода, карамели и бархатным ароматом жатецкого хмеля. \
        Рекомендуется упортреблять в охлажденном виде",
    },
    {
        "title": "STELLA ARTOIS МРК",
        "title_ru": "Стелла",
        "strength": 5,
        "description": "Самое популярное в мире бельгийское легкое пиво \
        премиум класса, имеет изысканный горьковатый оттенок, что выделяет \
        его на фоне других традиционных европейских сортов типа «лагер» \
        и высоко ценится знатоками пива. Рекомендуется употреблять \
        охлажденным. Отлично подходит для пикника или летнего застолья \
        с друзьями, легко пьется.",
    },
    {
        "title": "SPATEN MUNCHEN HELLES",
        "title_ru": "Шпатен",
        "strength": 5.2,
        "description": "Пиво умеренной крепости, с мягким пряным вкусом, \
        превосходно сочетающим в себе горечь хмеля и сладость \
        пивного сусла",
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


@lab7.route('/lab7/rest-api/beers/<int:id>', methods=['PUT'])
def put_beer(id):
    if id < 0 or id >= len(beers):
        abort(404)
    beer = request.get_json()
    beers[id] = beer
    return jsonify(beers[id])


@lab7.route('/lab7/rest-api/beers/', methods=['POST'])
def add_beer():
    beer = request.get_json()
    beers.append(beer)
    return jsonify(len(beers) - 1), 201