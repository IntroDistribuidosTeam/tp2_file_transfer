import socket
import logging
from common.constants import ACK_LEN, MAX_NACK, MAX_RECV_BYTES, ACK, FILE_PROBLEM

# inicia la comunicacion
class Handshake:

    '''Implements client-server connection stablishment'''

    def __init__(self,upd_socket:socket, addr: tuple):
        self.socket = upd_socket
        self.socket_addr = addr

    def receive_ack(self,msg):
        '''handles ack '''
        attempts = 0
        data = -1
        address = self.socket_addr
        while attempts < MAX_NACK and data == -1:
            try:
                data, address = self.socket.recvfrom(MAX_RECV_BYTES)

            except socket.timeout as _:

                self.socket.sendto(msg, self.socket_addr)


                attempts += 1

        if attempts == MAX_NACK:
            return -1, address

        if int.from_bytes(data[2:], 'big') == FILE_PROBLEM:
            return FILE_PROBLEM, self.socket_addr


        return int.from_bytes(data[2:], 'big'), address

    def client_handshake(self, msg):
        '''client Handshake'''
        seq_num = 0
        new_addr = self.socket_addr
        while seq_num != ACK and seq_num != FILE_PROBLEM:
            self.socket.sendto(msg, self.socket_addr)
            seq_num, new_addr = self.receive_ack(msg)
            if seq_num == -1 or seq_num == FILE_PROBLEM:
                new_addr = self.socket_addr

        return new_addr

    def server_handshake(self):
        ''' Server handshake side'''
        logging.info("New socket listing at: %s",self.socket.getsockname())

        ack_package = (ACK_LEN).to_bytes(2, 'big') + ACK.to_bytes(2, 'big')

        res = self.socket.sendto(ack_package, self.socket_addr)
        while res != ACK_LEN:
            logging.error("Coudn't sent ACK to: %s ", self.socket_addr)
            res = self.socket.sendto(ack_package, self.socket_addr)