import redis
import json
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class DashboardHandler(BaseHTTPRequestHandler):

    def okResponse(self):

		self.send_response(200)

		self.send_header('Content-type','text/plain')

		self.send_header('Access-Control-Allow-Origin', 'http://fsobral.ig.com.br:8000')

		self.send_header('Acess-Control-Allow-Credentials', '*')

		self.end_headers()	

    def do_GET(self):
        try:

		url = urlparse.urlparse(self.path)

		if url.path == '/dashboards':

			r = redis.StrictRedis('127.0.0.1', port=6379, db=0)

			self.okResponse()
			
			result = r.get('dashboards')

			print result

			self.wfile.write(result)

			self.wfile.close()

			return

		elif url.path == '/dashboard':

			r = redis.StrictRedis('127.0.0.1', port=6379, db=0)

			self.okResponse()

			result = ''

			qs = urlparse.parse_qs(url.query)

			if qs.has_key('id'):

				result = r.get(qs['id'][0])

			else:

				result = r.get('default')

			print result

			self.wfile.write(result)

			self.wfile.close()

			return

		else:

			self.send_error(400, 'Not Found')
			
        except IOError:

            self.send_error(404,'Error')
     
    def do_PUT(self):

	url = urlparse.urlparse(self.path)

	if url.path == '/dashboard':

		qs = urlparse.parse_qs(url.query)

		if not qs.has_key('id') or len(qs['id']) == 0:

			self.send_error(400, 'Missing dashboard name')

			return

		dashboard = self.rfile.read(int(self.headers['content-length']))

		try:

			json.loads(dashboard)

		except:
	
			self.send_error(400, 'Invalid json format for dashboard')

			return

		print dashboard

		r = redis.StrictRedis('127.0.0.1', port=6379, db=0)

		dashs = r.get('dashboards')

		jdashs = json.loads(dashs)

		jdashs['rows'].append({'id':qs['id'][0]})

		print jdashs

		r.set('dashboards', json.dumps(jdashs))

		r.set(qs['id'][0], dashboard)

		self.okResponse()

		return

	else:

		self.send_error(400, 'Not Found')


    def do_POST(self):
	pass

def main():

    try:

        server = HTTPServer(('redis.fsobral.ig.com.br', 2030), DashboardHandler)

	print 'Started server...'

	server.serve_forever()

    except KeyboardInterrupt:

	print 'Finishing...'

	server.socket.close()

if __name__ == '__main__':

    main()

