from glovelet.eventapi.event import EventListener, Event, EventDispatcher
from time import sleep
from random import randrange
from multiprocessing import Queue, Lock, Pipe, Pool
import ctypes
import os


class Example1Event(Event):
    def __init__(self, msg):
        self.msg1 = msg


class Example2Event(Event):
    def __init__(self, msg):
        self.msg2 = msg


# Example dispatcher
class ExampleEventDispatcher(EventDispatcher):
    def __init__(self):
        super().__init__([Example1Event, Example2Event], queue_sz=5)
        self.__pid = os.getpid()
        # self.__pipe,  = Pipe()

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def register(self, listener):
        for event_type in listener.event_callbacks:
            if event_type in self.listeners:
                if not issubclass(listener.__class__, EventListener):
                    raise TypeError(str(listener) + ' is not of type ' + str(EventListener))
                self.listeners[event_type].append(listener)

    def dispatch(self):
        if os.getpid() != self.__pid:
            print('Not on main process!')
        for event_type in self.listeners:
            if not self.event_queues[event_type].empty():
                for listener in self.listeners[event_type]:
                    e = self.event_queues[event_type].get()
                    listener.event_callbacks[event_type](e)

    def run(self, exmpl_queue, exmpl2_queue):
        count = 1
        for i in range(26):
            sleep(0.01)
            r = randrange(0,2)
            if r == 1:
                if exmpl_queue.full():
                    exmpl_queue.get()
                exmpl_queue.put(Example1Event('example1 {0: 2d}'.format(count)))
            else:
                if exmpl2_queue.full():
                    exmpl2_queue.get()
                exmpl_queue.put(Example1Event('example2 {0: 2d}'.format(count)))
            count += 1
            self.dispatch()


class ExampleEventListener(EventListener):
    def __init__(self, on_example1, on_example2):
        callbacks = {Example1Event: self.__on_example1, Example2Event: self.__on_example2}
        super().__init__(callbacks)
        self.__callbacks = (on_example1, on_example2)
        self.__on_example1_q = Queue(1)

    def __on_example1(self, event):
        self.__callbacks[0](event)

    def __on_example2(self, event):
        self.__callbacks[1](event)


class MyClassThatListensAndStuff(ExampleEventListener):
    def __init__(self):
        super().__init__(self.on_exmpl1, self.on_exmpl2)
        self.count = 0
        self.__msg_q = Queue(1)
        self.__msg = str()
        self.__lock = Lock()

    @property
    def msg(self):
        with self.__lock:
            return self.__msg

    def on_exmpl1(self, event):
        # print(event.msg1 + ': {}'.format(self.count))
        self.count += 1
        # if self.__msg_q.full():
        #     self.__msg_q.get()
        # self.__msg_q.put(event.msg1)
        self.__msg = (event.msg1 + ': {}'.format(self.count))

    def on_exmpl2(self, event):
        # print(event.msg2 + ': {}'.format(self.count))
        self.count += 1
        # if self.__msg_q.full():
        #     self.__msg_q.get()
        # self.__msg_q.put(event.msg2)
        self.__set_msg(event.msg2 + ': {}'.format(self.count))


if __name__ == '__main__':
    L = MyClassThatListensAndStuff()
    D = ExampleEventDispatcher()
    D.register(L)
    D.start()
    for i in range(4):
        sleep(0.08)
        print(L.msg)
    print('DONE!')
