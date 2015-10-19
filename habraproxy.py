#!-*-coding:utf-8-*-
# requirements: beautifulsoup4, requests
# python habraproxy.py [-p PORT] [-d DOMAIN] [-b]
# param: -p: port, -d: domain, -b: browser


import argparse
import re
import sys
import SocketServer
import SimpleHTTPServer
import webbrowser

from bs4 import BeautifulSoup, Comment
import requests


PORT, DOMAIN = 8000, 'http://habrahabr.ru'
EXTRA_SIGN, URL_PATH = u'\u2122', '/company/yandex/blog/258611/'


class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    domain = DOMAIN

    def do_GET(self):
        try:
            url = Proxy.domain + self.path
            print 'GET %s' % url
            page = requests.get(url)
            print 'request processing'
            if page.headers['Content-Type'].find('html') == -1:
                self.response(page.content)
                return

            soup = BeautifulSoup(page.content, 'html.parser')
            nav_strings = soup.body.findAll(
                text=re.compile(r'\b[\w]{6}\b', flags=re.U))
            for nav_string in nav_strings:
                # delete comment in html
                if isinstance(nav_string, Comment):
                    nav_string.extract()
                    continue

                # don not handle tags: <script> and <code>
                flag = False
                for parent in nav_string.parentGenerator():
                    try:
                        if parent.name in [u'script', u'code']:
                            flag = True
                            break
                    except AttributeError:
                        break  # reached the top
                if flag:
                    continue

                nav_string.replaceWith(
                    re.sub(r'(?P<word>\b[\w]{6})\b',
                           lambda m: m.group('word') + EXTRA_SIGN, nav_string,
                           flags=re.U))
            self.response(str(soup))
        except requests.ConnectionError, ex:
            self._error_message('error in receiving data (%s)\n' % ex)

    def response(self, html):
        print 'send response on %s' % self.path
        self.wfile.write(html)

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
    server = None
    try:
        port, Proxy.domain = int(namespace.port), namespace.domain
        server = SocketServer.ForkingTCPServer(('', port), Proxy)
        if namespace.b:
            print 'run browser'
            webbrowser.open('%s:%s%s' % (Proxy.domain, port, URL_PATH))
        print "Listening on port: ", port
        server.serve_forever()
    except KeyboardInterrupt:
        if server:
            server.socket.close()
    except ValueError:
        print 'Incorrect PORT'


if __name__ == '__main__':
    main()