//为路由提供请求的URL和其他需要的POST以及GET参数，随后路由需要根据这些数据执行相应的代码
/*
                   url.parse(string).query
                                           |
           url.parse(string).pathname      |
                       |                   |
                       |                   |
                     ------ -------------------
http://localhost:8888/start?foo=bar&hello=world
                                ---       -----
                                 |          |
                                 |          |
              querystring.parse(queryString)["foo"]    |
                                            |
                         querystring.parse(queryString)["hello"]
 */
var http = require('http');
var url = require('url');

function start(route) {
    function onRequest(request, response) {
        var pathname = url.parse(request.url).pathname;
        console.log("Request for " + pathname + "received");

        route(pathname);

        response.writeHead(200, {"Content-Type":"text/plain"});
        response.write("Hello World");
        response.end();
    }
    http.createServer(onRequest).listen(8888);
    console.log("Server Started");
}

exports.start = start;



