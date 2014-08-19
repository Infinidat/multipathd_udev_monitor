__import__("pkg_resources").declare_namespace(__name__)

import socket
import time
import syslog


DM_SOCKET_NAME = '\x00/org/kernel/dm/multipath_event'


class UeventMessage(object):
    def __init__(self, action, devpath):
        self._buffer = ''
        self._append_str('{action}@{devpath}\x00'.format(action=action, devpath=devpath))

    def get_buffer(self):
        return self._buffer

    def add_field(self, key, value):
        self._append_str('{key}={value}'.format(key=key, value=value))

    def _append_str(self, string):
        self._buffer += string + '\x00'


def relay(monitor, mpath_socket):
    for device in iter(monitor.poll, None):
        device_dict = dict(device.items())
        action = device_dict.get('ACTION')
        devpath = device_dict.get('DEVPATH')
        syslog.syslog(syslog.LOG_INFO, 'ACTION={action} DEVPATH={devpath}'.format(action=action, devpath=devpath))
        if not action or not devpath:
            syslog.syslog(syslog.LOG_ERROR, 'Skipping')
            continue
        msg = UeventMessage(action, devpath)
        for key,value in device_dict.iteritems():
            msg.add_field(key, value)

        mpath_socket.send(msg.get_buffer())


def poll():
    import pyudev
    # Register for block device udev events
    syslog.syslog(syslog.LOG_INFO, 'Registering for udev events')
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context, source='udev')
    monitor.filter_by('block')
    monitor.enable_receiving()

    # Connect to the multipathd socket
    mpath_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    while True:
        try:
            syslog.syslog(syslog.LOG_INFO, 'Trying to connect to multipathd unix socket')
            mpath_socket.connect(DM_SOCKET_NAME)
            syslog.syslog(syslog.LOG_INFO, 'Connected to multipathd unix socket')
            relay(monitor, mpath_socket)

        except socket.error, e:
            if 111 != e.errno:
                syslog.syslog(syslog.LOG_ERROR, 'Socket error {errno}'.format(e.errno))
            time.sleep(1)


def nothing():
    pass
