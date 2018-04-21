from events import Event, EventDispatcher, EventListener, EventDispatchManager
from time import sleep
from random import randrange
import os


class ExampleEvent1(Event):
    def __init__(self, msg):
        self.msg = msg
        self.id = id(self)


class ExampleEvent2(Event):
    def __init__(self, msg):
        self.type = 'ExampleEvent2'
        self.msg = msg
        self.id = id(self)


# Example dispatcher
class ExampleEventDispatcher(EventDispatcher):
    def __init__(self):
        super().__init__(ExampleEvent1, ExampleEvent2)

    def init(self):
        # Use mutable object if values need to be mutated.
        return (), {'count': [0]}

    def update(self, count):
        count[0] += 1
        res = randrange(0, 2)
        if res == 0:
            msg = '[ExampleEvent1] count={: 5d}'.format(count[0])
            return ExampleEvent1(msg)
        elif res == 1:
            msg = '[ExampleEvent2] count={: 5d}'.format(count[0])
            return ExampleEvent2(msg)

    def finish(self, count):
        print('Finishing . . .')


class ExampleEventListener(EventListener):
    def __init__(self):
        callbacks = {ExampleEvent1: self.on_example1, ExampleEvent2: self.on_example2}
        super().__init__(callbacks)

    def on_example1(self, event):
        print('{}, eventID={}'.format(event.msg, event.id))

    def on_example2(self, event):
        print('{}, eventID={}'.format(event.msg, event.id))


if __name__ == '__main__':
    listener = ExampleEventListener()
    disp = ExampleEventDispatcher()
    mgr = EventDispatchManager(disp, listener)
    mgr.deploy_dispatchers()
    for i in range(10):
        sleep(0.5)
        mgr.invoke_dispatch()
    mgr.end_dispatchers()
    print('DONE!')
