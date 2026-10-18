import os
import sys
import json
import webbrowser
import subprocess
from urllib.parse import urlparse, parse_qs, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(APP_DIR)
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
OUTPUT_BASE_DIR = os.path.join(WORKSPACE_DIR, "Generated_Dashboards")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

sys.path.insert(0, APP_DIR)
import pbi_engine


class PBIStudioHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            index_file = os.path.join(APP_DIR, "static", "index.html")
            with open(index_file, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/list_files":
            # List Excel/CSV files available in c:\馨 and c:\馨\Power BI and uploads
            found = []
            search_dirs = [WORKSPACE_DIR, os.path.dirname(WORKSPACE_DIR), UPLOAD_DIR]
            seen = set()
            for sdir in search_dirs:
                if not os.path.exists(sdir):
                    continue
                for fname in os.listdir(sdir):
                    if fname.lower().endswith((".xlsx", ".xls", ".csv")) and not fname.startswith("~$"):
                        fpath = os.path.abspath(os.path.join(sdir, fname))
                        if fpath not in seen:
                            seen.add(fpath)
                            found.append({
                                "name": fname,
                                "path": fpath,
                                "size_kb": round(os.path.getsize(fpath) / 1024, 1)
                            })
            self._send_json({"files": found})
            return

        if parsed.path == "/api/preview_html":
            qs = parse_qs(parsed.query)
            html_path = qs.get("path", [""])[0]
            if html_path and os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            self._send_json({"error": "File not found"}, 404)
            return

        if parsed.path == "/api/raw_file":
            qs = parse_qs(parsed.query)
            fpath = qs.get("path", [""])[0]
            if fpath and os.path.exists(fpath):
                with open(fpath, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            self._send_json({"error": "File not found"}, 404)
            return

        self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/upload":
                length = int(self.headers.get("Content-Length", 0))
                raw_filename = unquote(self.headers.get("X-File-Name", "uploaded_data.xlsx"))
                fname = os.path.basename(raw_filename)
                save_path = os.path.join(UPLOAD_DIR, fname)
                with open(save_path, "wb") as f:
                    f.write(self.rfile.read(length))
                info = pbi_engine.inspect_dataset(save_path, limit=15)
                self._send_json({"status": "ok", "inspection": info})
                return

            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            payload = json.loads(raw_body)

            if parsed.path == "/api/inspect_path":
                fpath = payload.get("file_path", "")
                info = pbi_engine.inspect_dataset(fpath, limit=15)
                self._send_json({"status": "ok", "inspection": info})
                return

            if parsed.path == "/api/parse_prompt":
                fpath = payload.get("file_path", "")
                prompt = payload.get("prompt", "")
                info = pbi_engine.inspect_dataset(fpath, limit=10)
                new_cfg = pbi_engine.parse_natural_language_request(prompt, info)
                self._send_json({"status": "ok", "config": new_cfg})
                return

            if parsed.path == "/api/build":
                fpath = payload.get("file_path", "")
                config = payload.get("config", {})
                base_name = pbi_engine.sanitize_table_name(os.path.splitext(os.path.basename(fpath))[0])
                out_dir = os.path.join(OUTPUT_BASE_DIR, base_name)
                res = pbi_engine.build_dashboard_bundle(fpath, config, out_dir, limit_top_n=25)
                self._send_json(res)
                return

            if parsed.path == "/api/open_file":
                target = payload.get("path", "")
                if target and os.path.exists(target):
                    os.startfile(target)
                    self._send_json({"status": "opened", "path": target})
                else:
                    self._send_json({"error": f"找不到檔案: {target}"}, 400)
                return

            if parsed.path == "/api/repack_pbix":
                src_pbix = payload.get("source_pbix", "")
                layout_json = payload.get("layout_json", "")
                out_pbix = src_pbix.replace(".pbix", "_跨電腦相容版.pbix")
                res = pbi_engine.repack_pbix_cross_pc(src_pbix, layout_json, out_pbix)
                self._send_json(res)
                return

            self._send_json({"error": "Unknown endpoint"}, 404)
        except Exception as e:
            import traceback
            self._send_json({"status": "error", "message": str(e), "trace": traceback.format_exc()}, 500)


def run_server(port: int = 8765, open_browser: bool = True):
    server = HTTPServer(("127.0.0.1", port), PBIStudioHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"Power BI Studio App running at {url}")
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port=p, open_browser=True)
