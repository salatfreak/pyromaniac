from unittest import TestCase
from unittest.mock import patch, Mock
from pyromaniac.server.server import Server

from . import temp


@patch('http.server.HTTPServer.__init__', Mock())
@patch('http.server.BaseHTTPRequestHandler.__init__', Mock())
@patch('pyromaniac.server.server.Handler.headers', Mock(), create=True)
@patch('pyromaniac.server.server.Handler.end_headers', Mock(), create=True)
class TestServer(TestCase):
    @patch('http.server.HTTPServer.__init__', Mock())
    @patch('http.server.HTTPServer.socket', Mock(), create=True)
    @patch('ssl.SSLContext', Mock())
    @temp.dir
    def test_certs(self, secrets):
        root_key = secrets / "root.key"
        root_crt = secrets / "root.cert"
        with (
            patch('pyromaniac.server.certs.ROOT_KEY', root_key),
            patch('pyromaniac.server.certs.ROOT_CRT', root_crt),
        ):
            Server('http', "127.0.0.1", None, lambda: "{}")
            self.assertFalse(root_key.exists())
            self.assertFalse(root_crt.exists())

            Server('https', "127.0.0.1", None, lambda: "{}")
            self.assertTrue(root_key.exists())
            self.assertTrue(root_crt.exists())

    @patch('sys.stdout', Mock())
    @patch('pyromaniac.server.server.Handler.send_response', create=True)
    @patch('pyromaniac.server.server.Handler.send_header', create=True)
    @patch('pyromaniac.server.server.Handler.wfile', create=True)
    def test_request_config(
        self, wfile: Mock, send_header: Mock, send_response: Mock
    ):
        server = Server('http', "127.0.0.1", None, lambda: "{}")
        handler = server.handle(None, ("127.0.0.1", 9000), server)
        path = "/config.ign"
        with patch('pyromaniac.server.server.Handler.path', path, create=True):
            handler.do_GET()
            send_response.assert_called_with(200)
            send_header.assert_called_with('Content-Type', "application/json")
            wfile.write.assert_called_with("{}".encode())
