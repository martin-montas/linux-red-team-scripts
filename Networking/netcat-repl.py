#!          /usr/bin/python3

"""
                   Networking/netcat-repl.py

                 this is a simple netcat replacement for when you
                 are in a server where netcat is not available and
                 you need to quickly transfer a file to your own 
                 computer or viceversa.

                 written by: martin-montas with the help of chatgpt 
"""

import socket

# import sys
import argparse
import threading


def handle_client(client_socket):
    with client_socket:
        with open("received_file.txt", "wb") as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
    print("File received and saved as 'received_file.txt'.")


def start_server(host="127.0.0.1", port=1234):
    """
    here we start the server
    we assume that the server is listening
    on the port specified.
    we also assume that the server is
    running on the host specified.
    """
    print("[*] Starting server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    print(f"[*] Listening on {host}:{port}...")
    server_socket.listen(1)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection from {client_address} has been established.")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


def send_file_to_server(file_path, host="127.0.0.1", port=1234):
    """
    here we send the file to the server.
    we assume that the server is listening
    on the port specified.

    the file is sent in chunks of 1024 bytes
    """
    print(f"[*] Sending file {file_path} to server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    with open(file_path, "rb") as f:
        while chunk := f.read(1024):
            client_socket.sendall(chunk)
    client_socket.close()
    print(f"[+] File {file_path} sent to {host}:{port}.")


def main():
    """
    here the argparse options are defined
    along with other things like the main
    logic of the program.

    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--listen", "-l", action="store_true", help="upload/listen to on a port."
    )
    parser.add_argument(
        "--upload", "-u", action="store_true", help="upload option to send. "
    )
    parser.add_argument(
        "--port", "-p", type=int, help="port to upload/listen for a file."
    )
    parser.add_argument(
        "--file", "-f", type=str, help="file/binary to send (please enter full path)."
    )
    parser.add_argument(
        "--host", "-o", type=str, help="the IP address for the operation."
    )

    args = parser.parse_args()

    # sets the listen mode:
    if args.listen:
        if not args.port:
            args.port = 1234
        if not args.host:
            args.host = "127.0.0.1"
        start_server(args.host, args.port)

    # sets the upload mode:
    if args.upload:
        if not args.port:
            args.port = 1234
        if not args.host:
            args.host = "127.0.0.1"
        send_file_to_server(args.file, args.host, args.port)


if __name__ == "__main__":
    main()
