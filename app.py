import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 (iOS 27 Spatial)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. iOS 27 Spatial Glass UI 樣式
st.markdown("""
<style>
/* 深色極光空間背景 */
html, body, .stApp {
    background: radial-gradient(circle at 50% 0%, #181c2e 0%, #0a0b10 100%) !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif !important;
    color: #f5f5f7 !important;
}

.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1050px;
}

/* Dynamic Island 動態島膠囊 */
.dynamic-island {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: fit-content;
    margin: 0 auto 20px auto;
    padding: 8px 20px;
    background: rgba(0, 0, 0, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 30px;
    backdrop-filter: blur(30px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(255, 255, 255, 0.05);
}

.island-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 10px;
    display: inline-block;
}

.island-dot.running { background: #00f0ff; box-shadow: 0 0 10px #00f0ff; }
.island-dot.paused { background: #ffcc00; box-shadow: 0 0 10px #ffcc00; }
.island-dot.finished { background: #00ff87; box-shadow: 0 0 10px #00ff87; }
.island-dot.idle { background: #8e8e93; }

.island-text {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: #ffffff;
}

/* iOS 27 空間流體玻璃卡片 (Spatial Liquid Glass) */
.spatial-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(25px) saturate(180%);
    -webkit-backdrop-filter: blur(25px) saturate(180%);
    border-radius: 26px;
    padding: 22px 26px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.spatial-section-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #a1a1a6;
    margin: 18px 0 8px 4px;
}

/* Spatial KPI Widget 數據框 */
.spatial-kpi-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 22px;
    padding: 16px 12px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.spatial-kpi-title {
    font-size: 11px;
    font-weight: 600;
    color: #a1a1a6;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.spatial-kpi-value {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
}

/* 3D 浮空骰子卡片 */
.dice-wrapper {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin: 12px 0;
    flex-wrap: wrap;
}

@keyframes spatial-pop {
    0% { transform: scale(0.82) translateY(10px) rotateX(20deg); opacity: 0.5; }
    60% { transform: scale(1.08) translateY(-4px) rotateX(-5deg); opacity: 0.95; }
    100% { transform: scale(1) translateY(0) rotateX(0deg); opacity: 1; }
}

.dice-card {
    width: 80px;
    height: 96px;
    background: rgba(255, 255, 255, 0.07);
    border-radius: 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    animation: spatial-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.dice-icon {
    font-size: 40px;
    line-height: 1;
    margin-bottom: 4px;
    color: #ffffff;
    filter: drop-shadow(0 2px 8px rgba(255,255,255,0.2));
}

.dice-badge {
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.12);
    color: #a1a1a6;
}

/* 相配成功狀態：霓虹翡翠綠 */
.dice-card.matched {
    background: linear-gradient(135deg, rgba(0, 255, 135, 0.25) 0%, rgba(0, 180, 100, 0.4) 100%);
    border: 1px solid #00ff87;
    box-shadow: 0 0 25px rgba(0, 255, 135, 0.4);
    transform: scale(1.06);
}

.dice-card.matched .dice-icon {
    color: #00ff87 !important;
    filter: drop-shadow(0 0 10px rgba(0,255,135,0.8));
}

.dice-card.matched .dice-badge {
    background: #00ff87;
    color: #000000 !important;
}

/* Sidebar & Buttons 覆蓋 */
div[data-testid="stSidebar"] {
    background: rgba(15, 17, 26, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

div.stButton > button {
    border-radius: 18px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 0.6rem 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.18) !important;
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #007aff 0%, #00f0ff 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(0, 240, 255, 0.35) !important;
}

/* 文字標籤修飾 */
.stMarkdown, p, span, label {
    color: #f5f5f7 !important;
}
</style>
""", unsafe_allow_html=True)

DICE_ICONS = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dynamic_island(status_text, status_type="idle"):
    return f"""
    <div class="dynamic-island">
        <span class="island-dot {status_type}"></span>
        <span class="island-text">{status_text}</span>
    </div>
    """

