from service.ncs_client import *

logging.config.fileConfig('logging.conf')
logger=logging.getLogger('myLogger')

if __name__=='__main__':
    ncs_address = "192.168.150.241"
    ncs_port=22700
    client=NcsClient(ncs_address,ncs_port)
    result=client.query_eid("lijq")
    logging.info(result)
