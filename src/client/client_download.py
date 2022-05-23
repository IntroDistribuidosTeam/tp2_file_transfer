from socket import *

BUFF_SIZE = 1024
ACK = 1
NACK = 0
EOF = 1
NOT_EOF = 0

def write_file(file_name, pieces_received):
    with open(file_name, 'w') as file:
        for piece in pieces_received:
            file.write(piece)
    file.close()

def recv_piece(payload, pieces_received, count_pieces):
    if payload[0] == EOF:
        return NOT_EOF
    else: 
        pieces_received[count_pieces]
        count_pieces += 1
        return EOF

def recv_first_piece(client_socket, pieces_received, count_pieces):
    bytes_recibed, server_addr = client_socket.recvfrom(BUFF_SIZE)
    return recv_piece(bytes_recibed.decode() , pieces_received, count_pieces)

def send_message(client_socket, request, server_addr):
        client_socket.sendto(request.encode(),server_addr)
        bytes_recibed, server_addr = client_socket.recvfrom(BUFF_SIZE)
        return bytes_recibed.decode()

def download_file(client, file_name, addr, logger):
    msg = 'd' + '/' + file_name

    ack = send_message(client, msg, addr)
    if ack ==  FileNotFoundError:
        logger.error(f"The file {file_name} was not found")
        return
    
    # Stop and wait protocol
    while ack == NACK:
        ack = send_message(client, msg, addr)
        
    pieces_received = []
    count_files = 0
    eof = recv_first_piece(client, pieces_received, count_files)

    while eof == NOT_EOF:
        payload = send_message(client, msg, addr)
        # Stop and wait protocol
        while payload == NACK:
            payload = send_message(client, msg, addr)
        eof = recv_piece(payload, pieces_received, count_files)
    
    write_file()
    logger.info("File downloaded")
    client.close()
        
   

        

    

