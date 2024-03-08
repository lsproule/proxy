import http.server
import http.client
import urllib.parse
import uuid
import os

# Assuming you have an environment variable named NEXT_PROXY_URL for the next proxy's URL
# and DATACENTER_LOCATION for the current datacenter's location.
# If NEXT_PROXY_URL is not set, default to a local URL for testing.
NEXT_PROXY_URL = os.getenv('NEXT_PROXY_URL', 'http://localhost:8001')
DATACENTER_LOCATION = os.getenv('DATACENTER_LOCATION', 'local_datacenter')

# Initialize a global list to store request tags and datacenter locations
request_traces = []


class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global request_traces

        # Generate a unique tag for this request
        request_tag = uuid.uuid4()
        print(f"Handling request with tag: {request_tag} from datacenter: {DATACENTER_LOCATION}")

        # Record the request tag and datacenter location
        request_traces.append(
            {'tag': request_tag, 'datacenter': DATACENTER_LOCATION})

        # Parse the original request URL
        url = self.path
        parsed_url = urllib.parse.urlparse(url)
        self.send_request(parsed_url, request_tag, method='GET')

    def send_request(self, parsed_url, request_tag, method):
        next_proxy = NEXT_PROXY_URL
        if parsed_url.netloc:
            host = parsed_url.netloc
        else:
            parsed_next_proxy = urllib.parse.urlparse(next_proxy)
            host = parsed_next_proxy.netloc

        if next_proxy.startswith('https://'):
            conn = http.client.HTTPSConnection(host)
        else:
            conn = http.client.HTTPConnection(host)

        path = parsed_next_proxy.path + parsed_url.path
        if parsed_url.query:
            path += '?' + parsed_url.query

        conn.request(method, path, headers={"X-Request-Tag": str(request_tag)})

        # Get the response
        response = conn.getresponse()
        self.send_response(response.status)
        for header, value in response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.read())


def run(server_class=http.server.HTTPServer,
        handler_class=ProxyHTTPRequestHandler,
        port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting proxy server on port {port} with datacenter location: {DATACENTER_LOCATION}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()

