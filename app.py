import time
import random
import numpy as np
import pandas as pd
import streamlit as st

# 頁面基本設定
st.set_page_config(
    page_title="6面骰子相配實驗動畫模擬", 
    page_icon="🎲", 
    layout="wide"
)

st.title("🎲 6 面骰子相配實驗 (Example 1-1.1) 動畫模擬器")

st.markdown("""
**實驗規則：**
丟擲一粒公平的 6 面骰子 6 次。若第 $k$ 次丟擲結果為點數 $k$（$k = 1, 2, 3, 4, 5, 6$），稱為發生一次**相配**。
6 次丟擲中**至少有 1 個相配**即為成功（事件 $A$）。
* **理論概率：** $P(A) = 1 - (\\frac{5}{6})^6 \\approx 0.6651$
""")

# 骰子 Unicode 圖標映射
DICE_ICONS = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

def render_dice_cards(dice_values, is_rolling=False):
    """渲染 6 顆骰子的 HTML 卡片元件"""
    html = '<div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin: 15px 0; flex-wrap: wrap;">'
    
    for idx, val in enumerate(dice_values):
        target_k = idx + 1
        is_match = (val == target_k) and not is_rolling
        
        # 卡片配色風格
        bg_color = "#d4edda" if is_match else "#ffffff"
        border_color = "#28a745" if is_match else "#d0d0d0"
        text_color = "#155724" if is_match else "#333333"
        badge_text = "✅ 相配!" if is_match else f"目標: {target_k}"
        
        # 滾動中的微幅旋轉效果
        transform = f"rotate({random.randint(-15, 15)}deg)" if is_rolling else "rotate(0deg)"
        
        html += f'''
        <div style="text-align: center; transform: {transform}; transition: all 0.1s ease;">
            <div style="font-size: 13px; color: #666; margin-bottom: 4px; font-weight: bold;">第 {target_k} 擲</div>
            <div style="
                width: 70px;
                height: 70px;
                border: 3px solid {border_color};
                background-color: {bg_color};
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <span style="font-size: 42px; line-height: 1; color: {text_color};">{DICE_ICONS[val]}</span>
            </div>
            <div style="font-size: 12px; font-weight: bold; margin-top: 6px; color: {text_color};">{badge_text}</div>
        </div>
        '''
    html += '</div>'
    return html

# 側邊欄控制
st.sidebar.header("⚙️ 模擬參數控制")
total_n = st.sidebar.slider("連續模擬總次數 (N)", min_value=100, max_value=2000, value=1000, step=100)
anim_speed = st.sidebar.slider("圖表動畫更新速度", min_value=5, max_value=50, value=20)
seed = st.sidebar.number_input("隨機種子 (Seed)", min_value=0, max_value=9999, value=42)

theoretical_p = 1 - (5/6)**6

# 分頁標籤
tab1, tab2 = st.tabs(["🎲 單次擲骰動畫體驗", "📈 1,000 次連續模擬與概率收斂"])

# -------------------------------------------------------------------
# 分頁 1：單次擲骰動畫體驗
# -------------------------------------------------------------------
with tab1:
    st.subheader("🎲 擲骰子視覺動畫示範")
    st.write("點擊下方按鈕，體驗單次實驗中 6 顆骰子的滾動與相配檢查判定：")
    
    roll_single_btn = st.button("🎲 開始投擲骰子！", type="primary")
    
    dice_placeholder = st.empty()
    result_placeholder = st.empty()
    
    # 預設展示狀態
    dice_placeholder.markdown(render_dice_cards([1, 2, 3, 4, 5, 6]), unsafe_allow_html=True)
    
    if roll_single_btn:
        # 1. 播放滾動動畫 (翻滾 10 幀)
        for _ in range(10):
            temp_rolls = [random.randint(1, 6) for _ in range(6)]
            dice_placeholder.markdown(render_dice_cards(temp_rolls, is_rolling=True), unsafe_allow_html=True)
            time.sleep(0.08)
            
        # 2. 顯示最終點數
        final_rolls = [random.randint(1, 6) for _ in range(6)]
        matches = [val == (i + 1) for i, val in enumerate(final_rolls)]
        has_match = any(matches)
        
        dice_placeholder.markdown(render_dice_cards(final_rolls, is_rolling=False), unsafe_allow_html=True)
        
        # 3. 顯示結果判定
        if has_match:
            match_positions = [str(i + 1) for i, m in enumerate(matches) if m]
            result_placeholder.success(f"🎉 **實驗成功！** 在第 {', '.join(match_positions)} 次丟擲發生相配！")
        else:
            result_placeholder.error("❌ **實驗失敗！** 6 次丟擲中完全沒有任何點數與次序相配。")

# -------------------------------------------------------------------
# 分頁 2：連續模擬動畫與概率收斂
# -------------------------------------------------------------------
with tab2:
    st.subheader("📊 連續實驗與相對頻率收斂趨勢")
    start_sim_btn = st.button("🚀 開始大量模擬動畫", type="primary")
    
    status_box = st.empty()
    live_dice_box = st.empty()
    chart_box = st.empty()
    table_title = st.empty()
    table_box = st.empty()
    
    if start_sim_btn:
        np.random.seed(seed)
        
        # 預先生成 N 次實驗數據
        rolls = np.random.randint(1, 7, size=(total_n, 6))
        target = np.array([1, 2, 3, 4, 5, 6])
        matches = (rolls == target)
        successes = np.any(matches, axis=1)
        
        cum_successes = np.cumsum(successes)
        trials = np.arange(1, total_n + 1)
        prob_A = cum_successes / trials
        
        df_full = pd.DataFrame({
            '模擬 P(A)': prob_A,
            '理論 P(A)': theoretical_p
        }, index=trials)
        
        # 動畫播放（分批更新）
        step_chunk = max(1, total_n // 80)
        
        for i in range(1, total_n + 1, step_chunk):
            current_rolls = rolls[i-1].tolist()
            
            # 隨機加入 2 幀極快速滾動視覺效果
            for _ in range(2):
                rand_rolls = [random.randint(1, 6) for _ in range(6)]
                live_dice_box.markdown(render_dice_cards(rand_rolls, is_rolling=True), unsafe_allow_html=True)
                time.sleep(0.01)
                
            # 更新最新一次實驗的實際骰子點數
            live_dice_box.markdown(render_dice_cards(current_rolls, is_rolling=False), unsafe_allow_html=True)
            
            # 更新狀態與圖表
            status_box.info(f"⏳ 模擬進行中... 第 **{i} / {total_n}** 次實驗 | 最新 P(A) = **{prob_A[i-1]:.4f}**")
            chart_box.line_chart(df_full.iloc[:i], height=380)
            
            time.sleep(1 / anim_speed)
            
        # 結束狀態顯示
        status_box.success(f"✅ 模擬完成！最終 $P(A) = {prob_A[-1]:.4f}$（理論值 $P(A) \\approx {theoretical_p:.4f}$）")
        chart_box.line_chart(df_full, height=380)
        
        # (b) 統計結果表格
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
