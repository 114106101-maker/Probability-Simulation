import time
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# 1. 頁面配置
st.set_page_config(
    page_title="🎲 骰子相配實驗 (iOS HD Edition)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 注入 iOS 純白空間感 CSS 樣式
st.markdown("""
<style>
.stApp {
    background-color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    color: #1c1c1e;
}
.ios-card {
    background: rgba(248, 249, 250, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 20px 26px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 0, 0, 0.06);
}
.dice-wrapper {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 14px 0;
    flex-wrap: wrap;
}
.dice-card {
    width: 80px;
    height: 94px;
    background: #ffffff;
    border-radius: 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid rgba(0, 0, 0, 0.08);
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
.dice-card.matched {
    background: linear-gradient(135deg, #34c759 0%, #28a745 100%);
    border: none;
    box-shadow: 0 10px 25px rgba(52, 199, 89, 0.38);
    transform: translateY(-4px) scale(1.05);
}
.dice-card.matched .dice-icon {
    color: #ffffff;
}
.dice-card.matched .dice-label {
    color: #ffffff;
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

# 4. 高清解析度與動態縮放的高階 Altair 圖表
def build_hd_interactive_chart(df_data):
    df_reset = df_data.reset_index().rename(columns={'index': 'n'})
    
    # 懸停對齊感應器
    hover = alt.selection_point(on='pointerover', nearest=True, empty=False)

    # 基礎圖表構建（Y 軸取消固定 zero，自動聚焦細微波動）
    base = alt.Chart(df_reset).encode(
        x=alt.X('n:Q', title='模擬次數 (n)', axis=alt.Axis(grid=True, gridColor='#f0f0f5', labelFontSize=11, titleFontSize=12)),
        y=alt.Y('模擬 P(A):Q', title='相對頻率 P(A)', 
                scale=alt.Scale(zero=False, padding=20),  # 核心關鍵：縮放 Y 軸，讓細節顯現
                axis=alt.Axis(grid=True, gridColor='#f0f0f5', labelFontSize=11, titleFontSize=12, format='.3f'))
    )

    # 理論 P(A) 參考虛線 (iOS 紅色)
    line_theo = alt.Chart(df_reset).mark_line(
        color='#ff3b30', 
        strokeWidth=2, 
        strokeDash=[6, 4]
    ).encode(
        x='n:Q',
        y='理論 P(A):Q'
    )

    # 模擬相對頻率折線 (iOS 高對比深藍色)
    line_sim = base.mark_line(
        color='#007aff', 
        strokeWidth=2.2
    )

    # 滑鼠懸停垂直指示線
    v_rule = base.mark_rule(color='rgba(0,122,255,0.25)', strokeWidth=1.5).encode(
        x='n:Q'
    ).transform_filter(hover)

    # 滑鼠懸停放大焦點與 Tooltip
    hover_points = base.mark_circle().encode(
        size=alt.condition(hover, alt.value(220), alt.value(0)), # 未懸停隱藏，懸停大幅放大
        color=alt.condition(hover, alt.value('#007aff'), alt.value('transparent')),
        tooltip=[
            alt.Tooltip('n:Q', title='模擬次數 (n)'),
            alt.Tooltip('模擬 P(A):Q', title='估算 P(A)', format='.4f'),
            alt.Tooltip('理論 P(A):Q', title='理論 P(A)', format='.4f')
        ]
    ).add_params(hover)

    # 組合圖表，開啓可雙向縮放平移 (.interactive())
    chart = (line_theo + line_sim + v_rule + hover_points).properties(
        height=380
    ).configure_view(
        strokeWidth=0
    ).interactive()
    
    return chart

# 5. 主頁面標頭與規則說明
st.title("🎲 6 面骰子相配實驗 (Example 1-1.1)")

st.markdown("""
<div class="ios-card">
    <div style="font-size: 15px; line-height: 1.6; color: #1c1c1e;">
        📌 <b>實驗規則：</b> 丟擲一粒公平骰子 6 次。若第 $k$ 次丟擲結果點數等於 $k$（$k=1..6$），稱為<b>「相配」</b>。<br>
        只要 6 次丟擲中<b>至少發生 1 次相配</b>即算成功（事件 $A$）。<br>
        🎯 <b>理論成功概率：</b> $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 控制面板
with st.sidebar:
    st.header("⚙️ 模擬控制面板")
    total_n = st.slider("模擬總次數 (N)", 100, 2000, 1000, 100)
    fps = st.slider("動畫幀率 (FPS)", 5, 40, 20)
    seed = st.number_input("隨機種子 (Seed)", 0, 9999, 42)
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_btn = st.button("🚀 開始動畫", type="primary", use_container_width=True)
    with col_btn2:
        quick_btn = st.button("⚡ 直接結算", use_container_width=True)

p_theoretical = 1 - (5/6)**6

# 7. 主體驗區域
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
        st.markdown("**📊 高清相對頻率 P(A) 收斂軌跡** *(可使用滑鼠滾輪縮放、平移拉動與懸停查看焦點)*")
        chart_spot = st.empty()
        
    df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))

    if quick_btn:
        kpi_n.metric("當前模擬次數", f"{total_n}")
        kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[-1]}")
        kpi_p.metric("估算 P(A)", f"{cum_p[-1]:.4f}", delta=f"{cum_p[-1]-p_theoretical:.4f}")
        
        dice_spot.markdown(render_dice_html(rolls[-1]), unsafe_allow_html=True)
        chart_spot.altair_chart(build_hd_interactive_chart(df_chart), use_container_width=True)
    else:
        progress_bar = st.progress(0)
        chunk = max(1, total_n // 50)
        
        for i in range(1, total_n + 1, chunk):
            progress_bar.progress(i / total_n)
            
            kpi_n.metric("當前模擬次數", f"{i}")
            kpi_succ.metric("成功次數 (事件 A)", f"{cum_successes[i-1]}")
            kpi_p.metric("估算 P(A)", f"{cum_p[i-1]:.4f}", delta=f"{cum_p[i-1]-p_theoretical:.4f}")
            
            dice_spot.markdown(render_dice_html(rolls[i-1]), unsafe_allow_html=True)
            chart_spot.altair_chart(build_hd_interactive_chart(df_chart.iloc[:i]), use_container_width=True)
            
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
