import time
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 | Dice Matching Experiment",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS 樣式 (蘋果 macOS Dock 放大效果)
custom_css = textwrap.dedent("""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", sans-serif !important;
    color: #1c1c1e !important;
}

.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px;
}

.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.06);
}

.ios-kpi-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 14px 10px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.06);
}

.ios-kpi-title {
    font-size: 12px;
    font-weight: 500;
    color: #8e8e93;
    margin-bottom: 4px;
    line-height: 1.3;
}

.ios-kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #1c1c1e;
}

/* --- Apple Dock 容器設定 --- */
.dice-wrapper {
    display: flex;
    justify-content: center;
    align-items: flex-end; /* 底部對齊，確保向上放大伸展 */
    gap: 14px;
    margin: 24px 0;
    padding: 15px 0;
    flex-wrap: wrap;
}

/* --- 骰子卡片基礎樣式 --- */
.dice-card {
    width: 85px;
    height: 92px;
    background: #ffffff;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.08);
    
    /* macOS Dock 核心：以底部為基準放大，搭配蘋果彈簧曲線 cubic-bezier */
    transform-origin: bottom center;
    transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1),
                box-shadow 0.35s ease,
                background-color 0.3s ease;
    cursor: pointer;
}

.dice-icon {
    font-size: 34px;
    line-height: 1;
    margin-bottom: 4px;
    color: #1c1c1e;
}

.dice-label {
    font-size: 10px;
    font-weight: 600;
    color: #8e8e93;
    text-align: center;
    line-height: 1.2;
}

/* --- macOS Dock 綠色相配彈跳放大 (Match State) --- */
.dice-card.matched {
    background: linear-gradient(135deg, #34c759 0%, #28a745 100%);
    border: none;
    box-shadow: 0 14px 28px rgba(52, 199, 89, 0.45);
    transform: translateY(-12px) scale(1.28); /* 向上浮空 + 放大 1.28 倍 */
    z-index: 10;
}

.dice-card.matched .dice-icon,
.dice-card.matched .dice-label {
    color: #ffffff !important;
}

/*  互動波浪效果 (Hover Wave Effect) --- */
/* 1. 當前 Hover 的骰子放大並浮起 */
.dice-card:hover {
    transform: translateY(-16px) scale(1.35) !important;
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.15) !important;
    z-index: 30 !important;
}

/* 2. 左右兩側相鄰的骰子微幅放大（營造波浪連續曲面） */
.dice-card:has(+ .dice-card:hover),
.dice-card:hover + .dice-card {
    transform: translateY(-6px) scale(1.12);
    z-index: 20;
}

div[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    border-right: 1px solid rgba(0, 0, 0, 0.06);
}

div.stButton > button {
    border-radius: 14px !important;
    background-color: #ffffff !important;
    border: 1px solid #d1d1d6 !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 0.25rem !important;
}

div.stButton > button, div.stButton > button p, div.stButton > button span {
    color: #1c1c1e !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

div.stButton > button:hover {
    background-color: #e5e5ea !important;
}

div.stButton > button[kind="primary"] {
    background-color: #007aff !important;
    border: none !important;
}

div.stButton > button[kind="primary"], div.stButton > button[kind="primary"] p, div.stButton > button[kind="primary"] span {
    color: #ffffff !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #0056b3 !important;
}
</style>
""")

st.markdown(custom_css, unsafe_allow_html=True)

DICE_ICONS = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dice_html(rolls):
    cards_html = []
    for i, val in enumerate(rolls, 1):
        is_match = (val == i)
        card_class = "dice-card matched" if is_match else "dice-card"
        badge = "✓ 相配 Match" if is_match else f"第 {i} 擲<br>Roll {i}"
        cards_html.append(f'<div class="{card_class}"><span class="dice-icon">{DICE_ICONS[val]}</span><span class="dice-label">{badge}</span></div>')
    return f'<div class="dice-wrapper">{"".join(cards_html)}</div>'

def render_kpi_html(title_cn, title_en, val, color="#1c1c1e"):
    return textwrap.dedent(f"""
    <div class="ios-kpi-card">
        <div class="ios-kpi-title">{title_cn}<br><span style="font-size:10px;">{title_en}</span></div>
        <div class="ios-kpi-value" style="color: {color};">{val}</div>
    </div>
    """)

# 3. 向量化模擬邏輯
@st.cache_data
def run_simulation(total_n, seed):
    np.random.seed(seed)
    rolls = np.random.randint(1, 7, size=(total_n, 6))
    matches = (rolls == np.arange(1, 7))
    successes = np.any(matches, axis=1)
    cum_successes = np.cumsum(successes)
    cum_p = cum_successes / np.arange(1, total_n + 1)
    return rolls, cum_successes, cum_p

