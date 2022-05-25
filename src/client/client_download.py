from socket import *

BUFF_SIZE = 1024
ACK = 1
NACK = 0
EOF = 1
NOT_EOF = 0
MODE_WRITE = "w"
MODE_ADD = "a"
DOWNLOAD = 'd'
DELIMITER = '/'

def write_piece(file_name, mode, piece, count_pieces, logger):
    try: 
        with open(file_name, mode) as file:
            file.write(piece)
            logger.info("Piece {} downloaded".fotmat(count_pieces))
    except Exception:
        logger.error("Error: Piece {} could not be downloaded".fotmat(count_pieces))    

def recv_piece(payload, count_pieces):
    if payload[0] == EOF:
        return EOF, NACK, ""
    else:
        count_pieces += 1
        return NOT_EOF, ACK, payload[2:]

# Falta implementar la parte del Checksum 
def are_corrupted(bytes):
    return False

def recv_first_piece(client_socket, pieces_received, count_pieces, response):
    bytes_recibed, addr = client_socket.recvfrom(BUFF_SIZE)
    if are_corrupted(bytes_recibed):
        response = NACK
    return recv_piece(bytes_recibed.decode(), pieces_received, count_pieces, response)

def send_message(client_socket, msg, addr, logger):
    bytes_sended = client_socket.sendto(msg.encode(),addr)
    if bytes_sended == len(msg):
        bytes_recibed, addr = client_socket.recvfrom(BUFF_SIZE)
        return bytes_recibed.decode()
    else: 
        logger.error("Error: Could not send message: {}".format(msg))

def download_file(client, file_name, addr, logger):
    request = DOWNLOAD + DELIMITER + file_name
    ack = send_message(client, request, addr)
    
    while ack == NACK:
        ack = send_message(client, request, addr)
        
    count_pieces = 0
    eof, response, piece = recv_first_piece(client, piece, count_pieces, response)

    while eof == NOT_EOF:
        payload = send_message(client, ACK, addr)
        eof, response, piece = recv_piece(payload, piece, count_pieces, response)
        
        if count_pieces == 1:
            write_piece(file_name, MODE_WRITE, piece, count_pieces, logger)
        write_piece(file_name, MODE_ADD, piece, count_pieces, logger)

    logger.info("File {} downloaded")
    client.close()


    

