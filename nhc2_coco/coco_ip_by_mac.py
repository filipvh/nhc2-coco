import binascii
import select
import threading
import socket
import netifaces
from getmac import get_mac_address


class CoCoIpByMac:
    """CoCoDiscover will help you discover NHC2.
    It will also tell you about NHC1, but the result will differ.

    You create CoCoDiscover, passing along a callback an the time you max want to wait.
    By default we wait 3 seconds.
    
    For every result with matching header the callback is called,
    with the address, mac-address and a boolean if it's a NHC2.
    """

    def __init__(self, mac_to_match, on_found_ip):
        self._thread = threading.Thread(target=self._scan_for_nhc)
        self._on_found_ip = on_found_ip
        self._mac_to_match = mac_to_match
        self._thread.start()

    def _get_broadcast_ips(self):
        interfaces = netifaces.interfaces()
        return filter(lambda x: x,
                              map(lambda x: netifaces.ifaddresses(x).get(netifaces.AF_INET)[0].get('broadcast') if (
                                      (netifaces.AF_INET in netifaces.ifaddresses(x))
                                      and ('broadcast' in netifaces.ifaddresses(x).get(netifaces.AF_INET)[0])

                              ) else None, interfaces))

    def _scan_for_nhc(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        """ We search for all broadcast ip4s, so that we don't only search the main interface """
        self._broadcast_ping(server)
        searching = True

        while searching:
            ready = select.select([server], [], [], 1)
            if ready[0]:
                data, addr = server.recvfrom(4096)
                raw_ip = list(map(lambda x: data[x], (6, 7, 8, 9)))
                raw_mac = ''.join('{:02X}'.format(a) for a in data[2:6])
                ip = "{}.{}.{}.{}".format(*raw_ip)
                mac = raw_mac[-4:]
                mac_to_match = self._mac_to_match.replace(':', '').upper()[-4:]
                if mac_to_match == mac and callable(self._on_found_ip):
                    print("found ip %s" % ip)
                    self._on_found_ip(ip)
                    searching = False
            self._broadcast_ping(server)
        server.close()
        print('Done searching')

    def _broadcast_ping(self,  server):
        broadcast_ips = self._get_broadcast_ips()
        for broadcast_ip in broadcast_ips:
            server.sendto(bytes([0x44]), (broadcast_ip, 10000))
        server.setblocking(0)
