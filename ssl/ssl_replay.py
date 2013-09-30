#!/usr/bin/env python2.7
'''
Replay server for SSL-encrytped raw TCP connections running over port 443.
See --help for usage.

Assumptions:
  * client ALWAYS talks first (sends ClientHello message)
'''

from twisted.internet import reactor
import Queue
import sys

sys.path.append('../lib')
import mitmproxy


def main():
    parsed = mitmproxy.ReplayOptionParser(4443)

    if parsed.opts.inputFile is None:
        print "Need to specify an input file."
        sys.exit(1)
    else:
        log = mitmproxy.Logger()
        if parsed.opts.logFile is not None:
            log.openLog(parsed.opts.logFile)

        sq = Queue.Queue()
        cq = Queue.Queue()

        mitmproxy.LogReader(parsed.opts.inputFile, sq, cq)

        sys.stderr.write(
            'Server running on localhost:%d\n' % parsed.opts.localPort)
        factory = mitmproxy.ReplayServerFactory(
            log, sq, cq, parsed.opts.delayMod)
        reactor.listenTCP(parsed.opts.localPort, factory)
        reactor.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)