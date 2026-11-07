"""Desktop-ops MCP server (HTTP, JSON). Exposes adapters as MCP tools.

Run with: python -m desktop_ops.mcp_server  (or `ops serve`)
Endpoints:
  GET  /health          liveness
  GET  /mcp/tools       list tools
  POST /mcp/call        {name, params} -> result
  GET  /capabilities    adapter capabilities
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from desktop_ops import registry


PORT = int(os.environ.get("DESKTOP_OPS_PORT", "9876"))


def _tools_list():
    tools = []
    for name in registry.list_adapters():
        mod = registry.get_adapter(name)
        for cap in (mod.capabilities() if hasattr(mod, "capabilities") else []):
            tools.append({"name": f"{name}.{cap.split('.')[-1]}", "adapter": name, "capability": cap,
                          "description": cap})
    return tools


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/health":
            self._send(200, {"status": "ok", "service": "desktop-ops"})
        elif p == "/mcp/tools":
            self._send(200, {"tools": _tools_list()})
        elif p == "/capabilities":
            out = {}
            for name in registry.list_adapters():
                mod = registry.get_adapter(name)
                out[name] = {
                    "probe": mod.probe() if hasattr(mod, "probe") else False,
                    "capabilities": mod.capabilities() if hasattr(mod, "capabilities") else [],
                }
            self._send(200, out)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        p = urlparse(self.path).path
        if p == "/mcp/call":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            name = body.get("name", "")
            params = body.get("params", {})
            # name format: "adapter.action"
            if "." not in name:
                self._send(400, {"error": "name must be adapter.action"})
                return
            adapter_name, action = name.split(".", 1)
            mod = registry.get_adapter(adapter_name)
            if mod is None:
                self._send(404, {"error": f"unknown adapter {adapter_name}"})
                return
            result = mod.run(action, params)
            self._send(200, result)
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass  # quiet


def serve(port=None):
    port = port or PORT
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    print(f"desktop-ops MCP server listening on :{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    serve()