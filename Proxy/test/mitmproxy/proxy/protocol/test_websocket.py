import pytest
import os
import tempfile
import traceback

from mitmproxy import options
from mitmproxy import exceptions
from mitmproxy.http import HTTPFlow
from mitmproxy.websocket import WebSocketFlow

from mitmproxy.net import tcp
from mitmproxy.net import http
from ...net import tservers as net_tservers
from ... import tservers

from mitmproxy.net import websockets


class _WebSocketServerBase(net_tservers.ServerTestBase):

    class handler(tcp.BaseHandler):

        def handle(self):
            try:
                request = http.http1.read_request(self.rfile)
                assert websockets.check_handshake(request.headers)

                response = http.Response(
                    "HTTP/1.1",
                    101,
                    reason=http.status_codes.RESPONSES.get(101),
                    headers=http.Headers(
                        connection='upgrade',
                        upgrade='websocket',
                        sec_websocket_accept=b'',
                    ),
                    content=b'',
                )
                self.wfile.write(http.http1.assemble_response(response))
                self.wfile.flush()

                self.server.handle_websockets(self.rfile, self.wfile)
            except:
                traceback.print_exc()


class _WebSocketTestBase:

    @classmethod
    def setup_class(cls):
        cls.options = cls.get_options()
        tmaster = tservers.TestMaster(cls.options)
        cls.proxy = tservers.ProxyThread(tmaster)
        cls.proxy.start()

    @classmethod
    def teardown_class(cls):
        cls.proxy.shutdown()

    @classmethod
    def get_options(cls):
        opts = options.Options(
            listen_port=0,
            upstream_cert=True,
            ssl_insecure=True,
            websocket=True,
        )
        opts.cadir = os.path.join(tempfile.gettempdir(), "mitmproxy")
        return opts

    @property
    def master(self):
        return self.proxy.tmaster

    def setup(self):
        self.master.reset([])
        self.server.server.handle_websockets = self.handle_websockets

    def teardown(self):
        if self.client:
            self.client.close()

    def setup_connection(self):
        self.client = tcp.TCPClient(("127.0.0.1", self.proxy.port))
        self.client.connect()

        request = http.Request(
            "authority",
            "CONNECT",
            "",
            "127.0.0.1",
            self.server.server.address[1],
            "",
            "HTTP/1.1",
            content=b'')
        self.client.wfile.write(http.http1.assemble_request(request))
        self.client.wfile.flush()

        response = http.http1.read_response(self.client.rfile, request)

        if self.ssl:
            self.client.convert_to_ssl()
            assert self.client.ssl_established

        request = http.Request(
            "relative",
            "GET",
            "http",
            "127.0.0.1",
            self.server.server.address[1],
            "/ws",
            "HTTP/1.1",
            headers=http.Headers(
                connection="upgrade",
                upgrade="websocket",
                sec_websocket_version="13",
                sec_websocket_key="1234",
            ),
            content=b'')
        self.client.wfile.write(http.http1.assemble_request(request))
        self.client.wfile.flush()

        response = http.http1.read_response(self.client.rfile, request)
        assert websockets.check_handshake(response.headers)


class _WebSocketTest(_WebSocketTestBase, _WebSocketServerBase):

    @classmethod
    def setup_class(cls):
        _WebSocketTestBase.setup_class()
        _WebSocketServerBase.setup_class(ssl=cls.ssl)

    @classmethod
    def teardown_class(cls):
        _WebSocketTestBase.teardown_class()
        _WebSocketServerBase.teardown_class()


class TestSimple(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.TEXT, payload=b'server-foobar')))
        wfile.flush()

        frame = websockets.Frame.from_file(rfile)
        wfile.write(bytes(frame))
        wfile.flush()

        frame = websockets.Frame.from_file(rfile)
        wfile.write(bytes(frame))
        wfile.flush()

    @pytest.mark.parametrize('streaming', [True, False])
    def test_simple(self, streaming):
        class Stream:
            def websocket_start(self, f):
                f.stream = streaming

        self.master.addons.add(Stream())
        self.setup_connection()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.payload == b'server-foobar'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.TEXT, payload=b'self.client-foobar')))
        self.client.wfile.flush()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.payload == b'self.client-foobar'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.BINARY, payload=b'\xde\xad\xbe\xef')))
        self.client.wfile.flush()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.payload == b'\xde\xad\xbe\xef'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE)))
        self.client.wfile.flush()

        assert len(self.master.state.flows) == 2
        assert isinstance(self.master.state.flows[0], HTTPFlow)
        assert isinstance(self.master.state.flows[1], WebSocketFlow)
        assert len(self.master.state.flows[1].messages) == 5
        assert self.master.state.flows[1].messages[0].content == b'server-foobar'
        assert self.master.state.flows[1].messages[0].type == websockets.OPCODE.TEXT
        assert self.master.state.flows[1].messages[1].content == b'self.client-foobar'
        assert self.master.state.flows[1].messages[1].type == websockets.OPCODE.TEXT
        assert self.master.state.flows[1].messages[2].content == b'self.client-foobar'
        assert self.master.state.flows[1].messages[2].type == websockets.OPCODE.TEXT
        assert self.master.state.flows[1].messages[3].content == b'\xde\xad\xbe\xef'
        assert self.master.state.flows[1].messages[3].type == websockets.OPCODE.BINARY
        assert self.master.state.flows[1].messages[4].content == b'\xde\xad\xbe\xef'
        assert self.master.state.flows[1].messages[4].type == websockets.OPCODE.BINARY


