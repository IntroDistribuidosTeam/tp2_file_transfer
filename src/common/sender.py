import logging
import socket
import time
import threading
from common.file_reader import FileReader
from common.constants import ACK, SEC_BASE, MAX_RECV_BYTES, MAX_NACK, MAX_WINDOW, LOG_FORMAT


class Sender:

    '''Implementation of sender'''

    def __init__(self, socket_address: tuple, file_path, file_name, udp_socket):
        self.socket = udp_socket
        self.socket_addr = socket_address
        self.base_num = SEC_BASE
        self.window_threads = {}
        self.file_reader = FileReader(file_path,file_name)
    
    
    def receive_ack(self):
        '''Receives ackowledge packet'''
        
        data = -1
        timeout_counter = 0

        while timeout_counter < MAX_NACK and data == -1:
            try:
                data, address = self.socket.recvfrom(MAX_RECV_BYTES)
            except socket.timeout as _:
                self.send_package(self.last_packet_sent)
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            return (0).to_bytes(2,'big')

        if self.socket_addr != address:
            self.socket_addr = address
        return data
        
    
    def repeat(self, socket_udp: socket, addr, packet):
        ''' Re send package if ACK has not been recieved yet'''
 
        while True:
            time.sleep(5)
            _ = socket_udp.sendto(packet, addr)

    def decode_packet(self,data):
        ''' Decode data in bytes to correct fields '''
        
        if len(data) <= 2:
            return -1,-1

        length = int.from_bytes(data[:2],'big')
        seq_num = int.from_bytes(data[2:],'big')
        return length, seq_num
    
    def init_thread_pool(self, packets):
        ''' Initilices packet threads'''
        threads = {}
        for i in range(self.base_num, MAX_WINDOW + 1):
            threads[i] += threading.Thread(target=self.repeat,
                                           args=[self.socket, self.socket_addr, packets[i]])
        return threads


    def get_new_base_num(self, buffer):
        ''' Calculates new base num from ordered buffer'''
        i = 1
        keep = True
        while keep and i < len(buffer):
            if buffer[i] > (buffer[i-1]+1):
                keep = False

        self.base_num = (buffer[i-1]+1)
        return (i-1)
        
    def move_window(self,seq_num,buffer):
        '''Moves buffer window'''
        if seq_num == self.base_num:
                buffer.sort()
                move_foward = self.get_new_base_num(buffer=buffer)
                packets = self.file_reader.get_packets(move_foward, buffer[-1])

                for i in range(1, len(packets) + 1):
                    self.window_threads[buffer[-1] + i] += threading.Thread(
                        target=self.repeat, args=[self.socket, self.socket_addr, packets[i-1]])
                    buffer.pop(i-1)

    def start_sender_selective_repeat(self):
        '''Starts sender using selective repeat protocol'''
      
        buffer = []
        packets = self.file_reader.get_packets(MAX_WINDOW, self.base_num)
        self.window_threads = self.init_thread_pool(packets=packets)

        while not self.file_reader.end_of_file():

            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)
        
            buffer.append(seq_num)
            self.window_threads[seq_num].cancel()
            self.window_threads.pop(seq_num)
            self.move_window(seq_num,buffer)
        
        
        while len(self.window_threads) > 0:
            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)
            buffer.append(seq_num)
            self.window_threads[seq_num].cancel()
            self.window_threads.pop(seq_num)

        self.window_threads.clear()

    def send_package(self, response):
        ''' Attemps to send the response for max_nack times'''
        return self.socket.sendto(response, self.socket_addr)
    

    def start_sender_stop_and_wait(self):
        ''' Start sender stop and wait'''
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

        end_of_file = False
        eof_ack = False
        contador = 0
        self.last_seq_acked = 0
        self.expected_ack = 1

        payloads = self.file_reader.get_packets(1, self.expected_ack - 1)
        end_of_file = self.file_reader.eof()
        res = self.send_package(payloads[0])
        contador += 1

        self.last_packet_sent = payloads[0]
        while not end_of_file or not eof_ack:
            # si salta el timeout por parte de la lectura cierro socket
            # porque es responsabilidad del cliente de reenviarmelo por timeout
            
            packet = self.receive_ack()
            _, ack = self.decode_packet(packet)

            if  ack == -1:
                logging.error("TIMEOUT on reading, closing socket %s", self.socket_addr)
                end_of_file = True
                eof_ack = True
            elif self.expected_ack == ack:
                  
                if end_of_file:
                    logging.info("Last ACK recieved from %s", self.socket_addr)
                    eof_ack = True
                else:
                    logging.info("ACK recieved from %s", self.socket_addr)

                    self.last_seq_acked = self.expected_ack
                    self.expected_ack = (self.expected_ack + 1) % 2
                    payloads = self.file_reader.get_packets(1,self.expected_ack - 1)
                    res = self.send_package(payloads[0])
                    contador += 1
                    self.last_packet_sent = payloads[0]

                    end_of_file = self.file_reader.eof()

                    if res == -1:
                        end_of_file = True
                        eof_ack = True
                    else:
                        logging.info("PACKET sent to %s".format(self.socket_addr))

            elif self.last_seq_acked == ack:
                    res = self.send_package(self.last_packet_sent)



        logging.info("Socket closed.")