import socket
import time
import threading
from file_reader import FileReader
from common.constants import SEC_BASE, MAX_RECV_BYTES, MAX_NACK, TIME,MAX_WINDOW


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
        
        data = 0
        timeout_counter = 0

        while timeout_counter < MAX_NACK and data == 0:
            try:
                data, address = self.socket.recvfrom(MAX_RECV_BYTES)
            except socket.timeout as _:
                timeout_counter += 1

        if self.socket_addr != address:
            self.socket_addr = address
        
        if timeout_counter == MAX_NACK:
            return (0).to_bytes(2,'big')
        
        return data
        
    
    def repeat(self, socket_udp: socket, addr, packet):
        ''' Re send package if ACK has not been recieved yet'''
 
        while True:
            time.sleep(TIME)
            _ = socket_udp.sendto(packet, addr)

    def decode_packet(self,data):
        ''' Decode data in bytes to correct fields '''
        
        if len(data) <= 2:
            return [-1] * 2

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