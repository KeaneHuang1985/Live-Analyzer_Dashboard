import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
# ===================================================
#   RF Scheduler Dashboard with Dynamic Delta Control
# ===================================================

def render_rf_sched_dashboard(sched_df):

    st.header("RF Scheduler")
    if sched_df.empty:
        st.info("No data...")
        return

    df = sched_df.copy()
    if "delta_rssi" not in df.columns:
        df["delta_rssi"] = (df["rssi"] - df["rssi_ref"]).abs()

    tab_name = [
        "📊 Current SFN RSSI",
        "📈 RSSI Reference Trend",
        "🎯 Delta RSSI Distribution",
        "📦 RSSI by RA Group"
    ]

    tab1, tab2, tab3, tab4 = st.tabs(tab_name)

    # =========================
    # 1. Current SFN RSSI
    # =========================
    with tab1:
        latest_sfn = df["sfn"].max()
        latest_df = df[df["sfn"] == latest_sfn]
        color_map = {"ALLOC": "#2ecc71","SKIP": "#e74c3c","SKIP_SFN": "#95a5a6","DEFER_UL_REQ": "#f39c12",}
        min_rssi = max(latest_df["rssi"].min() - 5, -130)
        max_rssi = min(latest_df["rssi"].max() + 5, -50)
        st.markdown("### 📍 Scheduler Decision (Scatter Plot)")
        st.write(
            "Each dot represents one ED in the latest SFN.\n"
            "Color indicates the scheduler decision."
        )

        fig1 = px.scatter(
            latest_df,
            x="ul_ra_group",
            y="rssi",
            color="status",
            hover_data={
            "ed_id": True,
            "rssi": True,
            "rssi_ref": True,
            "delta_rssi": True,
            "prio_cur": True,
            "prio_max": True,
            "duration": True,
            "ul_waste": True,
            # 已在圖上呈現，可隱藏
            "status": False,
            "ul_ra_group": False
            },
            category_orders={"ul_ra_group": sorted(df["ul_ra_group"].unique())},
            color_discrete_map=color_map,
            title=f"SFN {latest_sfn} Scheduler Decision",
        )

        fig1.update_traces(marker=dict(size=10, line=dict(width=1, color="black")))    
        fig1.update_layout(xaxis_title="UL RA Group",yaxis_title="RSSI (dBm)",yaxis=dict(range=[min_rssi, max_rssi]),legend_title="Status",)

        st.plotly_chart(fig1)
        st.markdown("---")
        st.markdown("### 📦 RSSI Distribution (Box Plot)")
        st.write(
            "Shows the RSSI distribution for each UL RA Group.\n"
            "The box indicates median and quartiles, while points represent outliers."
        )

        fig2 = px.box(
            latest_df,
            x="ul_ra_group",
            y="rssi",
            color="status",
            points="all",
            category_orders={"ul_ra_group": sorted(df["ul_ra_group"].unique())},
            color_discrete_map=color_map,
            title=f"SFN {latest_sfn} RSSI Distribution",
        )
        fig2.update_layout(xaxis_title="UL RA Group",yaxis_title="RSSI (dBm)",yaxis=dict(range=[min_rssi, max_rssi]),legend_title="Status")
        st.plotly_chart(fig2)
       
   # ===================================================
    # 2. RSSI Reference & ED Distribution Trend (升級版)
    # ===================================================
    with tab2:
        st.markdown("### 📈 RSSI Scheduler Window Trend")
        st.write(
            "This chart visualizes the Scheduler RSSI acceptance window.\n"
            "EDs inside the shaded region satisfy\n"
            "ABS(RSSI - RSSI_REF) < BBSCHED_MAX_RSSI_DELTA."
        )

        max_rssi_delta_config = st.number_input("Set BBSCHED_MAX_RSSI_DELTA Threshold (dB) : ",min_value=0,max_value=128,value=20,step=5)

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        window_min = st.selectbox("Show Last (minutes)",[1, 5, 10, 30, 60],index=1)
        end_time = df["timestamp"].max()
        start_time = end_time - timedelta(minutes=window_min)
        filtered_df = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)]
        valid_df = filtered_df[filtered_df["rssi"] > -135].copy()
        alloc_df = filtered_df[filtered_df["status"] == "ALLOC"]
        skip_df  = filtered_df[filtered_df["status"] == "SKIP"]
        
        if len(valid_df) == 0:
            st.info("No active ED packet data.")
        else:

            MAX_DELTA = max_rssi_delta_config  # 改成實際 BBSCHED_MAX_RSSI_DELTA

            ref_df = (
                valid_df.groupby("sfn", as_index=False)
                .agg({
                    "timestamp": "first",
                    "rssi_ref": "first"
                })
            )

            ref_df = ref_df.sort_values("timestamp")

            ref_df["upper_limit"] = ref_df["rssi_ref"] + MAX_DELTA
            ref_df["lower_limit"] = ref_df["rssi_ref"] - MAX_DELTA

            fig = go.Figure()

            # Scheduler Window 上界
            fig.add_trace(go.Scatter(
                x=ref_df["timestamp"],
                y=ref_df["upper_limit"],
                mode="lines",
                line=dict(width=0),
                showlegend=False
            ))

            # Scheduler Window 下界
            fig.add_trace(go.Scatter(
                x=ref_df["timestamp"],
                y=ref_df["lower_limit"],
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(46,204,113,0.15)",
                line=dict(width=0),
                name=f"Scheduler Window (±{MAX_DELTA} dB)"
            ))

            # RSSI_REF
            fig.add_trace(go.Scatter(
                x=ref_df["timestamp"],
                y=ref_df["rssi_ref"],
                mode="lines+markers",
                line=dict(color="#e67e22", width=3),
                name="RSSI_REF"
            ))

            # 所有 ED RSSI
            fig.add_trace(go.Scatter(
                x=valid_df["timestamp"],
                y=valid_df["rssi"],
                mode="markers",
                marker=dict(
                    size=5,
                    color="rgba(52,152,219,0.6)"
                ),
                name="ED RSSI"
            ))

            fig.add_trace(
                go.Scatter(
                    x=alloc_df["timestamp"],
                    y=alloc_df["rssi"],
                    mode="markers",
                    marker=dict(color="green", size=6),
                    name="ALLOC_UL"
                )
            )
            #
            fig.add_trace(
                go.Scatter(
                    x=skip_df["timestamp"],
                    y=skip_df["rssi"],
                    mode="markers",
                    marker=dict(color="red", size=6),
                    name="SKIP_UL"
                )
            )

            fig.update_layout(
                title="Scheduler RSSI Acceptance Window",
                xaxis_title="Timeline",
                yaxis_title="RSSI (dBm)",
                hovermode="x unified"
            )

            st.plotly_chart(fig, width="stretch")

    # ===================================================
    # 3. Delta RSSI Distribution (獨立控制版)
    # ===================================================
    with tab3:
        st.markdown("### 🎯 Delta RSSI Distribution & Simulation")
        
        # 🛠️ 將控制項直接移入 Tab 3 內部
        max_rssi_delta_config = st.number_input(
            "Adjust BBSCHED_MAX_RSSI_DELTA Limit (dB) : ",
            min_value=15,
            max_value=128,
            value=30,
            step=5,
            key="tab3_delta_input" # 設定唯一 key 確保 Streamlit 渲染正常
        )

        color_map = {
            "ALLOC": "#2ecc71", 
            "SKIP": "#e74c3c", 
            "SKIP_SFN": "#95a5a6", 
            "DEFER_UL_REQ": "#f39c12"
        }
        
        # 繪製直方圖
        fig = px.histogram(
            df,
            x="delta_rssi",
            nbins=30,
            color="status",
            color_discrete_map=color_map,
            marginal="rug", # 畫面上方邊緣的地毯圖
            title=f"RSSI Delta |ED_RSSI - RSSI_REF| (Current Simulation Threshold: {max_rssi_delta_config} dB)"
        )

        # 🛠️ 動態連動：在圖表上劃出使用者輸入的限制紅虛線
        fig.add_vline(
            x=max_rssi_delta_config, 
            line_dash="dash", 
            line_color="#e74c3c", 
            line_width=2,
            annotation_text=f"Limit: {max_rssi_delta_config} dB", 
            annotation_position="top right"
        )

        # 動態調整 X 軸範圍，確保當拉到 128 時，紅線不會衝出圖表外
        max_x_boundary = max(df["delta_rssi"].max() + 5, max_rssi_delta_config + 10)

        fig.update_layout(
            xaxis_title="Absolute Delta RSSI (dB)",
            yaxis_title="Packet Count",
            barmode="overlay",
            xaxis=dict(range=[0, max_x_boundary])
        )
        fig.update_traces(opacity=0.75)

        # 在圖表下方即時計算並顯示衝擊模擬（What-if Analysis）
        potential_skips = len(df[df["delta_rssi"] >= max_rssi_delta_config])
        
        if potential_skips > 0:
            st.warning(f"⚠️ **Simulation Alert**: Under a {max_rssi_delta_config} dB threshold, **{potential_skips}** historical packets would fail the RSSI check (located to the right of the red line) and likely get deferred/skipped.")
        else:
            st.success(f"✅ **Safe Zone**: All historical packets fall within the current {max_rssi_delta_config} dB threshold.")

        # 輸出圖表
        st.plotly_chart(fig)

    # =========================
    # 4. RSSI by RA Group
    # =========================
    with tab4:
        color_map = {"ALLOC": "#2ecc71", "SKIP": "#e74c3c", "SKIP_SFN": "#95a5a6", "DEFER_UL_REQ": "#f39c12"}

        fig = px.box(
            df,
            x="ul_ra_group",
            y="rssi",
            color="status",
            color_discrete_map=color_map,
            points="outliers",
            category_orders={"ul_ra_group": sorted(df["ul_ra_group"].unique())},
            title="Channel Reliability Boxplot (RSSI by RA Group)"
        )

        fig.update_layout(
            xaxis_title="UL RA Channel / Group",
            yaxis_title="Received RSSI (dBm)",
            boxmode="group"
        )
        st.plotly_chart(fig)