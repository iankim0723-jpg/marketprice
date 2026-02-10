import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

# 가독성 극대화 CSS (글씨가 안 보이는 문제 해결)
st.markdown("""
    <style>
    /* 배경은 검정, 글자는 완전 흰색 */
    .stApp { background-color: #000000; color: #FFFFFF !important; }
    
    /* 제목 및 강조색 (금색) */
    h1, h2, h3 { color: #D4AF37 !important; text-align: left; font-weight: bold; }
    
    /* 입력창 및 라벨 가독성 */
    label, p, span { color: #FFFFFF !important; font-size: 1.1rem !important; font-weight: bold; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 2px solid #D4AF37 !important; font-size: 1.2rem !important; }
    
    /* 테이블 디자인 (글씨 구분 확실하게) */
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 1.1rem; background-color: #1A1A1A; color: #FFFFFF; }
    .styled-table th { background-color: #D4AF37; color: #000000; padding: 15px; border: 1px solid #444; }
    .styled-table td { padding: 12px; border: 1px solid #444; text-align: center; font-weight: bold; }
    .styled-table tr:nth-child(even) { background-color: #262626; }
    
    /* 버튼 */
    .stButton>button { width: 100%; background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold !important; height: 3.5em; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI COST MASTER")

# --- 설정값 입력 ---
col1, col2 = st.columns(2)
with col1:
    ext_p = st.number_input("외부 코일 매입가 (kg)", value=1100)
    int_p = st.number_input("내부 코일 매입가 (kg)", value=1100)
with col2:
    eps_50t_base = st.number_input("EPS 50T 보드 기준가 (m)", value=3650)
    proc_f = st.number_input("가공비 (인건비+소모품)", value=2700) # 인건비 2,000원 포함

st.write("---")

# --- 변동폭(Gap) 기반 단가 산출 로직 ---
# 코일비 계산 (외부 1219폭: 4.784kg / 내부 1040폭: 4.082kg)
cost_coil_base = (4.784 * ext_p) + (4.082 * int_p) 

# 두께 리스트 및 변동폭 적용
# HP 양식의 핵심은 50T 대비 두께가 늘어날 때의 자재비 증가분(Gap)입니다.
t_list = [50, 75, 100, 125, 150, 175, 200, 225, 250, 260]

def get_total_price(t):
    # 50T 기준에서 두께 증가분에 따른 보드값 갭 계산
    core_gap_price = (t / 50) * eps_50t_base
    return int(cost_coil_base + core_gap_price + proc_f)

# 데이터 생성
results = []
for t in t_list:
    price = get_total_price(t)
    results.append({
        "두께(T)": f"{t}T",
        "제조 원가(m당)": f"{price:,} 원",
        "비고": "50T 대비 증가분 반영"
    })

df = pd.DataFrame(results)

# --- 결과 출력 (테이블) ---
st.subheader("📊 실시간 원가 산출표")
st.write(df.to_html(classes='styled-table', index=False), unsafe_allow_html=True)

# 카톡용 복사
if st.button("카톡 공유용 텍스트 생성"):
    msg = "[우리 스틸 테크 원가]\n"
    for t in t_list:
        msg += f"{t}T: {get_total_price(t):,}원\n"
    st.code(msg)
