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
        self.type1 = type(ExampleEvent)
        self.type2 = type(Example2Event)
        self.event_queues = {self.type1: Queue(1), self.type2: Queue(1)}
        self.listeners = dict({self.type1: list(), self.type2: list()})
        self.process = Process(target=self.run,\
            args=(self.event_queues[self.type1], self.event_queues[self.type2]))

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def register(self, listener):
        for event_type in listener.event_callbacks:
            if event_type in self.listeners:
                self.listeners[event_type].append(listener)

    def dispatch(self):
        pass

    def run(self, exmpl_queue, exmpl2_queue):
        for i in range(25):
            sleep(0.5)
            r = randrange(0,2)
            if r == 1:
                exmpl_queue.put(ExampleEvent())
            else:
                exmpl2_queue.put(Example2Event)



class EventListener:
    def __init__(self):
        self.event_callbacks = {type(ExampleEvent): self.on_example, type(Example2Event): self.on_example2}

    def on_example(self, event):
        raise NotImplementedError

    def on_example2(self, event):
        raise NotImplementedError


class TestEventListener(EventListener):
    def __init__(self):
        pass

    def on_example(self, event):
        print(event.msg)

    def on_example2(self, event):
        print(event.msg)