def render_dice_html(rolls):
    cards_html = []
    for i, val in enumerate(rolls, 1):
        is_match = (val == i)
        card_class = "dice-card matched" if is_match else "dice-card"
        badge_text = "✓ MATCH" if is_match else f"第 {i} 擲"
        cards_html.append(f'''
            <div class="{card_class}">
                <span class="dice-icon">{DICE_ICONS[val]}</span>
                <span class="dice-badge">{badge_text}</span>
            </div>
        ''')
    return f'<div class="dice-wrapper">{"".join(cards_html)}</div>'

def render_kpi_html(title, val, color="#ffffff"):
    return f"""
    <div class="spatial-kpi-card">
        <div class="spatial-kpi-title">{title}</div>
        <div class="spatial-kpi-value" style="color: {color};">{val}</div>
    </div>
    """

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

# 4. iOS 27 Spatial Plotly 圖表 (極光光軌)
def build_clean_plotly_chart(df_data, total_n_setting):
    df_reset = df_data.reset_index().rename(columns={'index': 'n'})
    
    fig = go.Figure()

    # 理論 P(A) 參考虛線 (iOS System Pink/Red Glow)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['理論 P(A)'],
        mode='lines',
        name='理論 P(A)',
        line=dict(color='#FF375F', width=2, dash='dash'),
        hovertemplate='理論 P(A): %{y:.4f}<extra></extra>'
    ))

    # 模擬 P(A) (Spatial Neon Cyan 光點與軌跡)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['模擬 P(A)'],
        mode='lines+markers',
        name='模擬 P(A)',
        line=dict(color='#00F0FF', width=2.5),
        marker=dict(size=4.5, color='#00F0FF', opacity=0.9),
        hovertemplate='模擬次數 n: %{x}<br>估算 P(A): %{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        height=370,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        font=dict(family="-apple-system, SF Pro Text", size=12, color="#f5f5f7"),
        xaxis=dict(
            title='模擬次數 (n)',
            range=[1, max(total_n_setting, 10)],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.06)',
            zeroline=False
        ),
        yaxis=dict(
            title='相對頻率 P(A)',
            range=[0.35, 0.95],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.06)',
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

# 5. Session State 管理
if "anim_status" not in st.session_state:
    st.session_state.anim_status = "idle"
if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0
if "total_n" not in st.session_state:
    st.session_state.total_n = 1000

# 6. 動態島狀態更新
island_spot = st.empty()

# 7. 主標題與說明卡片
st.markdown("""
<div class="spatial-card">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px;">🎲 6 面骰子相配實驗</div>
    <div style="font-size: 14px; line-height: 1.6; color: #a1a1a6;">
        📌 <b>規則：</b> 丟擲一粒公平骰子 6 次，若第 $k$ 次丟擲點數等於 $k$（$k=1..6$）稱為<b>「相配」</b>。<br>
        6 次中只要<b>至少發生 1 次相配</b>即算成功（事件 $A$）。<br>
        🎯 <b>理論成功概率：</b> $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
    </div>
</div>
""", unsafe_allow_html=True)

# 8. 側邊欄
with st.sidebar:
    st.markdown('<div class="spatial-section-title">⚙️ 控制中心</div>', unsafe_allow_html=True)

    def sync_from_slider():
        st.session_state.total_n = st.session_state.slider_n
        st.session_state.anim_status = "idle"

    def sync_from_input():
        st.session_state.total_n = st.session_state.input_n
        st.session_state.anim_status = "idle"

    st.session_state.slider_n = st.session_state.total_n
    st.session_state.input_n = st.session_state.total_n

    st.markdown("**模擬總次數 (N)**")
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        st.slider("拉動次數", 100, 10000, 100, key="slider_n", on_change=sync_from_slider, label_visibility="collapsed")
    with col_s2:
        st.number_input("輸入次數", 100, 10000, 100, key="input_n", on_change=sync_from_input, label_visibility="collapsed")

    total_n = st.session_state.total_n
    fps = st.slider("動畫速率 (FPS)", 2, 25, 8)
    seed = st.number_input("隨機種子 (Seed)", 0, 9999, 42)
    
    st.divider()

    col_b1, col_b2, col_b3 = st.columns(3)
    start_click = col_b1.button("🚀 開始", type="primary", use_container_width=True)
    pause_label = "▶️ 繼續" if st.session_state.anim_status == "paused" else "⏸️ 暫停"
    pause_click = col_b2.button(pause_label, use_container_width=True)
    quick_click = col_b3.button("⚡ 結算", use_container_width=True)

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

