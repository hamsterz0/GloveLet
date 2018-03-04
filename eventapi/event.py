from multiprocessing import Queue, Process


__all__ = ['Event', 'EventDispatcher', 'EventListener']


class Event:
    pass

class EventListener:
    def __init__(self, callbacks={}):
        type_err = '`EventListener` constructor requires a dict of `Event` \
                        type as key and `callable` callback function as value.'
        if not isinstance(callbacks, dict):
            raise TypeError(type_err)
        for event in callbacks:
            if not callable(callbacks[event]) or not issubclass(event, Event):
                raise TypeError(type_err)
        self.event_callbacks = callbacks


class EventDispatcher:
    def __init__(self, events, queue_sz=1):
        self.event_types = tuple(events)
        self.event_queues = dict()
        self.listeners = dict()
        for event in self.event_types:
            if not issubclass(event, Event):
                raise TypeError(str(event) + ' is not of type ' + str(Event))
            self.event_queues[event] = Queue(queue_sz)
            self.listeners[event] = list()
        _args = tuple([self.event_queues[x] for x in self.event_types])
        self.process = Process(target=self.run, args=_args)

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
        for event_type in self.listeners:
            if not self.event_queues[event_type].empty():
                for listener in self.listeners[event_type]:
                    e = self.event_queues[event_type].get()
                    listener.event_callbacks[event_type](e)

    # `run()` should take the same number of queues as its arguments as
    # the dispatcher has types of events
    def run(self):
        raise NotImplementedError('`run()` is abstract method that must be implemented per `EventDispatcher`.')
