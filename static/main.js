var list = document.getElementsByClassName("icon");
for (var i = 0; i < list.length; i++) {
        var item = list[i].name;
        list[i].addEventListener('click', function () {
            this.parentNode.parentNode.removeChild(this.parentNode);
            var url = "http://127.0.0.1:5555/wasikm/dl/delete/"+this.name;
            return fetch(url, {
                method: "DELETE",
            })
        });
};

var targetContainer = document.getElementById("notification");
var username = document.currentScript.getAttribute('user');

var eventSource = new EventSource("https://127.0.0.1:3000/wasikm/events/"+username);
eventSource.addEventListener('msg', event => {
   if (event.data) {
       var node = document.createElement( 'div' );
       var info = document.createElement( 'span' );
       info.innerHTML = ", aby go zobaczyć <a class='pointer' href='/wasikm/webapp/home'>odśwież</a> <strong class='pointer'>&times</strong>";
       info.classList.add("delete");
       node.innerHTML = "Dodano "+event.data;
       node.classList.add("notify");
       node.appendChild(info);
       targetContainer.appendChild(node);
       console.log('new data')
       info.childNodes[3].addEventListener('click',function(){
            node.parentNode.removeChild(node);
        });
    } else {
    console.log('no data')
    }
});