# 9. 數據與儀表板渲染
rolls, cum_successes, cum_p = run_simulation(total_n, seed)
num_frames = min(total_n, 60)
frame_indices = np.unique(np.linspace(1, total_n, num=num_frames, dtype=int))

st.markdown('<div class="spatial-section-title">📈 即時數據儀表板</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
spot_kpi1 = kpi1.empty()
spot_kpi2 = kpi2.empty()
spot_kpi3 = kpi3.empty()
spot_kpi4 = kpi4.empty()

with st.container():
    st.markdown('<div class="spatial-section-title">🎲 當前丟擲結果</div>', unsafe_allow_html=True)
    dice_spot = st.empty()

with st.container():
    st.markdown('<div class="spatial-section-title">📊 相對頻率 P(A) 收斂軌跡</div>', unsafe_allow_html=True)
    chart_spot = st.empty()

df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))

plotly_config = {
    'scrollZoom': True,
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d']
}

def render_frame_ui(frame_n):
    spot_kpi1.markdown(render_kpi_html("模擬次數", f"{frame_n}"), unsafe_allow_html=True)
    spot_kpi2.markdown(render_kpi_html("成功次數", f"{cum_successes[frame_n-1]}"), unsafe_allow_html=True)
    spot_kpi3.markdown(render_kpi_html("估算 P(A)", f"{cum_p[frame_n-1]:.4f}", "#00F0FF"), unsafe_allow_html=True)
    spot_kpi4.markdown(render_kpi_html("理論 P(A)", f"{p_theoretical:.4f}", "#FF375F"), unsafe_allow_html=True)

    dice_spot.markdown(render_dice_html(rolls[frame_n-1]), unsafe_allow_html=True)
    chart_spot.plotly_chart(build_clean_plotly_chart(df_chart.iloc[:frame_n], total_n), use_container_width=True, config=plotly_config)

# 動態處理邏輯
if st.session_state.anim_status == "idle":
    island_spot.markdown(render_dynamic_island("SYSTEM READY • 點擊開始模擬", "idle"), unsafe_allow_html=True)
    render_frame_ui(1)

elif st.session_state.anim_status == "finished":
    island_spot.markdown(render_dynamic_island("SIMULATION COMPLETED", "finished"), unsafe_allow_html=True)
    render_frame_ui(total_n)
    st.success(f"🎉 模擬完成！最終估算 P(A) = {cum_p[-1]:.4f}，理論誤差僅 {abs(cum_p[-1]-p_theoretical):.4f}")

elif st.session_state.anim_status == "paused":
    current_n = frame_indices[st.session_state.current_step_idx]
    island_spot.markdown(render_dynamic_island(f"PAUSED AT STEP {current_n}", "paused"), unsafe_allow_html=True)
    render_frame_ui(current_n)

elif st.session_state.anim_status == "running":
    progress_bar = st.progress(0)
    
    start_idx = st.session_state.current_step_idx
    for idx in range(start_idx, len(frame_indices)):
        st.session_state.current_step_idx = idx
        current_n = frame_indices[idx]
        
        island_spot.markdown(render_dynamic_island(f"SIMULATING... {current_n} / {total_n}", "running"), unsafe_allow_html=True)
        progress_bar.progress(int((idx + 1) / len(frame_indices) * 100))
        render_frame_ui(current_n)
        
        time.sleep(1 / fps)
    
    progress_bar.empty()
    st.session_state.anim_status = "finished"
    st.rerun()

# 數據表格
if st.session_state.anim_status in ["paused", "finished"]:
    st.markdown('<div class="spatial-section-title">📊 關鍵節點數據統計</div>', unsafe_allow_html=True)
    targets = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_df = pd.DataFrame({
        '模擬次數 (n)': targets,
        '事件 A 發生次數': [int(cum_successes[n-1]) for n in targets],
        '估算 P(A)': [f"{cum_p[n-1]:.4f}" for n in targets],
        '理論 P(A)': f"{p_theoretical:.4f}"
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)
