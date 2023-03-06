import os
import _thread as thread
import queue
import time
import collections
import struct

import _thread as thread
from queue import Queue
from functools import wraps


def unique_int(values):
    '''
    returns the first lowest integer
    that is not in the sequence passed in

    if a list looks like 3,6
    of the first call will return 1, and then 2
    and then 4 etc
    '''
    last = 0
    for num in values:
        if last not in values:
            break
        else:
            last += 1
    return last


class CallSerializer():
    def __init__(self):
        self.queue = Queue()
        thread.start_new_thread(self.call_functions, (),)

    def call_functions(self):
        while 1:
            func, args, kwargs = self.queue.get(block=True)
            func(*args, **kwargs)

    def serialize_call(self, function):
        '''
        a call to a function decorated will not have
        overlapping calls, i.e thread safe
        '''
        @wraps(function)
        def decorator(*args, **kwargs):
            self.queue.put((function, args, kwargs))
        return decorator


class SystemHotkeyError(Exception):pass
class SystemRegisterError(SystemHotkeyError):pass
class UnregisterError(SystemHotkeyError):pass
class InvalidKeyError(SystemHotkeyError):pass

if os.name == 'nt':
    import ctypes
    from ctypes import wintypes
    import win32con
    byref = ctypes.byref
    user32 = ctypes.windll.user32
    PM_REMOVE = 0x0001

    vk_codes= {
        'a':0x41,
        'b':0x42,
        'c':0x43,
        'd':0x44,
        'e':0x45,
        'f':0x46,
        'g':0x47,
        'h':0x48,
        'i':0x49,
        'j':0x4A,
        'k':0x4B,
        'l':0x4C,
        'm':0x4D,
        'n':0x4E,
        'o':0x5F,
        'p':0x50,
        'q':0x51,
        'r':0x52,
        's':0x53,
        't':0x54,
        'u':0x55,
        'v':0x56,
        'w':0x57,
        'x':0x58,
        'y':0x59,
        'z':0x5A,
        '0':0x30,
        '1':0x31,
        '2':0x32,
        '3':0x33,
        '4':0x34,
        '5':0x35,
        '6':0x36,
        '7':0x37,
        '8':0x38,
        '9':0x39,
        "up": win32con.VK_UP
        , "kp_up": win32con.VK_UP
        , "down": win32con.VK_DOWN
        , "kp_down": win32con.VK_DOWN
        , "left": win32con.VK_LEFT
        , "kp_left": win32con.VK_LEFT
        , "right": win32con.VK_RIGHT
        , "kp_right": win32con.VK_RIGHT
        , "prior": win32con.VK_PRIOR
        , "kp_prior": win32con.VK_PRIOR
        , "next": win32con.VK_NEXT
        , "kp_next": win32con.VK_NEXT
        , "home": win32con.VK_HOME
        , "kp_home": win32con.VK_HOME
        , "end": win32con.VK_END
        , "kp_end": win32con.VK_END
        , "insert": win32con.VK_INSERT
        , "return": win32con.VK_RETURN
        , "tab": win32con.VK_TAB
        , "space": win32con.VK_SPACE
        , "backspace": win32con.VK_BACK
        , "delete": win32con.VK_DELETE
        , "escape": win32con.VK_ESCAPE , "pause": win32con.VK_PAUSE
        , "kp_multiply": win32con.VK_MULTIPLY
        , "kp_add": win32con.VK_ADD
        , "kp_separator": win32con.VK_SEPARATOR
        , "kp_subtract": win32con.VK_SUBTRACT
        , "kp_decimal": win32con.VK_DECIMAL
        , "kp_divide": win32con.VK_DIVIDE
        , "kp_0": win32con.VK_NUMPAD0
        , "kp_1": win32con.VK_NUMPAD1
        , "kp_2": win32con.VK_NUMPAD2
        , "kp_3": win32con.VK_NUMPAD3
        , "kp_4": win32con.VK_NUMPAD4
        , "kp_5": win32con.VK_NUMPAD5
        , "kp_6": win32con.VK_NUMPAD6
        , "kp_7": win32con.VK_NUMPAD7
        , "kp_8": win32con.VK_NUMPAD8
        , "kp_9": win32con.VK_NUMPAD9
        , "f1": win32con.VK_F1
        , "f2": win32con.VK_F2
        , "f3": win32con.VK_F3
        , "f4": win32con.VK_F4
        , "f5": win32con.VK_F5
        , "f6": win32con.VK_F6
        , "f7": win32con.VK_F7
        , "f8": win32con.VK_F8
        , "f9": win32con.VK_F9
        , "f10": win32con.VK_F10
        , "f11": win32con.VK_F11
        , "f12": win32con.VK_F12
        , "f13": win32con.VK_F13
        , "f14": win32con.VK_F14
        , "f15": win32con.VK_F15
        , "f16": win32con.VK_F16
        , "f17": win32con.VK_F17
        , "f18": win32con.VK_F18
        , "f19": win32con.VK_F19
        , "f20": win32con.VK_F20
        , "f21": win32con.VK_F21
        , "f22": win32con.VK_F22
        , "f23": win32con.VK_F23
        , "f24": win32con.VK_F24
        }
    win_modders = {
        "shift": win32con.MOD_SHIFT
        ,"control": win32con.MOD_CONTROL
        ,"alt": win32con.MOD_ALT
        ,"super": win32con.MOD_WIN
        }
    win_trivial_mods = (
        0,
        # win32con.CAPSLOCK_ON,
        # win32con.NUMLOCK_ON,
        # win32con.NUMLOCK_ON | win32con.CAPSLOCK_ON
        )
 

