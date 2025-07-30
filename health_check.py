from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            logger.info("Health check request received")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found")

def run_health_server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f"Starting health check server on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 10000))
    run_health_server(port)