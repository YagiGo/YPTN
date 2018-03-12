var fs = require('fs');
//异步读取
fs.readFile('input.txt', function(err, data) {
    if(err) {
        return console.log(err);
    }
    console.log("异步读取：" + data.toString());
});

//同步读取
var data = fs.readFileSync('input.txt');
console.log("同步读取:" + data.toString());
console.log("Finished");

//文件操作的语法
/*
异步
fs.open(path, flags[,mode], callback)
path 文件路径
flags 文件打开行为
r	以读取模式打开文件。如果文件不存在抛出异常。
r+	以读写模式打开文件。如果文件不存在抛出异常。
rs	以同步的方式读取文件。
rs+	以同步的方式读取和写入文件。
w	以写入模式打开文件，如果文件不存在则创建。
wx	类似 'w'，但是如果文件路径存在，则文件写入失败。
w+	以读写模式打开文件，如果文件不存在则创建。
wx+	类似 'w+'， 但是如果文件路径存在，则文件读写失败。
a	以追加模式打开文件，如果文件不存在则创建。
ax	类似 'a'， 但是如果文件路径存在，则文件追加失败。
a+	以读取追加模式打开文件，如果文件不存在则创建。
ax+	类似 'a+'， 但是如果文件路径存在，则文件读取追加失败。

mode 设置文件权限，默认0666（可读，可写）
callback 回调函数 function（err, fd)
 */
console.log("准备打开文件");
fs.open('input.txt', 'r+', function(err, data) {
    if(err) {
        return console.error(err);
    }
    console.log("Success!");
});

//获取文件信息
/*
fs.stat(path, callback)
path 文件路径
callback 回调函数，有两个参数(err, stats)
 */
//fs.stat(path)执行后，会将stats类的实例返回给其回调函数。可以通过stats类中的提供方法判断文件的相关属性。例如判断是否为文件：
/*
常见stats类中的方法
stats.isFile()	如果是文件返回 true，否则返回 false。
stats.isDirectory()	如果是目录返回 true，否则返回 false。
stats.isBlockDevice()	如果是块设备返回 true，否则返回 false。
stats.isCharacterDevice()	如果是字符设备返回 true，否则返回 false。
stats.isSymbolicLink()	如果是软链接返回 true，否则返回 false。
stats.isFIFO()	如果是FIFO，返回true，否则返回 false。FIFO是UNIX中的一种特殊类型的命令管道。
stats.isSocket()	如果是 Socket 返回 true，否则返回 false。
 */
fs.stat('input.txt', function(err, stats) {
    if(err) {
        console.error(err);
    }
    console.log(stats);
    console.log("是否为文件？ " + stats.isFile());
    console.log("是否为目录？ " + stats.isDirectory());
});

//写入文件
/*
fs,writeFile(file, data[,options], callback)
file 文件名
data 写入数据
options 包含{encoding, mode, flag} 默认utf8, 0666, w
callback 回调函数，出现错误时返回(err)
 */
fs.writeFile('input.txt', 'Hello, I am the data written through fs', function(err) {
    if(err) {
        console.error(err);
    }
});
console.log("Start Writing Data");
console.log("Starting Reading Data");
fs.readFile('input.txt', function(err, data) {
    if(err) {
        console.error(err);
    }
    console.log("Data: " + data.toString());
});
console.log("Finished!");

//读取文件
/*
fs.read(fd, buffer, offset, length, position, callback)
fd 通过fs.open方法返回的文件描述符
buffer 数据写入的缓冲区
offset 缓冲区写入的写入偏移量
length 从文件中读取的字节数
position 文件读取的起始位置，默认从文件指针的位置读取
callback 回调函数，有三个参数err, bytesRead, buffer. err为错误信息，bytesRead表示读取的字节数，buffer为缓冲区对象
 */
console.log("准备打开已存在的文件");
var buf = new Buffer(1024);

fs.open('input.txt','r+', function(err,fd) {
    if(err) {
        console.error(err);
    }
    console.log("File opened!");
    console.log("Reading File...");
    fs.read(fd, buf, 0, buf.length, 0, function(err, bytes) {
        if(err) {
            console.error(err);
        }
        console.log("File Size: " + bytes);
        if(bytes > 0) {
            console.log("Content: " + buf.slice(0, bytes).toString());
        }
    });
    fs.close(fd, function(err) {
        if(err) {
            console.error(err);
        }
    });
});
//截取文件
/*
fs.ftruncate(fd, len, callback)
fd 通过fs.open方式返回的文件描述符
len 文件截取长度
callbcak 回调函数，没有参数
 */
//下面的代码先读出完整的文件，然后读出截取的10字节数据
fs.open('input.txt', 'r+', function(err, fd) {
    if(err) {
        console.error(err);
    }
    console.log("File Opened!");
    console.log("Reading File...");
    fs.read(fd, buf, 0, buf.length, 0, function(err, bytes) {
        if (err) {
            console.error(err);
        }
        console.log("File Size: " + bytes);
        console.log("File COntent:" + buf.slice(0, buf.length).toString());
    });
    fs.truncate(fd, 10, function(err) {
        if(err) {
            console.error(err);
        }
    });
    fs.read(fd, buf, 0, buf.length, 0, function (err, bytes) {
        if(err) {
            console.error(err);
        }
        console.log("Truncated File:" + bytes);
        console.log("Truncated File Content:" + buf.slice(0, buf.length).toString());
    });
    fs.close(fd, function(err) {
        if(err) {
            console.error(err);
        }
    });
});
//删除文件
/*
fs.unlink(path, callback)
path 删除文件
callback 回调函数
 */
//创建目录
/*
fs.mkdir(path[, mode], callback)
path 文件路径
mode 设置目录权限，默认为0777
callback 回调函数， 没有参数
 */
console.log("创建新目录");
fs.mkdir('/test', function(err) {
    if(err) {
        console.error(err);
    }
    console.log("目录创建成功");
});
