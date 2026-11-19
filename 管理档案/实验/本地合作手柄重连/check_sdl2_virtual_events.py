"""Use SDL2 virtual attachment, enumeration, and actual device-event payloads."""
import ctypes as c
import json

sdl=c.CDLL("libSDL2-2.0.so.0")
class Version(c.Structure):
    _fields_ = [("major",c.c_uint8),("minor",c.c_uint8),("patch",c.c_uint8)]
class Guid(c.Structure):
    _fields_ = [("data",c.c_uint8*16)]

class DeviceEvent(c.Structure):
    _fields_ = [("type",c.c_uint32),("timestamp",c.c_uint32),("which",c.c_int32)]

class Event(c.Union):
    _fields_ = [("device",DeviceEvent),("padding",c.c_uint8*56),("align",c.c_uint64)]

def api(name, result, *args):
    f=getattr(sdl,"SDL_"+name)
    f.restype,f.argtypes=result,list(args)
    return f

get_version=api("GetVersion",None,c.POINTER(Version))
init=api("Init",c.c_int,c.c_uint32)
quit=api("Quit",None)
count=api("NumJoysticks",c.c_int)
attach=api("JoystickAttachVirtual",c.c_int,c.c_int,c.c_int,c.c_int,c.c_int)
detach=api("JoystickDetachVirtual",c.c_int,c.c_int)
instance=api("JoystickGetDeviceInstanceID",c.c_int32,c.c_int)
guid=api("JoystickGetDeviceGUID",Guid,c.c_int)
name=api("JoystickNameForIndex",c.c_char_p,c.c_int)

poll=api("PollEvent",c.c_int,c.POINTER(Event))
event_names={0x605:"joystick_added",0x606:"joystick_removed",
             0x653:"controller_added",0x654:"controller_removed"}

def read_device_events():
    e=Event()
    out=[]
    while poll(c.byref(e)):
        if e.device.type in event_names:
            out.append([event_names[e.device.type],e.device.which])
    return sorted(out)

version=Version()
get_version(c.byref(version))
assert init(0x00002000) == 0 # SDL_INIT_GAMECONTROLLER, also initializes joystick/events
try:
    assert count() == 0, "Requires an isolated SDL process seeing no physical gamepads."
    def get():
        return [{"device_index":i,"instance_id":instance(i),"guid":bytes(guid(i).data).hex(),
                 "name":name(i).decode()} for i in range(count())]

    assert attach(1,2,4,0) == 0 and attach(1,2,4,0) == 1
    initial_events=read_device_events()
    assert initial_events==sorted([[kind,i] for kind in ("joystick_added","controller_added")
                                   for i in (0,1)])
    together=get()
    assert together[0]["guid"]==together[1]["guid"]
    assert together[0]["name"]==together[1]["name"]
    assert together[0]["instance_id"]!=together[1]["instance_id"]
    assert detach(0) == 0
    first_removal=read_device_events()
    assert first_removal==[["controller_removed",together[0]["instance_id"]],
                           ["joystick_removed",together[0]["instance_id"]]]
    after=get()
    assert len(after)==1 and after[0]["device_index"]==0
    assert after[0]["instance_id"]==together[1]["instance_id"]
    assert attach(1,2,4,0) == 1
    next_add=read_device_events()
    assert next_add==[["controller_added",1],["joystick_added",1]]
    readded=get()
    # The device at index 0 holds a different instance ID.
    assert after[0]["instance_id"]!=0
    assert detach(0)==0
    shifted_removal=read_device_events()
    assert shifted_removal==[["controller_removed",after[0]["instance_id"]],
                             ["joystick_removed",after[0]["instance_id"]]]
    after_shifted_removal=get()
    assert len(after_shifted_removal)==1
    assert after_shifted_removal[0]["instance_id"]==readded[1]["instance_id"]
    assert readded[1]["instance_id"] not in {g["instance_id"] for g in together}
    assert readded[1]["guid"]==together[0]["guid"]
    print(json.dumps({"sdl2_version":f"{version.major}.{version.minor}.{version.patch}",
                  "two_virtual":together,"after_remove_first":after,"after_add_identical_type":readded,
                  "after_remove_shifted":after_shifted_removal,
                  "device_events_sorted":{"initial":initial_events,"remove_first":first_removal,
                                          "add_same_type":next_add,"remove_shifted":shifted_removal}},indent=2))
finally:
    quit()
