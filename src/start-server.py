import logging
from common.parser import parse_server_arguments
from server import *
from server.server import start_server

def main():
    args = parse_server_arguments()

    addr = (args.own_host, args.own_port)
    
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    print(args)

    start_server(addr,args.storage_dir)

if __name__ == "__main__":
    main()