# 4. Plotly 圖表生成器
def build_clean_plotly_chart(df_data, total_n_setting):
    df_reset = df_data.reset_index().rename(columns={'index': 'n'})
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['理論 P(A)'],
        mode='lines',
        name='理論 P(A) / Theory P(A)',
        line=dict(color='#FF3B30', width=2, dash='dash'),
        hovertemplate='理論 P(A) / Theory P(A): %{y:.4f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['模擬 P(A)'],
        mode='lines+markers',
        name='估算 P(A) / Estimated P(A)',
        line=dict(color='#007AFF', width=2.2),
        marker=dict(size=4, color='#007AFF', opacity=0.85),
        hovertemplate='模擬次數 / Simulations n: %{x}<br>估算 P(A) / Estimated P(A): %{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        hovermode='x unified',
        xaxis=dict(
            title='模擬次數 (n) / Total Simulations (n)',
            range=[1, max(total_n_setting, 10)],
            showgrid=True,
            gridcolor='#f2f2f7',
            zeroline=False
        ),
        yaxis=dict(
            title='相對頻率 P(A) / Relative Frequency P(A)',
            range=[0.35, 0.95],
            showgrid=True,
            gridcolor='#f2f2f7',
            zeroline=False,
            tickformat='.3f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        uirevision='constant'
    )
    return fig

# 5. 初始化 Session State
if "anim_status" not in st.session_state:
    st.session_state.anim_status = "idle"
if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0
if "total_n" not in st.session_state:
    st.session_state.total_n = 1000

# 6. 主頁面說明
st.markdown(
    textwrap.dedent("""
<div class="card">
    <div style="font-size: 22px; font-weight: 800; margin-bottom: 8px; color: #1c1c1e;">🎲 6 面骰子相配實驗 (6-Sided Dice Matching Experiment)</div>
    <div style="font-size: 14px; line-height: 1.6; color: #3a3a3c;">
        📌 <b>規則 (Rules)：</b> 丟擲一粒公平骰子 6 次，若第 <i>k</i> 次丟擲點數等於 <i>k</i>（<i>k</i> = 1..6）稱為<b>「相配」</b>。<br>
        <i>Roll a fair 6-sided die 6 times. If the k-th roll equals k (k=1..6), it is considered a <b>"Match"</b>.</i><br>
        6 次中只要<b>至少發生 1 次相配</b>即算成功（事件 A）。<br>
        <i>At least 1 match in 6 rolls counts as a success (Event A).</i><br>
        🎯 <b>理論成功概率 (Theoretical Probability)：</b> P(A) = 1 - (5/6)⁶ ≈ 0.6651
    </div>
</div>
"""),
    unsafe_allow_html=True,
)

# 7. 側邊欄控制面板
with st.sidebar:
    st.header("⚙️ 控制面板 (Control Panel)")

    def sync_from_slider():
        st.session_state.total_n = st.session_state.slider_n
        st.session_state.anim_status = "idle"

    def sync_from_input():
        st.session_state.total_n = st.session_state.input_n
        st.session_state.anim_status = "idle"

    st.session_state.slider_n = st.session_state.total_n
    st.session_state.input_n = st.session_state.total_n

    st.markdown("**模擬總次數 (N) / Total Simulations (N)**")
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        st.slider("拉動次數 (Slider)", 100, 10000, 100, key="slider_n", on_change=sync_from_slider, label_visibility="collapsed")
    with col_s2:
        st.number_input("輸入次數 (Number Input)", 100, 10000, 100, key="input_n", on_change=sync_from_input, label_visibility="collapsed")

    total_n = st.session_state.total_n
    fps = st.slider("動畫速率 (FPS) / Speed", 2, 25, 8)
    seed = st.number_input("隨機種子 (Seed) / Random Seed", 0, 9999, 42)
    
    st.divider()

    col_b1, col_b2, col_b3 = st.columns(3)
    start_click = col_b1.button("🚀 開始 Start", type="primary", use_container_width=True)
    pause_label = "▶️ 繼續 Resume" if st.session_state.anim_status == "paused" else "⏸️ 暫停 Pause"
    pause_click = col_b2.button(pause_label, use_container_width=True)
    quick_click = col_b3.button("⚡ 結算 Finish", use_container_width=True)

    if start_click:
        st.session_state.anim_status = "running"
        st.session_state.current_step_idx = 0
        st.rerun()

    if pause_click:
        if st.session_state.anim_status == "running":
            st.session_state.anim_status = "paused"
        elif st.session_state.anim_status == "paused":
            st.session_state.anim_status = "running"
        st.rerun()

    if quick_click:
        st.session_state.anim_status = "finished"
        st.rerun()

