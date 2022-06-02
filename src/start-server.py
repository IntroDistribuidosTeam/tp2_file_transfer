import logging
from common.parser import parse_server_arguments
from server.server import Server
import os

def main():
    args = parse_server_arguments()
    addr = (args.own_host, args.own_port)

    print("args passed: host: %s port: %s",args.own_host, args.own_port)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    if not os.path.exists(args.storage_dir):
        logging.error('Dir does not exist')
        return

    server = Server(addr, args.storage_dir)
    server.start_server()

if __name__ == "__main__":
    main()
