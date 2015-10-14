#!-*-coding:utf-8-*-
#requirements: pip install BeautifulSoup
#run: python2.7 habraproxy.py and paste in browser
#http://localhost:8000/company/yandex/blog/258611/
#param: -p: port, -d: domain, -b: browser

import argparse
import re
import tempfile
import sys
import SocketServer
import SimpleHTTPServer
import urllib2
import webbrowser
from BeautifulSoup import BeautifulSoup


PORT, DOMAIN = 8000, '1http://habrahabr.ru'
EXTRA_SIGN, URL_PATH = u'\u2122', '/company/yandex/blog/258611/'


class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            print 'GET %s' % self.path
            in_stream = urllib2.urlopen(Proxy.domain + self.path)
            print 'request processing'
            if in_stream.headers['Content-Type'].find('html') == -1:
                self.copyfile(in_stream, self.wfile)
                return

            html = in_stream.read()
            soup = BeautifulSoup(html.decode('utf-8'))
            nav_strings = soup.body.findAll(
                text=re.compile(r'\b[\w]{6}\b', flags=re.U))
            for x in nav_strings:
                if x.parent.name not in [u'script', u'code']:
                    x.replaceWith(
                        re.sub(r'(?P<word>\b[\w]{6})\b',
                               lambda m: m.group('word') + EXTRA_SIGN, x,
                               flags=re.U))
            self.response(soup.prettify())
        except UnicodeDecodeError, ex:
            self._error_message('got a bad html')
        except (urllib2.URLError, ValueError), ex:
            self._error_message('error in receivinig data (%s)\n' % ex)

    def response(self, html):
        print 'send response on %s' % self.path
        with tempfile.TemporaryFile() as f:
                f.write(html)
                f.seek(0)
                self.copyfile(f, self.wfile)

    def _error_message(self, msg):
        print '%(div)s\n%(msg)s\n%(div)s' % dict(div='*' * 10, msg=msg)
        self.response(msg)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=PORT)
    parser.add_argument('-d', '--domain', default=DOMAIN)
    parser.add_argument('-b', action='store_const', const=True, default=False)
    return parser


def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    try:
        port, Proxy.domain = int(namespace.port), namespace.domain
        server = SocketServer.ForkingTCPServer(('', port), Proxy)
        if namespace.b:
            print 'run browser'
            webbrowser.open('%s:%s%s' % (Proxy.domain, port, URL_PATH))
        print "Listening on port: ", port
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
    except ValueError:
        print 'Incorrect PORT'


if __name__ == '__main__':
    main()