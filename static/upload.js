// NIE UYWAwać
function submit(){
        var elements = document.getElementsByName('file');
        var dataToSend = new FormData();
        dataToSend.append(elements[0].name, elements[0].files[0],elements[0].files[0].name);
        dataToSend.append('jwt',document.getElementsByName('jwt')[0].value)
    fetch("http://127.0.0.1:5555/wasikm/dl/upload", {
        method: "POST",
        mode: "no-cors",
        body: dataToSend
    }).then(function(response) {
        if (response.ok) {
          window.location.href = "http://127.0.0.1:5000/wasikm/webapp/home";
        } else {
            alert("Coś się wydarzyło ");
        }
    })
}