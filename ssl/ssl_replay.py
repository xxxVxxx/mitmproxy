#!/usr/bin/env python2
'''
Replay server for SSL-encrytped raw TCP connections running over port 443.
See --help for usage.
'''

from twisted.internet import reactor, ssl
import Queue
import sys
import os

sys.path.append('../lib')
import mitmproxy


def main():
    '''
    Parse options, open and read log file, start replay server
    '''
    (opts, _) = mitmproxy.replay_option_parser(4443)

    if not os.path.exists('keys/server.key') \
    or not os.path.exists('keys/server.crt'):
        print "Please do create server certificates."
        sys.exit(1)

    if opts.inputfile is None:
        print "Need to specify an input file."
        sys.exit(1)
    else:
        log = mitmproxy.Logger()
        if opts.logfile is not None:
            log.open_log(opts.logfile)

        serverq = Queue.Queue()
        clientq = Queue.Queue()
        clientfirst = None

        mitmproxy.logreader(opts.inputfile, serverq, clientq, clientfirst)

        sys.stderr.write(
            'Server running on localhost:%d\n' % opts.localport)
        factory = mitmproxy.ReplayServerFactory(
            log, (serverq, clientq), opts.delaymod, clientfirst)
        reactor.listenSSL(opts.localport, factory,
            ssl.DefaultOpenSSLContextFactory(
                'keys/server.key', 'keys/server.crt'))
        reactor.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
