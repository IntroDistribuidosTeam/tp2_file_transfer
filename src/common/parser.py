import argparse


def parse_client_upload_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-H",
        "--server-host",
        default="127.0.0.1",
        help="Dirección IP del servidor",
    )
    parser.add_argument(
        "-P",
        "--server-port",
        type=int,
        default=4444,
        help="Puerto usado por el servidor",
    )
    parser.add_argument(
        "-s",
        "--src",
        help="Path del archivo a enviar al servidor",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--name",
        help="Nombre que tendra el archivo en el servidor",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Logueo verbose",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Logeo quiet",
    )

    return parser.parse_args()


def parse_client_download_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-H",
        "--server-host",
        default="127.0.0.1",
        help="Dirección IP del servidor",
    )
    parser.add_argument(
        "-P",
        "--server-port",
        type=int,
        default=4444,
        help="Puerto usado por el servidor",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="Nombre del archivo a descargar",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dst",
        help="Path destino para la descarga del archivo",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Logeo verbose",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Logeo quiet",
    )

    return parser.parse_args()


def parse_server_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-H",
        "--own-host",
        default="127.0.0.1",
        help="Direccion IP del servidor",
    )
    parser.add_argument(
        "-P",
        "--own-port",
        type=int,
        default=4444,
        help="Puerto donde el servidor estara escuchando",
    )
    parser.add_argument(
        "-s",
        "--storage-dir",
        help="Directorio donde se almacenaran los archivos",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Logeo verbose",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Logeo quiet",
    )
    return parser.parse_args()