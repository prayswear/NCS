import socket
import threading
import logging.config
import binascii
from protocol.icn_head import ICNPacket
from util.db_tool import myDB
from util import hash
from util.util import int2byte

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("myLogger")

class NcsServer():

    def __init__(self,address,port):
        self.UDP_MTU = 1024
        self.address=address
        self.port=port

    def initDB(self,address,port,db_name,tbl_name):
        self.db_address=address
        self.db_port=port
        self.db_name=db_name
        self.tbl_name=tbl_name
        self.ncsdb=myDB(self.db_address,self.db_port,self.db_name)


    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.address,self.port))
        logger.info("NCS Server started...")
        while True:
            logger.info("Waiting for packet...")
            data, address = server_socket.recvfrom(self.UDP_MTU)
            logger.info("Recieve an UDP packet from " + str(address))
            logger.info(data)
            threading._start_new_thread(self.request_handler, (data, address))

    def request_handler(self,data,address):
        packet=ICNPacket()
        packet.byte2icn(data)
        payload=packet.payload
        cmd_type=int(binascii.b2a_hex(payload[:1]),16)
        reply=ICNPacket()
        reply.setHeader("c50000000000000000000000000000c5","d5700000000000000000000000000d57","00")
        if cmd_type==1:
            reply.setPayload(self.register(payload))
        elif cmd_type==3:
            reply.setPayload(self.query_eid(payload))
        elif cmd_type==5:
            reply.setPayload(self.query_hrn(payload))
        reply.fill_packet()
        reply.print_packet()
        self.send(reply,address)


    def register(self,data):
        hrn_len=int(binascii.b2a_hex(data[1:2]),16)
        hrn=data[2:2+hrn_len].decode("utf-8")
        eid=hash.generate_eid(hrn)
        result=self.ncsdb.query(self.tbl_name,{"EID":eid})
        if result==None:
            self.ncsdb.add(self.tbl_name,{"EID":eid,"HRN":hrn})
            payload=binascii.a2b_hex("02"+"01"+eid)
        else:
            payload = binascii.a2b_hex("02"+"02"+"00000000000000000000000000000000")
        return payload

    def query_eid(self,data):
        hrn_len=int(binascii.b2a_hex(data[1:2]),16)
        hrn=data[2:2+hrn_len].decode("utf-8")
        result=self.ncsdb.query(self.tbl_name,{"HRN":hrn})
        if result==None:
            payload = binascii.a2b_hex("04"+"02"+"00000000000000000000000000000000")
        else:
            payload = binascii.a2b_hex("04"+"01" + result["EID"])
        return payload

    def query_hrn(self,data):
        eid=binascii.b2a_hex(data[1:17]).decode("utf-8")
        result=self.ncsdb.query(self.tbl_name,{"EID":eid})
        if result==None:
            payload = binascii.a2b_hex("06"+"02"+"00")
        else:
            hrn=result["HRN"].encode("utf-8")
            hrn_len=len(hrn)
            payload = binascii.a2b_hex("06"+"01") +binascii.a2b_hex(int2byte(hrn_len, 8)) + hrn
        return payload

    def send(self,packet,address):
        data = packet.icn2byte()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, address)
        sock.close()

if __name__ == '__main__':
    ncs_ip, ncs_port = '127.0.0.1', 22700
    db_ip, db_port = '127.0.0.1', 27017
    db_name="ncs"
    tbl_name="NCS_tbl"
    server=NcsServer(ncs_ip,ncs_port)
    server.initDB(db_ip,db_port,db_name,tbl_name)
    # server.ncsdb.remove_all(tbl_name)
    server.start()
