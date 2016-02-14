import json, cgi, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class cg_http_handler(BaseHTTPRequestHandler):
	
	def do_POST(self):
		try:
			default_exception = 'unsupported request.'
			success = True
			data = None
			
			length = self.headers['content-length']
			if length == None:
				length = self.headers['content-length'] = 0
			if int(length) > (1<<16):
				raise Exception("data too large")
			http_form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE': "text/html"})
			
			form = {}
			for item in http_form:
				try:
					value = http_form[item].file.read().strip()
				except:
					value = http_form[item].value
				try:
					value = value.decode()
				except:
					pass
				form[item] = value
			
			parts = self.path.split('/', 2)
			if len(parts) != 3:
				raise Exception(default_exception)
			[null, version, path] = parts
			
			module = __import__('daemon.case_' + version)
			handler = module.__dict__['case_' + version].__dict__['case_handler']
			method = path.replace('/', '_')
			if not hasattr(handler, method):
				raise Exception(default_exception)
			
			data = handler.__dict__[method](form)
		except Exception as e:
			success = False
			data = {"reason": str(e)}
		finally:
			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps({"success": success, "data": data}).encode())
			self.wfile.write("\n".encode())
		return

class cg_http_server:
	
	port = 1725
	
	def run():
		server = HTTPServer(('0.0.0.0', cg_http_server.port), cg_http_handler)
		server.serve_forever()
	
	def start():
		http = threading.Thread(target = cg_http_server.run, args = ())
		http.setDaemon(True)
		http.start()
		return http
