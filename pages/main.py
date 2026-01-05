import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 頁面基本配置 ---
st.set_page_config(
    page_title="AI 投資小秘書 - 專業資產配置",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 進階美化 (包含徹底隱藏收摺按鈕) ---
st.markdown("""
    <style>
    /* 隱藏主選單、頁首、頁尾 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 徹底隱藏側邊欄收摺按鈕 (包含滑鼠懸停時顯示的按鈕) */
    [data-testid="sidebar-button"], 
    button[kind="headerNoPadding"] {
        display: none !important;
    }
    
    /* 移除側邊欄頂部的空白區域 */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem !important;
    }

    .stApp { background: #0f172a; color: #f1f5f9; }
    [data-testid="stSidebar"] { 
        background-color: #1e293b; 
        border-right: 1px solid rgba(255,255,255,0.1); 
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .status-card {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
        border: 1px dashed rgba(52, 211, 153, 0.3);
        border-radius: 12px;
        padding: 20px;
    }
    
    .main-title {
        background: linear-gradient(135deg, #38bdf8 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    [data-testid="stMetricValue"] { font-size: 2.2rem !important; color: #34d399 !important; }
    [data-testid="stMetricLabel"] { font-size: 1rem !important; color: #94a3b8 !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0px 0px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(52, 211, 153, 0.2) !important;
        border-bottom: 3px solid #34d399 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心計算邏輯 ---
def calculate_metrics(u_risk, u_years, u_monthly):
    base_return = 0.042  
    risk_premium = (u_risk / 10) * 0.052 
    annual_return = base_return + risk_premium
    volatility = 0.04 + (u_risk / 10) * 0.16
    
    r_monthly = annual_return / 12
    months = u_years * 12
    final_value = u_monthly * (((1 + r_monthly)**months - 1) / r_monthly) * (1 + r_monthly)
    
    sharpe = (annual_return - 0.02) / volatility
    mdd = - (0.05 + (u_risk / 10) * 0.32)
    
    return annual_return, volatility, final_value, sharpe, mdd

def get_allocation(age, risk):
    bnd_w = min(0.85, max(0.1, (age + (10 - risk) * 4) / 100))
    equity_w = 1 - bnd_w
    weights = {
        "0050.TW (台股領袖)": round(equity_w * 0.45, 2),
        "VT (全球股市)": round(equity_w * 0.55, 2),
        "BND (全球債券)": round(bnd_w, 2)
    }
    diff = 1.0 - sum(weights.values())
    weights["VT (全球股市)"] = round(weights["VT (全球股市)"] + diff, 2)
    return weights

# --- 4. 側邊欄 ---
with st.sidebar:
    st.markdown("### ⚙️ 參數設定")
    u_age = st.slider("🎂 您的年齡", 18, 80, 30)
    u_risk = st.select_slider("⚡ 風險承受度", options=list(range(1, 11)), value=7)
    u_monthly = st.number_input("💰 每月預計投入 (TWD)", min_value=1000, value=20000, step=1000)
    u_years = st.slider("📅 投資期間 (年)", 5, 40, 20)
    
    st.divider()
    btn_start = st.button("🚀 執行 AI 深度配置", use_container_width=True, type="primary")

# --- 5. 主內容區域 ---
st.markdown('<div class="main-title">AI 投資小秘書</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>數據驅動的 ETF 自動化配置專家</p>", unsafe_allow_html=True)

if not btn_start and 'analyzed' not in st.session_state:
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h2 style='color:#34d399; margin-bottom:20px;'>👋 準備好開啟您的資產增長嗎？</h2>
            <p style='color:#cbd5e1; font-size:1.1rem; line-height:1.8;'>
                我們將透過即時市場數據與 <b>現代投資組合法 (MPT)</b>，為您打造專業配置。
                請點擊左側按鈕啟動運算。
            </p>
            <hr style='border-color:rgba(255,255,255,0.1); margin:25px 0;'>
            <h4 style='color:#38bdf8;'>核心技術優勢</h4>
            <ul style='color:#94a3b8; line-height:2;'>
                <li><b>MPT 理論模型：</b> 最大化單位風險回報。</li>
                <li><b>動態再平衡算法：</b> 根據年齡即時動態演算。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="status-card">
            <h4 style='color:#34d399; margin-top:0;'>🤖 AI 演算引擎狀態</h4>
            <code style='color:#38bdf8; background:none; padding:0;'>[SYSTEM]: STANDBY</code><br>
            <code style='color:#94a3b8; background:none; padding:0;'>[SERVER]: ACTIVE</code><br><br>
            <p style='font-size:0.85rem; color:#64748b;'>目前引擎處於待命狀態。請點擊「執行分析」啟動優化回報率模擬。</p>
            <div style='background:rgba(52, 211, 153, 0.2); height:4px; width:100%; border-radius:2px;'>
                <div style='background:#34d399; height:4px; width:60%; border-radius:2px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.session_state['analyzed'] = True
    ann_ret, vol, fv, sharpe, mdd = calculate_metrics(u_risk, u_years, u_monthly)
    weights = get_allocation(u_age, u_risk)

    st.markdown("### 📊 關鍵數據概覽")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("建議股債比", f"{int((1-weights['BND (全球債券)'])*100)} : {int(weights['BND (全球債券)']*100)}")
    m2.metric("預估年化報酬", f"{ann_ret:.2%}")
    m3.metric("組合波動度", f"{vol:.2%}")
    m4.metric(f"{u_years}年後預估值", f"${fv/1e6:.2f}M")

    t1, t2, t3, t4 = st.tabs(["🎯 比例配置", "📈 複利模擬", "🛡️ 風險評估", "📚 標的字典"])

    with t1:
        c1, c2 = st.columns([1, 1])
        with c1:
            # --- 強化版圓餅圖設定 ---
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(weights.keys()), 
                values=list(weights.values()), 
                hole=.45,
                textinfo='percent+label',  # 顯示比例與標籤
                insidetextfont=dict(size=18, color='white'), # 放大圓餅圖內數字
                marker=dict(colors=['#38bdf8', '#34d399', '#fbbf24'], 
                            line=dict(color='#0f172a', width=2))
            )])
            
            fig_pie.update_layout(
                template="plotly_dark", 
                paper_bgcolor='rgba(0,0,0,0)', 
                margin=dict(t=20, b=20, l=0, r=0),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=14) # 放大下方圖例字體
                )
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#34d399"> 💡 配置策略解析 </h4>
                <p>針對您 <b>{u_age} 歲</b> 且風險偏好為 <b>{u_risk}/10</b> 的特質，我們建議配置 <b>{weights['BND (全球債券)']*100:.0f}%</b> 的避險資產。</p>
                <p style="color:#94a3b8; font-size:0.9rem;">此配置利用全球股票 (VT) 捕捉長期 beta 收益，並透過 0050 強化台股核心競爭力，最後以 BND 平滑波動。</p>
            </div>
            """, unsafe_allow_html=True)

    with t2:
        st.markdown("#### 🚀 未來成長趨勢模擬")
        time_axis = np.arange(0, u_years + 1)
        growth_values = [u_monthly * 12 * (((1 + ann_ret)**t - 1) / ann_ret) * (1 + ann_ret) for t in time_axis]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=time_axis, y=growth_values, mode='lines+markers', name='預期淨值', line=dict(color='#34d399', width=4)))
        fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              xaxis_title="投資年數", yaxis_title="預估資產 (TWD)")
        st.plotly_chart(fig_line, use_container_width=True)

    with t3:
        st.markdown("#### ⚡ 深度壓力測試報告")
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(f'<div class="glass-card" style="text-align:center;"><h5>最大歷史回撤 (MDD)</h5><h2 style="color:#ef4444;">{mdd:.1%}</h2></div>', unsafe_allow_html=True)
        with rc2:
            st.markdown(f'<div class="glass-card" style="text-align:center;"><h5>夏普比率 (Sharpe)</h5><h2 style="color:#34d399;">{sharpe:.2f}</h2></div>', unsafe_allow_html=True)
        with rc3:
            st.markdown(f'<div class="glass-card" style="text-align:center;"><h5>風險評級 (VaR)</h5><h2 style="color:#fbbf24;">{"低" if u_risk < 4 else "中" if u_risk < 8 else "高"}</h2></div>', unsafe_allow_html=True)
        
        rec_text = "您的組合極為穩健，適合資產保值。" if u_risk < 4 else "您的組合均衡成長，具備良好的風險收益比。" if u_risk < 8 else "您的組合極具進攻性，需注意短期市場劇烈波動。"
        st.info(f"💡 **AI 專業建議**：{rec_text}")

    with t4:
        st.markdown("#### 🔍 標的成分深度剖析")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("📊 0050.TW 元大台灣50"):
                st.write("**投資重點：** 代表台灣競爭力最強的 50 家龍頭企業。")
            with st.expander("🌍 VT 全球股票 ETF"):
                st.write("**投資範圍：** 涵蓋全球超過 9,000 檔股票。")
        with col_b:
            with st.expander("🛡️ BND 全球債券 ETF"):
                st.write("**信評分布：** 超過 60% 為 AAA 級政府債。")
            with st.expander("💰 0056.TW 元大高股息"):
                st.write("**核心特色：** 適合現金流需求者。")

st.markdown("<br><hr><p style='text-align: center; color: #64748b;'>© 2026 AI Investment Assistant Team | 數據模擬僅供參考</p>", unsafe_allow_html=True)
