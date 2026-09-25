import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. ページ基本設定
st.set_page_config(
    page_title="芳怜の記録",
    page_icon="🌸",
    layout="centered"
)

# --------------------------------------------------
# ルナルナベビー風 カスタムCSS (iPhone・モバイル最適化)
# --------------------------------------------------
st.markdown("""
<style>
    /* 全体背景：ほんのり桜色のやさしい背景 */
    .main {
        background-color: #FFF8F9;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
        color: #554848;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* ルナルナ風 ヘッダー */
    .luna-title-container {
        text-align: center;
        padding: 10px 0 15px 0;
        margin-bottom: 15px;
    }
    .luna-title {
        color: #FF5A79;
        font-size: 1.6rem;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .luna-subtitle {
        color: #9E8B8B;
        font-size: 0.8rem;
        margin-top: 2px;
    }

    /* ルナルナ風 ぷっくりカード */
    .luna-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(255, 138, 158, 0.08);
        border: 1px solid #FFEBEF;
    }

    /* ミントグリーン枠のアクセントカード */
    .luna-card-mint {
        background-color: #F2FAF7;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid #D5F0E6;
    }

    /* サブヘッダー */
    .luna-header {
        font-size: 1.05rem;
        font-weight: bold;
        color: #FF5A79;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* メトリクス表示 */
    .luna-metric-val {
        font-size: 2.0rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .luna-metric-lbl {
        font-size: 0.8rem;
        color: #8C7B7B;
    }

    /* タイムライン用ヘッダーデザイン */
    .timeline-header-bg {
        background-color: #FFEBF0;
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: bold;
        color: #FF5A79;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    /* タイムライン個別レコードカード (iPhone・モバイル表示時の最適化) */
    .timeline-item-card {
        background: #FFF0F3;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-left: 4px solid #FF5A79;
    }

    /* ボタン（ルナルナピンクの丸いボタン） */
    .stButton > button {
        border-radius: 25px !important;
        background: linear-gradient(135deg, #FF8A9E 0%, #FF5A79 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 12px rgba(255, 90, 121, 0.2) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(255, 90, 121, 0.3) !important;
    }

    /* 入力フォームの角丸・ピンクフチどり */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 14px !important;
        border-color: #FFD2DC !important;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="luna-title-container">
    <div class="luna-title">🌸 芳怜育児記録</div>
    <div class="luna-subtitle">赤ちゃんの毎日のすくすく成長記録</div>
</div>
""", unsafe_allow_html=True)

DATA_FILE = "baby_record.csv"


# 2. データ読み込み・保存関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(
            columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"]
        )


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


df = load_data()

# --------------------------------------------------
# 3. 入力エリア (ルナルナ風ピンクカード)
# --------------------------------------------------
st.markdown('<div class="luna-card">', unsafe_allow_html=True)
st.markdown('<div class="luna-header">📝 きょうの記録をつける</div>', unsafe_allow_html=True)

selected_date = st.date_input("日付", datetime.date.today(), format="YYYY/MM/DD")
date_display = f"{selected_date.year}年{selected_date.month}月{selected_date.day}日"
date_str = selected_date.strftime("%Y-%m-%d")

