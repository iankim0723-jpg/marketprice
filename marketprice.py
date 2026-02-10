import streamlit as st

# 1. 페이지 기본 설정 및 다크모드 가독성 강제 고정
st.set_page_config(page_title="WOORI COST SOLVER", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; font-weight: bold; }
    label, p, span { color: #FFFFFF !important; font-weight: bold; }
    /* 입력창 글자색 검정 방지 */
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    /* 선택박스 배경 및 글자색 강제 고정 */
    div[data-baseweb="select"] > div { background-color: #262626 !important; color: #FFFFFF !important; }
    div[role="listbox"] { background-color: #262626 !important; color: #FFFFFF !important; }
    /* 버튼: 금색 배경 / 검정 글자 */
    .stButton>button { 
        width: 100%; background-color: #D4AF37 !important; color: #000000 !important; 
        font-weight: bold !important; border-radius: 12px; height: 3.5em; border: none;
    }
    /* 결과값 숫자 강조 */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 3rem !important; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI COST SOLVER")

# --- 입력 섹션 ---
st.subheader("1. 원자재 매입가 설정")
col1, col2 = st.columns(2)
with col1:
    ext_coil_p = st.number_input("외부 코일 (kg당/원)", value=1100)
    int_coil_p = st.number_input("내부 코일 (kg당/원)", value=1100)
with col2:
    gw_48k_p = st.number_input("그라스울 48k (kg당/원)", value=1770)
    gw_64k_p = st.number_input("그라스울 64k (kg당/원)", value=1600)

st.write("---")

st.subheader("2. 제품 사양 선택")
# 심재 선택
material = st.selectbox("심재 종류", ["EPS", "그라스울(48k)", "그라스울(64k)", "우레탄"])

col3, col4 = st.columns(2)
with col3:
    # 대표님 데이터: EPS 50T 보드값 3,650원 기준
    default_m_p = 3650 if material == "EPS" else 18000 # 우레탄은 임시값
    # 그라스울은 kg당 단가를 사용하므로 보드값 입력창 비활성화 처리 가능
    m_label = "보드값/원액비 (m당)" if material != "그라스울(48k)" and material != "그라스울(64k)" else "심재 단가는 상단 매입가 적용됨"
    m_price = st.number_input(m_label, value=default_m_p if "그라스울" not in material else 0)
with col4:
    thickness = st.number_input("제품 두께 (T)", value=150)

coil_opt = st.radio("코일 조합", ["외부(1219) + 내부(1040)", "내부(1040) + 내부(1040)"], horizontal=True)

# 고정비: 인건비 2,000원 + 소모품 700원 = 2,700원
process_fee = 2700

# --- 계산 엔진 ---
# 1. 코일비 (중량: 1219폭 4.784kg / 1040폭 4.082kg)
if "외부" in coil_opt:
    cost_coil = (4.784 * ext_coil_p) + (4.082 * int_coil_p)
else:
    cost_coil = (4.082 * int_coil_p) * 2

# 2. 심재비
if material == "EPS":
    cost_core = (thickness / 50) * m_price
elif "그라스울" in material:
    density = 48 if "48k" in material else 64
    kg_price = gw_48k_p if density == 48 else gw_64k_p
    # 그라스울 중량 공식: 두께(m) * 밀도 * 폭(1.219)
    cost_core = (thickness / 1000) * density * 1.219 * kg_price
else: # 우레탄
    cost_core = (thickness / 50) * m_price

# 최종 합계
total_cost = int(cost_coil + cost_core + process_fee)

# --- 결과 섹션 ---
st.write("---")
st.write("### 💰 산출된 제조 원가 (1m)")
st.metric(label="", value=f"{total_cost:,} 원")

# 공유용 텍스트
if st.button("카톡 공유용 결과 복사"):
    share_msg = f"[우리 스틸 테크]\n{material} {thickness}T ({coil_opt})\n원가: {total_cost:,}원"
    st.code(share_msg)
    st.success("위 코드를 복사해서 카톡에 붙여넣으세요!")
