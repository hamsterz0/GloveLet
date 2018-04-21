from glovelet.eventapi.glovelet_vision_events import GloveletVisionEventDispatcher, GloveletVisionListener
from glovelet.eventapi.event import EventDispatchManager

if __name__ == '__main__':
    disp = GloveletVisionEventDispatcher()
    listen = GloveletVisionListener()
    manager = EventDispatchManager(disp, listen)
    manager.deploy_dispatchers()
    while True:
        manager.invoke_dispatch()