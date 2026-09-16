import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 (iOS Native)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 精緻 iOS 原生設計語言 CSS
st.markdown("""
<style>
/* iOS 系統背景與字型設定 */
html, body, .stApp {
    background-color: #f2f2f7 !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif !important;
    color: #1c1c1e !important;
}

/* 頁面邊距優化 */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1050px;
}

/* iOS Large Title 標題風格 */
.ios-large-title {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.8px;
    color: #000000;
    margin-bottom: 4px;
}

.ios-sub-title {
    font-size: 14px;
    color: #8e8e93;
    font-weight: 500;
    margin-bottom: 16px;
}

/* iOS 毛玻璃懸浮卡片 (Glassmorphism) */
.ios-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 22px;
    padding: 20px 24px;
    margin-bottom: 18px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02);
}

/* iOS 分組標題 (Grouped Section Header) */
.ios-section-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #8e8e93;
    margin: 16px 0 8px 4px;
}

/* iOS Widget 小工具數據卡片 */
.ios-kpi-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 16px 12px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.04);
}

.ios-kpi-title {
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.ios-kpi-value {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.6px;
    color: #1c1c1e;
}

/* iOS 骰子 Widget 與彈簧動態 */
.dice-wrapper {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 10px 0;
    flex-wrap: wrap;
}

@keyframes ios-spring-bounce {
    0% { transform: scale(0.88) translateY(6px); opacity: 0.6; }
    60% { transform: scale(1.05) translateY(-2px); opacity: 0.95; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

.dice-card {
    width: 76px;
    height: 90px;
    background: #ffffff;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 0, 0, 0.05);
    animation: ios-spring-bounce 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.dice-icon {
    font-size: 38px;
    line-height: 1;
    margin-bottom: 4px;
    color: #1c1c1e;
}

.dice-badge {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
    background: #e5e5ea;
    color: #8e8e93;
}

/* 相配成功狀態 (iOS System Green) */
.dice-card.matched {
    background: linear-gradient(135deg, #34c759 0%, #28a745 100%);
    border: none;
    box-shadow: 0 8px 24px rgba(52, 199, 89, 0.35);
    transform: scale(1.06);
}

.dice-card.matched .dice-icon {
    color: #ffffff !important;
}

.dice-card.matched .dice-badge {
    background: rgba(255, 255, 255, 0.25);
    color: #ffffff !important;
}

/* 覆蓋 Streamlit 元件圓角與觸控反饋 */
div[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid rgba(0,0,0,0.06);
}

div.stButton > button {
    border-radius: 16px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.55rem 1rem !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    transition: transform 0.15s ease, background-color 0.15s ease !important;
}

div.stButton > button:active {
    transform: scale(0.96) !important;
}

div.stButton > button[kind="primary"] {
    background-color: #007aff !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3) !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
}
</style>
""", unsafe_allow_html=True)

DICE_ICONS = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dice_html(rolls):
    cards_html = []
    for i, val in enumerate(rolls, 1):
        is_match = (val == i)
        card_class = "dice-card matched" if is_match else "dice-card"
        badge_text = "✓ 相配" if is_match else f"第 {i} 擲"
        cards_html.append(f'''
            <div class="{card_class}">
                <span class="dice-icon">{DICE_ICONS[val]}</span>
                <span class="dice-badge">{badge_text}</span>
            </div>
        ''')
    return f'<div class="dice-wrapper">{"".join(cards_html)}</div>'

