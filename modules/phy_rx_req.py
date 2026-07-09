import streamlit as st
import pandas as pd
#st.set_page_config(layout="wide")

# --------------------------------------------------------
# Demo data
# --------------------------------------------------------
# sample data

def render_phy_rx_req(events):

    st.header("PHY_RX_REQ Statistics")
    if events.empty:
        st.info("No data ...")
        return
    
    count = len(events)
    if count < 10 :
        st.write(f"events count : {{len(events)}} < 2")
        return
    
    latest_sfn = max(e["sfn"] for e in events)
    display_sfns = { latest_sfn - 3,    latest_sfn - 4}
    tabs = st.tabs(["phy_rx_req",'phy_rx_req_table'])
    events = [e for e in events if e["sfn"] in display_sfns]    
    if not events:
        st.warning(f" Not found SFN {latest_sfn - 1} or {latest_sfn - 2} data)。")
        return
    else:
        st.write(f"events = {len(events)}")

    start_slot = 14
    end_slot = 39
    
    with tabs[0]:   
        # --------------------------------------------------------
        # Layout
        # --------------------------------------------------------
        left = 120
        slot_width = 45
        svg_width = left + (end_slot-start_slot+2)*slot_width
        svg_height = 480
        lane_y = { "CA":80,"FEC OFF":140,"FEC ON":200}
        channel_y = {}
        base = 250
        for ch in range(8):
            channel_y[ch] = base + (7-ch)*28

        # --------------------------------------------------------
        # SVG Begin
        # --------------------------------------------------------

        svg = f"""
        <svg
            width="{svg_width}"
            height="{svg_height}"
            style="background:#111;font-family:Arial">
        """

        # --------------------------------------------------------
        # Vertical Grid
        # --------------------------------------------------------
        current_sfn = events[0]["sfn"]
        # SFN Title
        svg += f"""
        <text
            x="{left}"
            y="18"
            fill="#00E5FF"
            font-size="18"
            font-weight="bold">
            SFN {current_sfn}
        </text>
        """

        # Slot Label
        for slot in range(start_slot, end_slot + 1):
            x = left + (slot - start_slot) * slot_width
            svg += f"""
            <line
                x1="{x}"
                y1="40"
                x2="{x}"
                y2="{svg_height-20}"
                stroke="#333"
                stroke-dasharray="4"/>

            <text
                x="{x+12}"
                y="36"
                fill="white"
                font-size="13">
                {slot}
            </text>
            """

        # --------------------------------------------------------
        # PHY Labels
        # --------------------------------------------------------

        for lane,y in lane_y.items():

            svg += f"""
            <text
                x="10"
                y="{y+20}"
                fill="white"
                font-size="15">
                {lane}
            </text>

            <line
                x1="100"
                y1="{y+18}"
                x2="{svg_width}"
                y2="{y+18}"
                stroke="#444"/>
            """

        # --------------------------------------------------------
        # Channel Labels
        # --------------------------------------------------------

        for ch in range(7,-1,-1):

            y = channel_y[ch]

            svg += f"""
            <text
                x="10"
                y="{y+13}"
                fill="white"
                font-size="14">
                CH{ch}
            </text>

            <line
                x1="100"
                y1="{y+8}"
                x2="{svg_width}"
                y2="{y+8}"
                stroke="#333"/>
            """

        # --------------------------------------------------------
        # Draw Events
        # --------------------------------------------------------
        slot_ch_lanes = {}
        for ev in events:
            for s in range(ev["slot"], ev["slot"] + ev["duration"]):
                for ch in ev["channels"]:
                    if (s, ch) not in slot_ch_lanes:
                        slot_ch_lanes[(s, ch)] = set()
                    slot_ch_lanes[(s, ch)].add(ev["lane"])

        OVERLAP_COLOR = "#1900FFEB"

        for e in events:
            x = left + (e["slot"]-start_slot)*slot_width
            width = e["duration"]*slot_width
            y = lane_y[e["lane"]]
            if y is None:
                st.warning(f"Unknown lane: {e['lane']}")
                continue
            # PHY BAR
            svg += f"""
            <rect
                x="{x}"
                y="{y}"
                width="{width}"
                height="36"
                rx="5"
                fill="{e['color']}">

                <title>
                {e['label']}
                Slot : {e['slot']}
                Duration : {e['duration']}
                Channels : {e['channels']}
                </title>

            </rect>
            """

            svg += f"""
            <text
                x="{x+8}"
                y="{y+23}"
                text-anchor="start"
                font-size="8"
                fill="black">
                {e['label']}
            </text>
            """

            # Draw Channel Usage

            for ch in e["channels"]:

                cy = channel_y[ch]
                is_overlap = any(
                    "FEC ON" in slot_ch_lanes.get((s, ch), set()) 
                    and "FEC OFF" in slot_ch_lanes.get((s, ch), set())
                    and "CA" in slot_ch_lanes.get((s, ch), set())
                    for s in range(e["slot"], e["slot"] + e["duration"]))

                current_ch_color = OVERLAP_COLOR if is_overlap else e['color']

                svg += f"""
                <rect
                    x="{x}"
                    y="{cy}"
                    width="{width}"
                    height="18"
                    rx="3"
                    fill="{current_ch_color}">

                    <title>
                    Channel {ch}
                    Slot {e['slot']}
                    Duration {e['duration']}
                    </title>

                </rect>
                """

        svg += "</svg>"

        # --------------------------------------------------------
        # Streamlit
        # --------------------------------------------------------

        st.title("PHY_RX_Timeline")
        st.components.v1.html(svg,height=540,scrolling=True)
    
        with tabs[1]:
                st.subheader("Events Raw Data:")
                df = pd.DataFrame(events)
                st.dataframe(df)