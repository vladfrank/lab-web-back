function fillBeerList() {
    fetch('/lab7/rest-api/beers/')
    .then(function (data) {
        return data.json();
    })
    .then(function (beers) {
        let tbody = document.getElementById('beer-list');
        tbody.innerHTML = '';
        for(let i = 0; i<beers.length; i++) {
            let tr = document.createElement('tr');

            let tdTitle = document.createElement('td');
            let tdTitleRus = document.createElement('td');
            let tdStrength = document.createElement('td');
            let tdDescription = document.createElement('td'); 
            let tdActions = document.createElement('td');

            tdTitle.innerText = beers[i].title == beers[i].title_ru ? '' : beers[i].title;
            tdTitleRus.innerText = beers[i].title_ru;
            tdStrength.innerText = beers[i].strength;
            tdDescription.innerText = beers[i].description;

            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';
            editButton.onclick = function() {
                editBeer(i);
            };

            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';
            delButton.onclick = function() {
                deleteBeer(i, beers[i].title_ru);
            };

            tdActions.append(editButton);
            tdActions.append(delButton);

            tr.append(tdTitle);
            tr.append(tdTitleRus);
            tr.append(tdStrength);
            tr.appendChild(tdDescription);
            tr.appendChild(tdActions);

            tbody.append(tr);
        }
    })
}

function deleteBeer(id, title) {
    if(! confirm(`Вы точно хотите удалить пиво "${title}"?`))
        return;

    fetch(`/lab7/rest-api/beers/${id}`, {method: 'DELETE'})
        .then(function () {
            fillBeerList();
        })
}

function showModal() {
    document.querySelector('div.modal').style.display = 'block';
}
function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
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
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title-ru').value,
        strength: parseFloat(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value
    }

    const url = id === '' ? `/lab7/rest-api/beers/` : `/lab7/rest-api/beers/${id}`;
    const method = id === '' ? 'POST' : 'PUT';

    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(beer)
    })
    .then(function() {
        fillBeerList();
        hideModal();
    });
}

function editBeer(id) {
    fetch(`/lab7/rest-api/beers/${id}`)
    .then(function (data) {
        return data.json();
    })
    .then(function (beer) {
        document.getElementById('id').value = id;
        document.getElementById('title').value = beer.title;
        document.getElementById('title-ru').value = beer.title_ru;
        document.getElementById('year').value = beer.strength; 
        document.getElementById('description').value = beer.description;
        showModal();
    })
}