with st.form("record_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        hour = st.selectbox("時間帯", options=list(range(24)), format_func=lambda x: f"{x}時")
        minute = st.selectbox("分", options=list(range(0, 60, 5)), format_func=lambda x: f"{x:02d}分")
        time_str = f"{hour:02d}:{minute:02d}"

    with col2:
        milk_ml = st.number_input("🍼 ミルクの量 (ml)", min_value=0, max_value=300, step=10, value=0)
        poop_size = st.radio("💩 うんちの量", options=["なし", "小", "中", "大"], horizontal=True)

    memo = st.text_input("💬 メモ・ごきげん", placeholder="例：機嫌よくたくさん飲んだ！")

    submitted = st.form_submit_button("🌸 記録を保存する")

    if submitted:
        new_data = {
            "date": date_str,
            "hour": hour,
            "time_str": time_str,
            "milk_ml": milk_ml,
            "poop_size": poop_size,
            "memo": memo,
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        save_data(df)
        st.toast(f"{time_str} の記録を保存しました 💕")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 4. 可視化エリア
# --------------------------------------------------
day_data = df[df["date"] == date_str]

if not day_data.empty:
    total_milk = day_data["milk_ml"].sum()
    poop_count = len(day_data[day_data["poop_size"] != "なし"])

    # サマリーカード
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"""
        <div class="luna-card">
            <div class="luna-header">🍼 ミルク合計</div>
            <div class="luna-metric-val">{total_milk} <span style="font-size:0.9rem; color:#8C7B7B;">ml</span></div>
            <div class="luna-metric-lbl">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="luna-card-mint">
            <div class="luna-header" style="color: #2E8B75;">💩 うんち回数</div>
            <div class="luna-metric-val" style="color: #2E8B75;">{poop_count} <span style="font-size:0.9rem; color:#5C9E8E;">回</span></div>
            <div class="luna-metric-lbl" style="color: #5C9E8E;">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    # グラフカード
    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown('<div class="luna-header">📊 きょうの授乳グラフ</div>', unsafe_allow_html=True)

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
        height=480,
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

    # --------------------------------------------------
    # タイムラインカード (カラム名追加 & iPhone最適化)
    # --------------------------------------------------
    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown('<div class="luna-header">🕒 本日のタイムライン</div>', unsafe_allow_html=True)

    sorted_day_data = day_data.sort_values("time_str")

    # テーブルヘッダー（カラム名）
    h1, h2, h3, h4, h5 = st.columns([1.5, 1.8, 1.5, 3.0, 1.2])
    h1.markdown('<div style="font-weight:bold; color:#FF5A79; font-size:0.85rem;">時間</div>', unsafe_allow_html=True)
    h2.markdown('<div style="font-weight:bold; color:#FF5A79; font-size:0.85rem;">ミルク</div>', unsafe_allow_html=True)
    h3.markdown('<div style="font-weight:bold; color:#FF5A79; font-size:0.85rem;">うんち</div>', unsafe_allow_html=True)
    h4.markdown('<div style="font-weight:bold; color:#FF5A79; font-size:0.85rem;">メモ</div>', unsafe_allow_html=True)
    h5.markdown('<div style="font-weight:bold; color:#FF5A79; font-size:0.85rem;">削除</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin: 4px 0 12px 0; border: none; border-top: 1px solid #FFE1E8;">', unsafe_allow_html=True)

    # 各レコードの表示
    for idx, row in sorted_day_data.iterrows():
        c1, c2, c3, c4, c5 = st.columns([1.5, 1.8, 1.5, 3.0, 1.2])

        c1.markdown(f"<span style='color:#FF5A79; font-weight:bold; font-size:0.9rem;'>{row['time_str']}</span>", unsafe_allow_html=True)

        milk_txt = f"{row['milk_ml']}ml" if row["milk_ml"] > 0 else "-"
        c2.markdown(f"<span style='font-size:0.85rem;'>🍼 {milk_txt}</span>", unsafe_allow_html=True)

        poop_txt = f"{row['poop_size']}" if row["poop_size"] != "なし" else "-"
        c3.markdown(f"<span style='font-size:0.85rem;'>💩 {poop_txt}</span>", unsafe_allow_html=True)

        memo_txt = row["memo"] if pd.notna(row["memo"]) and row["memo"] != "" else "-"
        c4.markdown(f"<span style='font-size:0.85rem; color:#666;'>{memo_txt}</span>", unsafe_allow_html=True)

        if c5.button("🗑️", key=f"del_{idx}"):
            df = df.drop(idx)
            save_data(df)
            st.toast(f"{row['time_str']} の記録を削除しました")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="luna-card" style="text-align: center; padding: 30px 15px;">
        <div style="font-size: 2.0rem; margin-bottom: 6px;">🌸</div>
        <div style="font-weight: bold; font-size: 1.0rem; color: #FF5A79;">本日の記録はまだありません</div>
        <div style="color: #9E8B8B; font-size: 0.8rem; margin-top: 4px;">上のフォームからきょう最初の記録をつけてみましょう</div>
    </div>
    """, unsafe_allow_html=True)