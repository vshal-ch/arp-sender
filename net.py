import socket
import codecs

INTERFACE = "wlp2s0"
BROADCAST_MAC = "1" * 48
ZERO_MAC = "0" * 48

class ArpSender:
    def __init__(self, local_mac, target_ip, ip_input = 'str'):
        self.local_mac = local_mac
        self.target_ip = target_ip
        self.ip_input = ip_input

    def process(self):
        self.sock = socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)
        )
        self.sock.bind((INTERFACE, 0))
        self.build_arp()
        self.send_arp()
        # self.recieve()
        self.finalize()

    def build_arp(self,):
        arp_prot_bit_string = self.__bin(8) + self.__bin(6)
        hardware_type = self.__bin(0) + self.__bin(6)
        protocol = self.__bin(8) + self.__bin(0)
        hardware_length = self.__bin(6)
        ip_length = self.__bin(4)
        op_code = self.__bin(0) + self.__bin(1)
        local_mac_bit_string = self.__get_hex_string(self.local_mac)
        local_ip_bit_string = self.__get_ip_bit_string(
            socket.gethostbyname(socket.gethostname())
        )
        target_ip_bit_string = self.__get_ip_bit_string(self.target_ip) if self.ip_input == 'str' else self.target_ip

        arp = (
            BROADCAST_MAC
            + local_mac_bit_string
            + arp_prot_bit_string
            + hardware_type
            + protocol
            + hardware_length
            + ip_length
            + op_code
            + local_mac_bit_string
            + local_ip_bit_string
            + BROADCAST_MAC
            + target_ip_bit_string
        )

        self.packet = self.__bitstring_to_bytes(arp)

    def send_arp(self):
        print("INFO: Sending packet...")
        self.fd = self.sock.send(self.packet)
        print("INFO: Socket File descriptor = " + str(self.fd))

    # this ain't working as expected
    def recieve(self):
        data = self.sock.recvfrom(4096)
        print(codecs.decode(data[0], 'iso-8859-1'))

    def finalize(self):
        self.sock.close()

    # private methods

    def __bin(self, n):
        return "{0:08b}".format(n)

    def __bitstring_to_bytes(self, s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder="big")

    def __get_ip_array(self, ip_s):
        return list(map(int, ip_s.split(".")))

    def __get_hex_string(self, hex_s):
        arr = hex_s.split(":")
        s = ""
        for i in arr:
            s += self.__bin(int(i, 16))
        return s

    def __get_ip_bit_string(self, ip_string):
        ip_arr = self.__get_ip_array(ip_string)
        s = ""
        for i in ip_arr:
            s += self.__bin(i)
        return s
