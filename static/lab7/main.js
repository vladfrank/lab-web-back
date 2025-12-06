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