class Aliases():
    '''
    Easily check if something is an alias of other things
    '''
    def __init__(self, *aliases):
        self.aliases = {}
        for values in aliases:
            assert isinstance(values, tuple)
            for val in values:
                self.aliases[val] = values

    def get(self, thing, nonecase=None):
        return self.aliases.get(thing, nonecase)


NUMPAD_ALIASES = Aliases(
        ('kp_1', 'kp_end',),
        ('kp_2', 'kp_down',),
        ('kp_3', 'kp_next', 'kp_page_down'),
        ('kp_4', 'kp_left',),
        ('kp_5', 'kp_begin',),
        ('kp_6', 'kp_right',),
        ('kp_7', 'kp_home',),
        ('kp_8', 'kp_up',),
        ('kp_9', 'kp_prior', 'kp_page_up'),
        )

thread_safe = CallSerializer()

class MixIn():
    @thread_safe.serialize_call
    def register(self, hotkey, *args, callback=None, overwrite=False):
        '''
        Add a system wide hotkey,

        hotkey needs to be a tuple/list

        If the Systemhotkey class consumer attribute value is set to callback,
        callback will need to be a callable object that will be run

        Otherwise  pass in option arguments that will be passed to the
        to consumer function

        set overwrite to True to overwrite existing binds, otherwise a
        SystemRegisterError will be raised.

        Modifiers include
        control
        shift
        super
        alt

        thread safe
        '''
        assert isinstance(hotkey, collections.Iterable) and type(hotkey) not in (str, bytes)
        if self.consumer == 'callback' and not callback:
            raise TypeError('Function register requires callback argument in non sonsumer mode')

        hotkey = self.order_hotkey(hotkey)
        keycode, masks = self.parse_hotkeylist(hotkey)

        if tuple(hotkey) in self.keybinds:
            if overwrite:
                self.unregister(hotkey)
            else:
                msg = 'existing bind detected... unregister or set overwrite to True'
                raise SystemRegisterError(msg, *hotkey)
                return

        if os.name == 'nt':
            def nt_register():
                uniq = unique_int(self.hk_ref.keys())
                self.hk_ref[uniq] = ((keycode, masks))
                self._the_grab(keycode, masks, uniq)
            self.hk_action_queue.put(lambda:nt_register())
            time.sleep(self.check_queue_interval*3)
        

        if callback:
            self.keybinds[tuple(hotkey)] = callback
        else:
            self.keybinds[tuple(hotkey)] = args

        if self.verbose:
            print('Printing all keybinds')
            print(self.keybinds)
            print() 

        #~ This code works but im not sure abot pywin  support for differentiation between keypress/keyrelease so..
        #~ on my laptoop on linux anyway keyrelease fires even if key is still down...

        #~ assert event_type in ('keypress', 'keyrelease', 'both')
        #~
        #~ copy = list(hotkey)
        #~ if event_type != 'both':
            #~ copy.append(event_type)
            #~ self.keybinds[tuple(copy)].append(callback)
        #~ else:    # Binding to both keypress and keyrelease
            #~ copy.append('keypress')
            #~ self.keybinds[tuple(copy)].append(callback)
            #~ copy[-1] = 'keyrelease'
            #~ self.keybinds[tuple(copy)].append(callback)

    @thread_safe.serialize_call
    def unregister(self, hotkey):
        '''
        Remove the System wide hotkey,
        the order of the modifier keys is irrelevant
        '''
        keycode, masks = self.parse_hotkeylist(hotkey)
        if os.name == 'nt':
            def nt_unregister(hk_to_remove):
                for key, value in self.hk_ref.items():
                    if value == hk_to_remove:
                        del self.hk_ref[key]
                        user32.UnregisterHotKey(None, key)
                        #~ logging.debug('Checking Error from unregister hotkey %s' % (win32api.GetLastError()))
                        return hk_to_remove
            self.hk_action_queue.put(lambda: nt_unregister((keycode,masks)))
            time.sleep(self.check_queue_interval*3) 
        del self.keybinds[tuple(self.order_hotkey(hotkey))]

    def order_hotkey(self, hotkey):
        # Order doesn't matter for modifiers, so we force an order here
        # control - shift - alt - win, and when we read back the modifers we spit them
        # out in the same value so our dictionary keys always match
        if len(hotkey) > 2:
            new_hotkey = []
            for mod in hotkey[:-1]:
                if 'control' == mod:
                    new_hotkey.append(mod)
            for mod in hotkey[:-1]:
                if 'shift' == mod:
                    new_hotkey.append(mod)
            for mod in hotkey[:-1]:
                if 'alt' == mod:
                    new_hotkey.append(mod)
            for mod in hotkey[:-1]:
                if 'super' == mod:
                    new_hotkey.append(mod)
            new_hotkey.append(hotkey[-1])
            hotkey = new_hotkey
        return hotkey

    def parse_hotkeylist(self, full_hotkey):
        # Returns keycodes and masks from a list of hotkey masks
        masks = []
        keycode = self._get_keycode(full_hotkey[-1])
        if keycode is None:
            key = full_hotkey[-1]
            # Make sure kp keys are in the correct format
            if key[:3].lower() == 'kp_':
                keycode = self._get_keycode('KP_' + full_hotkey[-1][3:].capitalize())
            if keycode is None:
                msg = 'Unable to Register, Key not understood by systemhotkey'
                raise InvalidKeyError(msg)


        if len(full_hotkey) > 1:
            for item in full_hotkey[:-1]:
                try:
                    masks.append(self.modders[item])
                except KeyError:
                    raise SystemRegisterError('Modifier: %s not supported' % item)    #TODO rmeove how the keyerror gets displayed as well
            masks = self.or_modifiers_together(masks)
        else:
            masks = 0
        return keycode, masks

    def or_modifiers_together(self, modifiers):
        # Binary or the modifiers together
        result = 0
        for part in modifiers:
            result |= part
        return result

    def get_callback(self, hotkey):
        if self.verbose:
            print('Keybinds , key here -> ', tuple(hotkey))
            print(self.keybinds)
        try:
            yield self.keybinds[tuple(hotkey)]
        except KeyError:
            # On Linux
            # The event gets sent a few times to us with different
            # Information about the modifyer, we just ignore failed attempts
            if self.verbose:
                print('MFERROR', hotkey)
            # Possible numpad key? The keysym can change if shift is pressed (only tested on linux)
            # TODO test numpad bindings on a non english system
            aliases = NUMPAD_ALIASES.get(hotkey[-1])
            if aliases:
                for key in aliases:
                    try:
                        new_hotkey = hotkey[:-1]
                        new_hotkey.append(key)
                        yield self.keybinds[tuple(new_hotkey)]
                        break
                    except (KeyError, TypeError):
                        if self.verbose:
                            print('NUMERROR', new_hotkey)

        # this was for the event_type callback
        # def get_callback(self, hotkey ,event_type):
            # copy = list(hotkey)
            # copy.append(event_type)
            # if self.verbose:
                # print('Keybinds , key here -> ', tuple(copy))
                # pprint(self.keybinds)
            # for func in self.keybinds[tuple(copy)]:
                # yield func


    def parse_event(self, event):
        ''' Turns an event back into a hotkeylist'''
        hotkey = []
        if False: pass
        else:
            keycode, modifiers = self.hk_ref[event.wParam][0], self.hk_ref[event.wParam][1]
            hotkey += self.get_modifiersym(modifiers)
            hotkey.append(self._get_keysym(keycode).lower())
 
        if self.verbose:
            print('hotkey ', hotkey)
        return hotkey


    def get_modifiersym(self, state):
        ret = []
        if state & self.modders['control']:
            ret.append('control')
        if state & self.modders['shift']:
            ret.append('shift')
        if state & self.modders['alt']:
            ret.append('alt')
        if state & self.modders['super']:
            ret.append('super')
        return ret

    def _get_keysym(self, keycode):
        '''
        given a keycode returns a keysym
        '''
        # TODO
        # --quirks--
        # linux:
        #     numpad keys with multiple keysyms are currently undistinguishable
        # i.e kp_3 and kp_page_down look exactly the same, so we cannot implement our unite_kp..


