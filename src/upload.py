import logging
import os.path
import socket
from common.parser import parse_client_upload_arguments


PAYLOAD_SIZE = 1024

def wait_ack_loop(client):
    wait = True
    while wait:
        data, _ = client.recvfrom(1)
        if len(data) == 1:
            wait = False
    return data
      
def send_first_msg(client, file_name, addr):  
    msg = 'u' + '/' + file_name
    print(msg)
    client.sendto(msg.encode(), addr)
    ## espero ack
    #data = wait_ack_loop(client)
    #return data.decode()
    return 1

def upload_file(client, addr, file_src, file_name , logger):
    if not os.path.exists(file_src):
        logger.error(f"The file {file_src} does not exist")
        return
    logger.info("Sending file")
    file = open(file_src, "r", encoding="utf8")

    file_len = os.path.getsize(file_src)

    # envio el primer mensaje solo con el nombre hasta que tenga un ack = 1
    ack = 0
    while ack == 0:
        ack = send_first_msg(client, file_name, addr)

    # envio resto mensajes
    end = 1
    line = file.read(PAYLOAD_SIZE - 2)
    if file.tell() == file_len :
        end = 0
    msg = str(end) + '/'
    while line != '':
        ack = 0
        msg_send = msg + line
        print(msg_send)
        while ack == 0 :
            client.sendto(msg_send.encode(), addr)
            ack = wait_ack_loop(client)
        ## mensaje llego bien mando otro
        end = 1
        line = file.read(PAYLOAD_SIZE - 2)
        if file.tell() == file_len :
            end = 0
        msg = str(end) + '/'

    logger.info("File uploaded")
    file.close()
    client.close()

def main():
    args = parse_client_upload_arguments()

    addr = (args.server_host, args.server_port)
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)

    print(args)
    # RUN CLIENT
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    upload_file(client, addr, args.src, args.name, logger)

if __name__ == "__main__":
    main()
