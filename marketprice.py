import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

# 2. 디자인 CSS (검정 배경 + 금색 글씨 + 표 디자인)
st.markdown("""
    <style>
    /* 전체 배경 검정 */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    
    /* 입력창 라벨 및 텍스트 */
    h1, h2, h3, label { color: #D4AF37 !important; font-weight: bold; }
    p, span, div { color: #FFFFFF; }
    
    /* 입력 박스 디자인 */
    input { 
        background-color: #262626 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #D4AF37 !important; 
    }

    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; color: #FFF; border-radius: 4px; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37 !important; color: #000 !important; font-weight: bold; }

    /* ★ 표 디자인 (깨짐 방지) ★ */
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; color: #FFFFFF; text-align: center; }
    th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 10px; font-weight: bold; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 10px; }
    tr:hover td { background-color: #333; cursor: pointer; }
    
    /* 비고란 색상 */
    .remark { color: #FF6B6B; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER")

# ==========================================
# [사이드바] 구간 변동폭(Gap) 설정
# ==========================================
with st.sidebar:
    st.header("⚙️ 구간(Gap) 설정")
    st.info("50T 대비 두께별 인상액을 설정합니다.")
    
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
# [메인] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# --- EPS 탭 ---
with tab_eps:
    # 50T 기준가 입력
    c1, c2, c3, c4 = st.columns(4)
    with c1: base_eps_gen_35 = st.number_input("EPS 일반 (0.35T) 50T", value=9400)
    with c2: base_eps_gen_05 = st.number_input("EPS 일반 (0.5T) 50T", value=14000)
    with c3: base_eps_nan_05 = st.number_input("EPS 난연 (0.5T) 50T", value=15400)
    with c4: base_eps_cert = st.number_input("EPS 인증 75T 시작가", value=22800)

    # 데이터 생성 루프
    table_rows = ""
    thicknesses = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
    
    for i, t in enumerate(thicknesses):
        # 가격 계산
        p_gen_35 = base_eps_gen_35 + (i * gap_eps_gen)
        p_gen_05 = base_eps_gen_05 + (i * gap_eps_gen)
        p_nan_05 = base_eps_nan_05 + (i * gap_eps_nan)
        p_nan_35 = p_nan_05 - 1400 

        # 인증은 75T부터
        if t < 75:
            p_cert = "-"
        else:
            # 75T(인덱스 1)가 시작점이므로 (i-1)
            p_cert = f"{base_eps_cert + ((i-1) * gap_eps_cert):,}"

        # 비고
        rem = ""
        if t==75: rem="유니스톤"
        elif t==100: rem="유니스톤, 코르텐"
        elif t==260: rem="0.6T 변경 별도"

        # 행 추가 (HTML)
        table_rows += f"""
        <tr>
            <td>벽체</td>
            <td>{t}T</td>
            <td>{p_gen_35:,}</td>
            <td>{p_gen_05:,}</td>
            <td>{p_nan_35:,}</td>
            <td>{p_nan_05:,}</td>
            <td>{p_cert}</td>
            <td class="remark">{rem}</td>
        </tr>
        """

    # 최종 HTML 조립 (들여쓰기 제거하여 오류 방지)
    eps_html = f"""
    <table>
        <thead>
            <tr>
                <th rowspan="2">구분</th>
                <th rowspan="2">두께</th>
                <th colspan="2">일반 (EPS)</th>
                <th colspan="2">난연 (EPS)</th>
                <th>인증</th>
                <th rowspan="2">비고</th>
            </tr>
            <tr style="background-color: #B89630; color:black;">
                <th>양면 0.35T</th><th>양면 0.5T</th>
                <th>양면 0.35T</th><th>양면 0.5T</th>
                <th>양면 0.5T</th>
            </tr>
            <tr style="background-color: #333; color: #D4AF37; font-weight:bold;">
                <td>구간(Gap)</td><td>-</td>
                <td>{gap_eps_gen}</td><td>{gap_eps_gen}</td>
                <td>{gap_eps_nan}</td><td>{gap_eps_nan}</td>
                <td>{gap_eps_cert}</td>
                <td>-</td>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """
    
    # ★ 여기서 unsafe_allow_html=True가 있어야 표가 그려집니다 ★
    st.markdown(eps_html, unsafe_allow_html=True)


# --- 그라스울 탭 ---
with tab_gw:
    c1, c2, c3 = st.columns(3)
    with c1: base_gw48 = st.number_input("GW 48K 50T", value=20400)
    with c2: base_gw64 = st.number_input("GW 64K 50T", value=22400)
    with c3: st.warning("내화구조는 125T부터 자동 계산됩니다.")

    gw_rows = ""
    t_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
    
    for i, t in enumerate(t_gw):
        p48 = base_gw48 + (i * gap_gw_48)
        p64 = base_gw64 + (i * gap_gw_64)
        
        if t >= 125:
            f30_str = f"{p48 + 5000:,}"
            f60_48_str = f"{p48 + 6000:,}"
            f60_64_str = f"{p64 + 6000:,}"
        else:
            f30_str, f60_48_str, f60_64_str = "-", "-", "-"

        gw_rows += f"""
        <tr>
            <td>벽체/지붕</td>
            <td>{t}T</td>
            <td>{p48:,}</td>
            <td>{p64:,}</td>
            <td>{f30_str}</td>
            <td>{f60_48_str}</td>
            <td>{f60_64_str}</td>
        </tr>
        """

    gw_html = f"""
    <table>
        <thead>
            <tr>
                <th rowspan="2">구분</th>
                <th rowspan="2">두께</th>
                <th colspan="2">그라스울 (불연)</th>
                <th colspan="3">그라스울 (내화 구조)</th>
            </tr>
            <tr style="background-color: #B89630; color:black;">
                <th>48K (0.5T)</th><th>64K (0.5T)</th>
                <th>48K (30분)</th><th>48K (60분)</th><th>64K (60분)</th>
            </tr>
            <tr style="background-color: #333; color: #D4AF37; font-weight:bold;">
                <td>구간(Gap)</td><td>-</td>
                <td>{gap_gw_48}</td><td>{gap_gw_64}</td>
                <td>{gap_gw_48}</td><td>{gap_gw_48}</td><td>{gap_gw_64}</td>
            </tr>
        </thead>
        <tbody>
            {gw_rows}
        </tbody>
    </table>
    """
    st.markdown(gw_html, unsafe_allow_html=True)


# --- 우레탄 탭 ---
with tab_ure:
    c1, c2 = st.columns(2)
    with c1: base_ure_gen = st.number_input("우레탄 일반 50T", value=24500)
    with c2: base_ure_cert = st.number_input("우레탄 인증 50T", value=32000)

    ure_rows = ""
    t_ure = [50, 75, 100, 125, 150]
    
    for i, t in enumerate(t_ure):
        p_gen = base_ure_gen + (i * gap_ure_gen)
        p_cert = base_ure_cert + (i * gap_ure_cert)
        
        rem = ""
        if t==50: rem="일면 유색 +500"
        if t==75: rem="유니스톤"

        ure_rows += f"""
        <tr>
            <td>벽체</td>
            <td>{t}T</td>
            <td>{p_gen:,}</td>
            <td>{p_cert:,}</td>
            <td class="remark">{rem}</td>
        </tr>
        """

    ure_html = f"""
    <table>
        <thead>
            <tr>
                <th rowspan="2">구분</th>
                <th rowspan="2">두께</th>
                <th colspan="2">우레탄</th>
                <th rowspan="2">비고</th>
            </tr>
            <tr style="background-color: #B89630; color:black;">
                <th>일반 (0.5T)</th><th>인증 (0.5T)</th>
            </tr>
             <tr style="background-color: #333; color: #D4AF37; font-weight:bold;">
                <td>구간(Gap)</td><td>-</td>
                <td>{gap_ure_gen}</td><td>{gap_ure_cert}</td>
                <td>-</td>
            </tr>
        </thead>
        <tbody>
            {ure_rows}
        </tbody>
    </table>
    """
    st.markdown(ure_html, unsafe_allow_html=True)
