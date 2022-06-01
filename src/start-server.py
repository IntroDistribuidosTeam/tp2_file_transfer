import logging
from common.parser import parse_server_arguments
import server.server as server

def main():
    args = parse_server_arguments()
    addr = (args.own_host, args.own_port)

    print("args passed: host: %s port: %s",args.own_host, args.own_port)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    print(args)

    server.start_server(addr,args.storage_dir)

if __name__ == "__main__":
    main()
