#!/bin/python

import socket
import sys


def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    sock.settimeout(30)
    sock.sendall('cmd:1,1501,1')

    lastLength = 0
    while True:
        try:
            data = sock.recv(2000)
            if ('exit' in data) or (len(data) == 0):
                print('Last length data recv: %d' % lastLength)
                sock.close()
                print('conn closed')
                break
            elif len(data) > 0:
                print('recv %d bytes.' % len(data))
                if len(data) < 100:
                    sock.sendall(data)
                lastLength = len(data)
        except e:
            print e.message
            sock.close()
            print('conn closed')

if __name__ == '__main__':
    main()
