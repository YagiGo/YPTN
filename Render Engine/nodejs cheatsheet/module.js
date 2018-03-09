/*
在JavaScript中，一个函数可以作为另一个函数的参数。我们可以先定义一个函数，然后传递，也可以在传递参数的地方直接定义函数。

Node.js中函数的使用与Javascript类似，举例来说，你可以这样做：
 */
/*
function say(word) {
    console.log(word);
}

function execute(someFunction, value) {
    someFunction(value);
}

execute(say, "Hello");
//以上代码直接传递say函数本身

var hello = require('./hello');
hello.world();
*/
var Hello = require('./hello');
hello = new Hello();
hello.setName('Jeremy');
hello.sayHello();
