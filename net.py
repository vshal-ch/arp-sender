import socket
from helpers.binary import (
    get_hex_string,
    get_ip_bit_string,
    bin_8_bit,
    bitstring_to_bytes,
    get_ip_from_bits,
)
from helpers.logger import log, info

INTERFACE = "wlp2s0"
BROADCAST_MAC = "1" * 48
ZERO_MAC = "0" * 48


class ArpSender:
    PACKET_SIZE = 42
    OP_CODE_INDEX = [20, 21]
    SENDER_HARDWARE_INDEX = [22, 27]
    TIMEOUT = 2

    def __init__(self, local_mac, target_ip, ip_input="str"):
        log("In Constructor",newline=True)
        self.local_mac = local_mac
        self.target_ip = target_ip
        self.ip_input = ip_input
        self.ip_addr = self.target_ip if ip_input=="str" else get_ip_from_bits(target_ip)
        self.local_ip = socket.gethostbyname(socket.gethostname())

    def process(self):
        if self.__check_if_self():
            return
        self.sock = socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)
        )
        # self.sock.settimeout(self.TIMEOUT)
        self.sock.bind((INTERFACE, 0))
        self.build_arp()
        self.send_arp()
        try:
            self.wait_for_reply()
            target_mac = self.recieve()
            return (self.ip_addr, target_mac) if target_mac else None
        except TimeoutError as e:
            info("Timed out, Aborting!")
            return None
        finally:
            self.finalize()

    def build_arp(self):
        arp_prot_bit_string = bin_8_bit(8) + bin_8_bit(6)
        hardware_type = bin_8_bit(0) + bin_8_bit(6)
        protocol = bin_8_bit(8) + bin_8_bit(0)
        hardware_length = bin_8_bit(6)
        ip_length = bin_8_bit(4)
        op_code = bin_8_bit(0) + bin_8_bit(1)
        local_mac_bit_string = get_hex_string(self.local_mac)
        local_ip_bit_string = get_ip_bit_string(
            self.local_ip
        )
        target_ip_bit_string = (
            get_ip_bit_string(self.target_ip)
            if self.ip_input == "str"
            else self.target_ip
        )

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

        self.packet = bitstring_to_bytes(arp)

    def send_arp(self):
        info("Sending ARP request for MAC of IP: "+self.ip_addr)
        log("Sending packet...")
        self.fd = self.sock.send(self.packet)
        log("Packet sent.")
        info("Socket File descriptor = " + str(self.fd))

    def wait_for_reply(self):
        log("Waiting for reply...")
        self.reply = self.sock.recvfrom(4096)
        log("Recieved response.")

    def recieve(self):
        data = self.reply[0]
        op_code = self.__get_op_code(data)
        if op_code == 2:
            target_mac = self.__get_target_mac(data)
            info("Hardware address of " + self.ip_addr + " = " + target_mac)
            return target_mac
        else:
            info("OP code is not equal to 2(reply)")
            return None

    def finalize(self):
        self.sock.close()
        log("Socket closed.")

    # private methods

    def __get_op_code(self, data):
        op_code = data[self.OP_CODE_INDEX[1]]
        info("OP Code: " + str(op_code))
        return op_code

    def __get_target_mac(self, data):
        target_mac = ""
        for i in range(self.SENDER_HARDWARE_INDEX[0], self.SENDER_HARDWARE_INDEX[1]):
            val = hex(data[i])
            target_mac += str(val)[2:] + ":"
        target_mac += str(hex(data[self.SENDER_HARDWARE_INDEX[1]]))[2:]
        return target_mac

    def __check_if_self(self):
        if self.ip_addr == self.local_ip:
            info("Target IP is same as Local IP")
            log("Aborting.")
            return True
