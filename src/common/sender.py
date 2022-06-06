import logging
import socket
import time
import threading


from common.file_reader import FileReader
from common.constants import SEC_BASE, MAX_RECV_BYTES, MAX_NACK, MAX_WINDOW, LOG_FORMAT,SYN,EOF

ERROR = -1
WINDOW_TIMEOUT = 0.5

class Sender:

    '''Implementation of sender'''

    def __init__(self, socket_address: tuple, file_path, file_name, udp_socket):
        self.socket = udp_socket
        self.socket_addr = socket_address
        self.base_num = SEC_BASE
        self.window_threads = {}
        self.file_reader = FileReader(file_path,file_name)
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        
    
    
    def receive_ack(self):
        '''Receives ackowledge packet'''
        
        data = -1
        timeout_counter = 0

        while timeout_counter < MAX_NACK and data == -1:
            try:
                data, address = self.socket.recvfrom(MAX_RECV_BYTES)
                return data
            except socket.timeout as _:
                logging.warning('Sender TIMEOUT')
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            return (0).to_bytes(2,'big')

        if self.socket_addr != address:
            self.socket_addr = address
        
        return data
        
    
    def repeat(self, socket_udp: socket, addr, packet):
        ''' Re send package if ACK has not been recieved yet'''

        thread = threading.currentThread()
        while getattr(thread, "do_run", True):
            try:
                _ = socket_udp.sendto(packet, addr)
                time.sleep(WINDOW_TIMEOUT)
            except OSError as _:
                thread.do_run = False
            

    def decode_packet(self,data):
        ''' Decode data in bytes to correct fields '''
        
        if len(data) <= 2:
            return ERROR,ERROR

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
    
        return moves
        
    def move_window(self,seq_num,buffer):
        '''Moves buffer window'''
        if seq_num == self.base_num:
                buffer.sort()
                move_foward = self.get_new_base_num(buffer=buffer)
                packets = self.file_reader.get_packets(move_foward, self.base_num + MAX_WINDOW - move_foward)
                

                for i,packet in enumerate(packets):
                    index = self.base_num + MAX_WINDOW - move_foward
                    self.window_threads[index + i] = threading.Thread(
                        target=self.repeat, args=[self.socket, self.socket_addr, packet])
                    self.window_threads[index + i].start()

    def wait_for_last_ack(self,buffer):

        while len(self.window_threads) > 0:
            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)

            if seq_num == -1:
                logging.info("Receiver timeout ERROR, cleaning window.")
                for _,thread in self.window_threads.items():
                    thread.do_run = False
                    thread.join()
                self.window_threads.clear()

            elif seq_num not in buffer:
                logging.info('ACK received: %s' % seq_num )

                buffer.append(seq_num)
                self.window_threads[seq_num].do_run = False
                self.window_threads[seq_num].join()
                self.window_threads.pop(seq_num)

        return seq_num

    def close_conection(self):
        ''' Send FIN package and waits for FIN package or disconnect by timeout '''
        fin_msg = (5).to_bytes(2,'big') + (SYN).to_bytes(2,'big') + (EOF).to_bytes(1,'big')
        self.socket.sendto(fin_msg,self.socket_addr)

        bytes_received = self.receive_ack()
        _, seq_num = self.decode_packet(bytes_received)
        
        if seq_num == 0:
            logging.info("FIN received, cleaning window.")
        else:
            logging.info("TIMEOUT on sending, cleaning window.")
    
    def start_sender_selective_repeat(self):
        '''Starts sender using selective repeat protocol'''

        buffer = []
        packets = self.file_reader.get_packets(MAX_WINDOW, 1)
        self.window_threads = self.init_thread_pool(packets=packets)
        
        bytes_received = self.receive_ack()
        _, seq_num = self.decode_packet(bytes_received)
        
        if seq_num == ERROR:
            return

        while not self.file_reader.eof():  
            logging.info('ACK received: %s' % seq_num )
           
            if seq_num >= self.base_num and seq_num not in buffer:
                logging.info('Mark thread: %s as acked' % seq_num)
                buffer.append(seq_num)
                self.window_threads[seq_num].do_run = False
                self.window_threads[seq_num].join()
                self.window_threads.pop(seq_num)

                self.move_window(seq_num,buffer)

            bytes_received = self.receive_ack()
            _, seq_num = self.decode_packet(bytes_received)
       
        if self.wait_for_last_ack(buffer) < 0:
            return

        self.close_conection()

        logging.info(' Sender finished.')


