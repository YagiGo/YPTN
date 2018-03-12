//util.inherits 实现对象间的原型继承， JS的面向对象是通过原型复制实现的
var util = require('util');
function Base() {
    this.name = 'base';
    this.base = 1991;
    this.sayHello = function() {
        console.log('Hello' + this.name);
    };
}
//prototype 属性使您有能力向对象添加属性和方法。
//object.prototype.name=value
Base.prototype.showName = function() {
    console.log(this.name);
};

function Sub() {
    this.name = 'sub';
}
//使用util.inherits只会继承原型中的属性

util.inherits(Sub, Base);
var objBase = new  Base();
objBase.sayHello();
objBase.showName();
console.log(objBase);

var objSub = new Sub();
objSub.showName();
console.log(objSub);

function Abc() {
    this.property1 = '1';
    this.showProperty = function() {
        console.log("property 1 should not be inherited");
    }
}
Abc.prototype.prototypeFunction1 = function() {
    console.log("this should be inherited");
};
Abc.prototype.prototypeFunction2 = function() {
    console.log("This should also be inherited");
};

function Inhabc() {
    this.property2 = '2';
}
util.inherits(Inhabc, Abc);
var objAbc = new Abc();
console.log(objAbc);
objAbc.prototypeFunction1();
objAbc.prototypeFunction2();

var objInhabc = new Inhabc();
console.log(objInhabc);
objInhabc.prototypeFunction1();
objInhabc.prototypeFunction2();

//In a word, util.inherits只继承prototype的属性


