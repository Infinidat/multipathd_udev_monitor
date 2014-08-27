__version__ = "0.post11.gc3fd751"
__git_commiter_name__ = "Shai Keren"
__git_commiter_email__ = "shaik@infinidat.com"
__git_branch__ = 'develop'
__git_remote_tracking_branch__ = 'origin/develop'
__git_remote_url__ = 'git@infinigit.infinidat.com:/host/multipath-tools-udev-monitor.git'
__git_head_hash__ = 'c3fd751e58df343ae0b241a7f8a0d18457c1bcaf'
__git_head_subject__ = 'TRIVIAL changed pid filename to match sysv_service convention'
__git_head_message__ = ''
__git_dirty_diff__ = 'diff --git a/src/multipathd_udev_monitor/__version__.py b/src/multipathd_udev_monitor/__version__.py\nindex 55dd488..548a9cb 100644\n--- a/src/multipathd_udev_monitor/__version__.py\n+++ b/src/multipathd_udev_monitor/__version__.py\n@@ -1,10 +1,10 @@\n-__version__ = "0.post2.g4e6c087"\n+__version__ = "0.post11.gc3fd751"\n __git_commiter_name__ = "Shai Keren"\n __git_commiter_email__ = "shaik@infinidat.com"\n __git_branch__ = \'develop\'\n __git_remote_tracking_branch__ = \'origin/develop\'\n-__git_remote_url__ = \'git@infinigit.infinidat.com:host/multipath-tools-udev-monitor.git\'\n-__git_head_hash__ = \'4e6c087310674a8fcdf3284878e24fd0b9722c57\'\n-__git_head_subject__ = \'First commit\'\n+__git_remote_url__ = \'git@infinigit.infinidat.com:/host/multipath-tools-udev-monitor.git\'\n+__git_head_hash__ = \'c3fd751e58df343ae0b241a7f8a0d18457c1bcaf\'\n+__git_head_subject__ = \'TRIVIAL changed pid filename to match sysv_service convention\'\n __git_head_message__ = \'\'\n-__git_dirty_diff__ = \'diff --git i/buildout.cfg w/buildout.cfg\\nindex 12f8c7d..9aa17c4 100644\\n--- i/buildout.cfg\\n+++ w/buildout.cfg\\n@@ -3,21 +3,26 @@ prefer-final = false\\n newest = false\\n download-cache = .cache\\n develop = .\\n-parts = \\n+parts =\\n \\n [project]\\n-name = multipath-tools-poller\\n+name = multipath-tools-udev-monitor\\n company = Infinidat\\n namespace_packages = []\\n-install_requires = [\\\'setuptools\\\']\\n-version_file = src/multipath-tools-poller/__version__.py\\n+install_requires = [\\n+\\t\\\'pyudev\\\',\\n+\\t\\\'setuptools\\\'\\n+\\t]\\n+version_file = src/multipathd_udev_monitor/__version__.py\\n description = A workaround utility for malfunctioning multipathd in ubuntu 14.04\\n long_description = This utility runs in background an relays device related events from libudev to the unix domain socket read by multipathd\\n-console_scripts = []\\n+console_scripts = [\\n+\\t\\\'multipathd_udev_monitor = multipathd_udev_monitor:poll\\\'\\n+\\t]\\n gui_scripts = []\\n package_data = []\\n upgrade_code = {75e8a92b-2778-11e4-82ec-48d705bea411}\\n-product_name = multipath-tools-poller\\n+product_name = multipath-tools-udev-monitor\\n post_install_script_name = None\\n pre_uninstall_script_name = None\\n \\n@@ -71,7 +76,10 @@ recipe = pb.recipes.pydev\\n eggs = $\\\\{development-scripts:eggs}\\n \\n [pack]\\n-recipe = infi.recipe.application_packager\\n+recipe = infi.recipe.application_packager:executable\\n+isolated-python-section = isolated-python\\n+debug = true\\n+dependent-scripts = false\\n \\n [sublime]\\n recipe = corneti.recipes.codeintel\\ndiff --git i/src/multipathd_udev_monitor/__init__.py w/src/multipathd_udev_monitor/__init__.py\\nindex 5284146..1dc0a1b 100644\\n--- i/src/multipathd_udev_monitor/__init__.py\\n+++ w/src/multipathd_udev_monitor/__init__.py\\n@@ -1 +1,63 @@\\n __import__("pkg_resources").declare_namespace(__name__)\\n+\\n+import pyudev\\n+import socket\\n+import time\\n+import syslog\\n+\\n+\\n+DM_SOCKET_NAME = \\\'\\\\x00/org/kernel/dm/multipath_event\\\'\\n+\\n+\\n+class UeventMessage(object):\\n+    def __init__(self, action, devpath):\\n+        self._buffer = \\\'\\\'\\n+        self._append_str(\\\'{action}@{devpath}\\\\x00\\\'.format(action=action, devpath=devpath))\\n+\\n+    def get_buffer(self):\\n+        return self._buffer\\n+\\n+    def add_field(self, key, value):\\n+        self._append_str(\\\'{key}={value}\\\'.format(key=key, value=value))\\n+\\n+    def _append_str(self, string):\\n+        self._buffer += string + \\\'\\\\x00\\\'\\n+\\n+\\n+def relay(monitor, mpath_socket):\\n+    for device in iter(monitor.poll, None):\\n+        device_dict = dict(device.items())\\n+        action = device_dict.get(\\\'ACTION\\\')\\n+        devpath = device_dict.get(\\\'DEVPATH\\\')\\n+        syslog.syslog(syslog.LOG_INFO, \\\'ACTION={action} DEVPATH={devpath}\\\'.format(action=action, devpath=devpath))\\n+        if not action or not devpath:\\n+            syslog.syslog(syslog.LOG_ERROR, \\\'Skipping\\\')\\n+            continue\\n+        msg = UeventMessage(action, devpath)\\n+        for key,value in device_dict.iteritems():\\n+            msg.add_field(key, value)\\n+\\n+        mpath_socket.send(msg.get_buffer())\\n+\\n+\\n+def poll():\\n+    # Register for block device udev events\\n+    syslog.syslog(syslog.LOG_INFO, \\\'Registering for udev events\\\')\\n+    context = pyudev.Context()\\n+    monitor = pyudev.Monitor.from_netlink(context, source=\\\'udev\\\')\\n+    monitor.filter_by(\\\'block\\\')\\n+    monitor.enable_receiving()\\n+\\n+    # Connect to the multipathd socket\\n+    mpath_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)\\n+    while True:\\n+        try:\\n+            syslog.syslog(syslog.LOG_INFO, \\\'Trying to connect to multipathd unix socket\\\')\\n+            mpath_socket.connect(DM_SOCKET_NAME)\\n+            syslog.syslog(syslog.LOG_INFO, \\\'Connected to multipathd unix socket\\\')\\n+            relay(monitor, mpath_socket)\\n+\\n+        except socket.error, e:\\n+            if 111 != e.errno:\\n+                syslog.syslog(syslog.LOG_ERROR, \\\'Socket error {errno}\\\'.format(e.errno))\\n+            time.sleep(1)\\n\'\n\\ No newline at end of file\n+__git_dirty_diff__ = \'\'\n\\ No newline at end of file\n'