import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 (iOS Ultra Clean)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 強效 CSS 樣式 (包含骰子動態彈跳特效)
st.markdown("""
<style>
html, body, .stApp {
    background-color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    color: #1c1c1e !important;
}

.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

.stMarkdown, p, span, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stHeader"] {
    color: #1c1c1e !important;
}

.ios-card {
    background: #f8f9fa;
    border-radius: 20px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    border: 1px solid #e5e5ea;
}

.dice-wrapper {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin: 10px 0;
    flex-wrap: wrap;
}

/* 骰子更新時的彈跳動畫特效 */
@keyframes dice-pop {
    0% { transform: scale(0.85) translateY(-6px); opacity: 0.6; }
    50% { transform: scale(1.08) translateY(2px); opacity: 0.9; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

.dice-card {
    width: 76px;
    height: 90px;
    background: #ffffff;
    border-radius: 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    border: 1px solid #e5e5ea;
    animation: dice-pop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.dice-icon {
    font-size: 38px;
    line-height: 1;
    margin-bottom: 2px;
    color: #1c1c1e;
}

.dice-label {
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
}

.dice-card.matched {
    background: #34c759;
    border: none;
    box-shadow: 0 6px 18px rgba(52, 199, 89, 0.35);
    transform: scale(1.05);
}

.dice-card.matched .dice-icon,
.dice-card.matched .dice-label {
    color: #ffffff !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

DICE_ICONS = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dice_html(rolls):
    cards_html = []
    for i, val in enumerate(rolls, 1):
        is_match = (val == i)
        card_class = "dice-card matched" if is_match else "dice-card"
        badge = "✓ 相配" if is_match else f"第 {i} 擲"
        cards_html.append(f'<div class="{card_class}"><span class="dice-icon">{DICE_ICONS[val]}</span><span class="dice-label">{badge}</span></div>')
    return f'<div class="dice-wrapper">{"".join(cards_html)}</div>'

# 3. 向量化計算邏輯
@st.cache_data
def run_simulation(total_n, seed):
    np.random.seed(seed)
    rolls = np.random.randint(1, 7, size=(total_n, 6))
    matches = (rolls == np.arange(1, 7))
    successes = np.any(matches, axis=1)
    cum_successes = np.cumsum(successes)
    cum_p = cum_successes / np.arange(1, total_n + 1)
    return rolls, cum_successes, cum_p

# 4. 保留圓點的高畫質 Plotly 圖表生成器
def build_clean_plotly_chart(df_data, total_n_setting):
    df_reset = df_data.reset_index().rename(columns={'index': 'n'})
    
    fig = go.Figure()

    # 理論 P(A) 參考虛線 (紅色)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['理論 P(A)'],
        mode='lines',
        name='理論 P(A)',
        line=dict(color='#FF3B30', width=2, dash='dash'),
        hovertemplate='理論 P(A): %{y:.4f}<extra></extra>'
    ))

    # 模擬 P(A) (全時保留圓點模式 lines+markers)
    fig.add_trace(go.Scatter(
        x=df_reset['n'],
        y=df_reset['模擬 P(A)'],
        mode='lines+markers',
        name='模擬 P(A)',
        line=dict(color='#007AFF', width=1.8),
        marker=dict(size=3.5, color='#007AFF', opacity=0.85),
        hovertemplate='模擬次數 n: %{x}<br>估算 P(A): %{y:.4f}<extra></extra>'
    ))

    # 固定 X 軸與 Y 軸範圍
    fig.update_layout(
        height=390,
        margin=dict(l=15, r=15, t=30, b=15),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        hovermode='x unified',
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

# 5. 主頁面內容
st.title("🎲 6 面骰子相配實驗 (Example 1-1.1)")

st.markdown("""
<div class="ios-card">
    <div style="font-size: 15px; line-height: 1.6;">
        📌 <b>實驗規則：</b> 丟擲一粒公平骰子 6 次。若第 $k$ 次丟擲結果點數等於 $k$（$k=1..6$），稱為<b>「相配」</b>。<br>
        只要 6 次丟擲中<b>至少發生 1 次相配</b>即算成功（事件 $A$）。<br>
        🎯 <b>理論成功概率：</b> $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 側邊欄控制
with st.sidebar:
    st.header("⚙️ 模擬控制面板")
    
    if "total_n" not in st.session_state:
        st.session_state.total_n = 1000

    def sync_from_slider():
        st.session_state.total_n = st.session_state.slider_n

    def sync_from_input():
        st.session_state.total_n = st.session_state.input_n

    st.session_state.slider_n = st.session_state.total_n
    st.session_state.input_n = st.session_state.total_n

    st.markdown("**模擬總次數 (N)**")
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        st.slider("拉動次數", 100, 10000, 100, key="slider_n", on_change=sync_from_slider, label_visibility="collapsed")
    with col_s2:
        st.number_input("輸入次數", 100, 10000, 100, key="input_n", on_change=sync_from_input, label_visibility="collapsed")

    total_n = st.session_state.total_n
    fps = st.slider("動畫幀率 (FPS)", 5, 40, 20)
    seed = st.number_input("隨機種子 (Seed)", 0, 9999, 42)
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_btn = st.button("🚀 開始動畫", type="primary", use_container_width=True)
    with col_btn2:
        quick_btn = st.button("⚡ 直接結算", use_container_width=True)

p_theoretical = 1 - (5/6)**6

# 7. 主數據區塊
if start_btn or quick_btn:
    rolls, cum_successes, cum_p = run_simulation(total_n, seed)
    
    st.subheader("📈 數據儀表板")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    kpi_n = m_col1.metric("當前模擬次數", "0")
    kpi_succ = m_col2.metric("成功次數 (事件 A)", "0")
    kpi_p = m_col3.metric("估算 P(A)", "0.0000")
    kpi_theo = m_col4.metric("理論 P(A)", f"{p_theoretical:.4f}")

    with st.container(border=True):
        st.markdown("**🎲 最新一次丟擲結果**")
        dice_spot = st.empty()
        dice_spot.markdown(render_dice_html([1, 2, 3, 4, 5, 6]), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**📊 相對頻率 P(A) 收斂軌跡** *(右上角可全螢幕，可透過滾輪/框選自由放大細節)*")
        chart_spot = st.empty()
        
    df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))

    plotly_config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d']
    }

    if quick_btn:
        kpi_n.metric("當前模擬次數", f"{total_n}")
        kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[-1]}")
        kpi_p.metric("估算 P(A)", f"{cum_p[-1]:.4f}", delta=f"{cum_p[-1]-p_theoretical:.4f}")
        
        dice_spot.markdown(render_dice_html(rolls[-1]), unsafe_allow_html=True)
        chart_spot.plotly_chart(build_clean_plotly_chart(df_chart, total_n), use_container_width=True, config=plotly_config)
    else:
        progress_bar = st.progress(0)
        
        # 建立影格序列：確保均勻取樣且最後一影格必定為 total_n
        num_frames = min(total_n, 35)
        frame_indices = np.unique(np.linspace(1, total_n, num=num_frames, dtype=int))
        
        for idx, i in enumerate(frame_indices):
            progress_bar.progress(int((idx + 1) / len(frame_indices) * 100))
            
            kpi_n.metric("當前模擬次數", f"{i}")
            kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[i-1]}")
            kpi_p.metric("估算 P(A)", f"{cum_p[i-1]:.4f}", delta=f"{cum_p[i-1]-p_theoretical:.4f}")
            
            dice_spot.markdown(render_dice_html(rolls[i-1]), unsafe_allow_html=True)
            chart_spot.plotly_chart(build_clean_plotly_chart(df_chart.iloc[:i], total_n), use_container_width=True, config=plotly_config)
            
            time.sleep(1 / fps)
            
        progress_bar.empty()

    st.success(f"🎉 模擬完成！最終估算 P(A) = {cum_p[-1]:.4f}，與理論值誤差僅 {abs(cum_p[-1]-p_theoretical):.4f}")

    st.subheader("📊 指定模擬次數統計結果 (b)")
    targets = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_df = pd.DataFrame({
        '模擬次數 (n)': targets,
        '事件 A 發生次數': [int(cum_successes[n-1]) for n in targets],
        '估算 P(A)': [f"{cum_p[n-1]:.4f}" for n in targets],
        '理論 P(A)': f"{p_theoretical:.4f}"
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 請點擊左側控制面板的 **「🚀 開始動畫」** 或 **「⚡ 直接結算」** 啟動實驗模擬！")
