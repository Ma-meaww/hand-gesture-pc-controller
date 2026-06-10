import os

import pandas as pd
import streamlit as st

LOG_FILE = "event_log.csv"

CURRENT_COMMANDS = [
    "PING",
    "SCROLL_DOWN",
    "SCROLL_UP",
    "CLICK",
    "CONFIRM",
    "INPUT_TEXT",
    "CURSOR_MOVE",
    "OPEN_THAIJO",
    "THAIJO_INPUT_SEARCH",
    "THAIJO_SUBMIT_SEARCH",
]

st.set_page_config(
    page_title="PC Controller Dashboard",
    page_icon="🖥️",
    layout="wide",
)

st.title("PC Controller Dashboard")
st.caption("WebSocket command log, automation status, and latency monitoring")


def load_logs() -> pd.DataFrame:
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    return pd.read_csv(LOG_FILE)


df = load_logs()

if df.empty:
    st.warning("ยังไม่มีข้อมูลใน event_log.csv ให้รัน main.py แล้วส่ง command ก่อน")
    st.stop()

df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce")
df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ใช้เฉพาะ command ปัจจุบัน
df = df[df["command"].isin(CURRENT_COMMANDS)]

if df.empty:
    st.warning("ยังไม่มี log ของ command ปัจจุบัน")
    st.stop()

# เรียง log ล่าสุดไว้บนสุด
df_latest = df.sort_values("timestamp_dt", ascending=False).reset_index(drop=True)

# กราฟ latency เรียงจากเก่าไปใหม่
df_chart = df.sort_values("timestamp_dt", ascending=True).reset_index(drop=True)

# Sidebar filter
st.sidebar.header("Filters")

command_options = ["All"] + CURRENT_COMMANDS
selected_command = st.sidebar.selectbox("Command", command_options)

status_options = ["All", "success", "error"]
selected_status = st.sidebar.selectbox("Status", status_options)

row_limit = st.sidebar.slider(
    "Rows to display",
    min_value=10,
    max_value=200,
    value=50,
    step=10,
)

filtered_df = df_latest.copy()

if selected_command != "All":
    filtered_df = filtered_df[filtered_df["command"] == selected_command]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]

# Metrics
total_commands = len(df)
success_commands = len(df[df["status"] == "success"])
error_commands = len(df[df["status"] == "error"])
avg_latency = df["latency_ms"].mean()

latest = df_latest.iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Commands", total_commands)

with col2:
    st.metric("Success", success_commands)

with col3:
    st.metric("Errors", error_commands)

with col4:
    if pd.notna(avg_latency):
        st.metric("Average Latency", f"{avg_latency:.2f} ms")
    else:
        st.metric("Average Latency", "-")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Latest Command")
    st.write(f"**Time:** {latest['timestamp']}")
    st.write(f"**Command:** {latest['command']}")
    st.write(f"**Status:** {latest['status']}")
    st.write(f"**Message:** {latest['message']}")
    st.write(f"**Latency:** {latest['latency_ms']} ms")

with right:
    st.subheader("Command Count")
    command_count = df["command"].value_counts()
    st.bar_chart(command_count)

st.divider()

st.subheader("Latency Chart")
latency_df = df_chart[["timestamp", "latency_ms"]].dropna()

if latency_df.empty:
    st.info("ยังไม่มี latency data")
else:
    st.line_chart(latency_df.set_index("timestamp"))

st.divider()

st.subheader("Recent Event Logs")

display_df = filtered_df.drop(columns=["timestamp_dt"])
display_df = display_df.fillna("")
st.dataframe(
    display_df.head(row_limit),
    use_container_width=True,
    hide_index=True,
)

csv_data = display_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="filtered_event_log.csv",
    mime="text/csv",
)

if st.button("Refresh"):
    st.rerun()