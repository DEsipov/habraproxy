#!-*-coding:utf-8-*-

__author__ = 'virgo'

import SocketServer
import SimpleHTTPServer
import urllib

PORT = 8000
DOMAIN = 'http://habrahabr.ru'
FNAME = 'habra.html'
DEBUG = True

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        # self.copyfile(urllib.urlopen(self.path), self.wfile)
        try:
            if not DEBUG:
                html = urllib.urlopen(DOMAIN + self.path)
                f = open(FNAME, 'w')
                f.write(html.read())
                f.close()
            f = open(FNAME, 'r')
            self.copyfile(f, self.wfile)
        except Exception, ex:
            self.close_connection()

def main():
    print 'Coming soon...'
    httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
    print "serving at port", PORT
    if not DEBUG:
        httpd.serve_forever()
    httpd.handle_request()


if __name__ == '__main__':
    main()