def render_kpi_html(title, val, color="#1c1c1e"):
    return f"""
    <div class="ios-kpi-card">
        <div class="ios-kpi-title">{title}</div>
        <div class="ios-kpi-value" style="color: {color};">{val}</div>
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

# 4. iOS 風格 Plotly 圖表生成器 (含數據圓點)
def build_clean_plotly_chart(df_data, total_n_setting):
    df_reset = df_data.reset_index().rename(columns={'index': 'n'})
    
    fig = go.Figure()

    # 理論 P(A) 參考線 (iOS System Red)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['理論 P(A)'],
        mode='lines',
        name='理論 P(A)',
        line=dict(color='#FF3B30', width=2, dash='dash'),
        hovertemplate='理論 P(A): %{y:.4f}<extra></extra>'
    ))

    # 模擬 P(A) (iOS System Blue + 精細圓點標註)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['模擬 P(A)'],
        mode='lines+markers',
        name='模擬 P(A)',
        line=dict(color='#007AFF', width=2),
        marker=dict(size=4, color='#007AFF', opacity=0.8),
        hovertemplate='模擬次數 n: %{x}<br>估算 P(A): %{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#ffffff',
        hovermode='x unified',
        font=dict(family="-apple-system, SF Pro Text", size=12, color="#1c1c1e"),
        xaxis=dict(
            title='模擬次數 (n)',
            range=[1, max(total_n_setting, 10)],
            showgrid=True,
            gridcolor='#f2f2f7',
            zeroline=False
        ),
        yaxis=dict(
            title='相對頻率 P(A)',
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

# 6. 主頁面標頭 (iOS Large Title Style)
st.markdown('<div class="ios-large-title">🎲 6 面骰子相配實驗</div>', unsafe_allow_html=True)
st.markdown('<div class="ios-sub-title">機率論古典模型模擬與大數法則收斂動態展示</div>', unsafe_allow_html=True)

st.markdown("""
<div class="ios-card">
    <div style="font-size: 14px; line-height: 1.6; color: #1c1c1e;">
        📌 <b>實驗規則：</b> 丟擲一粒公平骰子 6 次。若第 $k$ 次丟擲點數等於 $k$（$k=1..6$），稱為<b>「相配」</b>。<br>
        6 次中只要<b>至少發生 1 次相配</b>即算成功（事件 $A$）。<br>
        🎯 <b>理論成功概率：</b> $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
    </div>
</div>
""", unsafe_allow_html=True)

# 7. 側邊欄控制面板
with st.sidebar:
    st.markdown('<div class="ios-section-label">⚙️ 控制選項</div>', unsafe_allow_html=True)

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

# 8. 數據準備與渲染 logic
rolls, cum_successes, cum_p = run_simulation(total_n, seed)
num_frames = min(total_n, 60)
frame_indices = np.unique(np.linspace(1, total_n, num=num_frames, dtype=int))

# 主數據面板
st.markdown('<div class="ios-section-label">📈 即時數據儀表板</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
spot_kpi1 = kpi1.empty()
spot_kpi2 = kpi2.empty()
spot_kpi3 = kpi3.empty()
spot_kpi4 = kpi4.empty()

with st.container():
    st.markdown('<div class="ios-section-label">🎲 當前丟擲結果</div>', unsafe_allow_html=True)
    dice_spot = st.empty()

with st.container():
    st.markdown('<div class="ios-section-label">📊 相對頻率 P(A) 收斂軌跡</div>', unsafe_allow_html=True)
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
    spot_kpi3.markdown(render_kpi_html("估算 P(A)", f"{cum_p[frame_n-1]:.4f}", "#007AFF"), unsafe_allow_html=True)
    spot_kpi4.markdown(render_kpi_html("理論 P(A)", f"{p_theoretical:.4f}", "#FF3B30"), unsafe_allow_html=True)

    dice_spot.markdown(render_dice_html(rolls[frame_n-1]), unsafe_allow_html=True)
    chart_spot.plotly_chart(build_clean_plotly_chart(df_chart.iloc[:frame_n], total_n), use_container_width=True, config=plotly_config)

# 根據播放狀態進行對應處理
if st.session_state.anim_status == "idle":
    render_frame_ui(1)
    st.info("👈 請點擊左側面板 **「🚀 開始」** 啟動實驗動畫，或點擊 **「⚡ 結算」** 直接獲取結果。")

elif st.session_state.anim_status == "finished":
    render_frame_ui(total_n)
    st.success(f"🎉 模擬完成！最終估算 P(A) = {cum_p[-1]:.4f}，與理論值誤差僅 {abs(cum_p[-1]-p_theoretical):.4f}")

elif st.session_state.anim_status == "paused":
    current_n = frame_indices[st.session_state.current_step_idx]
    render_frame_ui(current_n)
    st.warning(f"⏸️ 動畫已暫停於第 {current_n} 次模擬，點擊左側 **「▶️ 繼續」** 恢復播放。")

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

# 底部數據表格
if st.session_state.anim_status in ["paused", "finished"]:
    st.markdown('<div class="ios-section-label">📊 關鍵節點數據統計</div>', unsafe_allow_html=True)
    targets = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_df = pd.DataFrame({
        '模擬次數 (n)': targets,
        '事件 A 發生次數': [int(cum_successes[n-1]) for n in targets],
        '估算 P(A)': [f"{cum_p[n-1]:.4f}" for n in targets],
        '理論 P(A)': f"{p_theoretical:.4f}"
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)
