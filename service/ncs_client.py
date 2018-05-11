import socket
import logging.config
from protocol.icn_head import ICNPacket
import binascii
from util.util import int2byte

logging.config.fileConfig('../logging.conf')
logger = logging.getLogger('myLogger')


class NcsClient():

    def __init__(self, address, port):
        self.UDP_MTU = 1024
        self.ncs_address = address
        self.ncs_port = port

    def send(self, packet):
        data = packet.icn2byte()
        if len(data) > self.UDP_MTU:
            return None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (self.ncs_address, self.ncs_port))
        sock.settimeout(1)
        reply = None
        try:
            ack, remote_address = sock.recvfrom(self.UDP_MTU)
            print(ack)
            reply = ICNPacket()
            reply.byte2icn(ack)
            reply.print_packet()
        except socket.timeout:
            logger.error("Timeout")
        finally:
            sock.close()
        return reply

    def register(self, hrn):
        icn_packet = ICNPacket()
        icn_packet.setHeader("226cf119b78825f1720cf2ca485c2d85", "00000000000000000000000000000000", "00")
        cmd_type = binascii.a2b_hex("01")
        hrn_hex = hrn.encode("utf-8")
        print(hrn_hex)
        hrn_len = len(hrn_hex)
        icn_packet.setPayload(cmd_type + binascii.a2b_hex(int2byte(hrn_len, 8)) + hrn_hex)
        icn_packet.fill_packet()
        icn_packet.print_packet()
        reply = self.send(icn_packet)
        cmd_type=binascii.b2a_hex(reply.payload[:1])
        ack=binascii.b2a_hex(reply.payload[1:2])
        cmd_type=int(binascii.b2a_hex(reply.payload[:1]),16)
        ack=int(binascii.b2a_hex(reply.payload[1:2]),16)
        if cmd_type==2 and ack==1:
            eid=binascii.b2a_hex(reply.payload[2:18])
            return eid.decode("utf-8")
        else:
            return None

    def query_eid(self, hrn):
        icn_packet = ICNPacket()
        icn_packet.setHeader("226cf119b78825f1720cf2ca485c2d85", "00000000000000000000000000000000", "00")
        cmd_type = binascii.a2b_hex("03")
        hrn_hex = hrn.encode("utf-8")
        hrn_len = len(hrn_hex)
        icn_packet.setPayload(cmd_type + binascii.a2b_hex(int2byte(hrn_len, 8)) + hrn_hex)
        icn_packet.fill_packet()
        reply = self.send(icn_packet)
        cmd_type=int(binascii.b2a_hex(reply.payload[:1]),16)
        ack=int(binascii.b2a_hex(reply.payload[1:2]),16)
        if cmd_type==4 and ack==1:
            eid=binascii.b2a_hex(reply.payload[2:18])
            return eid.decode("utf-8")
        else:
            return None

    def query_hrn(self, eid):
        icn_packet = ICNPacket()
        icn_packet.setHeader("226cf119b78825f1720cf2ca485c2d85", "00000000000000000000000000000000", "00")
        cmd_type = binascii.a2b_hex("05")
        hrn_hex = binascii.a2b_hex(eid)
        icn_packet.setPayload(cmd_type + hrn_hex)
        icn_packet.fill_packet()
        reply = self.send(icn_packet)
        cmd_type=int(binascii.b2a_hex(reply.payload[:1]),16)
        ack=int(binascii.b2a_hex(reply.payload[1:2]),16)
        if cmd_type==6 and ack==1:
            hrn_len=int(binascii.b2a_hex(reply.payload[2:3]),16)
            hrn=reply.payload[3:3+hrn_len].decode("utf-8")
            return hrn
        else:
            return None


if __name__ == "__main__":
    ncs_address = "127.0.0.1"
    ncs_port = 22700
    client = NcsClient(ncs_address, ncs_port)

    # eid = client.register("lijq")
    result = client.query_eid("alijq2")
    # result = client.query_hrn("8d68b0cb795c0c6b8d483374c700ccc6")
    logging.info(result)
