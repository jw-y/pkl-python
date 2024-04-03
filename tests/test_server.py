from pkl.server import PKLServer


def test_server():
    server = PKLServer()
    server.terminate()
