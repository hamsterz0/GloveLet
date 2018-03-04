from multiprocessing import Queue, Process
from random import randrange
from time import sleep


class ExampleEvent:
    def __init__(self, msg):
        self.msg = msg


class Example2Event:
    def __init__(self, msg):
        self.msg = msg


class EventDispatcher:
    def __init__(self):
        self.event_types = (type(ExampleEvent), type(Example2Event))
        self.event_queues = {self.event_types[0]: Queue(1), self.event_types[1]: Queue(1)}
        self.listeners = {self.event_types[0]: list(), self.event_types[1]: list()}
        self.process = Process(target=self.run,\
            args=(self.event_queues[self.event_types[0]], self.event_queues[self.event_types[1]]))

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def register(self, listener):
        for event_type in listener.event_callbacks:
            if event_type in self.listeners:
                self.listeners[event_type].append(listener)

    def dispatch(self):
        for event_type in self.listeners:
            if not self.event_queues[event_type].empty():
                for listener in self.listeners[event_type]:
                    e = None
                    if event_type == type(ExampleEvent):
                        e = ExampleEvent('example 1')
                    elif event_type == type(Example2Event):
                        e = ExampleEvent('example 2')
                    listener.event_callbacks[event_type](e)

    def run(self, exmpl_queue, exmpl2_queue):
        for i in range(25):
            sleep(0.5)
            r = randrange(0,2)
            if r == 1:
                exmpl_queue.put(ExampleEvent())
            else:
                exmpl2_queue.put(Example2Event)


class EventListener:
    pass


class ExampleEventListener(EventListener):
    def __init__(self, on_example, on_example2):
        if isinstance(on_example, callable) and isinstance(on_example2, callable):
            self.event_callbacks = {type(ExampleEvent): on_example, type(Example2Event): on_example2}


class TestEventListener(ExampleEventListener):
    def __init__(self):
        super().__init__(self.on_example, self.on_example2)

    def on_example(self, event):
        print(event.msg)

    def on_example2(self, event):
        print(event.msg)
