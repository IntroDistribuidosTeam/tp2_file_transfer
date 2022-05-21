import logging
from common.parser import parse_client_upload_arguments


def main():
    args = parse_client_upload_arguments()

    addr = (args.server_host, args.server_port)
    
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    print(args)

    # RUN CLIENT

if __name__ == "__main__":
    main()
