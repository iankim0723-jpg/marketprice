import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 다크모드/가독성 CSS
st.set_page_config(page_title="HP STYLE PRICE MASTER", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 검정 */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* 제목 및 텍스트 스타일 */
    h1, h2, h3 { color: #D4AF37 !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A; border-radius: 5px; color: #FFFFFF; font-weight: bold; font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D4AF37 !important; color: #000000 !important;
    }
    
    /* 입력창 및 라벨 */
    label { color: #D4AF37 !important; font-weight: bold; font-size: 1rem; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; font-size: 1.1rem !important; }

    /* 테이블 스타일 (HP 양식 재현) */
    .hp-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.95rem; color: #FFFFFF; }
    .hp-table th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 10px; text-align: center; }
    .hp-table td { background-color: #1A1A1A; border: 1px solid #444; padding: 8px; text-align: center; }
    .hp-table tr:hover td { background-color: #333; }
    .remark { color: #FF6B6B; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER (HP 양식)")

# --- 탭 분리 ---
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# ==========================================
# [TAB 1] EPS 단가표 로직
# ==========================================
with tab_eps:
    st.subheader("EPS 단가 설정 (50T 기준값 입력)")
    c1, c2, c3 = st.columns(3)
    with c1: base_eps_gen = st.number_input("EPS 일반 50T", value=9400, step=100)
    with c2: base_eps_nan = st.number_input("EPS 난연 50T", value=10800, step=100)
    with c3: base_eps_cert = st.number_input("EPS 인증 50T", value=22800, step=100) # 이미지 기준 75T 시작이나 로직상 50T값 필요

    # HP 단가표 갭(Gap) 데이터 (50T 대비 차액)
    # 두께: [일반Gap, 난연Gap, 인증Gap, 비고]
    eps_gaps = {
        50:  [0, 0, -7400, ""], # 인증은 50T가 없거나 75T부터 시작하므로 역산용 마이너스 처리
        75:  [800, 1400, 0, "유니스톤"], # 인증 75T를 0(기준)으로 잡거나, 50T대비 갭으로 처리. 여기선 50T입력값 기준
        100: [1600, 2800, 2500, "유니스톤, 코르텐"],
        125: [2400, 4200, 5000, "리얼징크 +2000"],
        150: [3200, 5600, 7500, ""],
        155: [3400, 5900, 8000, ""],
        175: [4000, 7000, 9800, ""],
        200: [4800, 8400, 12500, ""],
        225: [5600, 9800, 15000, ""],
        250: [6400, 11200, 17500, "0.6T 변경 별도"],
        260: [6800, 11800, 18500, ""]
    }

    # 테이블 생성
    html = """<table class="hp-table">
    <thead><tr>
        <th>두께(T)</th><th>일반 (0.5T)</th><th>난연 (0.5T)</th><th>인증 (0.5T)</th><th>비고</th>
    </tr></thead><tbody>"""

    for t, gaps in eps_gaps.items():
        # 50T 기준가 + 갭
        p_gen = base_eps_gen + gaps[0]
        p_nan = base_eps_nan + gaps[1]
        
        # 인증판넬: 50T 입력값이 75T 가격이라고 가정하거나 별도 처리 필요. 
        # 여기서는 "인증 50T" 입력값을 75T 기준가로 보고 계산 (이미지상 75T가 시작점)
        # 만약 사용자가 22800(75T)을 입력했다면? -> 로직 조정
        # 심플하게: 인증 50T 입력창을 "인증 75T 시작가"로 간주
        if t == 50:
             p_cert = "-" 
        elif t == 75:
             p_cert = f"{base_eps_cert:,}" # 입력값을 그대로 75T에 표시
        else:
             # 75T 대비 갭 차이 (현재 갭 - 75T 갭)
             diff = gaps[2] # 위 딕셔너리에 75T를 0으로 잡았을 경우
             p_cert = f"{base_eps_cert + diff:,}"

        html += f"""<tr>
            <td>{t}T</td>
            <td>{p_gen:,}</td>
            <td>{p_nan:,}</td>
            <td>{p_cert}</td>
            <td class="remark">{gaps[3]}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ==========================================
# [TAB 2] 그라스울 단가표 로직
# ==========================================
with tab_gw:
    st.subheader("그라스울 단가 설정 (50T 기준값 입력)")
    c1, c2 = st.columns(2)
    with c1: base_gw48 = st.number_input("GW 48K (불연) 50T", value=20400, step=100)
    with c2: base_gw64 = st.number_input("GW 64K (불연) 50T", value=22400, step=100)

    # GW 갭 데이터 [48K Gap, 64K Gap, 비고]
    # 이미지 분석: 48K는 2400원씩, 64K는 3200원씩 증가
    gw_data = [
        (50, 0, 0, ""),
        (75, 2400, 3200, ""),
        (100, 4800, 6400, ""),
        (125, 7200, 9600, "내화 30분/60분 가능"),
        (138, 8500, 11300, ""),
        (150, 9600, 12800, ""),
        (184, 12800, 17100, ""),
        (200, 14400, 19200, ""),
        (220, 16400, 21800, ""),
        (250, 19200, 25600, "하지 1200이하")
    ]

    html = """<table class="hp-table">
    <thead><tr>
        <th>두께</th><th>48K (불연)</th><th>64K (불연)</th><th>내화인증(참고)</th><th>비고</th>
    </tr></thead><tbody>"""

    for row in gw_data:
        t, g48, g64, rem = row
        p48 = base_gw48 + g48
        p64 = base_gw64 + g64
        
        # 내화 가격 (이미지 기준 125T부터 존재, 불연 대비 +알파)
        fire_cert = f"48K:{p48+2600:,}" if t >= 125 else "-"

        html += f"""<tr>
            <td>{t}T</td>
            <td>{p48:,}</td>
            <td>{p64:,}</td>
            <td>{fire_cert}</td>
            <td class="remark">{rem}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ==========================================
# [TAB 3] 우레탄 단가표 로직
# ==========================================
with tab_ure:
    st.subheader("우레탄 단가 설정 (50T 기준값 입력)")
    c1, c2 = st.columns(2)
    with c1: base_ure_gen = st.number_input("우레탄 일반 50T", value=24500, step=100)
    with c2: base_ure_cert = st.number_input("우레탄 인증 50T", value=32000, step=100)

    # 우레탄 갭 [일반Gap, 인증Gap]
    # 일반: +4000씩 / 인증: +5000씩
    ure_data = [
        (50, 0, 0, "일면 유색 +500"),
        (75, 4000, 5000, "유니스톤"),
        (100, 8000, 10000, "유니스톤"),
        (125, 12000, 15000, ""),
        (150, 16000, 20000, "")
    ]

    html = """<table class="hp-table">
    <thead><tr>
        <th>두께(T)</th><th>일반 (0.5T)</th><th>인증 (0.5T)</th><th>비고</th>
    </tr></thead><tbody>"""

    for row in ure_data:
        t, g_gen, g_cert, rem = row
        p_gen = base_ure_gen + g_gen
        p_cert = base_ure_cert + g_cert
        
        html += f"""<tr>
            <td>{t}T</td>
            <td>{p_gen:,}</td>
            <td>{p_cert:,}</td>
            <td class="remark">{rem}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

st.write("---")
st.info("💡 팁: 상단의 50T(또는 시작가) 단가만 수정하면, HP 단가표의 구간 변동폭(Gap)이 적용되어 전체 표가 자동 계산됩니다.")
