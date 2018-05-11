from service.ncs_server import *


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

if __name__ == '__main__':
    ncs_ip, ncs_port = '127.0.0.1', 22700
    db_ip, db_port = '127.0.0.1', 27017
    db_name="ncs"
    tbl_name="NCS_tbl"
    server=NcsServer(ncs_ip,ncs_port)
    server.initDB(db_ip,db_port,db_name,tbl_name)
    # server.ncsdb.remove_all(tbl_name)
    server.start()