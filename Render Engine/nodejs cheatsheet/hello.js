/*
exports.world = function() {
    console.log('Hello World');
};
*/
//hello.js直接通过exports对象把world作为模块的访问接口，在调用的js文件中可以直接访问exports的成员函数
//使用module可以把一个对象封装到模块中
function Hello() {
    var name;
    this.setName = function(thyName) {
        name = thyName;
    };
    this.sayHello = function () {
        console.log('Hello' + name)
    };
};
moudle.exports = Hello;