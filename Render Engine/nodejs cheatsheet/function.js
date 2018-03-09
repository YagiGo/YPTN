//直接传递函数
function say(word) {
    console.log(word);
}

function execute(someFunction, value) {
    someFunction(value);
}

execute(say, "Hello");

//匿名函数
function execute(someFunction, value) {
    someFunction(value);
}

execute(function(word) {console.log(word);}, 'Hello');

//一个简单的node js HTTP服务器
var http = require('http');
http.createServer(function(request, response) {
    response.writeHead(200, {"Content-Type" : "text/plain"});
    response.write('Hello');
    response.end();
}).listen(8888);


