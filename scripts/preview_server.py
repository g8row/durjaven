#!/usr/bin/env python3
"""Serve the repository so the book can be read in a browser.

Why not `python3 -m http.server`: that entry point evaluates `os.getcwd()` at
import time to default its `--directory` flag, and raises PermissionError when
the launching process has no readable working directory -- which is exactly the
case under the sandboxed preview runner. Importing the module and passing an
explicit root sidesteps the getcwd entirely.

Why a server at all: pdf.js loads as an ES module and fetches the PDF, and both
are blocked under file://.

    python3 scripts/preview_server.py [port]     # default 8801

"/" lands on the pdf.js viewer with the chapter outline, via the root
index.html; /darzhaven-izpit-kn.pdf serves the raw file instead.
"""
import functools
import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8801


class Handler(http.server.SimpleHTTPRequestHandler):
    # "/" lands on the book rather than a directory listing because the root
    # index.html redirects to the viewer -- the same file that does it on
    # GitHub Pages, so hosted and local behave identically.

    # The book is rebuilt in place and the viewer is edited while it is open;
    # a cached copy of either is worse than useless.
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.TCPServer):
    allow_reuse_address = True   # do not fail on a socket still in TIME_WAIT
    daemon_threads = True


def main():
    os.chdir(ROOT)               # the runner may start us with no valid cwd
    handler = functools.partial(Handler, directory=ROOT)
    with Server(("127.0.0.1", PORT), handler) as httpd:
        print("serving %s on http://localhost:%d/" % (ROOT, PORT), flush=True)
        print("book viewer: http://localhost:%d/pdfjs-wrapper/" % PORT, flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
