import socket

DELIMETER = '/'
MAX_RECV_BYTES = 2

# inicia la comunicacion
class Handshake:

    def __init__(self, mode, file_name, socket, addr: tuple):
        self.mode = mode
        self.file = file_name
        self.socket = socket
        self.socket_addr = addr

    def recieve_ack(self):
        data, address = self.socket.recvfrom(MAX_RECV_BYTES)

        if self.socket_addr != address:
            self.socket_addr = address

        return data.decode()

    def init_handshake(self):
        msg = self.mode + DELIMETER + self.file
        seq_num = 1
        while seq_num != 0:
            bytes_sent = 0
            while bytes_sent != len(msg):
                bytes_sent += self.socket.sendto(
                    msg[bytes_sent:].encode(), self.socket_addr)
            seq_num = self.recieve_ack()
