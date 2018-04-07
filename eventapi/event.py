event_type__all__ = ['Event', 'EventDispatcher', 'EventListener', 'EventAPIException', 'EventDispatcherManager']


from multiprocessing import Process, Pipe


class EventAPIException(Exception):
    pass


class Event:
    """
    __Abstract Interface Class.__\n
    Subclasses of `Event` must be `pickable` objects, and typically
    should only possess publically accessable members.
    """
    pass


class EventListener:
    """
    __Abstract Interface Class.__\n
    Listens to events dispatched by `EventDispatcher`s.\n
    Must be registered to `EventDispatcher`s which dispatch at least one event type
    that this listener subscribes to.\n
    __** _Parameters_ **__\n
    \tcallbacks:\t
    \t\tA Python `dict` which has sublclasses of `Event` as keys
    \t\tand a `callable` function reference as its values.
    """

    def __init__(self, callbacks={}):
        type_err = '`EventListener` constructor requires a dict of `Event`'\
                 + ' type as key and `callable` callback function as value.'
        if not isinstance(callbacks, dict):
            raise TypeError(type_err)
        for event_type in callbacks:
            if not callable(callbacks[event_type]) or not issubclass(event_type, Event):
                raise TypeError(type_err)
        self.event_callbacks = callbacks


class EventDispatcher:
    """
    __Abstract Interface Class.__\n
    Dispatches events for registered `EventListener`s.\n
    __** _Parameters_ **__\n
    \tevents:\t
    \t\tThe event types which this event will dispatch.\t
    \t\tMust be a subclass of `Event`.\t
    \n
    __** _Required Method Implementations_ **__:\n
    __update:__ _See documentation for details on implementation._\t
    __finish:__ _See documentation for details on implementation._\t
    \n
    __** _Optional Method Implementations_ **__:\n
    __init:__ _See documentation for details on implementation._
    """
    def __init__(self, *events):
        self.__is_deployed = False
        self.event_types = tuple(events)
        self.event_parent_conns = dict()
        self.event_child_conns = dict()
        self.listeners = dict()
        # Create pipes for triggering events
        for event_type in self.event_types:
            if not issubclass(event_type, Event):
                raise TypeError(str(type(event_type)) + ' is not of type ' + str(Event))
            # Establish 1-way connections for sending events
            self.event_parent_conns[event_type], self.event_child_conns[event_type] = Pipe(duplex=False)
            self.listeners[event_type] = list()
        # Establish bi-way connection between the parent and child process
        self.__child_conn, self.__parent_conn = Pipe(duplex=True)
        # Init process
        self.process = None

    @property
    def is_deployed(self):
        if self.__parent_conn.poll():
            msg = self.__parent_conn.recv()
            if msg == 'term':
                self.__is_deployed = False
        return self.__is_deployed

    def deploy(self):
        """Start dispatcher process loop."""
        self.__is_deployed = True
        _args = (self.__child_conn, self.event_child_conns)
        self.process = Process(name="glovelet", target=self.__deploy, args=_args)
        self.process.start()

    def end(self):
        """Terminate the dispatcher process."""
        self.__parent_conn.send('term')
        while True:
            if self.__parent_conn.poll() and self.__parent_conn.recv() == 'end':
                self.__is_deployed = False
                break
        self.process.terminate()

    def register(self, listener):
        if self.is_deployed:
            raise EventAPIException('Cannot register `EventListener` objects with a `EventDispatcher` that is currently deployed.')
        for event_type in listener.event_callbacks:
            if event_type in self.listeners:
                if not issubclass(type(listener), EventListener):
                    raise TypeError(str(listener) + ' is not of type ' + str(EventListener))
                self.listeners[event_type].append(listener)

    def dispatch(self):
        """
        Dispatches events to registered listeners.
        """
        if not self.is_deployed:
            raise EventAPIException('`EventDispatcher` cannot dispatch events while not deployed.')
        if self.__parent_conn.poll():
            if self.__parent_conn.recv() == 'end':
                self.__is_deployed = False
                return
        for event_type in self.event_parent_conns:
            event = None
            if self.event_parent_conns[event_type].poll():
                event = self.event_parent_conns[event_type].recv()
            if event is not None:
                for listener in self.listeners[event_type]:
                    listener.event_callbacks[event_type](event)

    def init(self):
        """
        __**Optional abstract interface method**__\n
        Implement any initialization logic needed for your update function.\n
        __IMPORTANT:__\t
        Return a `tuple` of `args` and `dict` of `kwargs` from this function.
        These will be forwarded to the `update` and `end` methods.\n
        \tE.G.:
        \t  return (arg1, arg2), {'kwarg1': object, 'kwarg2': object}
        """
        return (), {}

    def update(self):
        """
        __**Required abstract interface method**__\n
        Implement the logic for creating events here.\t
        Return multiple events as an unpacked tuple.\n
        __IMPORTANT:__\t
        Objects initialized in the `init` method will be forwarded here as
        unpacked `args` and `kwargs`. This means _all objects_ returned
        as `args` and `kwargs` by `init` _must be_ parameters of this method,
        even if they remain unused in this method.
        """
        raise NotImplementedError('`update()` is abstract method that must be implemented per `EventDispatcher`.')

    def finish(self):
        """
        __**Required abstract interface method**__\n
        Implement any final logic that needs to run when the loop ends.\n
        __IMPORTANT:__\t
        Objects initialized in the `init` method will be forwarded here as
        unpacked `args` and `kwargs`. This means _all objects_ returned
        as `args` and `kwargs` by `init` _must be_ parameters of this method,
        even if they remain unused in this method.
        """
        raise NotImplementedError('`finish()` is abstract method that must be implemented per `EventDispatcher`.')

    def __deploy(self, command_conn, event_conns):
        """Dispatcher process loop."""
        args, kwargs = self.init()
        is_deployed = True
        try:
            while is_deployed:
                # Update and create events.
                events = self.update(*args, **kwargs)
                if not isinstance(events, tuple):
                    events = (events,)
                # Send events
                for event in events:
                    event_conns[type(event)].send(event)
                # Get communications from parent process
                if command_conn.poll():
                    cmd = command_conn.recv()
                    if cmd == 'term':
                        is_deployed = False
        finally:
            self.finish(*args, **kwargs)
            command_conn.send('end')


