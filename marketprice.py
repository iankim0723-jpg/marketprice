import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="WOORI COST & PRICE MASTER", layout="centered")

# 다크 모드 & 고대비 CSS (가독성 최적화)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    span, p, label, div { color: #FFFFFF !important; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    div[data-baseweb="select"] > div { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    /* 드롭다운 리스트 가독성 강제 고정 */
    ul[role="listbox"] { background-color: #262626 !important; }
    li[role="option"] { color: #FFFFFF !important; background-color: #262626 !important; }
    li[role="option"]:hover { background-color: #D4AF37 !important; color: #000000 !important; }
    .stButton>button { width: 100%; background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold !important; border-radius: 10px; height: 3.5em; border: none; }
    .metric-container { background-color: #1A1A1A; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.2rem !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI COST & PRICE MASTER")

# --- 1. 코일 및 기본 단가 입력 (상단 고정) ---
with st.expander("⚙️ 기본 매입 단가 설정", expanded=False):
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        ext_coil_p = st.number_input("외부 코일 단가 (kg)", value=1100)
        int_coil_p = st.number_input("내부 코일 단가 (kg)", value=1100)
    with col_c2:
        process_f = st.number_input("가공비 (인건비+소모품)", value=2700)
        gw_48_p = st.number_input("GW 48k 매입가 (kg)", value=1770)
        gw_64_p = st.number_input("GW 64k 매입가 (kg)", value=1600)

st.write("---")

# --- 2. 사양 선택 (홀덤 솔버 스타일) ---
col1, col2 = st.columns(2)
with col1:
    panel_type = st.selectbox("판넬 구분", ["벽체(일반)", "지붕(3골)", "지붕(4골)", "메탈/라인메탈"])
    core_type = st.radio("심재", ["EPS", "GW(48k)", "GW(64k)", "우레탄"])
with col2:
    thickness = st.number_input("두께 (T) 입력", value=150, step=5)
    coil_opt = st.selectbox("코일 조합", ["외부(1219)+내부(1040)", "내부(1040)+내부(1040)"])

# --- 3. 계산 로직 (제조 원가) ---
# 코일비 (중량 상수: 1219폭 4.784 / 1040폭 4.082)
if "외부" in coil_opt:
    cost_coil = (4.784 * ext_coil_p) + (4.082 * int_coil_p)
else:
    cost_coil = (4.082 * int_coil_p) * 2

# 심재비
if core_type == "EPS":
    # 대표님 데이터 기반 50T=3650원 비례
    cost_core = (thickness / 50) * 3650
elif "GW" in core_type:
    density = 48 if "48k" in core_type else 64
    price_kg = gw_48_p if density == 48 else gw_64_p
    cost_core = (thickness / 1000) * density * 1.219 * price_kg
else: # 우레탄 (가정치)
    cost_core = (thickness / 50) * 18000

total_cost = int(cost_coil + cost_core + process_f)

# --- 4. 결과 출력 (원가 vs 시장가 비교) ---
st.write("### 📊 산출 결과")

res1, res2 = st.columns(2)
with res1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("예상 제조 원가 (1m)", f"{total_cost:,} 원")
    st.markdown('</div>', unsafe_allow_html=True)

with res2:
    # 이미지 단가표 기반 샘플 매칭 (나중에 엑셀로 연동 가능)
    # 예: 지붕 3골 GW 48k 220T = 39,300원
    market_price = 39300 if "지붕" in panel_type and "48k" in core_type and thickness == 220 else 0
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("단가표 기준가 (1m)", f"{market_price:,} 원" if market_price > 0 else "데이터 없음")
    st.markdown('</div>', unsafe_allow_html=True)

if market_price > 0:
    profit = market_price - total_cost
    st.success(f"💡 예상 마진: {profit:,}원 (마진율 {round(profit/market_price*100, 1)}%)")

# 카톡 공유
if st.button("📱 결과 복사 (카톡 전송용)"):
    msg = f"[우리 스틸 테크]\n사양: {panel_type} {core_type} {thickness}T\n조합: {coil_opt}\n원가: {total_cost:,}원\n단가표: {market_price:,}원"
    st.code(msg)