import logging
import os
from common.constants import NOT_EOF, MAX_WINDOW, MAX_NACK, BUFF_SIZE, NACK, DELIMETER
import socket


def recv_payload(socket: socket):
    timeout_counter = 0
    error_list = [-1,0,0]

    while timeout_counter < MAX_NACK:
        try: 
            bytes_recv, _ = socket.recvfrom(BUFF_SIZE)
        except TimeoutError as _:
            timeout_counter += 1

    if (timeout_counter == MAX_NACK):
        return error_list

    packet = bytes_recv.decode()
    packet_parts = packet.split(DELIMETER, 2)
    return packet_parts


def write_file(path,buff,recv_base,payload):
    with open(path, 'w', encoding="utf8") as file:
        file.write(payload)
        recv_base += 1
        while buff[recv_base] != None:
            file.write(buff[recv_base])
            buff.pop(recv_base,None)
            recv_base += 1

    return recv_base
   

def is_error(sequence_number):
    return (sequence_number == -1)


def send_ack(sequence_number, socket, addr):
    bytes_sent = socket.sendto(str(sequence_number).encode(), addr)

    while bytes_sent != sequence_number:
        bytes_sent = socket.sendto(str(sequence_number).encode(), addr)


def receiver(path,file_name,sender_addr,socket):
    eof = NOT_EOF
    error = False
    buff = {}
    recv_base = 0 #TODO: ver si arrancamos en 0 o en 1

    #payload =[seq/eof/payload]

    while eof == NOT_EOF and not error:
        packet = recv_payload(socket)
        sequence_number = packet[0]
        eof = packet[1]
        payload = packet[2]

        send_ack(sequence_number,socket, sender_addr)

        if is_error(sequence_number):
            os.remove(path)
            error = True
        else:
            if sequence_number == recv_base:
                recv_base = write_file(path,buff,recv_base,payload)
                if (recv_base > int((1 << 16) - 1)):#TODO: ver si arrancamos en 0 o en 1
                    recv_base = 0
            else: 
                buff[sequence_number] = payload
    
    if error:
        logging.info("Stopped receiving after repeated sequence of nacks")
        return
    logging.info("Finished uploading file %s from client %s",file_name, sender_addr)



