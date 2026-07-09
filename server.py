import asyncio
import time
import json
import os  # 1. 引入 os 模組
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import paramiko

# 引入剛剛建立的 Parser Class 
from parser.CustomParser import LogParser

app = FastAPI()

# ==========================================
# remote SSH connection configuration
# ==========================================
# Windows (Command Prompt / cmd)
#   set SSH_HOST=IP_ADDRESS
#   set SSH_PASSWORD=你的真實密碼
#   python server.py
# Windows (PowerShell)
#   $env:SSH_HOST=IP_ADDRESS
#   $env:SSH_PASSWORD=PASSWORD
#   python server.py
# Linux / macOS
#   export SSH_HOST=IP_ADDRESS
#   export SSH_PASSWORD=PASSWORD
# ==========================================

SSH_CONFIG = {
    "host": os.getenv("SSH_HOST", "192.168.5.11"),
    "password": os.getenv("SSH_PASSWORD")
}
SSH_PORT = 45296        # HOST Port
SSH_USER = "guest"      
IDLE_TIMEOUT = 5        # tail timeout retry

# initialize the log parser
log_parser = LogParser()

# ==========================================
# SSH connection to remote gateway and log streaming function
# ==========================================
async def ssh_log_stream():
    while True:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print("[SSH] Connecting to remote host...")
            
            client.connect(
                hostname=SSH_CONFIG["host"],
                port=SSH_PORT,
                username=SSH_USER,
                password=SSH_CONFIG["password"],
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            transport = client.get_transport()
            channel = transport.open_session()           
            print("[SSH] Running tail command...")
            channel.exec_command("tail -n0 -F /tmp/vbs.log.*")
            buffer = ""
            last_activity = time.time()

            while True:
                if channel.exit_status_ready():
                    print("[SSH] Channel closed by remote host. Restarting...")
                    break

                if channel.recv_ready():
                    last_activity = time.time()
                    data = channel.recv(4096).decode(errors="ignore")
                    buffer += data
                    while "\n" in buffer:
                        try:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue                
                            event = log_parser.parse_line(line)
                            if event:
                                yield event
                                
                        except Exception as e:
                            print(f'[PARS ERROR] {line}')
                            print(f"[PARSE ERROR] err={repr(e)}")     
                else:
                    if time.time() - last_activity > IDLE_TIMEOUT:
                        print(f"[SSH] Idle timeout ({IDLE_TIMEOUT}s) reached → restarting tail command")
                        break
                    await asyncio.sleep(0.5)
                await asyncio.sleep(0.01)

        except Exception as e:
            print(f"[SSH ERROR] {e}")
            print(f"[SSH] Host: {SSH_CONFIG['host']}, Port: {SSH_PORT}, User: {SSH_USER}")
            print("[SSH] reconnect in 5 sec...")
            await asyncio.sleep(5)
        finally:
            print("[SSH] Cleaning up connection...")
            try:
                channel.close()
            except:
                pass
            try:
                client.close()
            except:
                pass

# ==========================================
# WebSocket route for streaming logs to the front end
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("The front end has been connected to WebSocket")
    try:
        async for event in ssh_log_stream():
            await websocket.send_text(json.dumps(event, default=str))       
    except WebSocketDisconnect:
        print(" APP WebSocket Disconnected")
    except Exception as e:
        print(f" WebSocket Transmission error: {e}")

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    if not SSH_CONFIG["password"]:
        print("[WARNING] The SSH_PASSWORD environment variable was not detected. The connection may fail!")
    multiprocessing.freeze_support()
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)