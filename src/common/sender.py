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
                return data
            except socket.timeout as _:
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            return (0).to_bytes(2,'big')

        if self.socket_addr != address:
            self.socket_addr = address
        
        return data
        
    
    def repeat(self, socket_udp: socket, addr, packet):
        ''' Re send package if ACK has not been recieved yet'''
 
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            _ = socket_udp.sendto(packet, addr)
            time.sleep(0.5)

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
        for i,packet in enumerate(packets):
            threads[i+1] = threading.Thread(target=self.repeat,
                                           args=[self.socket, self.socket_addr, packet])
            threads[i+ 1].start()
        return threads


    def get_new_base_num(self, buffer):
        ''' Calculates new base num from ordered buffer'''
        i = buffer.index(self.base_num)
        keep = True
        while keep and i < (len(buffer) - 1):
            if (buffer[i] + 1) < (buffer[i+1]):
                keep = False
            else:
                i += 1
        moves = buffer[i] + 1 - self.base_num
        self.base_num = buffer[i] + 1
        print(moves)
        return moves
        
    def move_window(self,seq_num,buffer):
        '''Moves buffer window'''
        if seq_num == self.base_num:
                buffer.sort()
                move_foward = self.get_new_base_num(buffer=buffer)
                packets = self.file_reader.get_packets(move_foward, self.base_num + MAX_WINDOW - move_foward)
                logging.info('Moving window %s stepts'% move_foward)
                for i,packet in enumerate(packets):
                    index = self.base_num + MAX_WINDOW - move_foward 
                    self.window_threads[index + i] = threading.Thread(
                        target=self.repeat, args=[self.socket, self.socket_addr, packet])
                    self.window_threads[index + i].start()
                    

    def start_sender_selective_repeat(self):
        '''Starts sender using selective repeat protocol'''
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        
        buffer = []
        packets = self.file_reader.get_packets(MAX_WINDOW, 1)
        self.window_threads = self.init_thread_pool(packets=packets)
        
        logging.info('sender listo')
        bytes_received = self.receive_ack()
        _, seq_num = self.decode_packet(bytes_received)
        
        if seq_num == -1:
            logging.info('No nos pudimos conectar correctamente')
            return

        while not self.file_reader.eof():    
            logging.info('recibi ack: %s' % seq_num )
            print(self.window_threads)
           
            if seq_num >= self.base_num and seq_num not in buffer:
                logging.info('ACK: %s' % seq_num)
                logging.info('Deleating thread: %s' % seq_num)
                buffer.append(seq_num)
                self.window_threads[seq_num].do_run = False
                self.window_threads[seq_num].join()
                self.window_threads.pop(seq_num)
                self.move_window(seq_num,buffer)

            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)
       
        logging.info('sender salio del primer while')
        while len(self.window_threads) > 0:
            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)
            if seq_num == -1:
                break
            if seq_num not in buffer:
                buffer.append(seq_num)
                self.window_threads[seq_num].do_run = False
                self.window_threads[seq_num].join()
                self.window_threads.pop(seq_num)
        
        logging.info("File sent, cleaning window.")
        self.window_threads.clear()

    def send_package(self, response):
        ''' Attemps to send the response for max_nack times'''

        res = self.socket.sendto(response, self.socket_addr)

        return res
