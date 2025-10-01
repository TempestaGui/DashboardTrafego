import types
from app.utils.protocols import proto_of_packet

def make_pkt(**kwargs):
    return types.SimpleNamespace(**kwargs)

def test_proto_tcp():
    assert proto_of_packet(make_pkt(tcp=True)) == "TCP"

def test_proto_udp():
    assert proto_of_packet(make_pkt(udp=True)) == "UDP"

def test_proto_icmp():
    assert proto_of_packet(make_pkt(icmp=True)) == "ICMP"

def test_proto_icmpv6():
    assert proto_of_packet(make_pkt(icmpv6=True)) == "ICMP"

def test_proto_other():
    assert proto_of_packet(make_pkt()) == "OTHER"
