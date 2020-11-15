import select
import sys
import time
import threading
import socket


class CoCoDiscover:
    """CoCoDiscover will help you discover NHC2.
    It will also tell you about NHC1, but the result will differ.

    You create CoCoDiscover, passing along a callback an the time you max want to wait.
    By default we do 2 cycles of one second each.
    
    For every result with matching header the callback is called,
    with the address and a boolean if it's a NHC2.
    """
    def __init__(self, callback, scan_time=2):
        self._thread = threading.Thread(target=self._scan_for_nhc)
        self._on_discover = callback
        self._scan_time = scan_time
        self._thread.start()

    def _scan_for_nhc(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.sendto(bytes([0x44]), ('<broadcast>', 10000))
        server.setblocking(0)
        loops = 0

        while loops < self._scan_time:
            loops = loops + 1
            ready = select.select([server], [], [], 1)
            if ready[0]:
                data, addr = server.recvfrom(4096)
                if data[0] is 0x44:  # NHC2 Header
                    is_nhc2 = (len(data) >= 16) and (data[15] is 0x02)
                    ident = None
                    if is_nhc2:

                    if self._on_discover:
                        self._on_discover(addr[0], ident, is_nhc2)

        server.close()
        sys.exit()


