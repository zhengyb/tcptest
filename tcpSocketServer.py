#!/usr/bin/env python
# -*- coding:utf-8 -*-
import SocketServer
import time
import string
import random
import sys
import logging
from logging.handlers import SysLogHandler

syslog_format = '%(filename)s[%(process)d]%(message)s'
debug_format = '%(asctime)s %(filename)s\t[line%(lineno)s]\t[%(levelname)s] %(message)s'


ch = None
fhs = None


def inLogSyslogConfig():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(syslog_format)
    sh = logging.handlers.SysLogHandler(address='/dev/log')
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger

logger = inLogSyslogConfig()


def inLogConsoleConfig(debug=False):
    global logger
    global ch
    if logger is None:
        inLogSyslogConfig()
    formatter = logging.Formatter(debug_format)
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    if ch is None:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)


def inLogFileConfig(logfilename=None, maxBytes=10 * 1024, backupCount=1, level=logging.DEBUG):
    global logger
    global fhs
    try:
        if logger is None:
            inLogSyslogConfig()
        formatter = logging.Formatter(debug_format)
        if logfilename is not None:
            if fhs is None:
                fhs = dict()
            if logfilename in fhs.keys():
                # remove the old handler
                fh = fhs[logfilename]
                logger.removeHandler(fh)
            if backupCount < 1:
                backupCount = 1
            fh = logging.handlers.RotatingFileHandler(
                logfilename, mode='a', maxBytes=maxBytes, backupCount=backupCount)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            fhs[logfilename] = fh
        else:
            # remove all file handlers
            for (key, fh) in fhs:
                logger.removeHandler(fh)
            fhs = None
    except Exception as exce:
        print("%s", exce)


class MyServer(SocketServer.BaseRequestHandler):

    def randomString(self, dataLength):
        baseString = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmkopqrstuvwxyz'
        # return string.join(random.sample(baseString, dataLength)).replace(' ', '')
        # for i in range(dataLength):
        return ''.join([random.choice(baseString) for _ in range(dataLength)]).replace(' ', '')

    def handle(self):
        conn = self.request
        print "Got connection from ", self.request.getpeername()
        conn.settimeout(5)

        min = 1
        max = 100
        method = 0
        try:
            rdata = conn.recv(100)
            if rdata[0:4] == 'cmd:':
                print('recv cmd: %s' % rdata[4:])
                logger.info('recv cmd: %s', rdata[4:])
                cmd = rdata[4:].split(',')
                minLength = string.atoi(cmd[0])
                maxLength = string.atoi(cmd[1])
                if minLength < 1:
                    minLength = 1
                if maxLength > 2000:
                    maxLength = 2000
                method = string.atoi(cmd[2])
        except Exception as e:
            logger.info(e.message)
            conn.close()
            logger.info('conn closed')

        time.sleep(2)

        endFail = False
        for dataLength in range(minLength, maxLength):
            if method == 1:
                data = self.randomString(dataLength)
            else:
                data = 'A' * dataLength

            amount_received = 0
            amount_expected = len(data)
            conn.sendall(data)
            logger.info('send data, %d bytes: %s%s', amount_expected, data[
                        0:10], '(trunced)' if len(data) > 10 else '')
            logger.debug('test %d bytes data: %s', amount_expected, data)
            try:
                rdata = conn.recv(2000)
                if len(rdata) < 0:
                    logger.info('recv error!!!!!')
                    logger.info.close()
                    logger.info('conn closed')
                    endFail = True
                elif len(rdata) == 0:
                    logger.info('timeout, no more data!!!!!')
                    logger.info.close()
                    logger.info('conn closed')
                    endFail = True
                    break
                elif len(rdata) < amount_expected:
                    logger.info(
                        'data truncted, only %d bytes received!!!!!' % len(rdata))
                    conn.close()
                    logger.info('conn closed')
                    endFail = True
                    break
                else:
                    logger.info('recv enough data, %d' % amount_expected)

                # time.sleep(1)
            except Exception as e:
                logger.info(e.message + "!!!!!")
                conn.close()
                logger.info('conn closed')
                endFail = True
                break

        if (endFail is not True):
            conn.sendall('exit')
            time.sleep(5)
            conn.close()
            logger.info('conn closed')


#class MyThreadingTCPServer(SocketServer.ThreadingTCPServer):
#    def server_bind(self):
#
#        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.socket.bind(self.server_address)

if __name__ == '__main__':
    server_addr = '127.0.0.1'
    server_port = 10000

    inLogFileConfig('./tcpserver.log', 10 * 1024 * 1024, 10)
    inLogConsoleConfig(False)

    if len(sys.argv) > 1:
        server_addr = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = string.aoti(sys.argv[2])

    print 'Run Tcp Server on ', (server_addr, server_port)
    logger.info('Run Tcp Server on (%s, %s)', server_addr, server_port)
    server = SocketServer.ThreadingTCPServer((server_addr, server_port), MyServer)
    #server = MyThreadingTCPServer((server_addr, server_port), MyServer)
    server.serve_forever()
