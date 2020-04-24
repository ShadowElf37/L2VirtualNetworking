IGNORE = 0

class EtherType:
    eth = 0x0000
    ipv4 = 0x0800
    arp = 0x0806

class addresses:
    broadcast = 0xffffffffffff

class ICMP:
    echo2 = echo_rep = 0
    echo1 = echo_req = 8
    unreachable = 3
    redirect = 5
    test = 7
    router_advert = 9
    router_discov = 10
    ttl_exp = 11
    timestamp1 = ts_req = 13
    timestamp2 = ts_rep = 14

class IPPROTO:
    icmp = 0x01
    igmp = 0x02
    ip_in_ip = 0x04
    tcp = 0x06
    udp = 0x11
    internal = 0x3d
    misc = 0x90