class TestSimpleTLS(_WebSocketTest):
    ssl = True

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.TEXT, payload=b'server-foobar')))
        wfile.flush()

        frame = websockets.Frame.from_file(rfile)
        wfile.write(bytes(frame))
        wfile.flush()

    def test_simple_tls(self):
        self.setup_connection()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.payload == b'server-foobar'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.TEXT, payload=b'self.client-foobar')))
        self.client.wfile.flush()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.payload == b'self.client-foobar'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE)))
        self.client.wfile.flush()


class TestPing(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.PING, payload=b'foobar')))
        wfile.flush()

        frame = websockets.Frame.from_file(rfile)
        assert frame.header.opcode == websockets.OPCODE.PONG
        assert frame.payload == b'foobar'

        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.TEXT, payload=b'pong-received')))
        wfile.flush()

    def test_ping(self):
        self.setup_connection()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.header.opcode == websockets.OPCODE.PING
        assert frame.payload == b'foobar'

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.PONG, payload=frame.payload)))
        self.client.wfile.flush()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.header.opcode == websockets.OPCODE.TEXT
        assert frame.payload == b'pong-received'


class TestPong(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        frame = websockets.Frame.from_file(rfile)
        assert frame.header.opcode == websockets.OPCODE.PING
        assert frame.payload == b'foobar'

        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.PONG, payload=frame.payload)))
        wfile.flush()

    def test_pong(self):
        self.setup_connection()

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.PING, payload=b'foobar')))
        self.client.wfile.flush()

        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.header.opcode == websockets.OPCODE.PONG
        assert frame.payload == b'foobar'


class TestClose(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        frame = websockets.Frame.from_file(rfile)
        wfile.write(bytes(frame))
        wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE)))
        wfile.flush()

        with pytest.raises(exceptions.TcpDisconnect):
            websockets.Frame.from_file(rfile)

    def test_close(self):
        self.setup_connection()

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE)))
        self.client.wfile.flush()

        websockets.Frame.from_file(self.client.rfile)
        with pytest.raises(exceptions.TcpDisconnect):
            websockets.Frame.from_file(self.client.rfile)

    def test_close_payload_1(self):
        self.setup_connection()

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE, payload=b'\00\42')))
        self.client.wfile.flush()

        websockets.Frame.from_file(self.client.rfile)
        with pytest.raises(exceptions.TcpDisconnect):
            websockets.Frame.from_file(self.client.rfile)

    def test_close_payload_2(self):
        self.setup_connection()

        self.client.wfile.write(bytes(websockets.Frame(fin=1, opcode=websockets.OPCODE.CLOSE, payload=b'\00\42foobar')))
        self.client.wfile.flush()

        websockets.Frame.from_file(self.client.rfile)
        with pytest.raises(exceptions.TcpDisconnect):
            websockets.Frame.from_file(self.client.rfile)


class TestInvalidFrame(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        wfile.write(bytes(websockets.Frame(fin=1, opcode=15, payload=b'foobar')))
        wfile.flush()

    def test_invalid_frame(self):
        self.setup_connection()

        # with pytest.raises(exceptions.TcpDisconnect):
        frame = websockets.Frame.from_file(self.client.rfile)
        assert frame.header.opcode == 15
        assert frame.payload == b'foobar'


class TestStreaming(_WebSocketTest):

    @classmethod
    def handle_websockets(cls, rfile, wfile):
        wfile.write(bytes(websockets.Frame(opcode=websockets.OPCODE.TEXT, payload=b'server-foobar')))
        wfile.flush()

    @pytest.mark.parametrize('streaming', [True, False])
    def test_streaming(self, streaming):
        class Stream:
            def websocket_start(self, f):
                f.stream = streaming

        self.master.addons.add(Stream())
        self.setup_connection()

        frame = None
        if not streaming:
            with pytest.raises(exceptions.TcpDisconnect):  # Reader.safe_read get nothing as result
                frame = websockets.Frame.from_file(self.client.rfile)
            assert frame is None

        else:
            frame = websockets.Frame.from_file(self.client.rfile)

            assert frame
            assert self.master.state.flows[1].messages == []  # Message not appended as the final frame isn't received
