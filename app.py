import time
import numpy as np
import pandas as pd
import streamlit as st

# 1. 頁面設定與全球 CSS 樣式 (將樣式抽離，極致精簡 HTML)
st.set_page_config(page_title="骰子相配模擬", page_icon="🎲", layout="wide")

st.markdown("""
<style>
.dice-container { display: flex; justify-content: center; gap: 12px; margin: 15px 0; }
.dice-box {
    width: 60px; height: 60px; border-radius: 12px; border: 2px solid #ddd;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-size: 28px; background: #ffffff; color: #333; transition: all 0.15s ease;
}
.dice-match { border-color: #28a745; background: #e8f5e9; color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

DICE_FACES = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dice_html(rolls):
    """產生精簡的骰子 HTML"""
    items = []
    for i, val in enumerate(rolls, 1):
        is_match = (val == i)
        cls = "dice-box dice-match" if is_match else "dice-box"
        badge = "✓ 相配" if is_match else f"第 {i} 擲"
        items.append(f'<div class="{cls}"><span>{DICE_FACES[val]}</span><span style="font-size:10px">{badge}</span></div>')
    return f'<div class="dice-container">{"".join(items)}</div>'

# 2. 高效向量化計算邏輯 (使用 Cache 提升效能)
@st.cache_data
def run_simulation(total_n, seed):
    np.random.seed(seed)
    rolls = np.random.randint(1, 7, size=(total_n, 6))
    matches = (rolls == np.arange(1, 7))
    successes = np.any(matches, axis=1)
    cum_successes = np.cumsum(successes)
    cum_p = cum_successes / np.arange(1, total_n + 1)
    return rolls, cum_successes, cum_p

# 3. 介面配置
st.title("🎲 6 面骰子相配實驗 (Example 1-1.1)")
st.caption("實驗說明：丟擲骰子 6 次，若第 k 次點數等於 k 稱為相配。至少 1 次相配為成功。")

p_theoretical = 1 - (5/6)**6

with st.sidebar:
    st.header("⚙️ 模擬控制")
    total_n = st.slider("模擬總次數 (N)", 100, 2000, 1000, 100)
    fps = st.slider("動畫幀率 (FPS)", 5, 40, 20)
    seed = st.number_input("隨機種子", 0, 9999, 42)
    start_btn = st.button("🚀 開始動態模擬", type="primary")

# 4. 動畫執行與結果渲染
if start_btn:
    rolls, cum_successes, cum_p = run_simulation(total_n, seed)
    
    # 動態 UI 佔位符
    progress_bar = st.progress(0)
    dice_spot = st.empty()
    chart_spot = st.empty()
    
    df_chart = pd.DataFrame({'模擬 P(A)': cum_p, '理論 P(A)': p_theoretical}, index=np.arange(1, total_n + 1))
    
    # 分頁批次更新動畫 (控制每秒刷新幀數，兼顧視覺與效能)
    chunk = max(1, total_n // 60)
    for i in range(1, total_n + 1, chunk):
        progress_bar.progress(i / total_n)
        dice_spot.markdown(render_dice_html(rolls[i-1]), unsafe_allow_html=True)
        chart_spot.line_chart(df_chart.iloc[:i], height=350)
        time.sleep(1 / fps)
        
    # 結算顯示
    progress_bar.empty()
    dice_spot.markdown(render_dice_html(rolls[-1]), unsafe_allow_html=True)
    chart_spot.line_chart(df_chart, height=350)
    
    st.success(f"✅ 模擬完成！最終估算 $P(A) = {cum_p[-1]:.4f}$（理論值 $\\approx {p_theoretical:.4f}$）")
    
    # (b) 統計數據表
    targets = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_df = pd.DataFrame({
        '模擬次數 (n)': targets,
        '事件 A 發生次數': [int(cum_successes[n-1]) for n in targets],
        '估算 P(A)': [f"{cum_p[n-1]:.4f}" for n in targets],
        '理論 P(A)': f"{p_theoretical:.4f}"
    })
    st.subheader("📊 指定模擬次數統計表 (b)")
    st.dataframe(table_df, use_container_width=True)
