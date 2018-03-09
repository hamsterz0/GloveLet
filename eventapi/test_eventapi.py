import numpy as np
from time import sleep

from glovelet.eventapi.event import Event, EventDispatcher, EventListener, EventDispatcherManager
from glovelet.sensorapi.sensorstream import SensorStream
from glovelet.eventapi.glovelet_hardware_events import GloveletImuEventDispatcher, GloveletImuListener


class TestEvent01(Event):
    def __init__(self, msg):
        self.msg = msg


class TestEvent02(Event):
    def __init__(self, data01, data02, data03):
        self.data01 = data01
        self.data02 = data02
        self.data03 = data03


class TestEventDispatcher01(EventDispatcher):
    def __init__(self):
        super().__init__(TestEvent01)

    def init(self):
        return (), {'count': {0: 0}}

    def update(self, count):
        count[0] += 1
        c = count[0]
        test_event01 = TestEvent01('TestEvent01 {}'.format(c))
        return test_event01

    def finish(self, count):
        pass


class TestEventDispatcher02(EventDispatcher):
    def __init__(self, rand_shape=(10, 10)):
        super().__init__(TestEvent02)
        self.rand_shape = rand_shape

    def init(self):
        return (), {'count': {0: 0}}

    def update(self, count):
        count[0] += 1
        c = count[0]
        data01 = np.random.rand(*self.rand_shape)
        data02 = np.random.rand(*self.rand_shape)
        data03 = np.random.rand(*self.rand_shape)
        test_event02 = TestEvent02(data01, data02, data03)
        return test_event02

    def finish(self, count):
        pass


class TestEventListener01(EventListener):
    def __init__(self, on_test01):
        callbacks = {TestEvent01: on_test01}
        super().__init__(callbacks)


class TestEventListener02(EventListener):
    def __init__(self, on_test02):
        callbacks = {TestEvent02: on_test02}
        super().__init__(callbacks)


class TestImplementListener01(TestEventListener01):
    def __init__(self):
        super().__init__(self.on_test01)
        self.msg = str()

    def on_test01(self, event):
        self.msg = event.msg


class TestImplementListener02(TestEventListener02):
    def __init__(self):
        super().__init__(self.on_test02)
        self.data01 = None
        self.data02 = None
        self.data03 = None

    def on_test02(self, event):
        self.data01 = event.data01
        self.data02 = event.data02
        self.data03 = event.data03


def run_test01():
    dispatcher_test01 = TestEventDispatcher01()
    dispatcher_test02 = TestEventDispatcher02(rand_shape=(3,))
    listener_test01 = TestImplementListener01()
    listener_test02 = TestImplementListener02()
    manager = EventDispatcherManager(dispatcher_test01, dispatcher_test02)
    manager.register_listener(listener_test01, listener_test02)
    manager.deploy_dispatcher()
    for i in range(100):
        manager.invoke_dispatch()
        if i % 8 == 4:
            print(listener_test01.msg)
        elif i % 8 == 0:
            print(listener_test02.data02)
    manager.end_dispatcher()


def run_test02():
    np.set_printoptions(precision=4, suppress=True)
    stream = SensorStream('/dev/ttyACM0', 115200)
    dispatcher = GloveletImuEventDispatcher(stream)
    listener = GloveletImuListener()
    event_manager = EventDispatcherManager(dispatcher)
    event_manager.register_listener(listener)
    event_manager.deploy_dispatcher()
    while listener.acceleration is None:
        event_manager.invoke_dispatch()
        continue
    while True:
        # sleep(0.1)
        event_manager.invoke_dispatch()
        print('acceleration: {}'.format(listener.acceleration[0]))
        # if i % 12 == 8:
        #     print('acceleration: {}'.format(listener.acceleration))
        # elif i % 12 == 4:
        #     print('velocity: {}'.format(listener.velocity))
        # elif i % 12 == 0:
        #     print('orientation: {}'.format(listener.orientation))
    event_manager.end_dispatcher()


if __name__ == '__main__':
    run_test01()
    run_test02()
