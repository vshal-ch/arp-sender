import socket
import netifaces
from net import ArpSender
from helpers.logger import info, log
from helpers.binary import get_ip_bit_string, get_ip_from_bits

addresses = netifaces.ifaddresses('wlp2s0')
netmask = addresses[netifaces.AF_INET][0]['netmask']
ip_address = socket.gethostbyname(socket.gethostname())
local_mac = "10:5b:ad:65:a4:75"

# this function takes netmask('255.255.255.0') as input and returns the cidr value(/8)
def get_cidr_value(netmask):
    info("Netmask: "+netmask)
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
    info("CIDR Value = "+str(cidr_value))
    return cidr_value

def generate_ip_address(ip, cidr_value):
    log("Generating IP addresses")
    ips = []
    ip_array = [i for i in get_ip_bit_string(ip)]

    for i in range(len(ip_array) - cidr_value, len(ip_array)):
        ip_array[i] = '0'

    for i in range(2**cidr_value - 2):
        last = len(ip_array) - 1
        while ip_array[last] == '1':
            ip_array[last] = '0'
            last = last -1
        ip_array[last] = '1'
        ips.append(''.join(ip_array))
    info("Generated IPs "+get_ip_from_bits(ips[0])+" ... "+get_ip_from_bits(ips[-1]))
    return ips

# def shift_first_100(ips):
#     new_arr = [None]*len(ips)
#     for i in range(100, len(ips)):
#         new_arr[i-100] = ips[i]
#     for i in range(100):
#         new_arr[i + len(ips)-101] = ips[i]
#     return new_arr

cidr_value = get_cidr_value(netmask)
ips = generate_ip_address(ip_address, cidr_value)

# ips = shift_first_100(ips)

confirmation = input("> Sending "+str(2**cidr_value - 2)+" requests. To confirm(Enter y): ")

successful_ips = []

if confirmation == 'y' or confirmation == 'Y':
    for i in ips:
        arp_sender = ArpSender(local_mac, i , ip_input='bin')
        result = arp_sender.process()
        if result:
            successful_ips.append(result)
    if len(successful_ips) ==0:
        info("No active hosts found!")
    else:
        output = ""
        for i in successful_ips:
            output += i[0] +": "+i[1] +"\t\n"
        info(output)
        
else:
    log("Aborted")