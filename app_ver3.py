import calendar
import datetime
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --------------------------------------------------
# 1. ページ基本設定
# --------------------------------------------------
st.set_page_config(
    page_title="芳怜ちゃん育児記録",
    page_icon="🌸",
    layout="centered"
)

# 本日の日付を取得
today_date = datetime.date.today()

# --------------------------------------------------
# カスタムCSS
# --------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #FFF8F9;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
        color: #554848;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
    }
    .luna-title-container {
        text-align: center;
        padding: 10px 0 15px 0;
        margin-bottom: 15px;
    }
    .luna-title {
        color: #FF5A79;
        font-size: 1.5rem;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .luna-subtitle {
        color: #9E8B8B;
        font-size: 0.8rem;
        margin-top: 2px;
    }
    .luna-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 14px 10px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(255, 138, 158, 0.08);
        border: 1px solid #FFEBEF;
    }
    .luna-card-mint {
        background-color: #F2FAF7;
        border-radius: 20px;
        padding: 14px 10px;
        margin-bottom: 16px;
        border: 1px solid #D5F0E6;
    }
    .luna-header {
        font-size: 1.0rem;
        font-weight: bold;
        color: #FF5A79;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .luna-metric-val {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .luna-metric-lbl {
        font-size: 0.75rem;
        color: #8C7B7B;
    }
    .timeline-card {
        background-color: #FFF5F7;
        border-left: 5px solid #FF5A79;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }
    .timeline-time {
        font-size: 0.95rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .timeline-badge {
        display: inline-block;
        background-color: #FFFFFF;
        border: 1px solid #FFD2DC;
        border-radius: 12px;
        padding: 2px 6px;
        font-size: 0.75rem;
        margin-right: 4px;
        color: #554848;
    }
    .cal-grid-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 3px;
        width: 100%;
        margin-top: 8px;
    }
    .cal-header-cell {
        text-align: center;
        font-weight: bold;
        font-size: 0.75rem;
        padding: 4px 0;
    }
    .cal-day-cell {
        background-color: #FFFFFF;
        border: 1px solid #FFE1E8;
        border-radius: 8px;
        padding: 3px 0px 0px 0px;
        text-align: center;
        min-height: 68px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
        overflow: hidden;
    }
    .cal-day-cell-empty {
        background-color: #FAF8F8;
        border: 1px solid #F2EDED;
        border-radius: 8px;
        min-height: 68px;
    }
    .cal-day-num {
        font-size: 0.7rem;
        color: #8C7B7B;
        font-weight: bold;
        line-height: 1.0;
    }
    .cal-milk-val {
        font-size: 0.75rem;
        font-weight: bold;
        color: #FF5A79;
        margin-top: 1px;
        line-height: 1.0;
    }
    .cal-bar-container {
        background-color: #FFEBF0;
        border-radius: 0 0 6px 6px;
        height: 22px;
        width: 100%;
        margin: 2px 0 0 0;
        display: flex;
        align-items: flex-end;
        overflow: hidden;
    }
    .cal-bar-fill {
        background: linear-gradient(0deg, #FF8A9E 0%, #FF5A79 100%);
        width: 100%;
        border-radius: 0;
    }
    .stButton > button {
        border-radius: 25px !important;
        background: linear-gradient(135deg, #FF8A9E 0%, #FF5A79 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 12px rgba(255, 90, 121, 0.2) !important;
        width: 100%;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 14px !important;
        border-color: #FFD2DC !important;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="luna-title-container">
    <div class="luna-title">🌸 芳怜ちゃん育児記録</div>
    <div class="luna-subtitle">毎日のすくすく成長記録</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 2. Googleスプレッドシート接続＆データ操作処理
# --------------------------------------------------
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    info = json.loads(st.secrets["gcp_service_account"]["json_text"])
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(credentials)


def get_worksheet():
    gc = get_gspread_client()
    spreadsheet_name = st.secrets["spreadsheet"]["spreadsheet_name"]
    sh = gc.open(spreadsheet_name)
    return sh.sheet1


@st.cache_data(ttl=60)
def load_data():
    try:
        ws = get_worksheet()
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame(columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"])
        df = pd.DataFrame(records)
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce").fillna(0).astype(int)
        df["milk_ml"] = pd.to_numeric(df["milk_ml"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"スプレッドシート読み込みエラー: {e}")
        return pd.DataFrame(columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"])


def append_row(new_row):
    try:
        ws = get_worksheet()
        ws.append_row([
            new_row["date"],
            int(new_row["hour"]),
            new_row["time_str"],
            int(new_row["milk_ml"]),
            new_row["poop_size"],
            new_row["memo"]
        ])
        st.cache_data.clear()
    except Exception as e:
        st.error(f"書き込みエラー: {e}")


def delete_row(date_val, time_str_val):
    try:
        ws = get_worksheet()
        records = ws.get_all_records()
        for idx, row in enumerate(records, start=2):
            if str(row.get("date")) == str(date_val) and str(row.get("time_str")) == str(time_str_val):
                ws.delete_rows(idx)
                st.cache_data.clear()
                break
    except Exception as e:
        st.error(f"削除エラー: {e}")


# --------------------------------------------------
# 入力リセット処理＆コールバック
# --------------------------------------------------
def reset_input_fields():
    st.session_state["input_hour"] = 0
    st.session_state["input_minute"] = 0
    st.session_state["input_milk_ml"] = 0
    st.session_state["input_poop_size"] = "なし"
    st.session_state["input_memo"] = ""


def on_date_change():
    reset_input_fields()


def save_and_reset_callback():
    sel_date = st.session_state.get("record_date_val", today_date)
    date_str_val = sel_date.strftime("%Y-%m-%d")
    time_str = f"{int(st.session_state['input_hour']):02d}:{int(st.session_state['input_minute']):02d}"

    new_data = {
        "date": date_str_val,
        "hour": int(st.session_state["input_hour"]),
        "time_str": time_str,
        "milk_ml": int(st.session_state["input_milk_ml"]),
        "poop_size": st.session_state["input_poop_size"],
        "memo": st.session_state["input_memo"],
    }

    append_row(new_data)
    reset_input_fields()
    st.session_state["save_toast_msg"] = f"{time_str} の記録を保存しました 💕"


if "input_hour" not in st.session_state:
    st.session_state["input_hour"] = 0
if "input_minute" not in st.session_state:
    st.session_state["input_minute"] = 0
if "input_milk_ml" not in st.session_state:
    st.session_state["input_milk_ml"] = 0
if "input_poop_size" not in st.session_state:
    st.session_state["input_poop_size"] = "なし"
if "input_memo" not in st.session_state:
    st.session_state["input_memo"] = ""

df = load_data()


# --------------------------------------------------
# 3. 入力エリア
# --------------------------------------------------
if "save_toast_msg" in st.session_state:
    st.toast(st.session_state.pop("save_toast_msg"))

st.markdown('<div class="luna-card">', unsafe_allow_html=True)
st.markdown('<div class="luna-header">📝 きょうの記録をつける</div>', unsafe_allow_html=True)

# 1. 未保持の場合は「本日の日付」を初期セット
if "record_date_val" not in st.session_state:
    st.session_state["record_date_val"] = today_date

# 2. key に動的な日付文字列を含めることで、過去のキャッシュ（9/28など）からの自動復元を防止
selected_date = st.date_input(
    "日付を選択",
    value=st.session_state["record_date_val"],
    format="YYYY/MM/DD",
    on_change=on_date_change,
    key=f"date_picker_{today_date.strftime('%Y%m%d')}"
)

# 3. 選択された日付を更新保持
st.session_state["record_date_val"] = selected_date

col1, col2 = st.columns(2)

with col1:
    st.selectbox(
        "時間帯",
        options=list(range(24)),
        format_func=lambda x: f"{x}時",
        key="input_hour"
    )
    st.selectbox(
        "分",
        options=list(range(0, 60, 5)),
        format_func=lambda x: f"{x:02d}分",
        key="input_minute"
    )

with col2:
    st.number_input(
        "🍼 ミルクの量 (ml)",
        min_value=0,
        max_value=300,
        step=10,
        key="input_milk_ml"
    )
    st.radio(
        "💩 うんちの量",
        options=["なし", "小", "中", "大"],
        horizontal=True,
        key="input_poop_size"
    )

st.text_input(
    "💬 メモ・ごきげん",
    placeholder="例：機嫌よくたくさん飲んだ！",
    key="input_memo"
)

if st.button("🌸 記録を保存する", on_click=save_and_reset_callback):
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# 4. 選択日付のサマリー・グラフ・タイムライン
# --------------------------------------------------
date_display = f"{selected_date.year}年{selected_date.month}月{selected_date.day}日"
date_str = selected_date.strftime("%Y-%m-%d")

day_data = df[df["date"] == date_str]

if not day_data.empty:
    total_milk = day_data["milk_ml"].sum()
    poop_count = len(day_data[day_data["poop_size"] != "なし"])

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"""
        <div class="luna-card">
            <div class="luna-header">🍼 ミルク合計</div>
            <div class="luna-metric-val">{total_milk} <span style="font-size:0.8rem; color:#8C7B7B;">ml</span></div>
            <div class="luna-metric-lbl">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="luna-card-mint">
            <div class="luna-header" style="color: #2E8B75;">💩 うんち回数</div>
            <div class="luna-metric-val" style="color: #2E8B75;">{poop_count} <span style="font-size:0.8rem; color:#5C9E8E;">回</span></div>
            <div class="luna-metric-lbl">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="luna-header">📊 {date_display} の時間別授乳グラフ </div>', unsafe_allow_html=True)

    full_hours = pd.DataFrame({"hour": list(range(24))})
    hourly_summary = day_data.groupby("hour")["milk_ml"].sum().reset_index()
    chart_data = pd.merge(full_hours, hourly_summary, on="hour", how="left").fillna(0)

    chart_data["hour_label"] = chart_data["hour"].apply(lambda x: f"{x:02d}:00")
    chart_data["text_label"] = chart_data["milk_ml"].apply(lambda x: f"{int(x)}ml" if x > 0 else "")

    fig = px.bar(
        chart_data,
        x="milk_ml",
        y="hour_label",
        orientation="h",
        labels={"milk_ml": "ミルク (ml)", "hour_label": "時間"},
        text="text_label",
        color="milk_ml",
        color_continuous_scale=["#FFEBF0", "#FF8A9E", "#FF5A79"]
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed", tickfont=dict(color="#665555", size=10)),
        xaxis=dict(tickfont=dict(color="#665555", size=10)),
        height=450,
        margin=dict(l=0, r=15, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#FF5A79", size=11),
        cliponaxis=False,
        marker=dict(line=dict(color="#FF8A9E", width=1))
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="luna-header">🕒 {date_display} のタイムライン</div>', unsafe_allow_html=True)

    sorted_day_data = day_data.sort_values("time_str")

    for idx, row in sorted_day_data.iterrows():
        milk_txt = f"{row['milk_ml']}ml" if row["milk_ml"] > 0 else "なし"
        poop_txt = f"{row['poop_size']}" if row["poop_size"] != "なし" else "なし"
        memo_txt = row["memo"] if pd.notna(row["memo"]) and str(row["memo"]).strip() != "" else "メモなし"

        col_text, col_btn = st.columns([8.5, 1.5])

        with col_text:
            st.markdown(f"""
            <div class="timeline-card">
                <div class="timeline-time">⏰ {row['time_str']}</div>
                <div style="margin-top: 6px;">
                    <span class="timeline-badge">🍼 ミルク: <b>{milk_txt}</b></span>
                    <span class="timeline-badge">💩 うんち: <b>{poop_txt}</b></span>
                </div>
                <div style="font-size: 0.8rem; color: #776666; margin-top: 6px; padding-left: 2px;">
                    💬 {memo_txt}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{idx}"):
                delete_row(row["date"], row["time_str"])
                st.toast(f"{row['time_str']} の記録を削除しました")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="luna-card" style="text-align: center; padding: 25px 15px;">
        <div style="font-size: 2.0rem; margin-bottom: 6px;">🌸</div>
        <div style="font-weight: bold; font-size: 1.0rem; color: #FF5A79;">{date_display} の記録はまだありません</div>
        <div style="color: #9E8B8B; font-size: 0.8rem; margin-top: 4px;">上のフォームから記録をつけると、ここにサマリーとタイムラインが表示されます</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# 5. カレンダー表示（月選択機能付き）
# --------------------------------------------------
st.markdown('<div class="luna-card">', unsafe_allow_html=True)
st.markdown('<div class="luna-header">📅 ミルクカレンダー</div>', unsafe_allow_html=True)

c_col1, c_col2 = st.columns(2)
current_year = today_date.year

years_options = list(range(current_year - 2, current_year + 2))
year_index = years_options.index(selected_date.year) if selected_date.year in years_options else years_options.index(current_year)

with c_col1:
    sel_year = st.selectbox(
        "年",
        options=years_options,
        index=year_index,
        key="cal_year_select"
    )

with c_col2:
    sel_month = st.selectbox(
        "月",
        options=list(range(1, 13)),
        index=selected_date.month - 1,
        format_func=lambda x: f"{x}月",
        key="cal_month_select"
    )

if not df.empty:
    temp_df = df.copy()
    temp_df["date_dt"] = pd.to_datetime(temp_df["date"], errors="coerce")
    monthly_df = temp_df[(temp_df["date_dt"].dt.year == sel_year) & (temp_df["date_dt"].dt.month == sel_month)]
    daily_milk = monthly_df.groupby("date")["milk_ml"].sum().to_dict()
    
    poop_df = monthly_df[monthly_df["poop_size"] != "なし"]
    poop_dates = set(poop_df["date"].unique())
else:
    daily_milk = {}
    poop_dates = set()

max_monthly_milk = max(daily_milk.values()) if daily_milk and max(daily_milk.values()) > 0 else 800

calendar.setfirstweekday(calendar.SUNDAY)
cal = calendar.monthcalendar(sel_year, sel_month)

weekdays = ["日", "月", "火", "水", "木", "金", "土"]

cal_html = '<div class="cal-grid-container">'

for wd in weekdays:
    if wd == "日":
        color = "#FF5A79"
    elif wd == "土":
        color = "#4A90E2"
    else:
        color = "#554848"
    cal_html += f'<div class="cal-header-cell" style="color:{color};">{wd}</div>'

for week in cal:
    for day in week:
        if day == 0:
            cal_html += '<div class="cal-day-cell-empty"></div>'
        else:
            d_str = f"{sel_year}-{sel_month:02d}-{day:02d}"
            milk_val = daily_milk.get(d_str, 0)
            has_poop = d_str in poop_dates

            bar_percent = min(100, int((milk_val / max_monthly_milk) * 100)) if milk_val > 0 else 0
            is_selected = (d_str == selected_date.strftime("%Y-%m-%d"))

            bg_style = "background-color: #FFF0F3; border: 1.5px solid #FF5A79;" if is_selected else ""
            poop_icon = "💩"

            if milk_val > 0:
                poop_html = f"{poop_icon}" if has_poop else "<span style='visibility:hidden;'>💩</span>"
                inner_content = f"<div class='cal-day-num'>{day}</div><div class='cal-milk-val'>{milk_val}<span style='font-size:0.55rem;'>ml</span><br>{poop_html}</div><div class='cal-bar-container'><div class='cal-bar-fill' style='height: {bar_percent}%;'></div></div>"
            elif has_poop:
                inner_content = f"<div class='cal-day-num'>{day}</div><div style='font-size:0.7rem;'><br>{poop_icon}</div><div class='cal-bar-container' style='background-color:transparent;'></div>"
            else:
                inner_content = f"<div class='cal-day-num'>{day}</div><div style='font-size:0.55rem; color:#DDD;'>-<br><span style='visibility:hidden;'>💩</span></div><div class='cal-bar-container' style='background-color:transparent;'></div>"

            cal_html += f'<div class="cal-day-cell" style="{bg_style}">{inner_content}</div>'

cal_html += '</div>'

st.markdown(cal_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
