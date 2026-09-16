import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dice Matching Experiment | 骰子相配實驗",
    page_icon="🎲",
    layout="wide",
)

# Minimal custom styling for dice container
st.markdown("""
<style>
.dice-container {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 12px 0;
}
.dice-card {
    width: 78px;
    padding: 10px 4px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    background: #ffffff;
    text-align: center;
}
.dice-card.matched {
    background: #2e7d32;
    color: #ffffff !important;
    border: none;
}
.dice-card.matched .dice-sub { color: #ffffff !important; }
.dice-val { font-size: 32px; line-height: 1; }
.dice-sub { font-size: 11px; margin-top: 4px; color: #666; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DICE_MAP = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}
P_THEORETICAL = 1 - (5 / 6) ** 6

@st.cache_data
def simulate_dice_rolls(n_trials: int, seed: int):
    np.random.seed(seed)
    rolls = np.random.randint(1, 7, size=(n_trials, 6))
    matches = (rolls == np.arange(1, 7))
    successes = np.any(matches, axis=1)
    cum_successes = np.cumsum(successes)
    cum_p = cum_successes / np.arange(1, n_trials + 1)
    return rolls, cum_successes, cum_p

def render_dice_row(roll):
    cards = []
    for i, val in enumerate(roll, 1):
        is_match = (val == i)
        cls = "dice-card matched" if is_match else "dice-card"
        sub = "MATCH" if is_match else f"Roll {i}"
        cards.append(f'<div class="{cls}"><div class="dice-val">{DICE_MAP[val]}</div><div class="dice-sub">{sub}</div></div>')
    return f'<div class="dice-container">{"".join(cards)}</div>'

def build_convergence_chart(df_sub, total_n):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sub['n'], y=df_sub['theory_p'],
        mode='lines', name='Theory P(A)',
        line=dict(color='#d32f2f', width=1.5, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df_sub['n'], y=df_sub['est_p'],
        mode='lines', name='Estimated P(A)',
        line=dict(color='#1976d2', width=2)
    ))
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Simulations (n)",
        yaxis_title="Probability P(A)",
        yaxis=dict(range=[0.35, 0.95]),
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right"),
        template="plotly_white"
    )
    return fig

# Session State Initialization
if "anim_status" not in st.session_state:
    st.session_state.anim_status = "idle"
if "curr_idx" not in st.session_state:
    st.session_state.curr_idx = 0
if "total_n" not in st.session_state:
    st.session_state.total_n = 1000

# Top Info Box
with st.container(border=True):
    st.markdown("### 🎲 6-Sided Dice Matching Experiment | 骰子相配實驗")
    st.markdown("""
    **Rules / 規則:** Roll a fair die 6 times. A **"Match"** occurs if roll $k$ equals $k$ ($k=1..6$). Success (Event $A$) means at least 1 match occurs.  
    *丟擲骰子 6 次，若第 $k$ 次點數等於 $k$ 即為「相配」。6 次中至少 1 次相配即為成功 (事件 $A$)。*  
    **Theoretical P(A):** $1 - (5/6)^6 \\approx 0.6651$
    """)

# Sidebar Controls
with st.sidebar:
    st.header("Control Panel")
    
    total_n = st.number_input("Total Simulations (N)", 100, 10000, st.session_state.total_n, step=100)
    if total_n != st.session_state.total_n:
        st.session_state.total_n = total_n
        st.session_state.anim_status = "idle"

    fps = st.slider("Animation Speed (FPS)", 2, 30, 10)
    seed = st.number_input("Random Seed", 0, 9999, 42)
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Start", type="primary", use_container_width=True):
        st.session_state.anim_status = "running"
        st.session_state.curr_idx = 0
        st.rerun()
        
    pause_btn_text = "Resume" if st.session_state.anim_status == "paused" else "Pause"
    if c2.button(pause_btn_text, use_container_width=True):
        st.session_state.anim_status = "running" if st.session_state.anim_status == "paused" else "paused"
        st.rerun()
        
    if c3.button("Finish", use_container_width=True):
        st.session_state.anim_status = "finished"
        st.rerun()

# Run Simulation Data
rolls, cum_successes, cum_p = simulate_dice_rolls(total_n, seed)
df_chart = pd.DataFrame({'n': np.arange(1, total_n + 1), 'est_p': cum_p, 'theory_p': P_THEORETICAL})

frame_indices = np.unique(np.linspace(1, total_n, num=min(total_n, 60), dtype=int))

# Main Dashboard View
m1, m2, m3, m4 = st.columns(4)
dice_placeholder = st.empty()
chart_placeholder = st.empty()

def update_ui(n_frame):
    m1.metric("Simulations (n)", f"{n_frame}")
    m2.metric("Successes", f"{cum_successes[n_frame-1]}")
    m3.metric("Estimated P(A)", f"{cum_p[n_frame-1]:.4f}")
    m4.metric("Theory P(A)", f"{P_THEORETICAL:.4f}")
    
    dice_placeholder.markdown(render_dice_row(rolls[n_frame-1]), unsafe_allow_html=True)
    chart_placeholder.plotly_chart(
        build_convergence_chart(df_chart.iloc[:n_frame], total_n), 
        use_container_width=True
    )

# Execution Flow
if st.session_state.anim_status == "idle":
    update_ui(1)
    st.info("Click **Start** to begin the animation or **Finish** to see final results.")

elif st.session_state.anim_status == "finished":
    update_ui(total_n)
    err = abs(cum_p[-1] - P_THEORETICAL)
    st.success(f"Simulation completed. Estimated P(A) = {cum_p[-1]:.4f} (Error: {err:.4f})")

elif st.session_state.anim_status == "paused":
    curr_n = frame_indices[st.session_state.curr_idx]
    update_ui(curr_n)
    st.warning(f"Paused at trial #{curr_n}.")

elif st.session_state.anim_status == "running":
    pbar = st.progress(0)
    for idx in range(st.session_state.curr_idx, len(frame_indices)):
        st.session_state.curr_idx = idx
        curr_n = frame_indices[idx]
        pbar.progress(int((idx + 1) / len(frame_indices) * 100))
        update_ui(curr_n)
        time.sleep(1 / fps)
    pbar.empty()
    st.session_state.anim_status = "finished"
    st.rerun()

# Summary Table
if st.session_state.anim_status in ["paused", "finished"]:
    st.markdown("#### Summary Benchmarks / 統計結果")
    checkpoints = [n for n in [50, 100, 250, 500, 1000, 5000, 10000] if n <= total_n]
    summary_df = pd.DataFrame({
        'Trial (n)': checkpoints,
        'Successes': [cum_successes[n-1] for n in checkpoints],
        'Estimated P(A)': [f"{cum_p[n-1]:.4f}" for n in checkpoints],
        'Theory P(A)': f"{P_THEORETICAL:.4f}"
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
