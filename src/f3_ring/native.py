# Narrowly match F3 devices, seize each HID entry, and receive unmodified reports.
import ctypes
import hashlib


P = ctypes.c_void_p
I = ctypes.c_int32
U = ctypes.c_uint32
N = ctypes.c_long
REPORT_CALLBACK = ctypes.CFUNCTYPE(None, P, I, P, U, U, ctypes.POINTER(ctypes.c_uint8), N)
REMOVAL_CALLBACK = ctypes.CFUNCTYPE(None, P, I, P)


def bind(library: object, name: str, result: object, arguments: list) -> object:
    function = getattr(library, name)
    function.restype = result
    function.argtypes = arguments
    return function


def libraries() -> tuple[object, object]:
    cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    io = ctypes.CDLL('/System/Library/Frameworks/IOKit.framework/IOKit')
    definitions = [
        (cf, 'CFStringCreateWithCString', P, [P, ctypes.c_char_p, U]),
        (cf, 'CFDictionaryCreate', P, [P, ctypes.POINTER(P), ctypes.POINTER(P), N, P, P]),
        (cf, 'CFSetGetCount', N, [P]), (cf, 'CFSetGetValues', None, [P, ctypes.POINTER(P)]),
        (cf, 'CFRetain', P, [P]), (cf, 'CFRelease', None, [P]),
        (cf, 'CFGetTypeID', ctypes.c_ulong, [P]), (cf, 'CFStringGetTypeID', ctypes.c_ulong, []),
        (cf, 'CFNumberGetTypeID', ctypes.c_ulong, []), (cf, 'CFDataGetTypeID', ctypes.c_ulong, []),
        (cf, 'CFStringGetCString', ctypes.c_bool, [P, ctypes.c_char_p, N, U]),
        (cf, 'CFNumberGetValue', ctypes.c_bool, [P, I, P]),
        (cf, 'CFDataGetLength', N, [P]), (cf, 'CFDataGetBytePtr', P, [P]),
        (cf, 'CFRunLoopGetCurrent', P, []), (cf, 'CFRunLoopRunInMode', I, [P, ctypes.c_double, ctypes.c_bool]),
        (io, 'IOHIDManagerCreate', P, [P, U]), (io, 'IOHIDManagerSetDeviceMatching', None, [P, P]),
        (io, 'IOHIDManagerOpen', I, [P, U]), (io, 'IOHIDManagerClose', I, [P, U]),
        (io, 'IOHIDManagerCopyDevices', P, [P]), (io, 'IOHIDDeviceGetProperty', P, [P, P]),
        (io, 'IOHIDDeviceOpen', I, [P, U]), (io, 'IOHIDDeviceClose', I, [P, U]),
        (io, 'IOHIDDeviceScheduleWithRunLoop', None, [P, P, P]),
        (io, 'IOHIDDeviceUnscheduleFromRunLoop', None, [P, P, P]),
        (io, 'IOHIDDeviceRegisterInputReportCallback', None, [P, P, N, REPORT_CALLBACK, P]),
        (io, 'IOHIDDeviceRegisterRemovalCallback', None, [P, REMOVAL_CALLBACK, P]),
        (io, 'IOHIDCheckAccess', I, [I]), (io, 'IOHIDRequestAccess', ctypes.c_bool, [I]),
    ]
    [bind(*definition) for definition in definitions]
    return cf, io


def string(cf: object, value: str) -> int:
    return cf.CFStringCreateWithCString(None, value.encode(), 0x08000100)


def property_value(cf: object, io: object, device: int, name: str) -> object:
    key = string(cf, name)
    value = io.IOHIDDeviceGetProperty(device, key)
    cf.CFRelease(key)
    if not value:
        return None
    kind = cf.CFGetTypeID(value)
    if kind == cf.CFStringGetTypeID():
        buffer = ctypes.create_string_buffer(4096)
        return buffer.value.decode('utf-8', errors='replace') if cf.CFStringGetCString(value, buffer, len(buffer), 0x08000100) else None
    if kind == cf.CFNumberGetTypeID():
        number = ctypes.c_int64()
        return number.value if cf.CFNumberGetValue(value, 4, ctypes.byref(number)) else None
    if kind == cf.CFDataGetTypeID():
        return ctypes.string_at(cf.CFDataGetBytePtr(value), cf.CFDataGetLength(value)).hex()
    return None


def inventory(cf: object, io: object, product: str) -> tuple[int, list]:
    manager = io.IOHIDManagerCreate(None, 0)
    key, value = string(cf, 'Product'), string(cf, product)
    keys, values = (P * 1)(key), (P * 1)(value)
    matching = cf.CFDictionaryCreate(None, keys, values, 1, None, None)
    io.IOHIDManagerSetDeviceMatching(manager, matching)
    result = io.IOHIDManagerOpen(manager, 0)
    device_set = io.IOHIDManagerCopyDevices(manager)
    devices = []
    if device_set:
        pointers = (P * cf.CFSetGetCount(device_set))()
        cf.CFSetGetValues(device_set, pointers)
        devices = [cf.CFRetain(pointer) for pointer in pointers
                   if property_value(cf, io, pointer, 'Product') == product]
        cf.CFRelease(device_set)
    io.IOHIDManagerClose(manager, 0)
    [cf.CFRelease(item) for item in (matching, key, value, manager)]
    return result, devices


def describe(cf: object, io: object, device: int) -> dict:
    names = ['Product', 'Manufacturer', 'Transport', 'VendorID', 'ProductID', 'VersionNumber',
             'PrimaryUsagePage', 'PrimaryUsage', 'LocationID', 'SerialNumber', 'MaxInputReportSize', 'ReportDescriptor']
    details = {name: property_value(cf, io, device, name) for name in names}
    descriptor = details.get('ReportDescriptor')
    details['report_descriptor_sha256'] = hashlib.sha256(bytes.fromhex(descriptor)).hexdigest() if descriptor is not None else None
    return details
