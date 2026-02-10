import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

# 2. 스타일 설정 (깨짐 방지용 CSS)
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    
    /* 텍스트 색상 */
    h1, h2, h3, label { color: #D4AF37 !important; font-weight: bold; }
    p, div, span { color: #FFFFFF; }
    
    /* 입력창 */
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; border-radius: 5px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37 !important; color: black !important; font-weight: bold; }

    /* ★ 표 디자인 (가장 중요) ★ */
    .woori-table {
        width: 100%;
        border-collapse: collapse;
        color: #FFFFFF;
        font-size: 0.95rem;
        text-align: center;
    }
    .woori-table th {
        background-color: #D4AF37;
        color: #000000;
        border: 1px solid #555;
        padding: 12px;
        font-weight: bold;
    }
    .woori-table td {
        background-color: #1A1A1A;
        border: 1px solid #444;
        padding: 10px;
    }
    .woori-table tr:hover td {
        background-color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER")

# ==========================================
# [사이드바] 구간 변동폭(Gap) 설정
# ==========================================
with st.sidebar:
    st.header("⚙️ 구간(Gap) 설정")
    st.info("50T 대비 두께별 인상액 설정")
    
    st.subheader("1. EPS 구간폭")
    gap_eps_gen = st.number_input("일반 구간폭", value=800, step=100)
    gap_eps_nan = st.number_input("난연 구간폭", value=1400, step=100)
    gap_eps_cert = st.number_input("인증 구간폭", value=2500, step=100)
    
    st.markdown("---")
    
    st.subheader("2. 그라스울 구간폭")
    gap_gw_48 = st.number_input("48K 구간폭", value=2400, step=100)
    gap_gw_64 = st.number_input("64K 구간폭", value=3200, step=100)
    
    st.markdown("---")
    
    st.subheader("3. 우레탄 구간폭")
    gap_ure_gen = st.number_input("일반 구간폭", value=4000, step=100)
    gap_ure_cert = st.number_input("인증 구간폭", value=5000, step=100)


# ==========================================
# [메인] 탭 구성 및 표 생성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# --- 1. EPS 탭 ---
with tab_eps:
    # 50T 기준가 입력
    c1, c2, c3, c4 = st.columns(4)
    with c1: base_eps_gen_35 = st.number_input("EPS 일반 (0.35T) 50T", value=9400)
    with c2: base_eps_gen_05 = st.number_input("EPS 일반 (0.5T) 50T", value=14000)
    with c3: base_eps_nan_05 = st.number_input("EPS 난연 (0.5T) 50T", value=15400)
    with c4: base_eps_cert = st.number_input("EPS 인증 75T 시작가", value=22800)

    # 데이터 행 만들기
    rows_html = ""
    thicknesses = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
    
    for i, t in enumerate(thicknesses):
        # 가격 계산
        p_gen_35 = base_eps_gen_35 + (i * gap_eps_gen)
        p_gen_05 = base_eps_gen_05 + (i * gap_eps_gen)
        p_nan_05 = base_eps_nan_05 + (i * gap_eps_nan)
        p_nan_35 = p_nan_05 - 1400
        
        # 인증 가격 (75T부터 시작)
        if t < 75:
            p_cert = "-"
        else:
            p_cert = f"{base_eps_cert + ((i-1) * gap_eps_cert):,}"
            
        # 비고
        rem = ""
        if t==75: rem="유니스톤"
        elif t==100: rem="유니스톤, 코르텐"
        elif t==260: rem="0.6T 변경 별도"

        rows_html += f"""
        <tr>
            <td>벽체</td>
            <td>{t}T</td>
            <td>{p_gen_35:,}</td>
            <td>{p_gen_05:,}</td>
            <td>{p_nan_35:,}</td>
            <td>{p_nan_05:,}</td>
            <td>{p_cert}</td>
            <td style="color:#FF6B6B;">{rem}</td>
        </tr>"""

    # 표 전체 조립 (HTML)
    full_html = f"""
    <table class="woori-table">
        <thead>
            <tr>
                <th rowspan="2">구분</th> <th rowspan="2">두께</th>
                <th colspan="2">일반 (EPS)</th> <th colspan="2">난연 (EPS)</th> <th>인증</th> <th rowspan="2">비고</th>
            </tr>
            <tr style="background-color:#B89630; color:black;">
                <th>양면 0.35T</th> <th>양면 0.5T</th> <th>양면 0.35T</th> <th>양면 0.5T</th> <th>양면 0.5T</th>
            </tr>
            <tr style="background-color:#333; color:#D4AF37;">
                <td>구간(Gap)</td> <td>-</td>
                <td>{gap_eps_gen}</td> <td>{gap_eps_gen}</td> <td>{gap_eps_nan}</td> <td>{gap_eps_nan}</td> <td>{gap_eps_cert}</td> <td>-</td>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(full_html, unsafe_allow_html=True)


# --- 2. 그라스울 탭 ---
with tab_gw:
    c1, c2, c3 = st.columns(3)
    with c1: base_gw48 = st.number_input("GW 48K 50T", value=20400)
    with c2: base_gw64 = st.number_input("GW 64K 50T", value=22400)
    with c3: st.warning("내화구조는 125T부터 자동 계산")

    rows_html = ""
    t_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
    
    for i, t in enumerate(t_gw):
        p48 = base_gw48 + (i * gap_gw_48)
        p64 = base_gw64 + (i * gap_gw_64)
        
        if t >= 125:
            f30 = f"{p48 + 5000:,}"
            f60_48 = f"{p48 + 6000:,}"
            f60_64 = f"{p64 + 6000:,}"
        else:
            f30 = f60_48 = f60_64 = "-"

        rows_html += f"""
        <tr>
            <td>벽체/지붕</td>
            <td>{t}T</td>
            <td>{p48:,}</td>
            <td>{p64:,}</td>
            <td>{f30}</td>
            <td>{f60_48}</td>
            <td>{f60_64}</td>
        </tr>"""

    full_html = f"""
    <table class="woori-table">
        <thead>
            <tr>
                <th rowspan="2">구분</th> <th rowspan="2">두께</th>
                <th colspan="2">그라스울 (불연)</th> <th colspan="3">그라스울 (내화)</th>
            </tr>
            <tr style="background-color:#B89630; color:black;">
                <th>48K (0.5T)</th> <th>64K (0.5T)</th> <th>48K (30분)</th> <th>48K (60분)</th> <th>64K (60분)</th>
            </tr>
            <tr style="background-color:#333; color:#D4AF37;">
                <td>구간(Gap)</td> <td>-</td>
                <td>{gap_gw_48}</td> <td>{gap_gw_64}</td> <td>{gap_gw_48}</td> <td>{gap_gw_48}</td> <td>{gap_gw_64}</td>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(full_html, unsafe_allow_html=True)


# --- 3. 우레탄 탭 ---
with tab_ure:
    c1, c2 = st.columns(2)
    with c1: base_ure_gen = st.number_input("우레탄 일반 50T", value=24500)
    with c2: base_ure_cert = st.number_input("우레탄 인증 50T", value=32000)

    rows_html = ""
    t_ure = [50, 75, 100, 125, 150]
    
    for i, t in enumerate(t_ure):
        p_gen = base_ure_gen + (i * gap_ure_gen)
        p_cert = base_ure_cert + (i * gap_ure_cert)
        
        rem = ""
        if t==50: rem="일면 유색 +500"
        if t==75: rem="유니스톤"

        rows_html += f"""
        <tr>
            <td>벽체</td> <td>{t}T</td>
            <td>{p_gen:,}</td> <td>{p_cert:,}</td>
            <td style="color:#FF6B6B;">{rem}</td>
        </tr>"""

    full_html = f"""
    <table class="woori-table">
        <thead>
            <tr>
                <th rowspan="2">구분</th> <th rowspan="2">두께</th>
                <th colspan="2">우레탄</th> <th rowspan="2">비고</th>
            </tr>
            <tr style="background-color:#B89630; color:black;">
                <th>일반 (0.5T)</th> <th>인증 (0.5T)</th>
            </tr>
            <tr style="background-color:#333; color:#D4AF37;">
                <td>구간(Gap)</td> <td>-</td>
                <td>{gap_ure_gen}</td> <td>{gap_ure_cert}</td> <td>-</td>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(full_html, unsafe_allow_html=True)
