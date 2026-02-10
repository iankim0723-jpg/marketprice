import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 다크모드/가독성 CSS 적용
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 검정, 글자 흰색 */
    .stApp { background-color: #000000; color: #FFFFFF !important; }
    
    /* 제목 금색 */
    h1, h2, h3 { color: #D4AF37 !important; font-weight: bold; }
    
    /* 탭(Tab) 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #1A1A1A; border-radius: 5px; color: #FFFFFF; font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D4AF37 !important; color: #000000 !important;
    }

    /* 입력창 스타일 */
    label, p, span { color: #FFFFFF !important; font-weight: bold; font-size: 1.0rem; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }

    /* 테이블 스타일 (가독성 극대화) */
    .styled-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 1rem; background-color: #1A1A1A; color: #FFFFFF; }
    .styled-table th { background-color: #D4AF37; color: #000000; padding: 12px; border: 1px solid #555; text-align: center; }
    .styled-table td { padding: 10px; border: 1px solid #555; text-align: center; font-weight: bold; }
    .remark-text { color: #FF6B6B; font-size: 0.9em; } /* 비고사항 강조색 */
    
    /* 버튼 스타일 */
    .stButton>button { width: 100%; background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold; border-radius: 8px; border: none; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER")

# --- 2. 공통 매입가 설정 (상단) ---
with st.expander("⚙️ 원자재 매입가 & 가공비 설정 (펼치기)", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1: ext_p = st.number_input("외부 코일 (kg)", value=1100, step=10)
    with c2: int_p = st.number_input("내부 코일 (kg)", value=1100, step=10)
    with c3: proc_f = st.number_input("가공비 (인건비+소모품)", value=2700, step=100)
    with c4: coil_opt = st.selectbox("코일 조합", ["외부(1219)+내부(1040)", "내부(1040)+내부(1040)"])

# 코일 기본가 계산 (50T 기준 베이스가 됨)
if "외부" in coil_opt:
    base_coil_cost = (4.784 * ext_p) + (4.082 * int_p)
else:
    base_coil_cost = (4.082 * int_p) * 2

st.write("")

# --- 3. 탭 분리 (EPS / 그라스울 / 우레탄) ---
tab1, tab2, tab3 = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# --- [TAB 1] EPS 로직 ---
with tab1:
    col_e1, col_e2 = st.columns([1, 3])
    with col_e1:
        st.subheader("EPS 설정")
        eps_base_m = st.number_input("EPS 50T 보드값 (m)", value=3650)
        # HP 단가표 기준 변동폭(Gap) 입력
        gap_gen = st.number_input("일반/난연 구간 인상액 (Gap)", value=800) 
        gap_cert = st.number_input("인증판넬 구간 인상액 (Gap)", value=2500)
        
        # 50T 기준 시작가 (Base Price)
        start_price_gen = int(base_coil_cost + eps_base_m + proc_f)
        start_price_cert = int(base_coil_cost + eps_base_m + proc_f + 5000) # 인증은 심재가 더 비싸다고 가정(+5000)

    with col_e2:
        # 데이터 생성
        t_list = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
        data_eps = []
        
        for idx, t in enumerate(t_list):
            # 비고 사항 (이미지 기반 하드코딩)
            remark = ""
            if t == 75: remark = "유니스톤"
            if t == 100: remark = "유니스톤, 코르텐"
            if t == 150: remark = "리얼징크"
            if t == 260: remark = "0.6T 변경 별도견적"

            # 갭 더하기 로직: (현재단계 - 50T단계) * 갭
            # 단, 이미지는 25T 단위가 아니므로 인덱스로 단순 곱하기보다 두께차이 비례가 정확할 수 있으나
            # 대표님 요청대로 '변동폭 픽스'라면 단순 계단식 증가로 구현
            step_gap_gen = idx * gap_gen
            step_gap_cert = idx * gap_cert

            row = {
                "두께(T)": f"{t}T",
                "일반 (0.5T)": f"{start_price_gen + step_gap_gen:,}",
                "난연 (0.5T)": f"{start_price_gen + step_gap_gen + 1400:,}", # 난연은 일반보다 베이스가 높음(예시)
                "인증 (0.5T)": f"{start_price_cert + step_gap_cert:,}",
                "비고": remark
            }
            data_eps.append(row)
            
        df_eps = pd.DataFrame(data_eps)
        st.write(df_eps.to_html(classes='styled-table', index=False), unsafe_allow_html=True)


# --- [TAB 2] 그라스울 로직 ---
with tab2:
    col_g1, col_g2 = st.columns([1, 3])
    with col_g1:
        st.subheader("GW 설정")
        gw_48_kg = st.number_input("GW 48K kg단가", value=1770)
        gw_64_kg = st.number_input("GW 64K kg단가", value=1600)
        
        # HP 단가표 기준 변동폭
        gap_48 = st.number_input("48K 구간 인상액", value=2400)
        gap_64 = st.number_input("64K 구간 인상액", value=3200)

        # 50T 기준 시작가 (무게: 50T * 밀도 * 1.219 * 1m) -> 여기서 50T 무게는 약 2.9kg
        w_48 = (50/1000)*48*1.219
        w_64 = (50/1000)*64*1.219
        
        start_gw48 = int(base_coil_cost + (w_48 * gw_48_kg) + proc_f)
        start_gw64 = int(base_coil_cost + (w_64 * gw_64_kg) + proc_f)

    with col_g2:
        t_gw_list = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
        data_gw = []
        
        for idx, t in enumerate(t_gw_list):
            remark = ""
            if t >= 125: remark = "내화인증 구간"

            step_gap_48 = idx * gap_48
            step_gap_64 = idx * gap_64
            
            row = {
                "두께(T)": f"{t}T",
                "48K (불연)": f"{start_gw48 + step_gap_48:,}",
                "64K (불연)": f"{start_gw64 + step_gap_64:,}",
                "48K (내화 30분)": f"{start_gw48 + step_gap_48 + 5000:,}" if t >= 125 else "-",
                "64K (내화 60분)": f"{start_gw64 + step_gap_64 + 6000:,}" if t >= 125 else "-",
                "비고": remark
            }
            data_gw.append(row)
        
        df_gw = pd.DataFrame(data_gw)
        st.write(df_gw.to_html(classes='styled-table', index=False), unsafe_allow_html=True)


# --- [TAB 3] 우레탄 로직 ---
with tab3:
    col_u1, col_u2 = st.columns([1, 3])
    with col_u1:
        st.subheader("우레탄 설정")
        ure_base_m = st.number_input("우레탄 50T 원액비", value=18000)
        gap_ure = st.number_input("우레탄 구간 인상액", value=4000)
        
        start_ure = int(base_coil_cost + ure_base_m + proc_f)
        start_ure_cert = int(start_ure + 8000) # 인증은 더 비쌈

    with col_u2:
        t_ure_list = [50, 75, 100, 125, 150]
        data_ure = []
        
        for idx, t in enumerate(t_ure_list):
            remark = ""
            if t == 50: remark = "일면 유색 +500원"
            if t == 75: remark = "유니스톤 +1000원"

            step_gap = idx * gap_ure
            # 인증은 갭이 더 큼 (이미지 기준 5000원)
            step_gap_cert = idx * 5000 
            
            row = {
                "두께(T)": f"{t}T",
                "일반 (0.5T)": f"{start_ure + step_gap:,}",
                "인증 (0.5T)": f"{start_ure_cert + step_gap_cert:,}",
                "비고": remark
            }
            data_ure.append(row)

        df_ure = pd.DataFrame(data_ure)
        st.write(df_ure.to_html(classes='styled-table', index=False), unsafe_allow_html=True)

# 카톡 복사 버튼
st.write("---")
if st.button("📱 현재 탭 단가표 텍스트 복사"):
    st.code("단가표 내용이 복사되었습니다 (실제 기능은 클립보드 API 제한으로 텍스트 드래그 필요)")
