//__filename 表示当前正在执行的脚本的文件名。它将输出文件所在位置的绝对路径，
// 且和命令行参数所指定的文件名不一定相同。 如果在模块中，返回的值是模块文件的路径。
console.log(__filename );

//__dirname 当前执行脚本所在目录
console.log(__dirname);

//setTimeOut(cb,ms) 在指定的毫秒数后执行指定函数（cb） 只执行一次指定函数
function printHello() {
    console.log("Hello World");
}
var t = setTimeout(printHello, 2000);

//clearTimeOut(t) 清除通过setTimeOut设置的定时器t
clearTimeout(t);

//node js 使用console向stdin与stderr中输出信息
/*
1	console.log([data][, ...])
向标准输出流打印字符并以换行符结束。该方法接收若干 个参数，如果只有一个参数，则输出这个参数的字符串形式。
如果有多个参数，则 以类似于C 语言 printf() 命令的格式输出。
2	console.info([data][, ...])
该命令的作用是返回信息性消息，这个命令与console.log差别并不大，除了在chrome中只会输出文字外，其余的会显示一个蓝色的惊叹号。
3	console.error([data][, ...])
输出错误消息的。控制台在出现错误时会显示是红色的叉子。
4	console.warn([data][, ...])
输出警告消息。控制台出现有黄色的惊叹号。
5	console.dir(obj[, options])
用来对一个对象进行检查（inspect），并以易于阅读和打印的格式显示。
6	console.time(label)
输出时间，表示计时开始。
7	console.timeEnd(label)
结束时间，表示计时结束。
8	console.trace(message[, ...])
当前执行的代码在堆栈中的调用路径，这个测试函数运行很有帮助，只要给想测试的函数里面加入 console.trace 就行了。
9	console.assert(value[, message][, ...])
用于判断某个表达式或变量是否为真，接收两个参数，第一个参数是表达式，第二个参数是字符串。
只有当第一个参数为false，才会输出第二个参数，否则不会有任何结果。
 */

//process是一个全局变量， 描述当前node js进程状态的对象， 提供了一个与操作系统的简单接口。
/*
exit 进程准备退出时触发
beforeExit node清空事件循环，并没有其他安排时触发此事件
uncaughtException 发生异常时触发
Signal 接收到信号时触发，信号为标准POSIX信号名
 */
process.on('exit', function(code) {
    //This will never be executed
    setTimeout(function() {
        console.log('This code will not run');
    }, 0);

    console.log("Exit Code:", code);
});
console.log("Finished");
//关于退出状态码




