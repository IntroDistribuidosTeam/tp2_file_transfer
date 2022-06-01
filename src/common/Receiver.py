import logging
import os
from common.constants import NOT_EOF, MAX_WINDOW, MAX_NACK, BUFF_SIZE, NACK, DELIMETER
import socket
import FileWriter

class Receiver:

    def __init__(self, sender_addr: tuple, file_path, file_name, socket):
        self.socket = socket
        self.window_size = MAX_WINDOW
        self.recv_base = 0 #TODO: ver si arrancamos en 0 o en 1
        self.recv_buff = {}
        self.sender_addr = sender_addr
        self.file_writer = FileWriter(file_path,file_name)
        self.file_path = file_path

    def recv_payload(self):
        timeout_counter = 0
        error_list = [-1,0,0]

        while timeout_counter < MAX_NACK:
            try: 
                bytes_recv, _ = self.socket.recvfrom(BUFF_SIZE)
            except TimeoutError as _:
                timeout_counter += 1

        if (timeout_counter == MAX_NACK):
            return error_list

        packet = bytes_recv.decode()
        packet_parts = packet.split(DELIMETER, 2)
        return packet_parts


    def write_file(self,payload):
        chunk = payload
        #self.file_writer.write(payload)
        self.recv_base += 1

        while self.recv_buff[self.recv_base] != None:
            #self.file_writer.write(self.recv_buff[self.recv_base])
            chunk += self.recv_buff[self.recv_base]
            self.recv_buff.pop(self.recv_base,None)
            self.recv_base += 1

        self.file_writer(chunk)
    

    

    def is_error(sequence_number):
        return (sequence_number == -1)


    def send_ack(self,sequence_number):
        bytes_sent = socket.sendto(str(sequence_number).encode(), self.sender_addr)

        while bytes_sent != sequence_number:
            bytes_sent = socket.sendto(str(sequence_number).encode(), self.sender_addr)


    def receive(self,file_name):
        eof = NOT_EOF
        error = False
        #payload =[seq/eof/payload]

        while eof == NOT_EOF and not error:
            packet = self.recv_payload()
            sequence_number = packet[0]
            eof = packet[1]
            payload = packet[2]

            self.send_ack(sequence_number)

            if self.is_error(sequence_number):
                os.remove(self.file_path)
                error = True
            else:
                if sequence_number == self.recv_base:
                    self.write_file(payload)
                    if (self.recv_base > int((1 << 16) - 1)):#TODO: ver si arrancamos en 0 o en 1
                        self.recv_base = 0
                else: 
                    self.recv_buff[sequence_number] = payload
        
        if error:
            logging.info("Stopped receiving after repeated sequence of nacks")
            return
        logging.info("Finished uploading file %s from client %s",file_name, self.sender_addr)



