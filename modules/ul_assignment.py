import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

def render_ul_assignment_dashboard(filtered_df: pd.DataFrame):
    st.title("📡 PHY UL Resource Grid & Link Adaptation Analysis")

    if filtered_df.empty:
        st.info("render_ll_lch_stats No data ...")
        return
    if filtered_df.empty:
        st.warning("No data available for the selected channels.")
        return
    # --- 核心 KPI  ---
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Grants", f"{len(filtered_df)}", help="Total number of dispatches") 
    # 計算眾數 (Mode) 替代無意義的純平均值
    if 'mcs_code' in filtered_df.columns and not filtered_df['mcs_code'].empty:
        most_common_mcs = filtered_df['mcs_code'].mode().iloc[0]
    else:
        most_common_mcs = 0
        
    kpi2.metric(
        label="Top MCS", 
        value=f"MCS {most_common_mcs}", help="Current mainstream modulation codes"
    )
    
    kpi3.metric("Active EDs", f"{filtered_df['ed_id'].nunique()}")
    
    # 計算 FEC 啟用率與關閉率
    fec_total = len(filtered_df)
    fec_on_cnt = filtered_df['mcs_name'].str.contains('FecOn').sum()
    fec_off_cnt = filtered_df['mcs_name'].str.contains('FecOff').sum()
    
    kpi4.metric("FEC ON Rate", f"{(fec_on_cnt / fec_total * 100):.1f}%", help="Error correction activation rate")
    kpi5.metric("FEC OFF Rate", f"{(fec_off_cnt / fec_total * 100):.1f}%", help="Error correction deactivation rate")
    
    st.subheader("Time-Frequency Resource Grid Analysis")

    # 建立動態且連續的 Slot 範圍（根據資料動態決定，預防 Hardcode 範圍不對齊）
    min_s = int(filtered_df['slice_no'].min())
    max_s = int(filtered_df['slice_no'].max())
    # 保留一點前後緩衝空間，或至少包含 Slot 20 ~ 41
    plot_min_slot = min(20, min_s)
    plot_max_slot = max(41, max_s)
    
    all_channels = np.arange(0, 8)  # 強制包含硬體定義的 CH 0 ~ 7
    all_slots = np.arange(plot_min_slot, plot_max_slot + 1, 1)

    heatmap_target = st.selectbox(
        "Heatmap Color Target:",
        ["Time-frequency resource grid hotspot map", "Terminal device priority scheduling heatmap"]
    )

    if heatmap_target == "Time-frequency resource grid hotspot map":
        # ==========================================
        # 核心優化：還原「時頻資源網格」連續性與空閒格
        # ==========================================
        # 1. 建立空矩陣
        z_grid = np.zeros((len(all_channels), len(all_slots)))
        text_grid = np.empty((len(all_channels), len(all_slots)), dtype=object)
        text_grid.fill("")
        hover_grid = np.empty((len(all_channels), len(all_slots)), dtype=object)
        hover_grid.fill("")
        
        # 2. 計算每個時頻格子的 Grant 累計數量
        grid_counts = filtered_df.groupby(['channle', 'slice_no']).size().reset_index(name='count')
        
        for _, row in grid_counts.iterrows():
            if row['channle'] in all_channels and row['slice_no'] in all_slots:
                ch_idx = np.where(all_channels == row['channle'])[0][0]
                slot_idx = np.where(all_slots == row['slice_no'])[0][0]
                z_grid[ch_idx, slot_idx] = row['count']
                text_grid[ch_idx, slot_idx] = str(row['count'])
        
        # 3. 建立對應的 Hover 資訊
        for ch_idx, ch in enumerate(all_channels):
            for s_idx, s in enumerate(all_slots):
                cnt = int(z_grid[ch_idx, s_idx])
                if cnt > 0:
                    hover_grid[ch_idx, s_idx] = (
                        f"<b>channle (Freq)</b>: CH {ch}<br>"
                        f"<b>slot (Time)</b>: Slot {s}<br>"
                        f"<b>Grant Count</b>: {cnt} 次<extra></extra>"
                    )
                else:
                    status = "🔒 Odd-numbered channels (protection zone disabled)" if ch % 2 != 0 else "Idle"
                    hover_grid[ch_idx, s_idx] = f"<b>Channle</b>: CH {ch}<br><b>Slot</b>: Slot {s}<br><b>status</b>: {status}<extra></extra>"

        fig_grid = go.Figure(
            data=go.Heatmap(
                z=z_grid,
                x=all_slots,
                y=all_channels.astype(str),
                colorscale="Viridis",
                text=text_grid,
                texttemplate="%{text}",
                textfont={"size": 11},
                
                # 💡 重點修改：將 textsrc 改為 hovertext，並微調 template
                hovertext=hover_grid,
                hovertemplate="%{hovertext}<extra></extra>",
                colorbar=dict(title="Grant Count")
            )
        )

        fig_grid.update_layout(
            title=dict(text="📊 Resource Grid Utilization Density", x=0.5),
            xaxis=dict(title="Time Domain (Slot Index)", type="linear", dtick=1),
            yaxis=dict(title="Frequency Domain (Channel ID)", type="category", categoryorder="category ascending"),
            height=550
        )
        st.plotly_chart(fig_grid)

    else:
        # ==========================================
        # 優先權熱圖分支 (已修正為使用 filtered_df)
        # ==========================================
        z_matrix = np.zeros((len(all_channels), len(all_slots)))
        text_matrix = np.empty((len(all_channels), len(all_slots)), dtype=object)
        text_matrix.fill("")
        hover_matrix = np.empty((len(all_channels), len(all_slots)), dtype=object)
        hover_matrix.fill("")
        # 關鍵修正：將原本的 df 更改為 filtered_df，確保側邊欄篩選器生效
        for _, row in filtered_df.iterrows():
            if row['channle'] in all_channels and row['slice_no'] in all_slots:
                ch_idx = np.where(all_channels == row['channle'])[0][0]
                slot_idx = np.where(all_slots == row['slice_no'])[0][0]               
                z_matrix[ch_idx, slot_idx] = row['prio'] + 1
                text_matrix[ch_idx, slot_idx] = f"ED:{row['ed_id']}<br>P:{row['prio']}"               
                is_prio_winner = "🔥 [High priority priority scheduling]" if (row['slice_no'] == 23 and row['prio'] > 0) else "Regular queue"         
                hover_matrix[ch_idx, slot_idx] = (
                    f"<b>channle</b>: CH {row['channle']}<br>"
                    f"<b>slice_no</b>: Slot {row['slice_no']}<br>"
                    f"<b>ed_id</b>: {row['ed_id']}<br>"
                    f"<b>priority (PRIO)</b>: {row['prio']} ({is_prio_winner})<br>"
                    f"<b>MCS</b>: {row['mcs_name'] if 'mcs_name' in row else row['mcs']}<extra></extra>"
                )
        for ch_idx, ch in enumerate(all_channels):
            for s_idx, s in enumerate(all_slots):
                if hover_matrix[ch_idx, s_idx] == "":
                    status = "🔒 Odd-numbered channels (protection zone disabled)" if ch % 2 != 0 else "(Idle)"
                    hover_matrix[ch_idx, s_idx] = f"<b>channle</b>: CH {ch}<br><b>Slot</b>: Slot {s}<br><b>state</b>: {status}<extra></extra>"
        fig = go.Figure(
            data=go.Heatmap(
                z=z_matrix,
                x=all_slots,
                y=all_channels.astype(str),
                colorscale="Cividis",
                text=text_matrix,
                texttemplate="%{text}",
                textfont={"size": 10},
                
                # 💡 重點修改：同樣將 textsrc 改為 hovertext，並微調 template
                hovertext=hover_matrix,
                hovertemplate="%{hovertext}<extra></extra>",
                
                colorbar=dict(
                    title="Priority level",
                    tickvals=[0, 1, 2, 3],
                    ticktext=["off/ldle", "PRIO: 0", "PRIO: 1", "PRIO: 2"]
                )
            )
        )

        fig.update_layout(
            title=dict(text="⏱️ Time-Frequency Resource Scheduling and Equipment Priority (PRIO) Analysis Chart", x=0.5),
            xaxis=dict(title="Time Domain (Slot Index)", type="linear", dtick=1),
            yaxis=dict(title="Frequency Domain (Channel ID)", type="category", categoryorder="category ascending"),
            height=550
        )
        st.plotly_chart(fig)

    # --- 下方圖表區 ---
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📊 MCS & FEC Link Adaptive Analysis")
        filtered_df['FEC_Status'] = filtered_df['mcs_name'].apply(lambda x: 'FEC_ON' if 'FecOn' in x else 'FEC_OFF')
        
        fig_mcs = px.histogram(
            filtered_df, x="mcs_code", color="FEC_Status",
            title="MCS Distribution with FEC Status",
            barmode="stack",
            color_discrete_map={'FEC_ON': '#EF553B', 'FEC_OFF': '#636EFA'}
        )
        st.plotly_chart(fig_mcs)

    with col_right:
        st.subheader("⚖️ PRIO Priority scheduling distribution")
        prio_counts = filtered_df['prio'].value_counts().reset_index()
        prio_counts.columns = ['Priority', 'Count']
        
        fig_prio = px.pie(
            prio_counts, names='Priority', values='Count',
            title="Scheduling Priority Distribution",
            hole=0.4
        )
        st.plotly_chart(fig_prio)

    # 原始日誌檢視器
    with st.expander("🔍 View Filtered Raw Assignment Data"):
        # 確保要呈現的欄位存在
        available_cols = [c for c in ['timestamp', 'sfn', 'ed_id', 'prio', 'slice_no', 'channle', 'mcs_name', 'mcs_code', 'duration'] if c in filtered_df.columns]
        st.dataframe(filtered_df[available_cols])