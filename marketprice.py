import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정 및 다크모드 고정
st.set_page_config(page_title="WOORI COST MASTER", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    label, p, span { color: #FFFFFF !important; font-weight: bold; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    /* 테이블 스타일 */
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; background-color: #1A1A1A; }
    .styled-table th { background-color: #D4AF37; color: #000000; text-align: center; padding: 12px 15px; }
    .styled-table td { padding: 10px 15px; border-bottom: 1px solid #333; text-align: center; }
    .stButton>button { width: 100%; background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold !important; border-radius: 12px; height: 3em; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI COST MASTER (HP 양식)")

# --- 2. 기본 정보 입력 (Side Bar) ---
with st.sidebar:
    st.header("⚙️ 단가표 생성 설정")
    ext_p = st.number_input("외부 코일 (kg)", value=1100)
    int_p = st.number_input("내부 코일 (kg)", value=1100)
    gw_48_p = st.number_input("GW 48k (kg)", value=1770)
    gw_64_p = st.number_input("GW 64k (kg)", value=1600)
    eps_50t_p = st.number_input("EPS 50T 보드값", value=3650)
    proc_f = st.number_input("가공비(인건비+소모품)", value=2700) # 인건비 2000원 포함
    margin_rate = st.slider("마진율 (%)", 0, 30, 10)

# --- 3. 데이터 생성 로직 ---
def calculate_cost(thick, core, coil_type):
    # 코일비 계산 (외부 4.784, 내부 4.082)
    cw = (4.784 * ext_p + 4.082 * int_p) if coil_type == "내외" else (4.082 * int_p * 2)
    # 심재비 계산
    if core == "EPS": core_v = (thick / 50) * eps_50t_p
    elif core == "GW48": core_v = (thick / 1000) * 48 * 1.219 * gw_48_p
    elif core == "GW64": core_v = (thick / 1000) * 64 * 1.219 * gw_64_p
    else: core_v = (thick / 50) * 18000
    # 합계
    cost = cw + core_v + proc_f
    return int(cost * (1 + margin_rate/100))

# HP 양식 두께 리스트
t_list = [50, 75, 100, 125, 150, 175, 200, 225, 250, 260]

# 데이터프레임 구성
data = {
    "두께(T)": [f"{t}T" for t in t_list],
    "EPS 벽체(내외)": [f"{calculate_cost(t, 'EPS', '내외'):,}" for t in t_list],
    "EPS 지붕(내외)": [f"{calculate_cost(t, 'EPS', '내외') + 500:,}" for t in t_list], # 지붕 할증 예시
    "GW 48K 벽체": [f"{calculate_cost(t, 'GW48', '내외'):,}" for t in t_list],
    "GW 64K 벽체": [f"{calculate_cost(t, 'GW64', '내외'):,}" for t in t_list]
}
df = pd.DataFrame(data)

# --- 4. 화면 출력 ---
st.subheader(f"📊 실시간 단가표 (마진 {margin_rate}% 포함)")

# HP 스타일 테이블 출력
st.write(df.to_html(classes='styled-table', index=False), unsafe_allow_html=True)

# 엑셀 다운로드 기능
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='단가표')
st.download_button(
    label="📥 엑셀 파일로 다운로드",
    data=output.getvalue(),
    file_name="WOORI_Price_List.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
