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

            tdTitle.innerText = beers[i].title == beers[i].title_ru ? '' : beers[i].title;
            tdTitleRus.innerText = beers[i].title_ru;
            tdStrength.innerText = beers[i].strength;

            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';

            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';

            tdActions.append(editButton);
            tdActions.append(delButton);

            tr.append(tdTitle);
            tr.append(tdTitleRus);
            tr.append(tdStrength);

            tbody.append(tr);
        }
    })
}