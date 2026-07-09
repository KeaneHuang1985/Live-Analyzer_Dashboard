import websocket
import streamlit as st
import json
import time
import pandas as pd
import threading
from core.background_consumer import background_queue_consumer
from core.queue_manager import get_global_queue
from core.data_center import get_global_data

GLOBAL_QUEUE = get_global_queue()
DATA_CENTER = get_global_data()
# =========================
# WebSocket 數據接入
# =========================
def on_message(ws, message):
    try:
        data = json.loads(message)
        data["timestamp"] = pd.to_datetime(data["timestamp"]).tz_localize(None)
        event_name = data.get("event")
        print(f"Recvice : {event_name}")
        GLOBAL_QUEUE.put(data)
    except Exception as e:
        print("parse error:", e)

@st.cache_resource
def init_background_threads():
    """ Ensure that WebSocket reception and background Consumer threads are started only once across the entire server. """
    def on_close(ws, code, reason):
        print(f"Closed: {code}, {reason}")

    def on_error(ws, error):
        print(f"Error: {error}")

    def on_open(ws):
        print("[WS] Connected")

    def run_ws():
        while True:
            try:
                ws = websocket.WebSocketApp(
                    "ws://127.0.0.1:8000/ws",
                    on_open=on_open,
                    on_message=on_message,
                    on_close=on_close,
                    on_error=on_error
                    )
                
                ws.run_forever(
                    ping_interval=30,
                    ping_timeout=10
                    )
                
            except Exception as e:
                print(f"[WS][Exception][{e}]")

            print("[WS] Reconnecting in 5 seconds...")
            time.sleep(5)

    threading.Thread(target=run_ws, daemon=True).start()
    threading.Thread(target=background_queue_consumer,args=(GLOBAL_QUEUE,DATA_CENTER), daemon=True).start()
    return True