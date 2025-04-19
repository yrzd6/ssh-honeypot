import socket
import threading
from config import load_config
from output import Output
from server import handle_connection
from utils import send_log

def main():

    send_log("#", "Starting SSH Honeypot...")
    send_log("@", "By yrzd6")

    config, rsa_key = load_config()
    output = Output(config)

    PORT = int(config['settings']['port'])
    host = "0.0.0.0"

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, PORT))
    server_sock.listen(100)
    server_sock.settimeout(0.5)
    output.startup(host, PORT)

    try:
        send_log("#", "Starting server...")
        while True:
            try:
                client_sock, client_addr = server_sock.accept()
                threading.Thread(
                    target=handle_connection,
                    args=(client_sock, client_addr, config, rsa_key, output),
                    daemon=True
                ).start()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        output.shutdown_server()
    finally:
        server_sock.close()

if __name__ == "__main__":
    main()