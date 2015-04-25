from infi.execute import execute_assert_success

PACKAGE_NAME = 'multipathd-udev-monitor'

def is_64bit():
    from sys import maxsize
    return maxsize > 2 ** 32

def get_arch_name():
    return 'x64' if is_64bit() else 'x86'

def get_arch_name_for_control():
    return 'amd64' if is_64bit() else 'i386'

def get_os_string():
        from platform import architecture, system, dist
        system_name = system().lower().replace('-', '').replace('_', '')
        dist_name, dist_version, dist_version_name = dist()
        dist_name = dist_name.lower()
        is_centos = dist_name == 'centos'
        is_ubuntu = dist_name == 'ubuntu'
        dist_version_string = dist_version_name.lower() if is_ubuntu else dist_version.lower().split('.')[0]
        string_by_os = {
                        "Windows": '-'.join([system_name, get_arch_name()]),
                        "Linux": '-'.join([system_name,
                                           self._get_centos_dist_name() if is_centos else dist_name,
                                           dist_version_string, get_arch_name()]),
        }
        return string_by_os.get(system())


def get_project_version__short():
    from multipathd_udev_monitor.__version__ import __version__
    from infi.os_info import shorten_version_string
    return shorten_version_string(__version__)


def get_deb_filename():
    return "{}-{}-{}.deb".format(PACKAGE_NAME, get_project_version__short(), get_os_string())


def build_deb_package():
    execute_assert_success(["projector", "devenv", "pack"])
    execute_assert_success(["mkdir", "-p", "./debian/sbin"])
    execute_assert_success(["cp", "./dist/multipathd_udev_monitor", "./debian/sbin"])
    execute_assert_success(["sed", "-i", "s/$version/{ver}/g".format(ver=get_project_version__short()),
                            "./debian/DEBIAN/control"])
    execute_assert_success(["sed", "-i", "s/$arch/{arch}/g".format(arch=get_arch_name_for_control()),
                            "./debian/DEBIAN/control"])
    execute_assert_success(["dpkg-deb", "--build", "./debian", "./parts/{name}".format(name=get_deb_filename())])


if __name__ == '__main__':
    build_deb_package()
