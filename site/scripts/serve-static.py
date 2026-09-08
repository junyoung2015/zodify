"""Local smoke server with real 404 status and the built error document."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        body = (Path(self.directory) / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

if __name__ == "__main__":
    directory = Path(__file__).resolve().parents[1] / "dist"
    ThreadingHTTPServer(("127.0.0.1", 4175), partial(Handler, directory=str(directory))).serve_forever()
