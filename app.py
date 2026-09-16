import time
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="骰子相配實驗模擬", page_icon="🎲", layout="wide")

st.title("🎲 6 面骰子相配實驗 (Example 1-1.1) 動畫模擬器")

st.markdown("""
**實驗規則：**
丟擲一粒公平的 6 面骰子 6 次。若第 $k$ 次丟擲結果為點數 $k$（$k = 1, 2, 3, 4, 5, 6$），稱為發生一次**相配**。
6 次丟擲中**至少有 1 個相配**即為成功（事件 $A$）。
* 理論概率：$P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
""")

# 側邊欄參數設定
st.sidebar.header("⚙️ 模擬參數")
total_n = st.sidebar.slider("總模擬次數 (N)", min_value=100, max_value=2000, value=1000, step=100)
anim_speed = st.sidebar.slider("動畫更新頻率 (FPS)", min_value=1, max_value=30, value=15)
seed = st.sidebar.number_input("隨機種子 (Seed)", min_value=0, max_value=9999, value=42)

start_btn = st.sidebar.button("🚀 開始模擬動畫", type="primary")

theoretical_p = 1 - (5/6)**6

if start_btn:
    np.random.seed(seed)
    
    # 建立動畫動態占位區域
    status_box = st.empty()
    chart_box = st.empty()
    table_title = st.empty()
    table_box = st.empty()
    
    # 預先生成實驗數據
    rolls = np.random.randint(1, 7, size=(total_n, 6))
    target = np.array([1, 2, 3, 4, 5, 6])
    matches = (rolls == target)
    successes = np.any(matches, axis=1)
    
    cum_successes = np.cumsum(successes)
    trials = np.arange(1, total_n + 1)
    prob_A = cum_successes / trials
    
    # 建立完整 DataFrame
    df_full = pd.DataFrame({
        '模擬相對頻率 P(A)': prob_A,
        '理論概率 (0.6651)': theoretical_p
    }, index=trials)
    
    # 動畫播放迴圈 (分批更新以確保流暢度)
    step_chunk = max(1, total_n // 100)
    for i in range(1, total_n + 1, step_chunk):
        status_box.info(f"⏳ 模擬進行中... 已完成 **{i} / {total_n}** 次 | 當前 $P(A) = {prob_A[i-1]:.4f}$")
        chart_box.line_chart(df_full.iloc[:i], height=400)
        time.sleep(1 / anim_speed)
        
    # 動畫結束顯示最終狀態
    status_box.success(f"✅ 模擬完成！最終 $P(A) = {prob_A[-1]:.4f}$（理論值 $\\approx {theoretical_p:.4f}$）")
    chart_box.line_chart(df_full, height=400)
    
    # (b) 統計列表
    target_steps = [n for n in [50, 100, 250, 500, 750, 1000] if n <= total_n]
    table_data = []
    for n in target_steps:
        succ = cum_successes[n - 1]
        p_hat = prob_A[n - 1]
        table_data.append({
            '模擬次數 (n)': n,
            '事件 A 發生次數': int(succ),
            '估算 P(A)': f"{p_hat:.4f}",
            '理論 P(A)': f"{theoretical_p:.4f}"
        })
        
    table_title.subheader("📊 指定模擬次數結果統計 (b)")
    table_box.dataframe(pd.DataFrame(table_data), use_container_width=True)