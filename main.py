from net import ArpSender

local_mac = "10:5b:ad:65:a4:75"
target_ip = input("> Enter target IP: ")

arp_sender = ArpSender(local_mac, target_ip)
arp_sender.process()
