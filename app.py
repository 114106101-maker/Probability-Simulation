import time
import numpy as np
import pandas as pd
import streamlit as st

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 (iOS Edition)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 注入 iOS 風格 CSS 樣式 (Glassmorphism + SF Pro 字體 + iOS 圓角與綠/藍配色)
st.markdown("""
<style>
/* 全局背景與 iOS SF 字體系 */
.stApp {
    background-color: #f2f2f7 !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", sans-serif;
}

/* iOS 毛玻璃卡片基底 */
.ios-card {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.8);
}

/* 骰子展示容器 */
.dice-wrapper {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin: 12px 0;
    flex-wrap: wrap;
}

/* iOS 經典大圓角骰子卡片 (Squircle) */
.dice-card {
    width: 76px;
    height: 90px;
    background: #ffffff;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(0, 0, 0, 0.03);
}

.dice-icon {
    font-size: 40px;
    line-height: 1;
    margin-bottom: 2px;
    color: #1c1c1e;
}

.dice-label {
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
    letter-spacing: -0.2px;
}

/* iOS 綠色成功態 (System Green Glow) */
.dice-card.matched {
    background: #34c759;
    box-shadow: 0 6px 18px rgba(52, 199, 89, 0.35);
    transform: scale(1.04);
    border: none;
}

.dice-card.matched .dice-icon {
    color: #ffffff;
}

.dice-card.matched .dice-label {
    color: rgba(255, 255, 255, 0.9);
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

# 3. 高效向量化計算邏輯
@st.cache_data
def run_simulation(total_n, seed):
    np.random.seed(seed)
    rolls = np.random.randint(1, 7, size=(total_n, 6))
    matches = (rolls == np.arange(1, 7))
    successes = np.any(matches, axis=1)
    cum_successes = np.cumsum(successes)
    cum_p = cum_successes / np.arange(1, total_n + 1)
    return rolls, cum_successes, cum_p

# 4. 主頁面標頭與規則說明卡片
st.title("🎲 6 面骰子相配實驗")

st.markdown("""
<div class="ios-card">
    <div style="font-size: 15px; color: #1c1c1e; line-height: 1.6;">
        <b>📌 實驗規則：</b> 丟擲一粒公平骰子 6 次。若第 $k$ 次丟擲結果為點數 $k$（$k=1..6$），稱為<b>「相配」</b>。<br>
        只要 6 次丟擲中<b>至少發生 1 次相配</b>即算成功（事件 $A$）。<br>
        <b>🎯 理論成功概率：</b> $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
    </div>
</div>
""", unsafe_allow_html=True)

# 5. 控制面板
with st.sidebar:
    st.header("⚙️ 模擬控制")
    total_n = st.slider("模擬總次數 (N)", 100, 2000, 1000, 100)
    fps = st.slider("動畫流暢度 (FPS)", 5, 40, 20)
    seed = st.number_input("隨機種子 (Seed)", 0, 9999, 42)
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_btn = st.button("🚀 開始動畫", type="primary", use_container_width=True)
    with col_btn2:
        quick_btn = st.button("⚡ 直接結算", use_container_width=True)

p_theoretical = 1 - (5/6)**6

# 6. 主體驗區域
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
        st.markdown("**📊 相對頻率 P(A) 收斂曲線**")
        chart_spot = st.empty()
        
    df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))

    if quick_btn:
        kpi_n.metric("當前模擬次數", f"{total_n}")
        kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[-1]}")
        kpi_p.metric("估算 P(A)", f"{cum_p[-1]:.4f}", delta=f"{cum_p[-1]-p_theoretical:.4f}")
        
        dice_spot.markdown(render_dice_html(rolls[-1]), unsafe_allow_html=True)
        chart_spot.line_chart(df_chart, height=350)
    else:
        progress_bar = st.progress(0)
        chunk = max(1, total_n // 50)
        
        for i in range(1, total_n + 1, chunk):
            progress_bar.progress(i / total_n)
            
            kpi_n.metric("當前模擬次數", f"{i}")
            kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[i-1]}")
            kpi_p.metric("估算 P(A)", f"{cum_p[i-1]:.4f}", delta=f"{cum_p[i-1]-p_theoretical:.4f}")
            
            dice_spot.markdown(render_dice_html(rolls[i-1]), unsafe_allow_html=True)
            chart_spot.line_chart(df_chart.iloc[:i], height=350)
            
            time.sleep(1 / fps)
            
        progress_bar.empty()

    st.success(f"🎉 模擬完成！最終估算 P(A) = {cum_p[-1]:.4f}，與理論值差距為 {abs(cum_p[-1]-p_theoretical):.4f}")

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
