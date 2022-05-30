from operator import imod
import threading
import time
import socket
from os import stat, path
from file_reader import FileReader

WIN_SIZE = 4
SEC_BASE = 1
DELIMETER = '/'
MAX_RECV_BYTES = 2
TIME = 10
PAYLOAD_SIZE = 1021

# Sender
# Recibe los acks con numero de secuencia
# NOTE
# Ahora, nuestro ACK tiene un tam de 2 bytes
# Asi podremos tener hasta un sequence number de 65k


class Sender:

    def __init__(self, socket_address: tuple, file_path, file_name, socket):
        self.socket = socket
        self.window_size = WIN_SIZE
        self.base_num = SEC_BASE
        self.window_threads = {}
        self.socket_addr = socket_address
        self.file_reader = FileReader(file_path,file_name)
        

    def recieve_ack(self):
        data, address = self.socket.recvfrom(MAX_RECV_BYTES)

        if self.socket_addr != address:
            self.socket_addr = address

        return data.decode()

    def init_handshake(self, mode):
        msg = mode + DELIMETER + self.file_name
        seq_num = 1
        while seq_num != 0:
            bytes_sent = 0
            while bytes_sent != len(msg):
                bytes_sent += self.socket.sendto(
                    msg[bytes_sent:].encode(), self.socket_addr)
            seq_num = self.recieve_ack()

    def repeat(self, socket: socket, addr, packet):
        byte = 0
        while byte != len(packet):
            time.sleep(TIME)
            byte += socket.sendto(packet[byte:].encode(), addr)

    def init_thread_pool(self, packets):
        threads = {}
        for i in range(self.base_num, self.window_size + 1):
            threads[i] += threading.Thread(target=self.repeat,
                                           args=[self.socket, self.socket_addr, packets[i]])
        return threads


    def get_new_base_num(self, buffer):
        i = 1
        keep = True
        while keep and i < len(buffer):
            if buffer[i] > (buffer[i-1]+1):
                keep = False

        self.base_num = (buffer[i-1]+1)
        return (i-1)

    def start_sender(self):
        self.file_exist()
        buffer = []
        packets = self.get_packets(self.window_size, self.base_num)
        self.window_threads = self.init_thread_pool(packets=packets)

        while self.seek < self.file_size:

            seq_num = int(self.recieve_ack())
            buffer.append(seq_num)

            self.window_threads[seq_num].cancel()
            self.window_threads.pop(seq_num)

            if seq_num == self.base_num:
                buffer.sort()
                move_foward = self.get_new_base_num(buffer=buffer)
                packets = self.file_reader.get_packets(move_foward, buffer[-1])

                for i in range(1, len(packets + 1)):
                    self.window_threads[buffer[-1] + i] += threading.Thread(
                        target=self.repeat, args=[self.socket, self.socket_addr, packets[i-1]])

        while len(buffer) != 4:
            seq_num = int(self.recieve_ack())
            buffer.append(seq_num)
            self.window_threads[seq_num].cancel()

        self.window_threads.clear()

        self.socket.close()
