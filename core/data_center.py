import pandas as pd
import streamlit as st
import threading
from collections import deque

class GlobalDataCenter:
    ''' Global Shared Resource Center (encapsulated as Mutex Lock)'''
    def __init__(self):
        # Core mutexes: used to protect thread-safe DataFrame, dict, and deque operations.
        self.lock = threading.Lock()    

        # Globally unique shared data structure
        self.dl_failures = deque(maxlen=50000)
        self.ed_status = pd.DataFrame()
        self.ed_start_time = {}
        self.fsm_events = deque(maxlen=50000)
        self.pwr_status = {}
        self.power_ctrl_latest = {}
        self.power_ctrl_events = deque(maxlen=50000)

        self.bb_sched = deque(maxlen=50000)
        self.max_ra_alloc = deque(maxlen=50000)
        self.ll_lch_log_stats = {}
        self.ul_assignment = deque(maxlen=50000)
        self.gateway_info = {}
        self.tx_fsm_status = {}
        self.phy_rx_req = deque(maxlen=50000)

    def get_phy_rx_req(self):
        with self.lock:
            return list(self.phy_rx_req)
    def get_ed_status_df(self):
        with self.lock:
            return self.ed_status.copy()     
    def get_dl_failures(self):
        with self.lock:
            return list(self.dl_failures)
    def get_fsm_list(self):
        with self.lock:
            return list(self.fsm_events)
    def get_pwr_status_vals(self):
        with self.lock:
            return list(self.pwr_status.values())
    def get_power_ctrl_latest_vals(self):
        with self.lock:
            return list(self.power_ctrl_latest.values())
    def get_power_ctrl_events_copy(self):
        with self.lock:
            return list(self.power_ctrl_events)
    def get_bb_sched_list(self):
        with self.lock:
            return list(self.bb_sched)
    def get_max_ra_alloc_list(self):
        with self.lock:
            return list(self.max_ra_alloc)
    def get_ll_lch_log_stats_vals(self):
        with self.lock:
            return list(self.ll_lch_log_stats.values())
    def get_gateway_info(self):
        with self.lock:
            return self.gateway_info.copy()
    def get_ul_assignment_vals(self):
        with self.lock:
            return list(self.ul_assignment)
    def get_tx_fsm_snapshot(self):
        with self.lock:
            return self.tx_fsm_status.copy()
        
    def get_snapshot(self):
        ''' for Streamlit to get data'''
        with self.lock:
            return {
                "ed_status_df": self.ed_status.copy(),
                "dl_failures": list(self.dl_failures),
                "fsm_list": list(self.fsm_events),
                "pwr_status_vals": list(self.pwr_status.values()),
                "power_ctrl_latest_vals": list(self.power_ctrl_latest.values()),
                "power_ctrl_events_copy": list(self.power_ctrl_events),
                "bb_sched_list": list(self.bb_sched),
                "max_ra_alloc_list": list(self.max_ra_alloc),
                "ll_lch_log_stats_vals": list(self.ll_lch_log_stats.values()),
                "gateway_info": self.gateway_info.copy(),
                "ul_assignment_vals": list(self.ul_assignment),
                "tx_fsm_snapshot": self.tx_fsm_status.copy()
            }
        
    def append_dl_failures(self,item):
        with self.lock:
            self.dl_failures.append(item)
    
    def append_pwr_status(self,item):
        with self.lock:
            self.pwr_status[item["ed_id"]] = {
            "timestamp": item["timestamp"],
            "ed_id": item["ed_id"],
            "type": item["type"],
            "max_tx_pwr": item["max_tx_pwr"],
            "ul_tx_pwr": item["ul_tx_pwr"],
            "link_pwr": item["link_pwr"],
            "Meas_Spl": item["Meas_Spl"],
            }
    
    def append_max_ra_alloc(self,item):
        with self.lock:
            self.max_ra_alloc.append(item)

    def append_power_ctrl_events(self,item):
        with self.lock:
            self.power_ctrl_events.append(item)
            self.power_ctrl_latest[item['ed_id']] = item
    
    def append_phy_rx_req(self,item):
        with self.lock:
            self.phy_rx_req.append(item)
    
    def append_ll_lch_log_stats(self,item):
        with self.lock:
            self.ll_lch_log_stats[item['ed_id']] = item
    
    def append_gateway_info(self,item):
        with self.lock:
            self.gateway_info[item['uuid']] = item
    
    def append_ul_assignment(self,item):
        with self.lock:
            self.ul_assignment.append(item)
    
    def append_fsm_pattern(self,item):
        with self.lock:
            self.fsm_events.append(item)
    
    def append_bb_sched(self,item):
        chk_ra_valid = {k: v for k, v in item.items() if k != "event"}
        with self.lock:
            self.bb_sched.append(chk_ra_valid)
    
    def append_tx_fsm_status(self,item):
       with self.lock:
            self.tx_fsm_status[item['ed_id']] = item

    def append_ed_status(self,item):
        status_rows = []
        status_event = {k: v for k, v in item.items() if k != "event"}
        status_rows.append(status_event)
        df_raw = pd.DataFrame(status_rows)
        with self.lock:
            if self.ed_status.empty:
                self.ed_status = df_raw
            else:
                self.ed_status = pd.concat([self.ed_status, df_raw], ignore_index=True).tail(5000)

@st.cache_resource
def get_global_data():
    return GlobalDataCenter()

print("data_center loaded")

