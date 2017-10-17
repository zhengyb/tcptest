#!/bin/python

import socket
import sys
import time


def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(10)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            time.sleep(2)            
            # Receive the data in small chunks and retransmit it
            while True:
                data = '0123456789'
                connection.sendall(data)
                print('send %d bytes' % len(data))
                string_received = ''
                amount_received = 0
                amount_expected = len(data)

                while amount_received < amount_expected:
                    rdata = sock.recv(16)
                    string_received += rdata
                    amount_received += len(rdata)
                    print('received "%s"' % rdata)

                print('received %d bytes' % amount_received)

        finally:
            # Clean up the connection
            connection.close()

if __name__ == '__main__':
    main()