class SystemHotkey(MixIn):
    '''
    Cross platform System Wide Hotkeys

    Modifer oder doesn't matter, e.g
    binding to  control shift k is the same as shift control k,
    limitation of the keyboard and operating systems not this library
    '''
    hk_ref = {}
    keybinds = {}

    def __init__(self, consumer='callback', check_queue_interval=0.0001, use_xlib=False, conn=None, verbose=False, unite_kp=True):
        '''
        if the consumer param = 'callback', -> All hotkeys will require
        a callback function

        Otherwise set consumer to a function to hanlde the event.
        the function signature: event, hotkey, args
        event is the xwindow/microsoft keyboard event
        hotkey is a tuple,
        args is a list of any ars parsed in at the time of registering

        check_queue_interval is in seconds and sets the sleep time on
        checking the queue for hotkey presses

        set use_xlib to true to use the xlib python bindings (GPL) instead of the xcb ones (BSD)
        You can pass an exisiting X display or connection using the conn keyword,
        otherwise one will be created for you.

        keybinds will work regardless if numlock/capslock are on/off.
        so kp_3 will also bind to kp_page_down
        If you do not want numpad keys to have the same function
        when numlock is on or off set unite_kp to False (only windows)
        TODO
        This is still under development, triggering the key with
        other modifyers such as shift or fn keys may or maynot work
        '''
        # Changes the class methods to point to differenct functions
        # Depening on the operating system and library used
        # Consumer can be set to a function also, which will be sent the event
        # as well as the key and mask already broken out
        # Last option for consumer is False, then you have to listen to the queue yourself
        # data_queue
        self.verbose = verbose
        self.use_xlib = use_xlib
        self.consumer = consumer
        self.check_queue_interval = check_queue_interval
        self.unite_kp = unite_kp
         
        def mark_event_type(event):
            # event gets an event_type attribute so the user has a portiabble way
            # actually on windows as far as i know you dont have the option of binding on keypress or release so...
            # anyway ahve to check it but for now u dont!
            if False:
                pass
            else:
                event.event_type = 'keypress'
            return event

        self.data_queue = queue.Queue()
        if True:
            self.hk_action_queue = queue.Queue()
            self.modders = win_modders
            self.trivial_mods = win_trivial_mods
            self._the_grab = self._nt_the_grab
            self._get_keycode = self._nt_get_keycode
            self._get_keysym = self._nt_get_keysym

            thread.start_new_thread(self._nt_wait,(),)
 
        if consumer == 'callback':
            if self.verbose:
                print('In Callback')
            def thread_me():
                while 1:
                    time.sleep(self.check_queue_interval)
                    try:
                        event = self.data_queue.get(block=False)
                    except queue.Empty:
                        pass
                    else:
                        event = mark_event_type(event)
                        hotkey = self.parse_event(event)
                        if not hotkey:
                            continue
                        #~ for cb in self.get_callback(hotkey, event.event_type):   #when i was using the keypress / keyrelease shit
                        for cb in self.get_callback(hotkey):
                            if event.event_type == 'keypress':
                                if self.verbose:
                                    print('calling ', repr(cb))
                                cb(event)   # TODO either throw these up in a thread, or pass in a queue to be put onto
            thread.start_new_thread(thread_me,(),)

        elif callable(consumer):
            def thread_me():
                while 1:
                    time.sleep(self.check_queue_interval)
                    try:
                        event = self.data_queue.get(block=False)
                    except queue.Empty:
                        pass
                    else:
                        hotkey = self.parse_event(mark_event_type(event))
                        if not hotkey:
                            continue
                        if event.event_type == 'keypress':
                            args = [cb for cb in self.get_callback(hotkey)]
                            #~ callbacks = [cb for cb in self.get_callback(hotkey, event.event_type)]
                            consumer(event, hotkey, args)
            thread.start_new_thread(thread_me,(),)
        else:
            print('You need to handle grabbing events yourself!')
 
    def _nt_wait(self):
        # Pushes Event onto queue
        # I don't understand the windows msg system
        # I can only get hotkeys to work if they are registeed in the
        # Thread that is listening for them.
        # So any changes to the hotkeys have to be signaled to be done
        # By the thread. (including unregistering)
        # A new queue is checked and runs functions, either adding
        # or removing new hotkeys, then the windows msg queue is checked
        msg = ctypes.wintypes.MSG ()
        while 1:
            try:
                remove_or_add = self.hk_action_queue.get(block=False)
            except queue.Empty:
                pass
            else:
                remove_or_add()
            # Checking the windows message Queue
            if user32.PeekMessageA(byref(msg), 0, 0, 0, PM_REMOVE):
                if msg.message == win32con.WM_HOTKEY:
                    self.data_queue.put(msg)
                else:
                    print('some other message')
            time.sleep(self.check_queue_interval)

    def _nt_get_keycode(self, key, disp=None):
        return vk_codes.get(key)

    def _nt_get_keysym(self, keycode):
        for key, value in vk_codes.items():
            if value == keycode:
                return key

    def _nt_the_grab(self, keycode, masks, id, root=None):
        keysym = self._get_keysym(keycode)
        aliases = NUMPAD_ALIASES.get(keysym)
        # register numpad aliases for the keypad
        if aliases and self.unite_kp:
            for alias in aliases:
                if alias != keysym and self._get_keycode(alias):
                    # Hack to avoid entering this control flow again..
                    self.unite_kp = False
                    self._the_grab(self._get_keycode(alias), masks, id)
                    self.unite_kp = True

        if not user32.RegisterHotKey(None, id, masks, keycode):
            keysym = self._nt_get_keysym(keycode)
            msg = 'The bind could be in use elsewhere: ' + keysym
            raise SystemRegisterError(msg)
 