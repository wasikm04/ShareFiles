const serverPort = 3000,
      https = require("https"),
      express = require("express"),
      fs = require('fs'),
      app = express()

var events = require('events');
var eventEmitter = new events.EventEmitter();

var key1 = fs.readFileSync('secured/app.key');
var cert1 =  fs.readFileSync('secured/app.crt');
var credentials = {key: key1, cert: cert1};
const serverHTTPS = https.createServer(credentials,app);


var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));
app.post('/wasikm/notification', function (request, response){
     var data = request.body;
     eventEmitter.emit(data.user, data.user);
     response.end();
  })


var users =[];
app.get('/wasikm/events/:user', function (request, response){
    var user1 = request.params.user;
    response.writeHead(200, {
      'Connection': 'keep-alive',
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin':'*'
    });
      var handler  = function handler(username) {
        if (user1 == username){
            let lastEventId = request.headers['last-event-id'] || '1';
            let id = parseInt(lastEventId);
            response.write('id: '+id+"\n");
            response.write('event: msg\n');
            response.write('data: nowy plik\n');
            response.write('\n\n');
            console.log("Wysłano powiadomienie");
        }
        };
    eventEmitter.on(user1, handler);
    console.log("Obecna ilość słuchaczy "+user1)
    console.log(eventEmitter.listeners(user1));

    response.on("close", function(){
       eventEmitter.removeListener(user1, handler);
    });
})

serverHTTPS.listen(serverPort, () => {
    console.log(`SSE server started on port ` + serverPort);
});