class EventDispatcherManager:
    """
    Manages `EventDispatcher` and `EventListener` objects.\n
    Dispatchers must be registered and deployed before the `invoke_dispatch` method will invoke
    dispatchers to dispatch events to registered listeners. `EventListener`s are automatically registered
    with all valid `EventDispatcher`s which dispatch at least one event type for which the `EventListener`
    subscribes to.\n
    __** _Parameters_ **__\n
    \tregistrees:
    \t\tThe `EventDispatcher`s and `EventListener`s to register
    \t\twith this `EventDispatcherManager` at object creation.
    """

    def __init__(self, *registrees):
        self.__dispatchers = dict()
        dispatchers = tuple([dispatcher for dispatcher in registrees if issubclass(dispatcher, EventDispatcher)])
        listeners = tuple([listener for listener in registrees if issubclass(listener, EventDispatcher)])
        self.register_dispatcher(*dispatchers)
        self.register_listener(*listeners)

    def invoke_dispatch(self, event_type=None):
        """
        Invoke `dispatch` method of `EventDispatcher` objects.\n
        If `event_type` is `None`, all registered dispatchers will `dispatch` any events,
        otherwise the `dispatch` method of the registered dispatcher which dispatches
        events of type `event_type` will be called.\n
        __** _Parameters_ **__\n
        \tevent_type:  *optional*
        \t\tSpecifies the dispatcher for which to invoke `dispatch`.
        \t\tIf `None`, all registered dispatchers not
        \t\tyet deployed will be deployed.
        """
        if event_type is None:
            for dispatcher in self.__dispatchers.values():
                if dispatcher.is_deployed:
                    dispatcher.dispatch()
        else:
            if self.__dispatchers[event_type].is_deployed:
                dispatcher.dispatch()

    def register_dispatcher(self, *dispatchers):
        """
        Registers `EventDispatcher` objects.\n
        Attempting to register more than one dispatcher for the same event type will
        raise an `EventAPIException`.\n
        __** _Parameters_ **__\n
        \tdispatchers:  the `EventDispatcher` object(s) to register
        """
        for i in range(len(dispatchers)):
            dispatcher = dispatchers[i]
            if issubclass(type(dispatcher), EventDispatcher):
                for event_type in dispatcher.event_types:
                    for disp in self.__dispatchers.values():
                        if event_type in disp.event_types:
                            raise EventAPIException('Cannont register multiple `EventDispatcher`s \
                                                    for same event type {}.'.format(event_type))
            else:
                raise TypeError('Type {} is not subclass of type {}'.format(type(dispatcher), EventDispatcher))
            for event_type in dispatcher.event_types:
                self.__dispatchers[event_type] = dispatcher

    def register_listener(self, *listeners):
        """
        Registers `EventListener` objects.\n
        __** _Parameters_ **__\n
        \tlisteners:   the `EventListener` object(s) to register
        """
        for listener in listeners:
            for event_type in listener.event_callbacks:
                self.__dispatchers[event_type].register(listener)

    def deploy_dispatcher(self, event_type=None):
        """
        Begins registered `EventDispatcher` object's process.\n
        If `event_type` is `None`, all registered dispatchers not yet deployed will be deployed.
        Otherwise the registered dispatcher which dispatches events of type `event_type`
        will be deployed.\n
        __** _Parameters_ **__\n
        \tevent_type:  *optional*
        \t\tSpecifies the dispatcher to deploy. If `None`,
        \t\tall registered dispatchers not yet deployed
        \t\twill be deployed.
        """
        if event_type is None:
            for dispatcher in self.__dispatchers.values():
                if not dispatcher.is_deployed:
                    dispatcher.deploy()
        else:
            if not self.__dispatchers[event_type].is_deployed:
                dispatcher.deploy()

    def end_dispatcher(self, event_type=None):
        """
        Ends registered `EventDispatcher` object's prcoess.\n
        If `event_type` is `None`, all registered dispatchers currently deployed will be terminated.
        Otherwise the registered dispatcher which dispatches events of type `event_type`
        will be terminated.\n
        __** _Parameters_ **__\n
        \tevent_type:  *optional*
        \t\tSpecifies the dispatcher to end. If `None`,
        \t\tall registered dispatchers currently deployed
        \t\twill be ended.
        """
        if event_type is None:
            for dispatcher in self.__dispatchers.values():
                if dispatcher.is_deployed:
                    dispatcher.end()
        else:
            if self.__dispatchers[event_type].is_deployed:
                dispatcher.end()
