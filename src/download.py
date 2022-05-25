import logging
from common.parser import parse_client_download_arguments

def main():
    args = parse_client_download_arguments()

    addr = (args.server_host, args.server_port)
    
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)

    print(args)
    #RUN CLIENT
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    download_file(client, 'hola.txt', logger)

if __name__ == "__main__":
    main()
