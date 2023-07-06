def bin_8_bit(n):
    return "{0:08b}".format(n)

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder="big")

def get_ip_bit_string(ip_string):
    def __get_ip_array(ip_s):
        return list(map(int, ip_s.split(".")))
    
    ip_arr = __get_ip_array(ip_string)
    s = ""
    for i in ip_arr:
        s += bin_8_bit(i)
    return s

def get_hex_string(hex_s):
    arr = hex_s.split(":")
    s = ""
    for i in arr:
        s += bin_8_bit(int(i, 16))
    return s

def get_ip_from_bits(bits):
    ip = []
    for i in range(0,32,8):
        val = int(bits[i:i+8], base=2)
        ip.append(str(val))
    return ".".join(ip)