p_theoretical = 1 - (5/6)**6

# 8. 數據準備與渲染
rolls, cum_successes, cum_p = run_simulation(total_n, seed)
num_frames = min(total_n, 60)
frame_indices = np.unique(np.linspace(1, total_n, num=num_frames, dtype=int))

st.subheader("📈 數據儀表板 (Data Dashboard)")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
spot_kpi1 = kpi1.empty()
spot_kpi2 = kpi2.empty()
spot_kpi3 = kpi3.empty()
spot_kpi4 = kpi4.empty()

with st.container():
    st.markdown("<div style='margin-top: 10px;'><b>🎲 當前丟擲結果 (Current Roll Results)</b></div>", unsafe_allow_html=True)
    dice_spot = st.empty()

with st.container():
    st.markdown("<div style='margin-top: 15px;'><b>📊 相對頻率 P(A) 收斂軌跡 (Convergence Trajectory)</b></div>", unsafe_allow_html=True)
    chart_spot = st.empty()

df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))

plotly_config = {
    'scrollZoom': True,
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d']
}

def render_frame_ui(frame_n):
    spot_kpi1.markdown(render_kpi_html("模擬次數", "Simulations", f"{frame_n}"), unsafe_allow_html=True)
    spot_kpi2.markdown(render_kpi_html("成功次數", "Successes", f"{cum_successes[frame_n-1]}"), unsafe_allow_html=True)
    spot_kpi3.markdown(render_kpi_html("估算 P(A)", "Estimated P(A)", f"{cum_p[frame_n-1]:.4f}", "#007AFF"), unsafe_allow_html=True)
    spot_kpi4.markdown(render_kpi_html("理論 P(A)", "Theory P(A)", f"{p_theoretical:.4f}", "#FF3B30"), unsafe_allow_html=True)

    dice_spot.markdown(render_dice_html(rolls[frame_n-1]), unsafe_allow_html=True)
    chart_spot.plotly_chart(build_clean_plotly_chart(df_chart.iloc[:frame_n], total_n), use_container_width=True, config=plotly_config)

if st.session_state.anim_status == "idle":
    render_frame_ui(1)
    st.info("👈 請點擊左側面板的 **「🚀 開始 / Start」** 播放動畫，或 **「⚡ 結算 / Finish」** 直接觀看結果！\n\n*Please click **'Start'** to run the animation, or **'Finish'** for immediate results!*")

elif st.session_state.anim_status == "finished":
    render_frame_ui(total_n)
    st.success(f"🎉 模擬完成！最終估算 P(A) = {cum_p[-1]:.4f}，與理論值誤差僅 {abs(cum_p[-1]-p_theoretical):.4f}\n\n*Simulation Finished! Final Estimated P(A) = {cum_p[-1]:.4f}, absolute error: {abs(cum_p[-1]-p_theoretical):.4f}*")

elif st.session_state.anim_status == "paused":
    current_n = frame_indices[st.session_state.current_step_idx]
    render_frame_ui(current_n)
    st.warning(f"⏸️ 動畫已暫停於第 {current_n} 次模擬，點擊左側 **「▶️ 繼續 / Resume」** 可繼續播放。\n\n*Paused at simulation #{current_n}. Click **'Resume'** to continue.*")

elif st.session_state.anim_status == "running":
    progress_bar = st.progress(0)
    
    start_idx = st.session_state.current_step_idx
    for idx in range(start_idx, len(frame_indices)):
        st.session_state.current_step_idx = idx
        current_n = frame_indices[idx]
        
        progress_bar.progress(int((idx + 1) / len(frame_indices) * 100))
        render_frame_ui(current_n)
        
        time.sleep(1 / fps)
    
    progress_bar.empty()
    st.session_state.anim_status = "finished"
    st.rerun()

if st.session_state.anim_status in ["paused", "finished"]:
    st.subheader("📊 指定模擬次數統計結果 (Summary Table)")
    targets = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_df = pd.DataFrame({
        '模擬次數 / Simulations (n)': targets,
        '事件 A 發生次數 / Successes': [int(cum_successes[n-1]) for n in targets],
        '估算 P(A) / Estimated P(A)': [f"{cum_p[n-1]:.4f}" for n in targets],
        '理論 P(A) / Theory P(A)': f"{p_theoretical:.4f}"
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)
