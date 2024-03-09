from pkll.server import PKLServer


def test_server():
    server = PKLServer()
    server.start_process()
    server.terminate()
