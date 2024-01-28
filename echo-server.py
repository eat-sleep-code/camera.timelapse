from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><head><title>Authentication Successful</title></head>")
        self.wfile.write(b"<body><h1>Authentication Successful</h1></body></html>")
        
        threading.Thread(target=self.server.shutdown).start()

def RunServer():
    with socketserver.TCPServer(("", 8080), OAuthCallbackHandler) as httpd:
        print("Server started at http://localhost:8080")
        httpd.serve_forever()

# Start the server in a separate thread
serverThread = threading.Thread(target=RunServer)
serverThread.start()