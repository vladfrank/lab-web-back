// Загружаем список пива
function fillBeerList() {
    fetch('/lab7/rest-api/beers/')
        .then(response => response.json())
        .then(beers => {
            const tbody = document.getElementById('beer-list');
            tbody.innerHTML = '';

            beers.forEach(beer => {
                const tr = document.createElement('tr');

                const tdRus = document.createElement('td');
                const tdOrig = document.createElement('td');
                const tdStrength = document.createElement('td');
                const tdDesc = document.createElement('td');
                const tdActions = document.createElement('td');

                // Русское название
                tdRus.textContent = beer.title_ru;

                // Оригинальное название: курсив + скобки
                if (beer.title && beer.title.trim() !== "") {
                    tdOrig.innerHTML = `<i>(${beer.title})</i>`;
                } else {
                    tdOrig.textContent = "—";
                }

                // Крепость
                tdStrength.textContent = beer.strength + '%';

                // Описание
                tdDesc.textContent = beer.description || '';

                // Кнопки
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Редактировать';
                editBtn.className = 'edit-button';
                editBtn.onclick = () => editBeer(beer.id);

                const delBtn = document.createElement('button');
                delBtn.textContent = 'Удалить';
                delBtn.className = 'delete-button';
                delBtn.onclick = () => deleteBeer(beer.id, beer.title_ru);

                tdActions.append(editBtn, delBtn);

                tr.append(tdRus, tdOrig, tdStrength, tdDesc, tdActions);
                tbody.appendChild(tr);
            });

        })
        .catch(err => console.error('Ошибка загрузки списка:', err));
}


// Удаление
function deleteBeer(id, title) {
    if (!confirm(`Удалить пиво "${title}"?`)) return;

    fetch(`/lab7/rest-api/beers/${id}`, { method: 'DELETE' })
        .then(() => fillBeerList());
}


// Модалка
function showModal() {
    document.querySelector('.modal').style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';

    document.getElementById('title-ru-error').textContent = '';
    document.getElementById('title-error').textContent = '';
    document.getElementById('strength-error').textContent = '';
    document.getElementById('description-error').textContent = '';
}

function hideModal() {
    document.querySelector('.modal').style.display = 'none';
    document.querySelector('.modal-backdrop').style.display = 'none';
}

function cancel() {
    hideModal();
}


// Добавление
function addBeer() {
    document.getElementById('id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';

    showModal();
}


// Сохранение
function sendBeer() {
    const id = document.getElementById('id').value;

    const beer = {
        title_ru: document.getElementById('title-ru').value.trim(),
        title: document.getElementById('title').value.trim(),
        strength: document.getElementById('year').value || 0,
        description: document.getElementById('description').value.trim()
    };

    // Если оригинал пуст — backend сам проставит title_ru
    if (!beer.title) {
        delete beer.title;
    }

    const method = id ? 'PUT' : 'POST';
    const url = id
        ? `/lab7/rest-api/beers/${id}`
        : `/lab7/rest-api/beers/`;

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(beer)
    })
    .then(resp => {
        if (!resp.ok) {
            return resp.json().then(err => { throw err; });
        }
        fillBeerList();
        hideModal();
    })
    .catch(errors => {
        if (errors.title_ru) document.getElementById('title-ru-error').textContent = errors.title_ru;
        if (errors.title) document.getElementById('title-error').textContent = errors.title;
        if (errors.strength) document.getElementById('strength-error').textContent = errors.strength;
        if (errors.description) document.getElementById('description-error').textContent = errors.description;
    });
}


// Редактирование
function editBeer(id) {
    fetch(`/lab7/rest-api/beers/${id}`)
        .then(resp => resp.json())
        .then(beer => {
            document.getElementById('id').value = id;
            document.getElementById('title-ru').value = beer.title_ru;
            document.getElementById('title').value = beer.title || '';
            document.getElementById('year').value = beer.strength;
            document.getElementById('description').value = beer.description;

            showModal();
        });
}


// Старт
document.addEventListener('DOMContentLoaded', fillBeerList);
