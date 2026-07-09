# **📡 RF Base Station Live Analyzer**
A real-time monitoring and visualization dashboard for RF Base Station.
RF Live Analyzer is a Streamlit-based web application designed to monitor, analyze, and visualize Base Station runtime information in real time. It connects to the RF log streaming service through WebSocket, parses incoming events, and presents them in an intuitive dashboard for debugging, performance analysis, and system monitoring.
---
## **Features**
-	📈 Real-time Dashboard
-	📡 Live WebSocket Log Streaming
-	📊 RF & PHY Visualization
-	📶 Power Control Monitoring
-	📋 ED Status Monitoring
-	📦 Traffic Statistics
-	🔄 FSM (Finite State Machine) State Statistics 
-	📑 Event Log Viewer
-	⚡ Automatic Refresh using st.fragment
-	🧩 Modular Page Architecture
---
## **System Architecture**
```text

                         RF
                            │
                       Runtime Logs
          Statistics ...   │
                            ▼
                  WebSocket Log Server
                            │
                            ▼
                 Background Queue Consumer
                            │
                            ▼
                    GlobalDataCenter
                            │
        ┌──────────┬────────┴─────────┬──────────┐
        ▼          ▼                  ▼          ▼
   ED Status   PHY RX Data      FSM Statistics  ...
        │          │                  │
        └──────────┴──────────┬───────┘
                              ▼
                    Streamlit Dashboard
                              │
                 Individual Pages (Fragment)
```

---
## **Project Structure**
```text
RF Live Analyzer
│
├── app.py                     # Streamlit entry point
│
├── pages/                     # Dashboard pages
│   ├── 01_Overview.py
│   ├── 02_ED_Status.py
│   ├── 03_PHY_RX_REQ.py
│   ├── 04_RF_Scheduler.py
│   ├── 05_FSM_Statistics.py
│   ├── 06_Power_Control.py
│   ├── 07_Traffic.py
│   ├── 08_Event_Log.py
│   └── 09_System_Status.py
│
├── modules/                   # Visualization modules
│   ├── ed_status.py
│   ├── phy_rx_req.py
│   ├── scheduler.py
│   ├── power_control.py
│   ├── traffic.py
│   └── GCT_PHY_FSM_Statistics.py
│
├── core/                      # Core components
│   ├── data_center.py
│   ├── background_consumer.py
│   ├── websocket_client.py
│   ├── queue_manager.py
│   └── render_helper.py
│
└── server.py                  # WebSocket log server
```
---
## **Data Flow**

```text
WebSocket
     │
     ▼
Receive JSON Event
     │
     ▼
Background Consumer
     │
     ▼
Normalize Event
     │
     ▼
GlobalDataCenter
     │
     ▼
Streamlit Fragment
     │
     ▼
Visualization Module
     │
     ▼
Dashboard
```
### How to Run the server 
# ==========================================
# remote SSH connection configuration
# ==========================================

#### Windows (Command Prompt / cmd)
```text
set SSH_HOST=IP_ADDRESS
set SSH_PASSWORD=PASSWORD
python server.py
ˋˋˋ
#### Windows (PowerShell)
ˋˋˋtext
   $env:SSH_HOST=IP_ADDRESS
   $env:SSH_PASSWORD=PASSWORD
   python server.py
ˋˋˋ
#### Linux / macOS
ˋˋˋtext
export SSH_HOST=IP_ADDRESS
export SSH_PASSWORD=PASSWORD
ˋˋˋ
### How to Run the app (front end)
```
# streamlit run app.py
```
---
## **Dashboard Pages**
### Overview
Displays the overall health of the Base Station.
Typical widgets include:
-	Connected ED
-	Current SFN
-	Queue Status
-	WebSocket Status
-	Throughput Summary

---
## **ED Status**
Displays all registered End Devices.
Information includes:
-	ED ID
-	Connection State
-	Connection Rate
-	Session Statistics
-	UL / DL Bytes
-	Registration Status
---
## **PHY RX Request**
Visualizes PHY RX scheduling information.
Features:
-	Resource Grid
-	Slot Allocation
-	Channel Usage
-	SFN Timeline
-	PHY RX Events
---
## **RF Scheduler**
Provides RF scheduling analysis.
Including:
-	RSSI Distribution
-	Scheduler Reference RSSI
-	Resource Allocation
-	UL Scheduling Statistics
---
## **Finite State Machine Statistics**
Displays PHY FSM decoding statistics.
Typical metrics:
-	IDLE  
-	PRE0 
-	SFD0
-	SFD1
-	PAYLOAD
-	Decode Success Rate
-	Channel Statistics
---
## **Power Control**
Monitors RF Power Control behavior.
Displays:
-	Link Power
-	UL RSSI
-	MCS
-	Power Offset
-	Waste Statistics
-	Historical Trend
---
## **Traffic**
Traffic analysis dashboard.
Including:
-	UL Bytes
-	DL Bytes
-	Throughput
-	Top Talkers
-	Session Statistics
---
## **Event Log**
Displays recent runtime events.
Examples:
-	Scheduler Events
-	Registration
-	Deregistration
-	Warning
-	Error
-	RF Events
---
## **System Status**
System runtime information.
Typical metrics:
-	Queue Length
-	WebSocket Connection
-	Background Thread
-	Memory Usage
-	Processing Rate
---
## **Core Components**
WebSocket Client
Responsible for:
-	Receiving runtime events
-	Automatic reconnect
-	JSON decoding
---
## **Background Consumer**
Responsible for:
-	Queue processing
-	Event classification
-	Data normalization
-	Updating GlobalDataCenter
---
## **GlobalDataCenter**
Acts as the in-memory data repository shared across all dashboard pages.
Responsibilities include:
-	Thread-safe data storage
-	Maintaining recent history
-	Providing query interfaces
-	Supporting real-time visualization
---
## **Streamlit Fragment**
Each dashboard page updates independently using:
```text
@st.fragment(run_every="6s")
```
Benefits:
-	Partial page refresh
-	Lower CPU usage
-	Better responsiveness
-	Independent dashboard updates

---
## **Design Philosophy**
The project follows a modular architecture.
-	Core handles data acquisition and storage.
-	Modules focus on visualization.
-	Pages organize the user interface.
-	GlobalDataCenter provides a shared, thread-safe data source.
This separation keeps the application easy to maintain and simplifies adding new dashboards or event types.
---
## **Requirements**
-	Python 3.11+
-	Streamlit 1.58+
-	pandas
-	plotly
-	FastAPI
-	websocket-client
---
## **Future Improvements**
-	SQLite event history
-	Historical trend analysis
-	User-configurable dashboard layouts
-	Alert and notification system
-	Export to CSV / Excel
-	Performance profiling
-	Multi-Base Station support
-	Dashboard authentication
---
License
Internal project for RF monitoring and analysis.
