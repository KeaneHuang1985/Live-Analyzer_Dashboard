import time
import queue
import queue
import pandas as pd
from core.dispatcher import dispatch_event


# =========================
# Background Consumer (背景解耦寫入，並使用 Lock 保護)
# =========================
def background_queue_consumer(GLOBAL_QUEUE,DATA_CENTER):
    """
    Independent background thread: Dedicated to periodically processing queues and safely writing data to DATA_CENTER.\n
    Completely independent of the Streamlit frontend refresh lifecycle."""

    while True:
        status_rows = []
        while not GLOBAL_QUEUE.empty():
            try:
                item = GLOBAL_QUEUE.get(timeout=1.0)
                event_name = item.get("event")

                print(f"Receive the {event_name}")
                # call match fuction do update 
                dispatch_event(item)
                while not GLOBAL_QUEUE.empty():
                    try:
                        next_item = GLOBAL_QUEUE.get_nowait()
                        dispatch_event(next_item)
                    except queue.Empty:
                        break
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error event_name : {event_name}")
                print(f"Error processing item in background thread: {e}") 

        if status_rows:
            new_df = pd.DataFrame(status_rows)
            DATA_CENTER.update_df(new_df)
            status_rows.clear()
        time.sleep(0.05)

