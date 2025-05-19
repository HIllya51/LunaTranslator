from myutils.config import globalconfig


def create_connection(url, header=None, http_proxy_host=None, http_proxy_port=None):
    if globalconfig["network_websocket"] == 1:
        from network.client.libcurl.websocket import WebSocket
    elif globalconfig["network_websocket"] == 0:
        from network.client.winhttp.websocket import WebSocket

    _ = WebSocket()
    _.connect(url, header, http_proxy_host, http_proxy_port)
    return _
