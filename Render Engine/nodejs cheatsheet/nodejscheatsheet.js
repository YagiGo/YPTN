/*
var events = require('events');
var eventEmitter = new events.EventEmitter();
var connectHandler = function connceted() {
    console.log('Access Success');
    eventEmitter.emit('data_received');
}
eventEmitter.on('connection', connectHandler);
eventEmitter.on('data_received', function() {
    console.log('Data Received');
});
eventEmitter.emit('connection');
console.log("Processs Finished");
*/
/*
var EventEmitter = require('events').EventEmitter;
var event = new EventEmitter();
event.on('some_event', function() {
    console.log("shijianchufa");
});
setTimeout(function() {
    event.emit('some_event')
}, 1000);
*/
/*
var EventEmitter = require('events').EventEmitter;
var event = new EventEmitter();
emitter.on('someEvent', function(arg1, arg2) {
    console.log('listener1', arg1, arg2);
});
emitter.on('someEvent', function(arg1, arg2) {
    console.log('listener2', arg1, arg2);
});
emitter.emit('someEvent', 'arg1', 'arg2');
*/
var EventEmitter = require('events').EventEmitter;
var eventEmitter = new EventEmitter();
// listener 1
var listener1 = function listener() {
    console.log("listener 1 now running");
};

var listener2 = function listener() {
    console.log("listener 2 now running");
};

eventEmitter.addListener('connection', listener1);
eventEmitter.on('connection', listener2);

var eventListeners = require('events').EventEmitter.listenerCount(eventEmitter, 'connection');
console.log(eventListeners + " Listeners Running at Present");

eventEmitter.emit('connection');

eventEmitter.removeListener('connection', listener1);
console.log('Listener1 quited');

eventEmitter.emit('connection');
eventListeners = require('events').EventEmitter.listenerCount(eventEmitter, 'connection');
console.log(eventListeners + " Listeners now running");

console.log("Finished");
const buf = Buffer.from('test', 'ascii');
console.log(buf.toString('hex'));
console.log(buf.toString('base64'));

//Buffer.alloc(size[, fill[, encoding]])： 返回一个指定大小的 Buffer 实例，如果没有设置 fill，则默认填满 0
//长度10，填满0的Buffer
const buf1 = Buffer.alloc(10);
//长度10，填满0x1的Buffer
const buf2 = Buffer.alloc(10, 1);
//Buffer.allocUnsafe(size)： 返回一个指定大小的 Buffer 实例，但是它不会被初始化，所以它可能包含敏感的数据
// 长度10， 未初始化的Buffer
const buf3 = Buffer.allocUnsafe(10);

// 创建一个包含 [0x1, 0x2, 0x3] 的 Buffer。
const buf4 = Buffer.from([1, 2, 3]);

// 创建一个包含 UTF-8 字节 [0x74, 0xc3, 0xa9, 0x73, 0x74] 的 Buffer。
const buf5 = Buffer.from('tést');

// 创建一个包含 Latin-1 字节 [0x74, 0xe9, 0x73, 0x74] 的 Buffer。
const buf6 = Buffer.from('tést', 'latin1');



//写入缓冲区和从缓冲区读取数据
//写入缓冲区
/*
buf.write(string[, offset[, length]][, encoding])
string - 写入缓冲区的字符串。

offset - 缓冲区开始写入的索引值，默认为 0 。

length - 写入的字节数，默认为 buffer.length

encoding - 使用的编码。默认为 'utf8' 。

返回实际写入的大小。如果 buffer 空间不足， 则只会写入部分字符串。

 */
const buf7 = Buffer.alloc(256);
len = buf7.write('www.example.com');
console.log(len + ' Bytes was written');

//从缓冲区读取数据
/*
buf.toString([encoding[, start[, end]]])
encoding - 使用的编码。默认为 'utf8' 。

start - 指定开始读取的索引位置，默认为 0。

end - 结束位置，默认为缓冲区的末尾。
 */
