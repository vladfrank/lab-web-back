function fillBeerList() {
    fetch('/lab7/rest-api/beers/')
        .then(response => response.json())
        .then(beers => {
            const tbody = document.getElementById('beer-list');
            tbody.innerHTML = '';

            beers.forEach((beer, index) => {
                const tr = document.createElement('tr');

                const tdRus = document.createElement('td');
                const tdOrig = document.createElement('td');
                const tdStrength = document.createElement('td');
                const tdDesc = document.createElement('td');
                const tdActions = document.createElement('td');

                // Русское название
                tdRus.textContent = beer.title_ru;
                tdRus.style.fontWeight = '500';

                // Оригинальное название
                if (beer.title?.trim()) {
                    const span = document.createElement('span');
                    span.className = 'original-name';
                    span.textContent = `(${beer.title})`;
                    tdOrig.appendChild(span);
                }

                // Крепость
                tdStrength.textContent = beer.strength + '%';

                // Описание с обрезкой
                let desc = beer.description || '';
                if (desc.length > 100) {
                    desc = desc.substring(0, 100) + '...';
                }
                tdDesc.textContent = desc;

                // Кнопки
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Редактировать';
                editBtn.onclick = () => editBeer(index);

                const delBtn = document.createElement('button');
                delBtn.textContent = 'Удалить';
                delBtn.onclick = () => deleteBeer(index, beer.title_ru);

                tdActions.append(editBtn, delBtn);

                // Собираем строку
                tr.append(tdRus, tdOrig, tdStrength, tdDesc, tdActions);
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error('Не удалось загрузить список пива:', err);
        });
}

function deleteBeer(id, title) {
    if (!confirm(`Удалить пиво "${title}"?`)) return;

    fetch(`/lab7/rest-api/beers/${id}`, { method: 'DELETE' })
        .then(() => fillBeerList());
}

function showModal() {
    document.getElementById('description-error').textContent = '';
    document.querySelector('.modal').style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';
}

function hideModal() {
    document.querySelector('.modal').style.display = 'none';
    document.querySelector('.modal-backdrop').style.display = 'none';
}

function cancel() {
    hideModal();
}

function addBeer() {
    document.getElementById('id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    showModal();
}

function sendBeer() {
    const id = document.getElementById('id').value;

    const beer = {
        title_ru: document.getElementById('title-ru').value.trim(),
        title: document.getElementById('title').value.trim(),
        strength: parseFloat(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value.trim()
    };

    // Если оригинальное название пустое — не отправляем поле (бэкенд сам скопирует русское)
    if (!beer.title) {
        delete beer.title;
    }

    const method = id ? 'PUT' : 'POST';
    const url = id ? `/lab7/rest-api/beers/${id}` : '/lab7/rest-api/beers/';

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
    .catch(err => {
        if (err.description) {
            document.getElementById('description-error').textContent = err.description;
        }
        if (err.title_ru) {
            alert(err.title_ru);
        }
    });
}

// ГЛАВНОЕ: всегда показываем настоящее оригинальное название при редактировании
function editBeer(id) {
    fetch(`/lab7/rest-api/beers/${id}`)
        .then(resp => resp.json())
        .then(beer => {
            document.getElementById('id').value = id;
            document.getElementById('title-ru').value = beer.title_ru;
            document.getElementById('title').value = beer.title || '';  // ← ВСЁ ВРЕМЯ ПОКАЗЫВАЕМ РЕАЛЬНОЕ ЗНАЧЕНИЕ
            document.getElementById('year').value = beer.strength;
            document.getElementById('description').value = beer.description;
            showModal();
        });
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', fillBeerList);