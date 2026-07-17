# parser/parser.py
import re
from datetime import datetime

class LogParser:

    PRODUCT_TYPE_MAP = {
        "0": "Scone",
        "1": "Jelly"
    }

    def __init__(self):
        # 將所有正則表達式模式初始化為實例屬性

        self.phy_Rx_req_stats_pattern = re.compile(
        r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
        r"\[SFN:(?P<SFN>\d+):(?P<Slot>\d+)\]"
        r"\[PHY_RX_REQ\]\[(?P<Type>.*?):(?P<Val>\d+)\]\[.*?\]"
        r"\[(?P<Fec>.*?):(?P<Mcs>\d+)\]"
        r"\[NUM_CH_USED:(?P<Num>\d+)\]"
        r"\[DURATION:(?P<Dur>\d+)\]"
        r"\[CH_MASK:(?P<Mask>\d+)\]"
        )

        self.gateway_info_pattern = re.compile(
            r"\[(?P<uuid>[0-9A-Fa-f]{32})\]"
            r"\[v(?P<version>\d+\.\d+\.\d+\.\d+(?:-[0-9A-Za-zT]+)?)\]"
            r"\[RUNTIME:(?P<runtime>\d+)\]"
            r"\[UPTIME:(?P<uptime>\d+)\]"
        )

        self.tx_queue_drained_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[SFN:(?P<sfn>\d+)\]"
            r"\[ED:(?P<ed>\d+)\]\[(?P<lch_type>\w+)\].*?"
            r"\[PEER_NESN:(?P<peer_nesn>\d+)\]\[NO_TX_WIN\]"
            r"\[END_SN:(?P<end_sn>\d+)\]"
        )
        self.tx_queue_nack_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[SFN:(?P<sfn>\d+):\d+\]"
            r"\[ED:(?P<ed>\d+)\]"
            r"\[(?P<lch_type>\w+)\]"
            r"\s\[(?P<ack_stats>\w+:\w+)\]"
            r"\[SN:(?P<sn>\d+)\]"
            r"\[WIN_SN:(?P<win_sn>\d+)\]"
        )
        self.invalid_bpd_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"ED\[(?P<ed>\d+)\].*?Invalid ACK BPD (?P<invalid_cnt>\d+).*?"
            r"/(?P<check_valid>\d+)"
        )
        self.nesn_pattern = re.compile(
            r"(?P<date>\d{8})\s+(?P<time>\d{2}:\d{2}:\d{2}\.\d{4,6})\]:\s+"
            r"\[SFN:(?P<sfn>\d+)(?::\d+)?\]"
            r"\[ED:(?P<ed>\d+)\]\[(?P<lch_type>[^\]]+)\].*?"
            r"\[SN:(?P<sn>\d+)\]\s+Update\s+NESN:(?P<old_nesn>\d+)->(?P<new_nesn>\d+)"
        )
        self.accept_ack_pattern = re.compile(
            r"(?P<date>\d{8})\s+(?P<time>\d{2}:\d{2}:\d{2}\.\d{4,6})\]:\s+"
            r"\[SFN:(?P<sfn>\d+)(?::\d+)?\]"
            r"\[ED:(?P<ed>\d+)\]\[(?P<lch_type>[^\]]+)\].*?"
            r"\[ACCEPT_ACK\]\[NESN:(?P<nesn>\d+)\]"
        )
        self.bpd_acked_pattern = re.compile(
            r"(?P<date>\d{8})\s+(?P<time>\d{2}:\d{2}:\d{2}\.\d{4,6})\]:\s+"
            r"\[SFN:(?P<sfn>\d+)\]\[ED:(?P<ed>\d+)\]"
            r"\[(?P<lch_type>[^\]]+)\].*?"
            r"\[SN:(?P<sn>\d+)\]\[BPD is ACKed\]"
        )
        self.ul_assignment_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[SFN\:(?P<SFN_number>\d+)\]"
            r"\[ED:(?P<ed>\d+)\]"
            r"\[PRIO:(?P<prio>\d+)\]"
            r"\[S:(?P<slice_no>\d+)\:(?P<next_slice_no>\d+)\]"
            r"\[CH:(?P<channle>\d+)\]"
            r"\[(?P<mcs_name>\w+):(?P<mcs_code>\d+)\]"
            r"\[duration:(?P<duration>\d+)\]"
        )
        self.max_ra_alloc_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[SFN:(?P<sfn>\d+)\]"
            r"\[MAX_RA_ALLOC\]"
            r"\[EVEN:(?P<even>\d+)\]"
            r"\[ODD:(?P<odd>\d+)\]"
            r"\[PENDING_REG:(?P<pending>\d+)\]"
            r"\[CONNECTED/TOTAL:(?P<connected>\d+)/(?P<total>\d+)\]"
            r"\[CA_RATIO:(?P<ca_ratio>\d+)\]"
            r"\[CA_PROHIBIT:(?P<ca_prohibit>\d+)\]"
        )
        self.ll_lch_log_stats_re = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[ED:(?P<ed>\d+)\]"
            r"\[(?P<lch_type>\w+)\]\s\[Stats\]"
            r"\[RX\:(?P<rx_cnt>\d+)\:(?P<rx_byte>\w+)\]"
            r"\[TX\:(?P<tx_cnt>\d+)\:(?P<tx_byte>\d+)\]"
            r"\[RETX\:(?P<retx_cnt>\d+)\:(?P<retx_byte>\d+)\]"
        )
        self.POWER_Ctrl_RE = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\]"
            r".*?"
            r"\[SFN:\d+:\d+\]"
            r"\[ED:(?P<ed>\d+)\]"
            r"\[TYPE:(?P<type>\d+)\]"
            r"\[(?P<tech>[NW])B_UL_RSSI:(?P<rssi>-?\d+)\]"
            r".*?"
            r"\[(?P<ulmcsname>\w+):(?P<mcscode>\d+)\]"
            r"\[TX_PWR\]"
            r"\[MIN:(?P<min_tx_pwr>-?\d+)\]"
            r"\[MAX:(?P<max_tx_pwr>-?\d+)\]"
            r"\[UL:(?P<ul_tx_pwr>-?\d+)\]"
            r"\[LINK_PWR:(?P<link_pwr_old>-?\d+)->(?P<link_pwr_new>-?\d+):(?P<avg_count>\d+)\]"
            r"(?:\[RRM_WASTE:(?P<waste>\d+)\])?"
            r"(?:\[LINK_PWR_OFFSET:(?P<link_pwr_offset>-?\d+)\])?"
        )
        self.Power_Ctrl_Status_RE = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[ED:(?P<ed>\d+)\]\[TYPE:(?P<type>\d+)\].*?"
            r"\[TX_PWR\]\[MAX:(?P<max_tx_power>-?\d+)\]\[UL:(?P<ul_tx_power>-?\d+)\]\[LINK_PWR:(?P<link_pwr>-?\d+):(?P<avg_count>\d+)\]"
        )
        self.Deregister_RE = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[ED:(?P<ed>\d+)\].*?"
            r"\[Deregister\].*?"
            r"\[Cause:(?P<reason>[^:]+):(?P<code>\d+)\]"
        )
        self.DL_FAILED_RE = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[ED:(?P<ed>\d+)\].*?"
            r"\[(?P<reason>[A-Z0-9_]+):(?P<code>\d+)\]\[failed to send\]"
        )
        self.mini_dcu_fsm_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[BPD Type:(?P<bpd_type>\w+)\]"
            r"\[FSM_ST_MAX:(?P<ch0>\d+):(?P<ch1>\d+):(?P<ch2>\d+):(?P<ch3>\d+):(?P<ch4>\d+):(?P<ch5>\d+):(?P<ch6>\d+):(?P<ch7>\d+)\]"
        )

        self.mini_dcu_rssi_raw_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[RSSI_raw\:(?P<ch0>-?\d+)\:(?P<ch1>-?\d+)\:(?P<ch2>-?\d+)\:(?P<ch3>-?\d+)\:(?P<ch4>-?\d+)\:(?P<ch5>-?\d+)\:(?P<ch6>-?\d+)\:(?P<ch7>-?\d+)\]"
        )

        self.mini_dcu_foi_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[FOI:(?P<ch0>\d+)\:(?P<ch1>\d+)\:(?P<ch2>\d+)\:(?P<ch3>\d+)\:(?P<ch4>\d+)\:(?P<ch5>\d+)\:(?P<ch6>\d+)\:(?P<ch7>\d+)\]"
        )

        self.mini_dcu_toa_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[TOA:(?P<ch0>\d+)\:(?P<ch1>\d+)\:(?P<ch2>\d+)\:(?P<ch3>\d+)\:(?P<ch4>\d+)\:(?P<ch5>\d+)\:(?P<ch6>\d+)\:(?P<ch7>\d+)\]"
        )

        self.mini_dcu_bbg_pattern = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[BBG:(?P<ch0>\d+)\:(?P<ch1>\d+)\:(?P<ch2>\d+)\:(?P<ch3>\d+)\:(?P<ch4>\d+)\:(?P<ch5>\d+)\:(?P<ch6>\d+)\:(?P<ch7>\d+)\]"
        )
        
        self.BB_SCHED_RE = re.compile(
            r"\[(?P<date>\d{8})\s(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\].*?"
            r"\[SFN:(?P<sfn>\d+)\]"
            r"\[ED:(?P<ed_id>\d+)\]"
            r"\[(?P<channel>UL_RA\d+)\]"
            r"\[(?P<action>[A-Z_]+)\]"
            r"\[DURATION:(?P<duration>\d+)\]"
            r"\[PRIO:(?P<prio_cur>\d+):(?P<prio_max>\d+)\]"
            r"(?:\[UL_WASTE:(?P<ul_waste>\d+)\])?"
            r"\[RSSI:(?P<rssi>-?\d+)\]"
            r"\[RSSI_REF:(?P<rssi_ref>-?\d+)\]"
        )

    # ==========================================
    # 核心進入點方法 (外部呼叫這個)
    # ==========================================
    def parse_line(self, line: str):
        event = None

        if "SFN" in line and "ED" in line and "S:" in line and "duration" in line:
            event = self._parse_ul_assignment_line(line)
        elif "vBS" in line and 'RUNTIME' in line and 'UPTIME' and 'FILE' in line:
            event = self._parse_gateway_info_line(line)
        
        if "FSM_ST_MAX" in line:
            event = self._parse_gct_fsm_pattern_line(line)
        
        if "NB_UL_RSSI" in line and "LINK_PWR" in line and 'MIN' in line:
            row = self._parse_power_ctrl(line)
            if row:
                row["status"] = self._compute_status(row)
            event = row

        if 'CH_MASK' in line and 'NUM_CH_USED' in line:
            return self._parse_phy_rx_req_line(line)
        
        if "TYPE" in line and "LINK_PWR" in line:
            event = self._parse_ed_power_ctrl_status(line)
        
        if 'RETX' in line and ("LCH_UAC" in line or "LCH_UAD" in line):
            event = self._parse_ll_lch_log_stats_line(line)
        
        if 'NO_TX_WIN' in line:
            event = self._parse_tx_queue_drained_line(line)
        
        if 'WIN_SN' in line:
            event = self._parse_tx_queue_nack_line(line)
        
        if 'Update NESN' in line:
            event = self._parse_ll_lch_update_nesn_line(line)
        
        if 'BPD is ACKed' in line:
            event = self._parse_ll_lch_bpd_acked_line(line)
        
        if 'MAX_RA_ALLOC' in line and 'PENDING_REG' in line:
            event = self._parse_max_ra_alloc_line(line)
        
        if "RSSI_REF" in line:
            event = self._parse_bb_sched(line)
        
        if "failed to send" in line:
            event = self._parse_DL_failed_event_line(line)
        if "SCHED_UL" in line:
            event = self._parse_ED_Status_line(line)
        if "Deregister" in line:
            event = self._parse_Deregister_event_line(line)

        if event:
            try:
                return self._normalize(event)
            except Exception as e:
                print(f" normalize {e}")
                print(event)
        return None

    # ==========================================
    # 內部解析子方法 (前方加底線代表私有方法)
    # ==========================================

    def _mask_to_channels(self,mask: str):
        channels = []
        for ch, bit in enumerate(mask[::-1]):
            if bit == "1":
                channels.append(ch)
        return channels
    
   

    def _type_to_color(self,type:str,fec_type:str):
        if type == "CA":
            return "#2196F3"
        fecone = [7,10]
        if type == 'NORMAL' and "FecOn" in fec_type:
            return "#FFC107"
        else: # type == 'NORMAL' and "Fecoff" in fec_type:
            return "#8BC34A"
    
    def _get_lane_from_event(self,type:str,fec_type:str):
        # 根據您的需求判斷 lane
        if type == "CA":
            return "CA"
        elif type == 'NORMAL' and "FecOn" in fec_type:
            return "FEC ON"
        else:
            return "FEC OFF"


    def _parse_phy_rx_req_line(self,line: str) -> dict:
        m = self.phy_Rx_req_stats_pattern.search(line)
        if not m:
            return None
        return{
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'ed_id': "UNKNOWN",
            'event' : "phy_rx_req",
            'sfn' :  int(m.group('SFN')),
            'slot' : int(m.group('Slot')),
            'color' : self._type_to_color(m.group('Type'),m.group('Fec')),
            'fec' : m.group('Fec'),
            'label' : f"{int(m.group('Mcs'))} Num {int(m.group('Num'))}",
            'duration' : int(m.group('Dur')),
            'lane' : self._get_lane_from_event(m.group('Type'),m.group('Fec')),
            "channels": self._mask_to_channels(m.group("Mask"))
        }

    def _parse_tx_queue_nack_line(self, line: str) -> dict:
        m = self.tx_queue_nack_pattern.search(line)
        if not m:
            return None
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'last_update_datetime': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'll_lch_nack',
            'sfn': int(m.group('sfn')),
            'ed_id': int(m.group('ed')),
            'tx_win_empty': False,
            'lch_type': m.group('lch_type'),
            'sn': int(m.group('sn')),
            'win_sn': int(m.group('win_sn'))
        }

    def _parse_ll_lch_accept_ack_line(self, line: str) -> dict:
        m = self.accept_ack_pattern.search(line)
        if not m:
            return None
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'last_update_datetime': datetime.strptime(f"{m.group('date')} {m.group('time')[:-2]}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'll_lch_accept_ack',
            'sfn': int(m.group('sfn')),
            'ed_id': int(m.group('ed')),
            'lch_type': m.group('lch_type'),
            'nesn': int(m.group('nesn'))
        }

    def _parse_ll_lch_update_nesn_line(self, line: str) -> dict:
        m = self.nesn_pattern.search(line)
        if not m:
            return None
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'last_update_datetime': datetime.strptime(f"{m.group('date')} {m.group('time')[:-2]}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'll_lch_update_nesn',
            'sfn': int(m.group('sfn')),
            'ed_id': int(m.group('ed')),
            'lch_type': m.group('lch_type'),
            'sn': int(m.group('sn')),
            'nesn_info': f"{m.group('old_nesn')}->{m.group('new_nesn')}"
        }

    def _parse_ll_lch_bpd_acked_line(self, line: str) -> dict:
        m = self.bpd_acked_pattern.search(line)
        if not m:
            return None
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'last_update_datetime': datetime.strptime(f"{m.group('date')} {m.group('time')[:-2]}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'll_lch_bpd_acked',
            'sfn': int(m.group('sfn')),
            'ed_id': int(m.group('ed')),
            'lch_type': m.group('lch_type'),
            'sn': int(m.group('sn'))
        }

    def _parse_tx_queue_drained_line(self, line: str) -> dict:
        m = self.tx_queue_drained_pattern.search(line)
        if not m:
            return None
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'last_update_datetime': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'll_lch_tx_window_empty',
            'sfn': int(m.group('sfn')),
            'ed_id': int(m.group('ed')),
            'tx_win_empty': True,
            'lch_type': m.group('lch_type'),
            'peer_nesn': int(m.group('peer_nesn')),
            'end_sn': int(m.group('end_sn'))
        }

    def _parse_gateway_info_line(self, line: str) -> dict:
        m = self.gateway_info_pattern.search(line)
        if not m:
            return None
        return {
            'event': 'gateway_info',
            'uuid': m.group('uuid'),
            "ed_id": "UNKNOWN",
            'version': m.group('version'),
            'runtime': int(m.group('runtime')),
            'uptime': int(m.group('uptime'))
        }

    def _parse_ul_assignment_line(self, line: str) -> dict:
        m = self.ul_assignment_pattern.search(line)
        if not m:
            return None 
        return {
            'timestamp': datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y%m%d %H:%M:%S.%f"),
            'event': 'ul_assignment',
            'sfn': int(m.group('SFN_number')),
            "ed_id": int(m.group('ed')),
            'prio': int(m.group('prio')),
            'slice_no': int(m.group('slice_no')),
            'next_slice_no': int(m.group('next_slice_no')),
            'channle': int(m.group('channle')),
            'mcs_name': m.group('mcs_name'),
            'mcs_code': int(m.group('mcs_code')),
            'duration': int(m.group('duration'))
        }

    def _parse_max_ra_alloc_line(self, line: str) -> dict:
        m = self.max_ra_alloc_pattern.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            'timestamp': datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            'event': 'MAX_RA_ALLOC',
            "ed_id": "UNKNOWN",
            'sfn': int(m.group('sfn')),
            'even': int(m.group('even')),
            'odd': int(m.group('odd')),
            'pending': int(m.group('pending')),
            'connected': int(m.group('connected')),
            'total': int(m.group('total')),
            'ca_ratio': int(m.group('ca_ratio'))
        }
        
    def _parse_ll_lch_log_stats_line(self, line: str) -> dict:
        m = self.ll_lch_log_stats_re.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "ll_lch_log_stats",
            "ed_id": int(m.group('ed')),
            "lch_type": m.group('lch_type'),
            'rx_cnt': int(m.group('rx_cnt')),
            'rx_byte': int(m.group('rx_byte')),
            'tx_cnt': int(m.group('tx_cnt')),
            'tx_byte': int(m.group('tx_byte')),
            'retx_cnt': int(m.group('retx_cnt')),
            'retx_byte': int(m.group('retx_byte'))
        }

    def _parse_gct_fsm_pattern_line(self, line: str) -> dict:
        m = self.mini_dcu_fsm_pattern.search(line)
        if not m:
            return None   
        ts_str = f"{m.group('date')} {m.group('time')}"
        subchannels = [int(m.group(f'ch{i}')) for i in range(8)]
        return {
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "FSM_PATTERN",
            "ed_id": "UNKNOWN",
            "bpd_type": m.group("bpd_type"),
            "subchannel_0": subchannels[0],
            "subchannel_1": subchannels[1],
            "subchannel_2": subchannels[2],
            "subchannel_3": subchannels[3],
            "subchannel_4": subchannels[4],
            "subchannel_5": subchannels[5],
            "subchannel_6": subchannels[6],
            "subchannel_7": subchannels[7],
        }

    def _parse_bb_sched(self, line: str) -> dict:
        m = self.BB_SCHED_RE.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "chk_ra_valid",
            "ed_id": int(m.group('ed_id')),
            'sfn': int(m.group('sfn')),
            "ul_ra_group": (m.group('channel')),
            "status": m.group('action'),
            'duration': int(m.group('duration')),
            'rssi': int(m.group('rssi')),
            'rssi_ref': int(m.group('rssi_ref')),
            'ul_waste': int(m.group("ul_waste")) if m.group("ul_waste") is not None else None,
            'prio_cur': int(m.group('prio_cur')),
            'prio_max': int(m.group('prio_max'))
        }

    def _parse_power_ctrl(self, line: str) -> dict:
        m = self.POWER_Ctrl_RE.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}" 
        return {
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "Power_Ctrl",
            "ed_id": int(m.group("ed")),
            "type": m.group('type'),
            "nb_ul_rssi": int(m.group('rssi')),
            "ul_mcs_name": m.group('ulmcsname'), 
            'mcs_code': int(m.group('mcscode')),
            'min_tx_pwr': int(m.group('min_tx_pwr')),
            'max_tx_pwr': int(m.group('max_tx_pwr')),
            'ul_tx_pwr': int(m.group('ul_tx_pwr')),
            'link_pwr_old': int(m.group('link_pwr_old')),
            'link_pwr_new': int(m.group('link_pwr_new')),
            'avg_count': int(m.group('avg_count')),
            'waste': int(m.group("waste")) if m.group("waste") is not None else None,
            'link_pwr_offset': int(m.group("link_pwr_offset")) if m.group("link_pwr_offset") is not None else None,
        }

    def _parse_ed_power_ctrl_status(self, line: str) -> dict:
        m = self.Power_Ctrl_Status_RE.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            "ed_id": int(m.group("ed")),
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "PWR_Current_Status",
            "type": self.PRODUCT_TYPE_MAP.get(m.group("type"), "Unknown"),
            'max_tx_pwr': int(m.group('max_tx_power')),
            'ul_tx_pwr': int(m.group('ul_tx_power')),
            'link_pwr': int(m.group('link_pwr')),
            'Meas_Spl': int(m.group('avg_count')), 
        }

    def _parse_Deregister_event_line(self, line: str) -> dict:
        m = self.Deregister_RE.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            "ed_id": int(m.group("ed")),
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "Deregister",
            "reason": m.group("reason"),
            "reason_code": int(m.group("code"))
        }

    def _parse_DL_failed_event_line(self, line: str) -> dict:
        m = self.DL_FAILED_RE.search(line)
        if not m:
            return None
        ts_str = f"{m.group('date')} {m.group('time')}"
        return {
            "ed_id": int(m.group("ed")),
            "timestamp": datetime.strptime(ts_str, "%Y%m%d %H:%M:%S.%f"),
            "event": "DL_FAILED",
            "reason": m.group("reason"),
            "reason_code": int(m.group("code"))
        }

    def _parse_ED_Status_line(self, line: str) -> dict:
        ts_match = re.search(r'\[(\d{8} \d{2}:\d{2}:\d{2}\.\d+)\]', line)
        sfn_match = re.search(r'\[SFN:(\d+)\]', line)
        ed_match = re.search(r'\[ED:(\d+)\]', line)
        uuid_match = re.search(r'\[([0-9A-F]{32}):(\d+):(\d+)\]', line)
        age_match = re.search(r'\[AGE:(\d+)\]', line)
        join_match = re.search(r'\[JOIN_UL:(\d+)\]', line)
        ul_match = re.search(r'\[UL:(\d+):(\d+)\]', line)
        counters_match = re.search(r'\[COUNTERS\].*?\[UL:(\d+):(\d+)B\].*?\[DL:(\d+):(\d+)B\]', line)
        pcounters_match = re.search(r'\[P-COUNTERS\].*?\[UL:(\d+):(\d+)B\].*?\[DL:(\d+):(\d+)B\]', line)

        if not (ts_match and sfn_match and ed_match and uuid_match and age_match):
            return None

        ts = datetime.strptime(ts_match.group(1), "%Y%m%d %H:%M:%S.%f")
        registered = int(uuid_match.group(2))
        connected = int(uuid_match.group(3))
        connect_rate = (connected / registered * 100 if registered > 0 else 0)
        state = "CONNECTED" if ul_match else "REGISTERED"

        data = {
            "timestamp": ts,
            "sfn": int(sfn_match.group(1)),
            "ed_id": int(ed_match.group(1)),
            "event": "ED_STATUS",
            "uuid": uuid_match.group(1),
            "state": state,
            "registered_count": registered,
            "connected_count": connected,
            "connect_rate": round(connect_rate, 2),
            "age_sec": int(age_match.group(1)),
            "join_schedule_count": 0,
            "ul_schedule_count": 0,
            "ul_schedule_interval": 0,
            "ul_rx_count": 0,
            "ul_rx_bytes": 0,
            "dl_tx_count": 0,
            "dl_tx_bytes": 0,
            "total_ul_rx_count": 0,
            "total_ul_rx_bytes": 0,
            "total_dl_tx_count": 0,
            "total_dl_tx_bytes": 0,
            "ul_efficiency": None,
        }

        if join_match:
            data["join_schedule_count"] = int(join_match.group(1))
        if ul_match:
            data["ul_schedule_count"] = int(ul_match.group(1)) if ul_match.group(1) is not None else 0
            data["ul_schedule_interval"] = int(ul_match.group(2)) if ul_match.group(2) is not None else 0
        if counters_match:
            data["ul_rx_count"] = int(counters_match.group(1)) if counters_match.group(1) is not None else 0
            data["ul_rx_bytes"] = int(counters_match.group(2)) if counters_match.group(2) is not None else 0
            data["dl_tx_count"] = int(counters_match.group(3)) if counters_match.group(3) is not None else 0
            data["dl_tx_bytes"] = int(counters_match.group(4)) if counters_match.group(4) is not None else 0
        if pcounters_match:
            data["total_ul_rx_count"] = int(pcounters_match.group(1)) if pcounters_match.group(1) is not None else 0
            data["total_ul_rx_bytes"] = int(pcounters_match.group(2)) if pcounters_match.group(2) is not None else 0
            data["total_dl_tx_count"] = int(pcounters_match.group(3)) if pcounters_match.group(3) is not None else 0
            data["total_dl_tx_bytes"] = int(pcounters_match.group(4)) if pcounters_match.group(4) is not None else 0
        if data["ul_schedule_count"] > 0:
            data["ul_efficiency"] = round(data["ul_rx_count"] / data["ul_schedule_count"] * 100, 2)

        return data

    def _compute_status(self, data, min_rx_sens=-115, margin=5):
        ul = data["ul_tx_pwr"]
        max_p = data["max_tx_pwr"]
        link = data["link_pwr_new"]
        offset = data.get("link_pwr_offset")
        waste = data.get("waste")
        critical_threshold = min_rx_sens + margin

        if offset is None and waste is None:
            if ul >= max_p:
                return "BASIC_MAX_POWER"
            if link < critical_threshold:
                return "BASIC_CRITICAL"
            return "BASIC"
        if ul >= max_p:
            if link < critical_threshold:
                return "MAX_POWER_WEAK"
            return "MAX_POWER"
        if waste is not None and waste > 0:
            return "OVERPOWERED"
        if offset is not None and offset < 0:
            return "OPTIMIZING"
        if offset is not None and offset > 0:
            return "BOOSTING"
        return "STABLE"

    def _normalize(self, event: dict):
        try:
            if not event:
                return None
            evt = event.get("event")
            if not evt:
                return None
            
            # 1. 先建立基礎的最外層字典
            base = {
                "timestamp": event.get("timestamp"),
                "event": evt,
            }

            # 2. 自動動態檢查：如果原始資料有 ed_id，就把它保留在最外層
            if "ed_id" in event:
                base["ed_id"] = event.get("ed_id")

            # 3. 把其餘的衍生欄位包進 payload，並排除已經放在最外層的欄位
            payload = {
                k: v for k, v in event.items()
                if k not in ["timestamp", "event", "ed_id"]
            }
            base.update(payload)
            
            return base
        except Exception as e:
            print(f"normalize Error:{e}, Event:{event}")
            return None