const buf8 = Buffer.alloc(26);
for (var i = 0; i < 26; i++) {
    buf8[i] = i + 97;
}
console.log(buf8.toString('ascii'));
console.log(buf8.toString('ascii', 0, 5));
console.log(buf8.toString('ascii', 0, 5));
console.log(buf8.toString('utf8', 0, 5));

// Buffer to JSON
/*
buf.toJSON()
 */
const buf9 = Buffer.from([0x1,0x2,0x3,0x4,0x5]);
const json = JSON.stringify(buf9);
// 输出: {"type":"Buffer","data":[1,2,3,4,5]}
console.log(json);
// =>箭头函数， 可以直接对参数进行调整
/*
(参数1, 参数2, …, 参数N) => {函数声明}
(参数1, 参数2, …, 参数N) => 表达式（单一）
//相当于：(参数1, 参数2, …, 参数N) =>{ return表达式}

// 当只有一个参数时，圆括号是可选的：
(单一参数) => {函数声明}
单一参数 => {函数声明}

// 没有参数的函数应该写成一对圆括号。
() => {函数声明}
 */

//缓冲区合并
/*
Buffer.concat(list[, totalength)
list - 用于合并的 Buffer 对象数组列表。

totalLength - 指定合并后Buffer对象的总长度。

 */
var buf10 = Buffer.from(('123'));
var buf11 = Buffer.from(('456'));
var buf12 = Buffer.concat([buf10, buf11]);
//Output: 123456
console.log("buf12: " + buf12.toString());

//缓冲区比较
/*
buf.compare(otherBuffer)
otherBuffer 比较的另外一个Buffer
返回一个数字，表示 buf 在 otherBuffer 之前，之后或相同。

 */
var buf13 = Buffer.from('ABC');
var buf14 = Buffer.from('ABCD');
var result = buf13.compare(buf14);

if(result < 0) {
    console.log(buf13 + '在' + buf14 + '之前');
}
else if(result == 0) {
    console.log(buf13 + '与' + buf14 + '相同');
}
else {
    console.log(buf13 + '在' + buf14 + '之后');
}



//字符串的裁剪，拷贝，求长度
//拷贝
/*
buf.copy(targetBuffer[, targetStart[, sourceStart[, sourceEnd]]])
targetBuffer - 要拷贝的 Buffer 对象。

targetStart - 数字, 可选, 默认: 0

sourceStart - 数字, 可选, 默认: 0

sourceEnd - 数字, 可选, 默认: buffer.length
 */
var buf15 = Buffer.from('abcdefghijklmn');
var buf16 = Buffer.from('OPQRSTUVWXYZ');
buf16.copy(buf15)

//裁剪
/*
buf.slice([start[, end]])
返回一个新的缓冲区，它和旧缓冲区指向同一块内存，但是从索引 start 到 end 的位置剪切。
 */
var buf17 = Buffer.from('ABCDEFG');
var buf18 = buf17.slice(0,2);
console.log('Content: ' + buf18.toString());
//buf.length 长度


/*
 */
var fs = require('fs');
var data = '';

//创建可读流
var readerStream = fs.createReadStream('input.txt');
//设置编码为UTF8
readerStream.setEncoding('UTF8');
//处理流事件 --->data, end, and error
readerStream.on('data', function(chunk) {
    data += chunk;
});

readerStream.on('end', function() {
    console.log(data);
});

readerStream.on('error', function(err) {
    console.log(err.stack);
});
console.log("Finished");


//创建写入流
var writerStream = fs.createWriteStream('output.txt');
writerStream.write('This is writing test', 'UTF8');

writerStream.end()  //标记文件末尾

//处理流事件
writerStream.on('finish', function() {
    console.log('Finished!');
});

writerStream.on('error', function(err) {
    console.log(err.stack);
});
console.log('Program Finished');


//创建管道流
readerStream.pipe(writerStream);

//创建链式流
//链式是通过连接输出流到另外一个流并创建多个流操作链的机制。链式流一般用于管道操作。





















































