import logging
import socket

from common.file_writer import FileWriter
from common.constants import BUFF_SIZE, EOF, MAX_NACK, ACK, MAX_WINDOW, NOT_EOF, SEC_BASE, ACK_LEN


SEQUENCE_NUMBER_BYTES = 2

class Receiver:

    '''Implementation of receiver'''

    def __init__(self, sender_addr: tuple, file_path, file_name, udp_socket):
        self.socket = udp_socket
        self.recv_base = SEC_BASE
        self.recv_buff = {}
        self.sender_addr = sender_addr
        self.file_writer = FileWriter(file_path, file_name)

    def recv_payload(self):
        ''' Returns bytes read from private socket '''
        timeout_counter = 0
        bytes_recv = 0

        while timeout_counter < MAX_NACK and bytes_recv == 0:
            try:
                bytes_recv, addr = self.socket.recvfrom(BUFF_SIZE)
                print('addr:',addr)
                return bytes_recv

            except socket.timeout as _:
                logging.info("TIMEOUT")
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            bytes_recv = (0).to_bytes(2,'big')

        return bytes_recv

    def write_file(self, payload):
        ''' Make file_writer writes payload'''

        chunk = payload
        logging.info('writing sequence number: %s'% self.recv_base)
        self.recv_base += 1

        while self.recv_base in self.recv_buff.keys():
            chunk += self.recv_buff[self.recv_base]
            self.recv_buff.pop(self.recv_base, None)
            logging.info('writing sequence number: %s'% self.recv_base)
            self.recv_base += 1
            
        self.file_writer.write(chunk)

    def is_error(self, sequence_number):
        ''' Checks for an error '''
        
        return (sequence_number == -1)

    def send_response(self, sequence_number):
        '''Sends ack for packet received'''
        response = (ACK_LEN).to_bytes(2, 'big') + sequence_number.to_bytes(2, 'big')
        bytes_sent = self.socket.sendto(response, self.sender_addr)

        return bytes_sent
        
    def decode_packet(self,bytes_recieved):
        ''' Make correct fields from bytes package'''
        print('bytes: received: ',len(bytes_recieved))
        if len(bytes_recieved) == 2:
            
            return [-1] * 4

        length = int.from_bytes(bytes_recieved[:2],'big')
        seq_num = int.from_bytes(bytes_recieved[2:4],'big')
        eof = int.from_bytes(bytes_recieved[4:5],'big')
        payload = bytes_recieved[5:]
        
        return seq_num, length, eof, payload
        
    def packet_in_window(self,sequence_number):
        max_possible_packets = self.recv_base + MAX_WINDOW - 1
        if self.recv_base <= sequence_number and sequence_number <= max_possible_packets:
            return True
        return False


    def manage_packet(self, sequence_number, payload):
        '''' Decides if the package has to be stored or wrote '''
        if sequence_number == self.recv_base:
            self.write_file(payload)

        elif self.packet_in_window(sequence_number) and (sequence_number not in self.recv_buff.keys()):
            self.recv_buff[sequence_number] = payload

    def start_receiver_selective_repeat(self):
        ''' Selective Repeat RTA'''

        eof = NOT_EOF
        error = False

        while eof == NOT_EOF or len(self.recv_buff) != 0:

            bytes_received = self.recv_payload()
            sequence_number, length, eof_received, payload = self.decode_packet(
                bytes_received)
            print('sequence_number:',sequence_number)

            if self.is_error(sequence_number):
                logging.error("ELIMINANDO EL ARCHIVO")
                self.file_writer.remove_path()
                error = True
                self.socket.close
                
                break
            elif len(bytes_received) == length:
                
                if eof_received == EOF:
                    eof = eof_received
                _ = self.send_response(sequence_number)

                if sequence_number >= self.recv_base:
                    self.manage_packet(sequence_number, payload)
        if error:
            logging.info("Stopped receiving packets due to error")
        else:
            logging.info("Finished uploading file {} from client {}".format(self.file_writer.get_filename(), self.sender_addr))



 