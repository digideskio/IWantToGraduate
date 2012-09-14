from tornado import httpserver, ioloop
from urlparse import urlparse
import cgi

message = None

def parseArg(uri):
    print 'in parse Arg: ', uri
    parsedUri = urlparse(uri)
    print "parsedUri: ", parsedUri
    print "parsedUri.query: ", parsedUri.query
    parsedQuery = cgi.parse_qs(parsedUri.query)
    print 'parsedQuery: ', parsedQuery

def handle_request(request):
   message = "You requested %s\n" % request.uri
   requestUri = request.uri
   if(requestUri.startswith('/course_req/api?')):
       message += "you are right"
       parseArg(request.uri)
   #f = open(request.uri, 'r')
   #message = f.read()
   request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s" % (
	                   len(message), message))
   request.finish()

http_server = httpserver.HTTPServer(handle_request)
http_server.listen(80)
ioloop.IOLoop.instance().start()
