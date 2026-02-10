import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    h1, h2, h3, label { color: #D4AF37 !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; border-radius: 5px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37 !important; color: black !important; font-weight: bold; }
    input { background-color: #262626 !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; }
    
    /* 상단 헤더 스타일 */
    .header-container {
        text-align: center;
        border-bottom: 1px solid #444;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }
    .phone-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #D4AF37;
        margin-bottom: 5px;
    }
    .disclaimer {
        font-size: 1.1rem;
        color: #FF4B4B;
        font-weight: bold;
    }
    
    /* 검색창 박스 스타일 */
    .search-box {
        background-color: #1A1A1A;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .price-display {
        font-size: 2rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-top: 10px;
    }
    
    /* 필독 공지 스타일 */
    .notice-box {
        background-color: #3d0c0c; 
        border: 1px solid #FF4B4B; 
        border-radius: 5px; 
        padding: 10px; 
        text-align: center; 
        margin-bottom: 15px;
        color: #FF4B4B;
        font-weight: bold;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [★신규★] 상단 배너 (제목 + 전화번호 + 운임/부가세)
# ==========================================
st.title("WOORI PRICE MASTER")

st.markdown("""
    <div class="header-container">
        <div class="phone-number">📞 상담문의 T. 1577-8790</div>
        <div class="disclaimer">※ 운반비 별도 / 부가세 별도</div>
    </div>
    <div class="notice-box">📢 [필독] 견적 산출 시, 최하단 '별도 옵션표' 확인 필수</div>
    """, unsafe_allow_html=True)


# ==========================================
# [사이드바] 관리자 설정 & 기본값
# ==========================================
with st.sidebar:
    st.header("🔒 관리자 접속")
    admin_pw = st.text_input("비밀번호", type="password")
    is_admin = (admin_pw == "0723")

    if is_admin:
        st.success("✅ 관리자 모드")
        st.markdown("---")
        st.subheader("1. 기준 단가 (50T 기준)")
        base_eps_gen = st.number_input("EPS 일반 50T", value=11500, step=100)
        base_gw_wall = st.number_input("GW 벽체 50T", value=13800, step=100)
        base_ure_wall = st.number_input("URE 벽체 50T", value=24500, step=100)
        
        st.markdown("---")
        st.subheader("2. 두께별 인상폭(Gap)")
        gap_eps_gen = st.number_input("EPS 일반 Gap", value=800, step=100)
        gap_eps_nan = st.number_input("EPS 난연 Gap", value=1400, step=100)
        gap_eps_cert = st.number_input("EPS 인증 Gap", value=2500, step=100)
        st.markdown("---")
        gap_gw_48 = st.number_input("GW 48K Gap", value=2400, step=100)
        gap_gw_64 = st.number_input("GW 64K Gap", value=3200, step=100)
        st.markdown("---")
        gap_ure_gen = st.number_input("우레탄 일반 Gap", value=4000, step=100)
        gap_ure_cert = st.number_input("우레탄 인증 Gap", value=5000, step=100)
    else:
        # [고객용 고정값]
        base_eps_gen = 11500
        base_gw_wall = 13800
        base_ure_wall = 24500
        
        gap_eps_gen, gap_eps_nan, gap_eps_cert = 800, 1400, 2500
        gap_gw_48, gap_gw_64 = 2400, 3200
        gap_ure_gen, gap_ure_cert = 4000, 5000

# ==========================================
# [데이터 계산 로직]
# ==========================================
# EPS
base_eps_nan = base_eps_gen + 1400
base_eps_cert = base_eps_gen + 6300
d_eps = {'벽체':0, '외벽체': 2400, '지붕': 2900, '징크': 4500, '라인메탈': 14700, '정메탈': 24300}
gaps_eps = {'일반': gap_eps_gen, '난연': gap_eps_nan, '인증': gap_eps_cert}
thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]

# GW
bgw = base_gw_wall
d_gw = {'벽체':0, '외벽체': 2500, '지붕': 2500, '징크': 4900, '라인메탈': 6300, '정메탈': 15100}
gaps_gw = {'48K': gap_gw_48, '64K': gap_gw_64}
thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]

# URE
bur = base_ure_wall
d_ur = {'벽체':0, '외벽체': 1000, '지붕': 2000, '징크': 6000, '라인메탈': 11000, '정메탈': 21000}
gaps_ure = {'일반': gap_ure_gen, '인증': gap_ure_cert}
thicks_ur = [50, 75, 100, 125, 150]

# ==========================================
# [기능] 🔍 빠른 단가 조회 (New!)
# ==========================================
st.markdown("### 🔍 빠른 단가 조회")
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        s_mat = st.selectbox("1. 자재", ["EPS", "그라스울", "우레탄"])
    
    with c2:
        # 자재별 품목 리스트
        s_type = st.selectbox("2. 품목", ["벽체", "외벽체", "지붕", "징크", "라인메탈", "정메탈"])
    
    with c3:
        # 자재별 두께 리스트
        if s_mat == "EPS": s_thick = st.selectbox("3. 두께", thicks_eps)
        elif s_mat == "그라스울": s_thick = st.selectbox("3. 두께", thicks_gw)
        else: s_thick = st.selectbox("3. 두께", thicks_ur)
        
    with c4:
        # 자재별 등급
        if s_mat == "EPS": s_grade = st.selectbox("4. 등급", ["인증", "난연", "일반"])
        elif s_mat == "그라스울": s_grade = st.selectbox("4. 밀도", ["48K", "64K"])
        else: s_grade = st.selectbox("4. 등급", ["인증", "일반"])

    # --- 계산 로직 ---
    final_price = 0
    idx = 0
    
    if s_mat == "EPS":
        idx = thicks_eps.index(s_thick)
        if s_grade == "인증":
            base = base_eps_cert + d_eps[s_type]
            if s_thick < 75: final_price = 0 
            else: final_price = base + ((idx-1) * gaps_eps['인증'])
        elif s_grade == "난연":
            base = base_eps_nan + d_eps[s_type]
            final_price = base + (idx * gaps_eps['난연'])
        else: # 일반
            base = base_eps_gen + d_eps[s_type]
            final_price = base + (idx * gaps_eps['일반'])
            
    elif s_mat == "그라스울":
        idx = thicks_gw.index(s_thick)
        base = bgw + d_gw[s_type]
        if s_grade == "48K": final_price = base + (idx * gaps_gw['48K'])
        else: final_price = (base + 2000) + (idx * gaps_gw['64K'])
        
    elif s_mat == "우레탄":
        idx = thicks_ur.index(s_thick)
        base = bur + d_ur[s_type]
        if s_grade == "일반": final_price = base + (idx * gaps_ure['일반'])
        else: final_price = (base + 8000) + (idx * gaps_ure['인증'])

    # --- 결과 출력 ---
    st.markdown(f"""
    <div style="background-color: #222; border: 1px solid #444; border-radius: 10px; padding: 15px; text-align: center;">
        <span style="color: #aaa;">선택하신 사양의 단가는</span><br>
        <span class="price-display">{final_price:,}원</span> <span style="color:white">입니다.</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 카톡 복사용 텍스트 생성 ---
    copy_text = f"""[우리 스틸 견적]
품목: {s_mat} {s_type}
사양: {s_grade}
두께: {s_thick}T
단가: {final_price:,}원
*운반비 별도 / 부가세 별도"""
    
    with st.expander("💬 카톡 복사용 텍스트 (클릭)", expanded=True):
        st.code(copy_text, language="text")
        st.caption("▲ 오른쪽 위 복사 아이콘을 누르세요.")

st.markdown("---")

# ==========================================
# [공통 함수] 표 생성기
# ==========================================
def make_html_table(title, price_dict, thick_list, gap_dict, mat_type="EPS"):
    rows = ""
    for i, t in enumerate(thick_list):
        if mat_type == "EPS":
            p_cert = price_dict['cert'] + (i * gap_dict['cert'])
            p_gen = price_dict['gen'] + (i * gap_dict['gen'])
            p_nan = price_dict['nan'] + (i * gap_dict['nan'])
            str_cert = f"{p_cert:,}" if t >= 75 else "-"
            cols = f"<td>{p_gen-4600:,}</td> <td>{p_gen:,}</td> <td>{p_nan-1400:,}</td> <td>{p_nan:,}</td> <td style='color:#D4AF37; font-weight:bold;'>{str_cert}</td>"
        elif mat_type == "GW":
            p_48 = price_dict['48'] + (i * gap_dict['48'])
            p_64 = price_dict['64'] + (i * gap_dict['64'])
            if t >= 125: f30, f60_48, f60_64 = f"{p_48+5000:,}", f"{p_48+6000:,}", f"{p_64+6000:,}"
            else: f30, f60_48, f60_64 = "-", "-", "-"
            cols = f"<td>{p_48:,}</td> <td>{p_64:,}</td> <td>{f30}</td> <td>{f60_48}</td> <td>{f60_64}</td>"
        elif mat_type == "URE":
            p_gen = price_dict['gen'] + (i * gap_dict['gen'])
            p_cert = price_dict['cert'] + (i * gap_dict['cert'])
            cols = f"<td>{p_gen:,}</td> <td>{p_cert:,}</td>"
        rows += f"<tr><td>{t}T</td>{cols}</tr>"
        
    header = ""
    if mat_type == "EPS": header = """<tr><th rowspan="2">두께</th><th colspan="2">일반</th><th colspan="2">난연</th><th>인증 (기본)</th></tr><tr class="sub-header"><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"""
    elif mat_type == "GW": header = """<tr><th rowspan="2">두께</th><th colspan="2">그라스울 (불연)</th><th colspan="3">그라스울 (내화)</th></tr><tr class="sub-header"><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"""
    elif mat_type == "URE": header = """<tr><th rowspan="2">두께</th><th colspan="2">우레탄</th></tr><tr class="sub-header"><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"""
    return f"""<div style="margin-bottom: 40px;"><h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3><table><thead>{header}</thead><tbody>{rows}</tbody></table></div>"""

style_block = """<style>
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; border: 1px solid #555; }
    th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 8px; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 6px; color: white; }
    .sub-header th { background-color: #B89630; font-size: 12px; }
    h3 { border-left: 5px solid #D4AF37; padding-left: 10px; }
</style>"""

# ==========================================
# [화면 출력] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

with tab_eps:
    if is_admin: st.info(f"관리자: EPS 일반 50T {base_eps_gen:,}원 기준")
    html = style_block
    html += make_html_table("1. EPS 벽체", {'gen': base_eps_gen, 'nan': base_eps_nan, 'cert': base_eps_cert}, thicks_eps, gaps_eps)
    html += make_html_table("2. EPS 외벽체", {'gen': base_eps_gen+d_eps['외벽체'], 'nan': base_eps_nan+d_eps['외벽체'], 'cert': base_eps_cert+d_eps['외벽체']}, thicks_eps, gaps_eps)
    html += make_html_table("3. EPS 지붕", {'gen': base_eps_gen+d_eps['지붕'], 'nan': base_eps_nan+d_eps['지붕'], 'cert': base_eps_cert+d_eps['지붕']}, thicks_eps, gaps_eps)
    html += make_html_table("4. EPS 징크", {'gen': base_eps_gen+d_eps['징크'], 'nan': base_eps_nan+d_eps['징크'], 'cert': base_eps_cert+d_eps['징크']}, thicks_eps, gaps_eps)
    html += make_html_table("5. EPS 라인메탈", {'gen': base_eps_gen+d_eps['라인메탈'], 'nan': base_eps_nan+d_eps['라인메탈'], 'cert': base_eps_cert+d_eps['라인메탈']}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)
    html += make_html_table("6. EPS 정메탈", {'gen': base_eps_gen+d_eps['정메탈'], 'nan': base_eps_nan+d_eps['정메탈'], 'cert': base_eps_cert+d_eps['정메탈']}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)
    components.html(html, height=2000, scrolling=True)

with tab_gw:
    if is_admin: st.info(f"관리자: GW 벽체 50T {base_gw_wall:,}원 기준")
    html = style_block
    html += make_html_table("1. GW 벽체", {'48': bgw, '64': bgw+2000}, thicks_gw, gaps_gw, "GW")
    html += make_html_table("2. GW 외벽체", {'48': bgw+d_gw['외벽체'], '64': bgw+d_gw['외벽체']+2000}, thicks_gw, gaps_gw, "GW")
    html += make_html_table("3. GW 지붕", {'48': bgw+d_gw['지붕'], '64': bgw+d_gw['지붕']+2000}, thicks_gw, gaps_gw, "GW")
    html += make_html_table("4. GW 징크", {'48': bgw+d_gw['징크'], '64': bgw+d_gw['징크']+2000}, thicks_gw, gaps_gw, "GW")
    html += make_html_table("5. GW 라인메탈", {'48': bgw+d_gw['라인메탈'], '64': bgw+d_gw['라인메탈']+2000}, thicks_gw, gaps_gw, "GW")
    html += make_html_table("6. GW 정메탈", {'48': bgw+d_gw['정메탈'], '64': bgw+d_gw['정메탈']+2000}, thicks_gw, gaps_gw, "GW")
    components.html(html, height=2000, scrolling=True)

with tab_ure:
    if is_admin: st.info(f"관리자: URE 벽체 50T {base_ure_wall:,}원 기준")
    html = style_block
    html += make_html_table("1. 우레탄 벽체", {'gen': bur, 'cert': bur+8000}, thicks_ur, gaps_ure, "URE")
    html += make_html_table("2. 우레탄 외벽체", {'gen': bur+d_ur['외벽체'], 'cert': bur+d_ur['외벽체']+8000}, thicks_ur, gaps_ure, "URE")
    html += make_html_table("3. 우레탄 지붕", {'gen': bur+d_ur['지붕'], 'cert': bur+d_ur['지붕']+8000}, thicks_ur, gaps_ure, "URE")
    html += make_html_table("4. 우레탄 징크", {'gen': bur+d_ur['징크'], 'cert': bur+d_ur['징크']+8000}, thicks_ur, gaps_ure, "URE")
    html += make_html_table("5. 우레탄 라인메탈", {'gen': bur+d_ur['라인메탈'], 'cert': bur+d_ur['라인메탈']+8000}, thicks_ur, gaps_ure, "URE")
    html += make_html_table("6. 우레탄 정메탈", {'gen': bur+d_ur['정메탈'], 'cert': bur+d_ur['정메탈']+8000}, thicks_ur, gaps_ure, "URE")
    components.html(html, height=2000, scrolling=True)

# ==========================================
# [하단 고정] 옵션표
# ==========================================
st.markdown("---")
st.subheader("📌 공통 기준 및 별도 옵션")

footer_html = """
<style>
    .footer-container { display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; font-family: sans-serif; color: white; }
    .box { flex: 1; min-width: 350px; border: 1px solid #444; padding: 10px; background-color: #111; }
    .box h4 { color: #D4AF37; margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 5px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    th { background-color: #333; color: #D4AF37; border: 1px solid #555; padding: 6px; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 6px; }
    .plus { color: #FF6B6B; font-weight: bold; }
    .minus { color: #4dabf7; font-weight: bold; }
</style>

<div class="footer-container">
    <div class="box">
        <h4>1. 공통사항 및 내화인증</h4>
        <table>
            <tr><th colspan="2">기본 공통</th></tr>
            <tr><td>보호필름</td><td class="plus">+300원</td></tr>
            <tr><td>특이색상(오렌지/검정/노랑)</td><td class="plus">+500원</td></tr>
            <tr><td>캐노피/행가 (50T)</td><td>20,500원</td></tr>
            <tr><td>캐노피/행가 (75T)</td><td>21,900원</td></tr>
        </table>
        <br>
        <table>
            <tr><th colspan="5">내화인증 기준 (그라스울)</th></tr>
            <tr><th>타입</th><th>두께</th><th>밀도</th><th>성능</th><th>비고</th></tr>
            <tr><td>벽체</td><td>125T~</td><td>48K</td><td>1시간</td><td>무하지</td></tr>
            <tr><td>외벽</td><td>100T~</td><td>48K</td><td>0.5시간</td><td>하지1700↓</td></tr>
            <tr><td>지붕</td><td>184T~</td><td>48K</td><td>0.5시간</td><td>하지1200↓</td></tr>
            <tr><td>징크</td><td>125T~</td><td>64K</td><td>1시간</td><td>하지1700↓</td></tr>
        </table>
    </div>

    <div class="box">
        <h4>2. 품목별 별도 옵션</h4>
        <table>
            <tr><th>구분</th><th>항목</th><th>금액</th></tr>
            <tr><td>벽체</td><td>일면 유색</td><td class="plus">+500원</td></tr>
            <tr><td rowspan="4">외벽체/지붕</td><td>유니스톤</td><td class="plus">+1,000원</td></tr>
            <tr><td>리얼/코르텐/징크</td><td class="plus">+2,000원</td></tr>
            <tr><td>0.6T 변경</td><td class="plus">+1,700원</td></tr>
            <tr><td>0.8T 변경</td><td class="plus">+4,700원</td></tr>
            <tr><td rowspan="2">징크</td><td>유니스톤</td><td class="minus">-500원 (공제)</td></tr>
            <tr><td>일면 유색</td><td class="minus">-1,000원 (공제)</td></tr>
            <tr><td rowspan="2">라인메탈</td><td>메지 간격</td><td>1000 고정</td></tr>
            <tr><td>0.8T 변경</td><td class="plus">+3,400원</td></tr>
            <tr><td>정메탈</td><td>측면/두걱 가공</td><td style="color:#D4AF37;">별도 견적</td></tr>
        </table>
    </div>
</div>
"""
components.html(footer_html, height=800, scrolling=True)
