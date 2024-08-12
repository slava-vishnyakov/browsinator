import atexit
import base64
import json
import os
import platform
import subprocess
import time
from threading import Thread

import requests
import websocket

__version__ = "0.1.1"

class Browser:
    def __init__(self):
        self.raise_exc = None
        self.c = requests.Session()
        self.uid = 0
        self.callbacks = {}
        self.responses = {}
        self.requests = {}
        self.debug_params = {}
        self.match_network_url_parts = []
        self.base_uri = 'http://localhost:9222'
        self.tab = None
        self.ws = None
        self.t = None

    @staticmethod
    def start(path=None, minimized=True, debug_port=9222):
        if path is None:
            if platform.system() == "Darwin":
                path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            elif platform.system() == "Linux":
                path = "google-chrome"
            elif platform.system() == "Windows":
                path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            else:
                raise OSError("Unsupported operating system")

        cmd = [
            path,
            f"--remote-debugging-port={debug_port}",
            "--remote-allow-origins=*",
            "--user-data-dir=/tmp/chrome_debug_profile",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if minimized:
            cmd.append("--start-minimized")

        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)  # Wait for Chrome to start

    def connect(self):
        res = self.c.put(self.base_uri + '/json/new')
        self.tab = res.json()
        url = self.tab['webSocketDebuggerUrl']
        
        def on_error(ws, error):
            print(f'DEBUG: Websocket error: {error}')
        
        self.ws = websocket.WebSocketApp(url, on_message=self.on_message, on_error=on_error)
        self.t = Thread(target=self._start, daemon=True)
        self.t.start()
        while not self.ws.sock or not self.ws.sock.connected:
            time.sleep(0.1)
        self.run_method_cb('Page.enable')
        atexit.register(self.close)

    def close(self):
        if self.tab:
            self.c.post(self.base_uri + '/json/close/' + self.tab['id'])
            self.tab = None

    def _start(self):
        self.ws.run_forever()
        if self.raise_exc:
            raise self.raise_exc

    def run_method_cb(self, method, params: dict = None, cb: callable = None):
        if self.raise_exc: raise self.raise_exc

        # print(f'Run {method}')
        if params is None:
            params = {}
        self.uid += 1

        self.debug_params[self.uid] = (method, params)
        # print(f'DEBUG: Sending {method} with params {params}')
        self.ws.send(json.dumps({
            'id': self.uid,
            'method': method,
            'params': params,
        }))

        if cb is not None:
            self.callbacks[self.uid] = cb

    def on_message(self, ws, data):
        data = json.loads(data)
        # print('on_message:', data)

        if 'id' in data:
            if 'error' in data:
                self.raise_exc = Exception(f'WebSocket reported error on call to {self.debug_params[data["id"]]}: {data["error"]["message"]}')
                self.ws.close()

            if data['id'] in self.callbacks:
                self.callbacks[data['id']](data['result'])
                del self.callbacks[data['id']]
                del self.debug_params[data['id']]
                return

        if 'method' in data:
            if data['method'] in self.callbacks:
                self.callbacks[data['method']]()
                del self.callbacks[data['method']]
                return

            if data['method'] == 'Network.requestWillBeSent':
                request_id = data['params']['requestId']
                self.requests[request_id] = data['params']['request']
                # print('Network.requestWillBeSent:', request_id, data['params']['request'])
                return

            if data['method'] == 'Network.responseReceived':
                request_id = data['params']['requestId']
                self.responses[request_id] = data['params']['response']
                # print('Network.responseReceived:', request_id, data['params']['response'])
                return

            if data['method'] == 'Network.loadingFinished':
                # print('Network.loadingFinished', data)
                request_id = data['params']['requestId']
                self.run_method_cb('Network.getResponseBody', {'requestId': request_id}, lambda data: self.got_network_response(request_id, data))
                return

        # print('UNHANDLED on_message:', data)

    def load(self, url, cb=None, wait=False):
        self.run_method_cb('Page.navigate', {'url': url})
        if cb:
            self.add_callback('Page.loadEventFired', cb)
        else:
            data = {}

            def done():
                data['done'] = 1

            if wait:
                self.add_callback('Page.loadEventFired', done)
            while 'done' not in data:
                time.sleep(0.1)
            self.c.post(self.base_uri + '/json/activate/' + self.tab['id'])

    def add_callback(self, method, cb):
        self.callbacks[method] = cb

    def run_script(self, script, cb=None):
        self.run_method_cb('Runtime.evaluate', {'expression': script}, cb)

    def run_script_sync_get_result(self, script):
        script2 = f'JSON.stringify({script})'
        results = self.run_method_sync('Runtime.evaluate', {'expression': script2})
        if 'exceptionDetails' in results:
            raise Exception(results['exceptionDetails'])
        return json.loads(results['result']['value'])

    def run_method_sync(self, method, params=None):
        if params is None:
            params = {}
        results = {}
        def done(res):
            results['result'] = res
        self.run_method_cb(method, params, done)
        while 'result' not in results:
            time.sleep(0.05)
        return results['result']

    def monitor_network(self):
        self.run_method_sync('Network.enable')

    def match_network(self, url_part, cb):
        self.match_network_url_parts.append((url_part, cb))

    def got_network_response(self, request_id, data):
        request = self.requests[request_id]
        response = self.responses[request_id]
        url = request['url']
        # print(request) # request['url']
        # print(response) # response['status'] ['headers'] ['content-type']
        data = base64.b64decode(data['body']) if data['base64Encoded'] else data['body']
        # print(url[:250], repr(data)[:250])

        for url_part, cb in self.match_network_url_parts:
            if url_part in url:
                cb(request, response, data)

        del self.requests[request_id]
        del self.responses[request_id]

    def keyboard_type(self, text):
        for c in text:
            self.run_method_cb('Input.dispatchKeyEvent', {'type': 'char', 'text': c})

    def keyboard_press_enter(self):
        self.run_method_sync('Input.dispatchKeyEvent', {'type': 'char', 'windowsVirtualKeyCode': 13})

    def keyboard_paste(self):
        # import pyperclip
        # pyperclip.copy('Hello, World!')
        self.run_method_sync('Input.dispatchKeyEvent', {'type': 'char', 'commands': ['Paste']})

    def keyboard_undo(self):
        self.run_method_sync('Input.dispatchKeyEvent', {'type': 'char', 'commands': ['Undo']})

    def mouse_click_selector(self, selector, dx=1, dy=1):
        coords = self.run_script_sync_get_result(f"document.querySelector({json.dumps(selector)}).getBoundingClientRect()")
        self.run_method_sync('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': coords['x']+dx, 'y': coords['y']+dy, 'button': 'left'})
        self.run_method_sync('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': coords['x']+dx, 'y': coords['y']+dy, 'button': 'left'})

