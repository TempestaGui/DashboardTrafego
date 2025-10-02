import types
from app.utils.protocols import proto_of_packet

# Função auxiliar para criar pacotes fictícios com atributos dinâmicos
def make_pkt(**kwargs):
    return types.SimpleNamespace(**kwargs)

# Testa se a função identifica corretamente pacotes TCP
def test_proto_tcp():
    assert proto_of_packet(make_pkt(tcp=True)) == "TCP"

# Testa se a função identifica corretamente pacotes UDP
def test_proto_udp():
    assert proto_of_packet(make_pkt(udp=True)) == "UDP"

# Testa se a função identifica corretamente pacotes ICMP (IPv4)
def test_proto_icmp():
    assert proto_of_packet(make_pkt(icmp=True)) == "ICMP"

# Testa se a função identifica corretamente pacotes ICMPv6
def test_proto_icmpv6():
    assert proto_of_packet(make_pkt(icmpv6=True)) == "ICMP"

# Testa o caso padrão: pacote sem protocolos reconhecidos
def test_proto_other():
    assert proto_of_packet(make_pkt()) == "OTHER"
