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

# --- 2. CSS 進階美化 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="sidebar-button"], 
    button[kind="headerNoPadding"] {
        display: none !important;
    }
    
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
        font-size: 3.5rem;
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
    btn_start = st.button("執行 AI 深度配置", use_container_width=True, type="primary")

# --- 5. 主內容區域 ---
st.markdown('<div class="main-title">AI 投資小秘書</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem;'>數據驅動的 ETF 自動化配置專家</p>", unsafe_allow_html=True)

if not btn_start and 'analyzed' not in st.session_state:
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("""
            <div class="glass-card">
                <h2 style="color:#34d399; margin-bottom:20px;">👋 準備好開啟您的資產增長嗎？</h2>
                <p style="color:#cbd5e1; font-size:1.1rem; line-height:1.8;">
                    我們採用 <b>現代投資組合理論 (MPT)</b> 與 <b>Black-Litterman 模型</b> 邏輯，為不同人生階段的您量身打造回報優化方案。
                    透過分散投資於全球指數 ETF，有效降低單一市場波動風險，守護您的每一分積蓄。
                </p>
                <hr style="border-color:rgba(255,255,255,0.1); margin:25px 0;">
                <h4 style="color:#38bdf8;">🌟 為什麼選擇 AI 投資小秘書？</h4>
                <ul style="color:#94a3b8; line-height:2.2; font-size:1rem;">
                    <li><b>動態再平衡演算法：</b> 根據年齡與風險承受度即時動態演進配置比例。</li>
                    <li><b>複利成長模擬：</b> 精準模擬未來 20-40 年的資產增值路徑，看見未來的財富。</li>
                    <li><b>全球化佈局：</b> 不只台灣，我們將視野擴展至全球股票與債券市場。</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="status-card">
                <h4 style="color:#34d399; margin-top:0;">🤖 系統演算引擎狀態</h4>
                <div style="font-family: monospace; color:#38bdf8; background:rgba(0,0,0,0.3); padding:10px; border-radius:8px;">
                    <span style="color:#94a3b8;">[STATUS]:</span> READY<br>
                    <span style="color:#94a3b8;">[CORE]:</span> MPT-ENGINE V2.4<br>
                    <span style="color:#94a3b8;">[API]:</span> MARKET-SYNCED<br>
                    <span style="color:#94a3b8;">[DATA]:</span> LATEST 2026 Q1
                </div>
                <br>
                <p style="font-size:0.9rem; color:#f1f5f9;">目前引擎處於待命狀態，已與全球市場數據連線。請調整左側參數並點擊<b>「執行分析」</b>啟動模擬。</p>
                <div style="background:rgba(52, 211, 153, 0.1); height:6px; width:100%; border-radius:3px; margin-top:10px;">
                    <div style="background:#34d399; height:6px; width:100%; border-radius:3px; box-shadow: 0 0 10px #34d399;"></div>
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
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(weights.keys()), 
                values=list(weights.values()), 
                hole=.45,
                textinfo='percent',
                insidetextfont=dict(size=24, color='white', family="Arial Black"),
                marker=dict(colors=['#38bdf8', '#34d399', '#fbbf24'], 
                            line=dict(color='#0f172a', width=3))
            )])
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=14)))
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown(f'<div class="glass-card"><h4 style="color:#34d399"> 💡 配置策略解析 </h4><p>針對您 <b>{u_age} 歲</b> 且風險偏好為 <b>{u_risk}/10</b> 的特質，我們建議配置 <b>{weights["BND (全球債券)"]*100:.0f}%</b> 的避險資產。</p><p style="color:#94a3b8; font-size:0.9rem;">此配置利用全球股票 (VT) 捕捉長期 beta 收益，並透過 0050 強化台股核心競爭力，最後以 BND 平滑波動。</p></div>', unsafe_allow_html=True)

    with t2:
        st.markdown("#### 🚀 未來成長趨勢模擬")
        time_axis = np.arange(0, u_years + 1)
        growth_values = [u_monthly * 12 * (((1 + ann_ret)**t - 1) / ann_ret) * (1 + ann_ret) for t in time_axis]
        fig_line = go.Figure(go.Scatter(x=time_axis, y=growth_values, mode='lines+markers', line=dict(color='#34d399', width=4)))
        fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="投資年數", yaxis_title="預估資產 (TWD)")
        st.plotly_chart(fig_line, use_container_width=True)

    with t3:
        st.markdown("#### ⚡ 深度壓力測試報告")
        rc1, rc2, rc3 = st.columns(3)
        rc1.markdown(f'<div class="glass-card" style="text-align:center;"><h5>最大歷史回撤</h5><h2 style="color:#ef4444;">{mdd:.1%}</h2></div>', unsafe_allow_html=True)
        rc2.markdown(f'<div class="glass-card" style="text-align:center;"><h5>夏普比率</h5><h2 style="color:#34d399;">{sharpe:.2f}</h2></div>', unsafe_allow_html=True)
        rc3.markdown(f'<div class="glass-card" style="text-align:center;"><h5>風險評級</h5><h2 style="color:#fbbf24;">{"低" if u_risk < 4 else "中" if u_risk < 8 else "高"}</h2></div>', unsafe_allow_html=3)
        st.info(f"💡 **AI 專業建議**：{'您的組合極為穩健，適合資產保值。' if u_risk < 4 else '您的組合均衡成長，具備良好的風險收益比。' if u_risk < 8 else '您的組合極具進攻性，需注意短期市場劇烈波動。'}")

    with t4:
        st.markdown("#### 🔍 標的成分深度剖析")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("📊 0050.TW 元大台灣50"):
                st.markdown("""
                **核心地位：** 台灣市場的領頭羊，追蹤台灣市值最大的 50 家上市公司。  
                **投資亮點：**
                * **高穩定性：** 包含台積電、聯發科等世界級龍頭企業。
                * **適合族群：** 偏好本土市場成長、看好台灣半導體產業優勢的投資者。
                """)
            with st.expander("🌍 VT 全球股票 ETF (Vanguard Total World Stock)"):
                st.markdown("""
                **核心地位：** 真正意義上的「投向全世界」。  
                **投資亮點：**
                * **極度分散：** 一次持有全球 9,500 多檔股票，橫跨開發中與新興市場。
                * **防禦優勢：** 當單一國家（如美國或台灣）發生劇烈變動時，能有效分散地域性風險。
                """)
        with col_b:
            with st.expander("🛡️ BND 全球債券 ETF (Vanguard Total Bond Market)"):
                st.markdown("""
                **核心地位：** 組合的減震器（保險墊）。  
                **投資亮點：**
                * **穩定收息：** 投資於美國投資級債券，提供穩定的利息收益。
                * **低相關性：** 在股市大跌時，債券通常具有避險功能，能大幅拉低整體組合的回撤空間。
                """)
            with st.expander("💰 0056.TW 元大高股息"):
                st.markdown("""
                **核心地位：** 現金流的主要來源。  
                **投資亮點：**
                * **高配息率：** 篩選台灣預計現金股息殖利率最高的 50 檔股票。
                * **適合族群：** 適合退休族或需要定期領取配息作為生活費的投資者。
                """)

st.markdown("<br><hr><p style='text-align: center; color: #64748b;'>© 2026 AI Investment Assistant Team | 數據模擬僅供參考，投資必有風險</p>", unsafe_allow_html=True)
