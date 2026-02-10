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
    
    /* 헤더 스타일 */
    .header-box { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #444; padding-bottom: 20px; }
    .phone { font-size: 2.2rem; font-weight: bold; color: #D4AF37; margin-bottom: 5px; }
    .sub-info { font-size: 1.1rem; color: #FF4B4B; font-weight: bold; }
    
    /* 공지 박스 */
    .notice { background-color: #3d0c0c; border: 1px solid #FF4B4B; border-radius: 5px; padding: 10px; text-align: center; color: #FF4B4B; font-weight: bold; }
    
    /* 검색 결과 박스 */
    .result-box { background-color: #222; border: 2px solid #D4AF37; border-radius: 10px; padding: 15px; text-align: center; margin-top: 10px; }
    .result-price { font-size: 2rem; font-weight: bold; color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [상단] 배너 & 전화번호
# ==========================================
st.title("WOORI PRICE MASTER")
st.markdown("""
    <div class="header-box">
        <div class="phone">📞 상담문의 T. 1577-8790</div>
        <div class="sub-info">※ 운반비 별도 / 부가세 별도</div>
    </div>
    <div class="notice">📢 [필독] 견적 산출 시, 화면 최하단의 '별도 옵션표'를 반드시 확인해 주세요!</div>
    """, unsafe_allow_html=True)


# ==========================================
# [사이드바] 관리자 & 데이터 설정
# ==========================================
with st.sidebar:
    st.header("🔒 관리자 접속")
    admin_pw = st.text_input("비밀번호", type="password")
    is_admin = (admin_pw == "0723")

    if is_admin:
        st.success("✅ 관리자 모드")
        st.markdown("---")
        st.subheader("1. 기준 단가 (50T)")
        base_eps_gen = st.number_input("EPS 일반 50T", value=11500, step=100)
        base_gw_wall = st.number_input("GW 벽체 50T", value=13800, step=100)
        base_ure_wall = st.number_input("URE 벽체 50T", value=24500, step=100)
        
        st.markdown("---")
        st.subheader("2. 인상폭(Gap)")
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
# [데이터 계산 로직] - ★키값 오류 수정됨★
# ==========================================
# EPS (일반 50T 기준)
base_eps_nan = base_eps_gen + 1400
base_eps_cert = base_eps_gen + 6300
d_eps = {'벽체':0, '외벽체':2400, '지붕':2900, '징크':4500, '라인메탈':14700, '정메탈':24300}

# ★ 수정된 부분: 키값을 함수와 일치시킴 (일반->gen, 난연->nan, 인증->cert)
gaps_eps = {'gen':gap_eps_gen, 'nan':gap_eps_nan, 'cert':gap_eps_cert}
thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]

# GW
bgw = base_gw_wall
d_gw = {'벽체':0, '외벽체':2500, '지붕':2500, '징크':4900, '라인메탈':6300, '정메탈':15100}
# ★ 수정된 부분: (48K->48, 64K->64)
gaps_gw = {'48':gap_gw_48, '64':gap_gw_64}
thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]

# URE
bur = base_ure_wall
d_ur = {'벽체':0, '외벽체':1000, '지붕':2000, '징크':6000, '라인메탈':11000, '정메탈':21000}
# ★ 수정된 부분: (일반->gen, 인증->cert)
gaps_ure = {'gen':gap_ure_gen, 'cert':gap_ure_cert}
thicks_ur = [50, 75, 100, 125, 150]


# ==========================================
# [기능] 🔍 빠른 단가 조회
# ==========================================
st.markdown("### 🔍 빠른 단가 조회")
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    s_mat = c1.selectbox("1. 자재", ["EPS", "그라스울", "우레탄"])
    s_type = c2.selectbox("2. 품목", ["벽체", "외벽체", "지붕", "징크", "라인메탈", "정메탈"])
    
    if s_mat == "EPS": 
        s_thick = c3.selectbox("3. 두께", thicks_eps)
        s_grade = c4.selectbox("4. 등급", ["인증", "난연", "일반"])
    elif s_mat == "그라스울": 
        s_thick = c3.selectbox("3. 두께", thicks_gw)
        s_grade = c4.selectbox("4. 밀도", ["48K", "64K"])
    else: 
        s_thick = c3.selectbox("3. 두께", thicks_ur)
        s_grade = c4.selectbox("4. 등급", ["인증", "일반"])

    # 계산 (빠른조회용 로직)
    final_price = 0
    idx = 0
    if s_mat == "EPS":
        idx = thicks_eps.index(s_thick)
        if s_grade == "인증":
            base = base_eps_cert + d_eps[s_type]
            final_price = base + ((idx-1) * gaps_eps['cert']) if s_thick >= 75 else 0
        elif s_grade == "난연":
            base = base_eps_nan + d_eps[s_type]
            final_price = base + (idx * gaps_eps['nan'])
        else:
            base = base_eps_gen + d_eps[s_type]
            final_price = base + (idx * gaps_eps['gen'])
    elif s_mat == "그라스울":
        idx = thicks_gw.index(s_thick)
        base = bgw + d_gw[s_type]
        final_price = base + (idx * gaps_gw['48']) if s_grade=="48K" else (base+2000) + (idx * gaps_gw['64'])
    elif s_mat == "우레탄":
        idx = thicks_ur.index(s_thick)
        base = bur + d_ur[s_type]
        final_price = base + (idx * gaps_ure['gen']) if s_grade=="일반" else (base+8000) + (idx * gaps_ure['cert'])

    # 결과 표시
    st.markdown(f"""
    <div class="result-box">
        <span style="color:#aaa;">선택하신 사양의 단가는</span><br>
        <span class="result-price">{final_price:,}원</span> <span style="color:white">입니다.</span>
    </div>
    """, unsafe_allow_html=True)
    
    copy_text = f"[우리 스틸 견적]\n{s_mat} {s_type} {s_thick}T ({s_grade})\n단가: {final_price:,}원\n*운반비/부가세 별도"
    with st.expander("💬 카톡 복사 (클릭)"):
        st.code(copy_text, language="text")

st.markdown("---")


# ==========================================
# [공통 함수] 테이블 HTML 생성
# ==========================================
def make_html_table(title, p_dict, t_list, g_dict, m_type="EPS"):
    rows = ""
    for i, t in enumerate(t_list):
        if m_type == "EPS":
            # 사전 키와 매칭: cert, gen, nan
            pc = p_dict['cert'] + (i * g_dict['cert'])
            pg = p_dict['gen'] + (i * g_dict['gen'])
            pn = p_dict['nan'] + (i * g_dict['nan'])
            sc = f"{pc:,}" if t >= 75 else "-"
            cols = f"<td>{pg-4600:,}</td><td>{pg:,}</td><td>{pn-1400:,}</td><td>{pn:,}</td><td style='color:#D4AF37;font-weight:bold;'>{sc}</td>"
        elif m_type == "GW":
            # 사전 키와 매칭: 48, 64
            p48 = p_dict['48'] + (i * g_dict['48'])
            p64 = p_dict['64'] + (i * g_dict['64'])
            if t>=125: f30,f60a,f60b = f"{p48+5000:,}", f"{p48+6000:,}", f"{p64+6000:,}"
            else: f30,f60a,f60b = "-","-","-"
            cols = f"<td>{p48:,}</td><td>{p64:,}</td><td>{f30}</td><td>{f60a}</td><td>{f60b}</td>"
        elif m_type == "URE":
            # 사전 키와 매칭: gen, cert
            pg = p_dict['gen'] + (i * g_dict['gen'])
            pc = p_dict['cert'] + (i * g_dict['cert'])
            cols = f"<td>{pg:,}</td><td>{pc:,}</td>"
        rows += f"<tr><td>{t}T</td>{cols}</tr>"

    head = ""
    if m_type == "EPS": head = "<tr><th rowspan='2'>두께</th><th colspan='2'>일반</th><th colspan='2'>난연</th><th>인증 (기본)</th></tr><tr class='sub-header'><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"
    elif m_type == "GW": head = "<tr><th rowspan='2'>두께</th><th colspan='2'>그라스울 (불연)</th><th colspan='3'>그라스울 (내화)</th></tr><tr class='sub-header'><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"
    elif m_type == "URE": head = "<tr><th rowspan='2'>두께</th><th colspan='2'>우레탄</th></tr><tr class='sub-header'><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"

    return f"<div style='margin-bottom:40px;'><h3 style='color:#D4AF37;'>{title}</h3><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>"

style_t = "<style>table{width:100%;border-collapse:collapse;font-size:13px;text-align:center;} th{background:#D4AF37;color:black;border:1px solid #555;padding:8px;} td{background:#1A1A1A;border:1px solid #444;padding:6px;color:white;} .sub-header th{background:#B89630;font-size:12px;}</style>"


# ==========================================
# [화면 출력] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

with tab_eps:
    if is_admin: st.info(f"관리자: EPS 일반 50T {base_eps_gen:,}원 기준")
    h = style_t
    h += make_html_table("1. EPS 벽체", {'gen':base_eps_gen, 'nan':base_eps_nan, 'cert':base_eps_cert}, thicks_eps, gaps_eps)
    h += make_html_table("2. EPS 외벽체", {'gen':base_eps_gen+d_eps['외벽체'], 'nan':base_eps_nan+d_eps['외벽체'], 'cert':base_eps_cert+d_eps['외벽체']}, thicks_eps, gaps_eps)
    h += make_html_table("3. EPS 지붕", {'gen':base_eps_gen+d_eps['지붕'], 'nan':base_eps_nan+d_eps['지붕'], 'cert':base_eps_cert+d_eps['지붕']}, thicks_eps, gaps_eps)
    h += make_html_table("4. EPS 징크", {'gen':base_eps_gen+d_eps['징크'], 'nan':base_eps_nan+d_eps['징크'], 'cert':base_eps_cert+d_eps['징크']}, thicks_eps, gaps_eps)
    h += make_html_table("5. EPS 라인메탈", {'gen':base_eps_gen+d_eps['라인메탈'], 'nan':base_eps_nan+d_eps['라인메탈'], 'cert':base_eps_cert+d_eps['라인메탈']}, [100,125,150,175,200,225,250], gaps_eps)
    h += make_html_table("6. EPS 정메탈", {'gen':base_eps_gen+d_eps['정메탈'], 'nan':base_eps_nan+d_eps['정메탈'], 'cert':base_eps_cert+d_eps['정메탈']}, [100,125,150,175,200,225,250], gaps_eps)
    components.html(h, height=2000, scrolling=True)

with tab_gw:
    if is_admin: st.info(f"관리자: GW 벽체 50T {base_gw_wall:,}원 기준")
    h = style_t
    h += make_html_table("1. GW 벽체", {'48':bgw, '64':bgw+2000}, thicks_gw, gaps_gw, "GW")
    h += make_html_table("2. GW 외벽체", {'48':bgw+d_gw['외벽체'], '64':bgw+d_gw['외벽체']+2000}, thicks_gw, gaps_gw, "GW")
    h += make_html_table("3. GW 지붕", {'48':bgw+d_gw['지붕'], '64':bgw+d_gw['지붕']+2000}, thicks_gw, gaps_gw, "GW")
    h += make_html_table("4. GW 징크", {'48':bgw+d_gw['징크'], '64':bgw+d_gw['징크']+2000}, thicks_gw, gaps_gw, "GW")
    h += make_html_table("5. GW 라인메탈", {'48':bgw+d_gw['라인메탈'], '64':bgw+d_gw['라인메탈']+2000}, thicks_gw, gaps_gw, "GW")
    h += make_html_table("6. GW 정메탈", {'48':bgw+d_gw['정메탈'], '64':bgw+d_gw['정메탈']+2000}, thicks_gw, gaps_gw, "GW")
    components.html(h, height=2000, scrolling=True)

with tab_ure:
    if is_admin: st.info(f"관리자: URE 벽체 50T {base_ure_wall:,}원 기준")
    h = style_t
    h += make_html_table("1. 우레탄 벽체", {'gen':bur, 'cert':bur+8000}, thicks_ur, gaps_ure, "URE")
    h += make_html_table("2. 우레탄 외벽체", {'gen':bur+d_ur['외벽체'], 'cert':bur+d_ur['외벽체']+8000}, thicks_ur, gaps_ure, "URE")
    h += make_html_table("3. 우레탄 지붕", {'gen':bur+d_ur['지붕'], 'cert':bur+d_ur['지붕']+8000}, thicks_ur, gaps_ure, "URE")
    h += make_html_table("4. 우레탄 징크", {'gen':bur+d_ur['징크'], 'cert':bur+d_ur['징크']+8000}, thicks_ur, gaps_ure, "URE")
    h += make_html_table("5. 우레탄 라인메탈", {'gen':bur+d_ur['라인메탈'], 'cert':bur+d_ur['라인메탈']+8000}, thicks_ur, gaps_ure, "URE")
    h += make_html_table("6. 우레탄 정메탈", {'gen':bur+d_ur['정메탈'], 'cert':bur+d_ur['정메탈']+8000}, thicks_ur, gaps_ure, "URE")
    components.html(h, height=2000, scrolling=True)


# ==========================================
# [하단] 옵션표
# ==========================================
st.markdown("---")
st.subheader("📌 공통 기준 및 별도 옵션")

footer = """
<style>
    .footer-wrap { display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; color: white; font-family: sans-serif; }
    .box { flex: 1; min-width: 350px; border: 1px solid #444; padding: 10px; background: #111; }
    h4 { color: #D4AF37; border-bottom: 1px solid #333; padding-bottom: 5px; margin-top: 0; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    th { background: #333; color: #D4AF37; border: 1px solid #555; padding: 6px; }
    td { background: #1A1A1A; border: 1px solid #444; padding: 6px; }
    .p { color: #FF6B6B; font-weight: bold; }
    .m { color: #4dabf7; font-weight: bold; }
</style>
<div class="footer-wrap">
    <div class="box">
        <h4>1. 공통사항 및 내화인증</h4>
        <table>
            <tr><th colspan="2">기본 공통</th></tr>
            <tr><td>보호필름</td><td class="p">+300원</td></tr>
            <tr><td>특이색상(오렌지/검정/노랑)</td><td class="p">+500원</td></tr>
            <tr><td>캐노피/행가 (50T)</td><td>20,500원</td></tr>
            <tr><td>캐노피/행가 (75T)</td><td>21,900원</td></tr>
        </table><br>
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
            <tr><td>벽체</td><td>일면 유색</td><td class="p">+500원</td></tr>
            <tr><td rowspan="4">외벽체/지붕</td><td>유니스톤</td><td class="p">+1,000원</td></tr>
            <tr><td>리얼/코르텐/징크</td><td class="p">+2,000원</td></tr>
            <tr><td>0.6T 변경</td><td class="p">+1,700원</td></tr>
            <tr><td>0.8T 변경</td><td class="p">+4,700원</td></tr>
            <tr><td rowspan="2">징크</td><td>유니스톤</td><td class="m">-500원 (공제)</td></tr>
            <tr><td>일면 유색</td><td class="m">-1,000원 (공제)</td></tr>
            <tr><td rowspan="2">라인메탈</td><td>메지 간격</td><td>1000 고정</td></tr>
            <tr><td>0.8T 변경</td><td class="p">+3,400원</td></tr>
            <tr><td>정메탈</td><td>측면/두걱 가공</td><td style="color:#D4AF37;">별도 견적</td></tr>
        </table>
    </div>
</div>
"""
components.html(footer, height=800, scrolling=True)
