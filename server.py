"""
Server for AI English Voice Coach (VerbaFlow AI)
Port: 8766
"""

import json
import os
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(CURRENT_DIR))

# Safe UTF-8 console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from tutor_engine import SCENARIOS, generate_tutor_response
from tts_service import generate_coach_speech

STATIC_DIR = CURRENT_DIR / "static"
PORT = 8766

class EnglishTutorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: Scenarios
        if path == "/api/scenarios":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(SCENARIOS, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API: TTS Streaming
        elif path == "/api/tts":
            text = query.get("text", [""])[0]
            engine = query.get("engine", ["edge_tts"])[0]
            voice = query.get("voice", ["us_female"])[0]
            speed = query.get("speed", ["1.0"])[0]

            if not text:
                self.send_error(400, "Missing text parameter")
                return

            try:
                audio_bytes, filename = generate_coach_speech(
                    text=text,
                    engine=engine,
                    voice=voice,
                    speed=speed
                )
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(audio_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(audio_bytes)
            except Exception as e:
                print(f"[Tutor TTS Error]: {e}")
                self.send_error(500, f"TTS generation failed: {e}")
            return

        # 3. API: Status check
        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status_data = {
                "status": "online",
                "app": "VerbaFlow AI - English Voice Coach",
                "elevenlabs_available": bool(os.environ.get("ELEVENLABS_API_KEY")),
                "edge_tts_available": True
            }
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode("utf-8"))
            return

        # Default static file serving
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                speech = data.get("speech", "")
                history = data.get("history", [])
                scenario_id = data.get("scenario_id", "grammar_freetalk")
                gemini_key = data.get("gemini_key", "")
                openai_key = data.get("openai_key", "")

                resp_data = generate_tutor_response(
                    user_speech=speech,
                    history=history,
                    scenario_id=scenario_id,
                    gemini_key=gemini_key,
                    openai_key=openai_key
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(resp_data, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                print(f"[Tutor Chat Error]: {e}")
                self.send_error(500, f"Chat processing failed: {e}")
            return

        self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port=PORT):
    # Bind to 0.0.0.0 for cloud hosting (Render, Docker) and local access
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, EnglishTutorHandler)
    print("\n=======================================================")
    print(" [VerbaFlow AI - English Voice Coach Running]")
    print(f" Port: {port} (Bound to 0.0.0.0)")
    print("=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    env_port = os.environ.get("PORT")
    if env_port:
        port = int(env_port)
    elif len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = PORT
    run_server(port)
