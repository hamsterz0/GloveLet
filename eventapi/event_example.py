from glovelet.eventapi.event import EventListener, Event, EventDispatcher
from time import sleep
from random import randrange
from multiprocessing import Queue


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
        callbacks = {Example1Event: on_example1, Example2Event: on_example2}
        super().__init__(callbacks)


class MyClassThatListensAndStuff(ExampleEventListener):
    def __init__(self):
        super().__init__(self.on_exmpl1, self.on_exmpl2)
        self.count = 0
        self.__msg_q = Queue(1)
        self.__msg = str()

    @property
    def msg(self):
        if not self.__msg_q.empty():
            self.__msg = self.__msg_q.get()
        return self.__msg

    def on_exmpl1(self, event):
        # print(event.msg1 + ': {}'.format(self.count))
        self.count += 1
        if self.__msg_q.full():
            self.__msg_q.get()
        self.__msg_q.put(event.msg1)

    def on_exmpl2(self, event):
        # print(event.msg2 + ': {}'.format(self.count))
        self.count += 1
        if self.__msg_q.full():
            self.__msg_q.get()
        self.__msg_q.put(event.msg2)


if __name__ == '__main__':
    L = MyClassThatListensAndStuff()
    D = ExampleEventDispatcher()
    D.register(L)
    D.start()
    for i in range(4):
        sleep(0.08)
        print(L.msg)
    print('DONE!')
