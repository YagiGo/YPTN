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
