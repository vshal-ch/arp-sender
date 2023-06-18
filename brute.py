import socket
import netifaces
from net import ArpSender

addresses = netifaces.ifaddresses('wlp2s0')
netmask = addresses[netifaces.AF_INET][0]['netmask']
ip_address = socket.gethostbyname(socket.gethostname())
local_mac = "10:5b:ad:65:a4:75"

# this function takes netmask('255.255.255.0') as input and returns the cidr value(8)
def get_cidr_value(netmask):
    pieces = netmask.split('.')
    cidr_value = 0

    for i in range(len(pieces)-1,-1,-1):
        num = int(pieces[i])
        if num == 0:
            cidr_value += 8
            continue
        else:
            temp = num
            while temp%2 == 0:
                cidr_value += 1
                temp = temp // 2
            break
    return cidr_value

def generate_ip_address(ip, cidr_value):
    def __bin(n):
        return "{0:08b}".format(n)
    def __get_ip_array(ip_s):
        return list(map(int, ip_s.split(".")))
    def __get_ip_bit_string(ip_string):
        ip_arr = __get_ip_array(ip_string)
        s = ""
        for i in ip_arr:
            s += __bin(i)
        return s

    ips = []
    ip_array = [i for i in __get_ip_bit_string(ip)]

    for i in range(len(ip_array) - cidr_value, len(ip_array)):
        ip_array[i] = '0'

    for i in range(2**cidr_value - 2):
        last = len(ip_array) - 1
        while ip_array[last] == '1':
            ip_array[last] = '0'
            last = last -1
        ip_array[last] = '1'
        ips.append(''.join(ip_array))
    return ips


cidr_value = get_cidr_value(netmask)
ips = generate_ip_address(ip_address, cidr_value)

confirmation = input("Sending "+str(2**cidr_value - 2)+" requests. To confirm(Enter y): ")

if confirmation == 'y' or confirmation == 'Y':
    arp_sender = ArpSender(local_mac, ips[0],ip_input='bin')
    for i in ips:
        arp_sender.target_ip = i
        arp_sender.process()
else:
    print("Aborted")