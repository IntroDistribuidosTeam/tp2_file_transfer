from cmath import log
from distutils.log import info
import socket
import logging
from common.constants import ACK_LEN, BUFF_SIZE, MAX_RECV_BYTES, ACK,LOG_FORMAT, SYN,ATTEMPS

# inicia la comunicacion
class Handshake:

    '''Implements client-server connection stablishment'''

    def __init__(self,upd_socket:socket, addr: tuple):
        self.socket = upd_socket
        self.socket_addr = addr
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    def client_handshake_dos(self,msg):
        attemps = 0
        address = self.socket_addr
        while attemps < ATTEMPS:
            self.socket.sendto(msg, self.socket_addr)
            logging.info('Sent client request')
            try:
                data, address = self.socket.recvfrom(MAX_RECV_BYTES)
                attemps = ATTEMPS
            except socket.timeout as _:
                logging.warning('Hanshake timeout')
                attemps +=1
                data = (ACK_LEN).to_bytes(2,'big') + (ACK).to_bytes(2,'big')
        
        if int.from_bytes(data[2:],'big') == SYN:
            logging.info('SYN received from server socket')
            ack_package = (ACK_LEN).to_bytes(2, 'big') + SYN.to_bytes(2, 'big')
            self.socket.sendto(ack_package, address)
            return data, address

        return data,address
        

    def server_handshake(self,mode):
        ''' Server handshake side'''
        logging.info("New socket listing at: %s" ,self.socket.getsockname())

        ack_package = (ACK_LEN).to_bytes(2, 'big') + SYN.to_bytes(2, 'big')
        _ = self.socket.sendto(ack_package, self.socket_addr)

        attemps = 0
        while attemps  < ATTEMPS:
            try:
                logging.info('Socket waiting for syn ack')
                data, _ = self.socket.recvfrom(BUFF_SIZE)
 
                if int.from_bytes(data[2:4],'big') == SYN and len(data) == ACK_LEN:
                    logging.info('Received expected mode code')
                    return 0
                else:
                    logging.warning('Received unexpected mode code')
                    attemps +=1
            except socket.timeout as _:
                logging.error('Socket timeout')
                attemps +=1
        
        return -1