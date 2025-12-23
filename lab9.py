from flask import Blueprint, render_template, request, jsonify, session
import random

lab9 = Blueprint('lab9', __name__)

BOX_COUNT = 10

# Генерация позиций без сильного наложения
positions = []
attempts = 0
max_attempts = 1000

while len(positions) < BOX_COUNT and attempts < max_attempts:
    top = random.randint(10, 70)
    left = random.randint(5, 80)

    overlap = False
    for pos in positions:
        dt = abs(int(pos["top"][:-1]) - top)
        dl = abs(int(pos["left"][:-1]) - left)
        if dt < 18 and dl < 18:
            overlap = True
            break

    if not overlap:
        positions.append({"top": f"{top}%", "left": f"{left}%"})

    attempts += 1

while len(positions) < BOX_COUNT:
    positions.append({"top": f"{random.randint(10, 70)}%", "left": f"{random.randint(5, 80)}%"})

# Подарки: текст + happy*.jpg
gifts = [
    {"text": "С Новым 2026 годом! Здоровья и счастья!", "img": "/static/lab9/happy1.jfif"},
    {"text": "Пусть 2026 принесёт успех и радость!", "img": "/static/lab9/happy2.jfif"},
    {"text": "Море позитива и волшебства в Новом году!", "img": "/static/lab9/happy3.jfif"},
    {"text": "Счастья, любви и исполнения всех желаний!", "img": "/static/lab9/happy4.jfif"},
    {"text": "Дачу у моря и море удачи!", "img": "/static/lab9/happy5.jfif"},
    {"text": "Финансового благополучия и стабильности!", "img": "/static/lab9/happy6.jfif"},
    {"text": "Тепла, уюта и семейного счастья!", "img": "/static/lab9/happy7.jfif"},
    {"text": "Новых достижений и ярких эмоций!", "img": "/static/lab9/happy8.jfif"},
    {"text": "Мира, добра и настоящего волшебства!", "img": "/static/lab9/happy9.jfif"},
    {"text": "Пусть все мечты сбудутся в 2026 году!", "img": "/static/lab9/happy10.jfif"},
]

opened_boxes = set()

@lab9.route('/lab9/')
def main():
    return render_template('lab9/index.html', positions=positions)

@lab9.route('/lab9/open', methods=['POST'])
def open_box():
    if 'opened_count' not in session:
        session['opened_count'] = 0

    data = request.get_json()
    box_id = data.get('box_id')

    if not 0 <= box_id < BOX_COUNT:
        return jsonify({"success": False, "message": "Неверный номер коробки"})

    if box_id in opened_boxes:
        return jsonify({"success": False, "message": "Эта коробка уже открыта"})

    if session['opened_count'] >= 3:
        return jsonify({"success": False, "message": "Вы уже открыли максимум 3 подарка!"})

    opened_boxes.add(box_id)
    session['opened_count'] += 1

    gift = gifts[box_id]
    remaining = BOX_COUNT - len(opened_boxes)

    return jsonify({
        "success": True,
        "text": gift["text"],
        "img": gift["img"],
        "remaining": remaining,
        "opened_count": session['opened_count']
    })

@lab9.route('/lab9/status')
def status():
    remaining = BOX_COUNT - len(opened_boxes)
    opened_count = session.get('opened_count', 0)
    return jsonify({"remaining": remaining, "opened_count": opened_count})

@lab9.route('/lab9/reset', methods=['POST'])
def reset_personal():
    session['opened_count'] = 0
    remaining = BOX_COUNT - len(opened_boxes)
    return jsonify({
        "success": True,
        "opened_count": 0,
        "remaining": remaining,
        "message": "Лимит сброшен! Теперь можно открыть ещё 3 подарка."
    })