from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse


class TestServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract the request tag from headers if present
        request_tag = self.headers.get('X-Request-Tag', 'No tag found')

        # Send a simple response indicating the request was received
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        message = f"<html><body><h1>Test Server Response</h1><p>Request Tag: {request_tag}</p></body></html>"
        self.wfile.write(bytes(message, "utf8"))


def run(server_class=HTTPServer, handler_class=TestServerHandler, port=8002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting test server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
