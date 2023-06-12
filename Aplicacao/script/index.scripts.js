function extrairDados() {
    var form = document.getElementById('form');
    var formData = new FormData(form);

    var request = new XMLHttpRequest();
    request.open('POST', '/processar');
    request.onreadystatechange = function() {
        if (request.readyState === 4 && request.status === 200) {
            window.location.href = './dados.html';
        }
    };
    request.send(formData);}