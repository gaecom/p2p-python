import socket
import os
import random
from tempfile import gettempdir
from p2p_python.config import V, Debug


def get_version():
    if Debug.P_EXCEPTION:
        return 'debug'
    hear = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(hear, '__init__.py'), mode='r') as fp:
        for word in fp.readlines():
            if word.startswith('__version__'):
                return word.replace('"', "'").split("'")[-2]
    return 'dev'


def get_name():
    hear = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(hear, 'name_list.txt')) as fp:
        name = fp.read().split()
    return "{}:{}".format(random.choice(name), random.randint(10000, 99999))


def setup_p2p_params(network_ver, p2p_port, p2p_accept=True,
                     p2p_udp_accept=True, sub_dir=None, f_debug=False):
    """ setup general connection setting """
    if f_debug:
        Debug.P_EXCEPTION = True
        Debug.P_RECEIVE_MSG_INFO = True
        Debug.F_LONG_MSG_INFO = True
    # directory params
    if V.DATA_PATH is not None:
        raise BaseException('Already setup params.')
    V.DATA_PATH = os.path.join(os.path.expanduser('~'), 'p2p-python')
    V.TMP_PATH = os.path.join(gettempdir(), 'p2p-python')
    if not os.path.exists(V.DATA_PATH):
        os.makedirs(V.DATA_PATH)
    if not os.path.exists(V.TMP_PATH):
        os.makedirs(V.TMP_PATH)
    if sub_dir:
        V.DATA_PATH = os.path.join(V.DATA_PATH, sub_dir)
        V.TMP_PATH = os.path.join(V.TMP_PATH, sub_dir)
    if not os.path.exists(V.DATA_PATH):
        os.makedirs(V.DATA_PATH)
    if not os.path.exists(V.TMP_PATH):
        os.makedirs(V.TMP_PATH)
    # Network params
    V.CLIENT_VER = get_version()
    V.SERVER_NAME = get_name()
    V.NETWORK_VER = network_ver
    V.P2P_PORT = p2p_port
    V.P2P_ACCEPT = p2p_accept
    V.P2P_UDP_ACCEPT = p2p_udp_accept


def setup_tor_connection(proxy_host='127.0.0.1', port=9150, f_raise_error=True):
    """ client connection to onion router """
    # Typically, Tor listens for SOCKS connections on port 9050.
    # Tor-browser listens on port 9150.
    host_port = (proxy_host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if V.P2P_ACCEPT or V.P2P_UDP_ACCEPT:
        raise ConnectionError('P2P socket accept enable? tcp={} udp={}'
                              .format(V.P2P_ACCEPT, V.P2P_UDP_ACCEPT))
    if 0 != sock.connect_ex(host_port):
        if f_raise_error:
            raise ConnectionError('Cannot connect proxy by test.')
    else:
        V.TOR_CONNECTION = host_port
    sock.close()


def is_reachable(host, port):
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, host_port = res
        try:
            sock = socket.socket(af, socktype, proto)
        except OSError:
            continue
        result = sock.connect_ex(host_port)
        sock.close()
        if result == 0:
            return True
    else:
        # create no connection
        return False


def trim_msg(item, num):
    str_item = str(item)
    return str_item[:num] + ('...' if len(str_item) > num else '')


__all__ = [
    "get_version", "get_name", "is_reachable",
    "setup_tor_connection", "setup_p2p_params", "trim_msg",
]
