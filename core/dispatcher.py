from core.data_center import get_global_data
data_center = get_global_data()

def dispatch_event(item):
    event = item.get("event")
    print(f"dispatch to data coneter: {event}")
    match event:
        
        case 'BBG_SAMPLE':
            data_center.append_bbg_sample(item)
        
        case 'FOI_SAMPLE':
            data_center.append_foi_sample(item)
        
        case 'TOA_SAMPLE':
            data_center.append_toa_sample(item)

        case 'ED_STATUS':
            data_center.append_ed_status(item)

        case 'DL_FAILED' | 'Deregister':
            data_center.append_dl_failures(item)

        case "PWR_Current_Status":
            data_center.append_pwr_status(item)
        
        case "MAX_RA_ALLOC":
            data_center.append_max_ra_alloc(item)
        
        case "FSM_PATTERN":
            data_center.append_fsm_pattern(item)
        
        case "Power_Ctrl":
            data_center.append_power_ctrl_events(item)
        
        case "phy_rx_req":
            data_center.append_phy_rx_req(item)
        
        case "ll_lch_log_stats":
            data_center.append_ll_lch_log_stats(item)
        
        case "gateway_info":
            data_center.append_gateway_info(item)
        
        case "ul_assignment":
            data_center.append_ul_assignment(item)
        
        case "chk_ra_valid":
            data_center.append_bb_sched(item)
        
        case "ll_lch_nack" | "ll_lch_tx_window_empty" | "ll_lch_invalid_ack_bpd" | "ll_lch_update_nesn" | "ll_lch_bpd_acked" | "ll_lch_accept_ack":
            ll_lch_message_merge(event,item)

def ll_lch_message_merge(event_name,item):
    match event_name:
        case 'll_lch_nack':
                ed_id = item.get("ed_id")
                if ed_id is not None:
                    fsm_status = data_center.tx_fsm_status.get(ed_id,{}) 
                    fsm_status[ed_id] = {
                        "timestamp": item.get("last_update_datetime"),
                        "state": "🟠 NACK_RETRANSMIT",
                        "invalid_cnt": 0,
                        "sfn": item.get("sfn"),
                        "lch_type": item.get("lch_type"),
                        "info": f"SN: {item.get('sn')} Requested to retransmit (Win_SN: {item.get('win_sn')})"}
                    data_center.append_tx_fsm_status(fsm_status)

        case 'll_lch_tx_window_empty':          
            ed_id = item.get("ed_id")
            if ed_id is not None:
                fsm_status = data_center.tx_fsm_status.get(ed_id ,{}) 
                fsm_status[ed_id] = {
                    "timestamp": item.get("last_update_datetime"),
                    "state": "🟢 WINDOW_EMPTY",
                    "invalid_cnt": 0,
                    "sfn": item.get("sfn"),
                    "lch_type": item.get("lch_type"),
                    "info": f"Clear the window. Peer_NESN: {item.get('peer_nesn')} / End_SN: {item.get('end_sn')}"
                }
                data_center.append_tx_fsm_status(fsm_status)

        case 'll_lch_invalid_ack_bpd': 
            ed_id = item.get("ed_id")
            if ed_id is not None:
                fsm_status = data_center.tx_fsm_status.get(ed_id, {"invalid_cnt": 0, "state": "🟡 TRANSMITTING"})
                new_cnt = fsm_status["invalid_cnt"] + 1                             
                current_state = "🔴 BPD_INVALID_ALARM" if new_cnt >= 3 else fsm_status["state"]                             
                fsm_status[ed_id] = {
                    "timestamp": item.get("last_update_datetime"),
                    "state": current_state,
                    "invalid_cnt": new_cnt,
                    "sfn": item.get("sfn"),
                    "lch_type": item.get("lch_type"),
                    "info": f"⚠️ Serial number out of bounds or invalid! Consecutive failures: {new_cnt} cnt (log: {item.get('line', '')})"
                }
                data_center.append_tx_fsm_status(fsm_status)
        
        case 'll_lch_update_nesn':
            ed_id = item.get("ed_id")
            if ed_id is not None: 
                fsm_status = data_center.tx_fsm_status.get(ed_id, {"invalid_cnt": 0, "state": "🟡 TRANSMITTING"})
                fsm_status[ed_id] = {
                    "timestamp": item.get("last_update_datetime"),
                    "state": "🟡 TRANSMITTING",
                    "invalid_cnt": 0,
                    "sfn": item.get("sfn"),
                    "lch_type": item.get("lch_type"),
                    "info": f"SN: {item.get('sn')} confirm (NESN: {item.get('nesn_info')})"
                }
                data_center.append_tx_fsm_status(fsm_status)
        
        case 'll_lch_bpd_acked':
            ed_id = item.get("ed_id")
            if ed_id is not None:  
                fsm_status = data_center.tx_fsm_status[ed_id] = {
                    "timestamp": item.get("last_update_datetime"),
                    "state": "🟡 TRANSMITTING",
                    "invalid_cnt": 0,
                    "sfn": item.get("sfn"),
                    "lch_type": item.get("lch_type"),
                    "info": f"SN: {item.get('sn')} Successfully received ACK。"
                }
                data_center.append_tx_fsm_status(fsm_status)

        case 'll_lch_accept_ack':
            ed_id = item.get("ed_id")
            if ed_id is not None:   
                fsm_status = data_center.tx_fsm_status[ed_id] = {
                    "timestamp": item.get("last_update_datetime"),
                    "state": "🟡 TRANSMITTING",
                    "invalid_cnt": 0,
                    "sfn": item.get("sfn"),
                    "lch_type": item.get("lch_type"),
                    "info": f"Implicitly Confirmed！Peer has accepted ,Latest expected NESN: {item.get('nesn')}"
                }
                data_center.append_tx_fsm_status(fsm_status)