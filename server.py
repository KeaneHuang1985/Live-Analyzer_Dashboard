import asyncio
import time
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import paramiko

# 引入剛剛建立的 Parser Class 
from parser.CustomParser import LogParser

app = FastAPI()

# ==========================================
# SSH 連線設定
# ==========================================
SSH_HOST = "10.0.8.155" # HOST IP "172.2.1.226" #
SSH_PORT = 45296        # HOST Port
SSH_USER = "guest"      
SSH_PASSWORD = "gFVJhYdxMalTwkvhvZBdbXjTdQtckLYn" #"Q5+NEcmSpo12OaI6gaSlPdZ5iuPTgtpw" #
IDLE_TIMEOUT = 5 # tail timeout retry

# 初始化全域的 Parser 物件
log_parser = LogParser()

# ==========================================
# SSH Tail 核心異步產生器
# ==========================================
async def ssh_log_stream():
    while True:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print("[SSH] Connecting to remote host...")
            client.connect(
                SSH_HOST,
                port=SSH_PORT,
                username=SSH_USER,
                password=SSH_PASSWORD,
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
                            #  核心重構：改為呼叫 Class 實例的方法
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
# WebSocket 路由
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
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)