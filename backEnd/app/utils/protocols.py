# Identifica protocolo do pacote:
# - retorna TCP, UDP, ICMP ou OTHER

def proto_of_packet(pkt):
    if hasattr(pkt, "tcp"): return "TCP"
    if hasattr(pkt, "udp"): return "UDP"
    if hasattr(pkt, "icmp") or hasattr(pkt, "icmpv6"): return "ICMP"
    return "OTHER"
