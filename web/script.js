// fetch from localhost:5000 and display the data
let url = 'http://localhost:5000';
fetch(url).then(response => response.json()).then(data => {
    console.log(data);
    document.getElementById('data').innerHTML = JSON.stringify(data);
})
