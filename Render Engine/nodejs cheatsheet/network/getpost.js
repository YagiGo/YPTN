var http = require('http');
var url = require('url');
var util = require('util');
/*
http.createServer(function(req, res) {
    res.writeHead(200, {"Content-Type" : "text/plain; charset=utf8"});
    var param = url.parse(req.url, true).query;
    res.write("Name: " + param.name);
    res.write('\n');
    res.write("URL: " + param.url);
    res.end()
}).listen(3000);
*/
//POST
/*
var querystring = require('querystring');
http.createServer(function(req,res) {
    var post = '';
    req.on('data', function(chunk) {
        post += chunk;
    });
    //end事件触发之后通过querystring.parse将post解析为真正的POST请求格式，向客户端返回
    req.on('end', function() {
        post = querystring.parse(post);
        res.end(util.inspect(post));
    });
}).listen(3000);
*/
var querystring = require('querystring');
var fs = require('fs');
/*
function readHTMLFile(path) {
    fs.readFile(path, function(err, data) {
        if(err) {
            return console.error(err);
        }
        return data.toString();
    })
}
const postHTML = readHTMLFile('index.html');
console.log(postHTML)
*/
var postHTML = fs.readFileSync('index.html').toString(); //必须使用同步，不然HTML代码无法传入

//ECMA6的promise特性，使用promise传输数据
/*
var readFile = function(fileName) {
    var promise = new Promise((resolve, reject) => {
        fs.readFile(fileName, 'utf8', (err, data) => {
            if(err) {
                reject(err);
            }
            resolve(data);
        });
    });
    return promise;
};
var postHTML = readFile('index.html').then(function(data){return (data.toString())}, function(err) {
    return console.error(err);
});
*/
/*
    '<html><head><meta charset="utf-8"><title>Greet Site</title></head>'+
    '<body>' +
    '<form method=="post">' +
    'Name: <input name = "name"><br>' +
    'Age: <input name = "age"><br>' +
    '<input type="submit">' +
    '</form>' +
    '</body>' +
    '</html>';
   */
console.log(postHTML);
http.createServer(function(req,res) {
    var body = "";
    req.on('data', function(chunk) {
        body += chunk;
    });
    req.on('end', function() {
        body = querystring.parse(body);
        res.writeHead(200, {"Content-Type" : "text/html; charset=utf8"});
        console.log(body);
        if(body.name && body.age) {
            res.write("Hello! " + body.name );
            res.write('<br>');
            res.write("You are " + body.age + ' years old');
        }
        else {res.write(postHTML);}
        res.end();
    });
}).listen(3000);