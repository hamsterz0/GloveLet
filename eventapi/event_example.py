from glovelet.eventapi.event import EventListener, Event, EventDispatcher
from time import sleep
from random import randrange


class Example1Event(Event):
    def __init__(self, msg):
        self.msg1 = msg


class Example2Event(Event):
    def __init__(self, msg):
        self.msg2 = msg


# Example dispatcher
class ExampleEventDispatcher(EventDispatcher):
    def __init__(self):
        super().__init__([Example1Event, Example2Event])

    def run(self, exmpl_queue, exmpl2_queue):
        for i in range(25):
            sleep(0.1)
            r = randrange(0,2)
            if r == 1:
                if exmpl_queue.full():
                    exmpl_queue.get()
                exmpl_queue.put(Example1Event('example 1'))
            else:
                if exmpl2_queue.full():
                    exmpl2_queue.get()
                exmpl2_queue.put(Example2Event('example 2'))
            self.dispatch()


class ExampleEventListener(EventListener):
    def __init__(self, on_example1, on_example2):
        callbacks = {Example1Event: on_example1, Example2Event: on_example2}
        super().__init__(callbacks)


class MyClassThatListensAndStuff(ExampleEventListener):
    def __init__(self):
        super().__init__(self.on_exmpl1, self.on_exmpl2)

    def on_exmpl1(self, event):
        print(event.msg1)

    def on_exmpl2(self, event):
        print(event.msg2)


if __name__ == '__main__':
    L = MyClassThatListensAndStuff()
    D = ExampleEventDispatcher()
    D.register(L)
    D.start()
    sleep(2.75)
    print('DONE!')
