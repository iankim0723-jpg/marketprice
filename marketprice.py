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
    .streamlit-expanderHeader { background-color: #222 !important; color: #aaa !important; font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER")

# ==========================================
# [공통 함수] 계산 및 표 생성
# ==========================================
def calculate_base_from_target(target, thick, thick_list, gap):
    try:
        idx = thick_list.index(thick)
        return target - (idx * gap)
    except:
        return target

def make_html_table(title, price_dict, thick_list, gap_dict, mat_type="EPS"):
    rows = ""
    for i, t in enumerate(thick_list):
        if mat_type == "EPS":
            p_cert = price_dict['cert'] + (i * gap_dict['cert'])
            p_gen = price_dict['gen'] + (i * gap_dict['gen'])
            p_nan = price_dict['nan'] + (i * gap_dict['nan'])
            
            # 인증은 75T 미만 표시 안 함
            str_cert = f"{p_cert:,}" if t >= 75 else "-"
            # 일반 0.35T는 0.5T 대비 -4600원 가정
            cols = f"<td>{p_gen-4600:,}</td> <td>{p_gen:,}</td> <td>{p_nan-1400:,}</td> <td>{p_nan:,}</td> <td style='color:#D4AF37; font-weight:bold;'>{str_cert}</td>"
            
        elif mat_type == "GW":
            p_48 = price_dict['48'] + (i * gap_dict['48'])
            p_64 = price_dict['64'] + (i * gap_dict['64'])
            # 내화구조 (125T 이상)
            if t >= 125:
                f30, f60_48, f60_64 = f"{p_48+5000:,}", f"{p_48+6000:,}", f"{p_64+6000:,}"
            else:
                f30, f60_48, f60_64 = "-", "-", "-"
            cols = f"<td>{p_48:,}</td> <td>{p_64:,}</td> <td>{f30}</td> <td>{f60_48}</td> <td>{f60_64}</td>"

        elif mat_type == "URE":
            p_gen = price_dict['gen'] + (i * gap_dict['gen'])
            p_cert = price_dict['cert'] + (i * gap_dict['cert'])
            cols = f"<td>{p_gen:,}</td> <td>{p_cert:,}</td>"

        rows += f"<tr><td>{t}T</td>{cols}</tr>"

    header = ""
    if mat_type == "EPS":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">일반</th><th colspan="2">난연</th><th>인증 (기본)</th></tr><tr class="sub-header"><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"""
    elif mat_type == "GW":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">그라스울 (불연)</th><th colspan="3">그라스울 (내화)</th></tr><tr class="sub-header"><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"""
    elif mat_type == "URE":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">우레탄</th></tr><tr class="sub-header"><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"""

    return f"""<div style="margin-bottom: 40px;"><h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3><table><thead>{header}</thead><tbody>{rows}</tbody></table></div>"""

style_block = """<style>
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; border: 1px solid #555; }
    th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 8px; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 6px; color: white; }
    .sub-header th { background-color: #B89630; font-size: 12px; }
    h3 { border-left: 5px solid #D4AF37; padding-left: 10px; }
</style>"""


# ==========================================
# [★핵심★] 관리자 모드 vs 뷰어 모드 (변수 설정)
# ==========================================
with st.sidebar:
    st.header("🔒 관리자 접속")
    admin_pw = st.text_input("비밀번호 (수정하려면 입력)", type="password")
    is_admin = (admin_pw == "0723")

    if is_admin:
        st.success("✅ 관리자 모드 ON")
        st.markdown("---")
        st.subheader("인상폭(Gap) 설정")
        # 관리자: 갭 수정 가능
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
        # 뷰어(고객용): 갭 고정
        gap_eps_gen, gap_eps_nan, gap_eps_cert = 800, 1400, 2500
        gap_gw_48, gap_gw_64 = 2400, 3200
        gap_ure_gen, gap_ure_cert = 4000, 5000


# 두께 리스트 정의
thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
thicks_ur = [50, 75, 100, 125, 150]


# ==========================================
# [데이터 로직] 관리자 vs 뷰어 값 결정
# ==========================================

# 1. EPS 데이터
if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("EPS 계산기 (관리자)")
    adm_t_eps = st.sidebar.selectbox("EPS 기준두께", thicks_eps, index=2) # 100T
    adm_p_eps = st.sidebar.number_input("EPS 인증 단가", value=22800, step=100)
    # 역산
    base_eps_cert = calculate_base_from_target(adm_p_eps, adm_t_eps, thicks_eps, gap_eps_cert)
    base_eps_gen = base_eps_cert - 6300 # 일반은 인증보다 6300원 저렴하다고 가정
else:
    # ★★★★★ [여기서 EPS 고정 단가를 수정하세요] ★★★★★
    base_eps_cert = 17800  # EPS 인증판넬 50T 가격
    base_eps_gen = 11500   # EPS 일반판넬 50T 가격
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

# EPS 품목별 차액 (벽체 대비)
diff_eps = {'ext': 2400, 'roof': 2900, 'zinc': 4500, 'line': 14700, 'jung': 24300}


# 2. GW 데이터
if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("GW 계산기 (관리자)")
    adm_t_gw = st.sidebar.selectbox("GW 기준두께", thicks_gw, index=0)
    adm_p_gw = st.sidebar.number_input("GW 벽체 단가", value=13800, step=100)
    base_gw_wall = calculate_base_from_target(adm_p_gw, adm_t_gw, thicks_gw, gap_gw_48)
else:
    # ★★★★★ [여기서 그라스울 고정 단가를 수정하세요] ★★★★★
    base_gw_wall = 13800   # GW 벽체 50T (48K) 가격
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

# GW 품목별 차액
diff_gw = {'ext': 2500, 'roof': 2500, 'zinc': 4900, 'line': 6300, 'jung': 15100}


# 3. URE 데이터
if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("우레탄 계산기 (관리자)")
    adm_t_ur = st.sidebar.selectbox("URE 기준두께", thicks_ur, index=0)
    adm_p_ur = st.sidebar.number_input("URE 벽체 단가", value=24500, step=100)
    base_ur_wall = calculate_base_from_target(adm_p_ur, adm_t_ur, thicks_ur, gap_ure_gen)
else:
    # ★★★★★ [여기서 우레탄 고정 단가를 수정하세요] ★★★★★
    base_ur_wall = 24500   # 우레탄 벽체 50T (일반) 가격
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

# URE 품목별 차액
diff_ur = {'ext': 1000, 'roof': 2000, 'zinc': 6000, 'line': 11000, 'jung': 21000}


# ==========================================
# [화면 출력] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# --- EPS 탭 ---
with tab_eps:
    if is_admin: st.info(f"관리자 모드: {adm_t_eps}T {adm_p_eps:,}원 기준 역산 중")
    
    gaps = {'gen': gap_eps_gen, 'nan': gap_eps_nan, 'cert': gap_eps_cert}
    
    html = style_block
    # 벽체
    html += make_html_table("1. EPS 벽체", {'gen': base_eps_gen, 'nan': base_eps_gen+1400, 'cert': base_eps_cert}, thicks_eps, gaps)
    # 외벽
    html += make_html_table("2. EPS 외벽체", {'gen': base_eps_gen+diff_eps['ext'], 'nan': base_eps_gen+diff_eps['ext']+1400, 'cert': base_eps_cert+diff_eps['ext']}, thicks_eps, gaps)
    # 지붕
    html += make_html_table("3. EPS 지붕", {'gen': base_eps_gen+diff_eps['roof'], 'nan': base_eps_gen+diff_eps['roof']+1400, 'cert': base_eps_cert+diff_eps['roof']}, thicks_eps, gaps)
    # 징크
    html += make_html_table("4. EPS 징크", {'gen': base_eps_gen+diff_eps['zinc'], 'nan': base_eps_gen+diff_eps['zinc']+1400, 'cert': base_eps_cert+diff_eps['zinc']}, thicks_eps, gaps)
    # 메탈
    html += make_html_table("5. EPS 라인메탈", {'gen': base_eps_gen+diff_eps['line'], 'nan': base_eps_gen+diff_eps['line']+1400, 'cert': base_eps_cert+diff_eps['line']}, [100, 125, 150, 175, 200, 225, 250], gaps)
    html += make_html_table("6. EPS 정메탈", {'gen': base_eps_gen+diff_eps['jung'], 'nan': base_eps_gen+diff_eps['jung']+1400, 'cert': base_eps_cert+diff_eps['jung']}, [100, 125, 150, 175, 200, 225, 250], gaps)
    
    components.html(html, height=2000, scrolling=True)

# --- GW 탭 ---
with tab_gw:
    if is_admin: st.info(f"관리자 모드: {adm_t_gw}T {adm_p_gw:,}원 기준 역산 중")
    
    gaps = {'48': gap_gw_48, '64': gap_gw_64}
    bgw = base_gw_wall # 단축
    
    html = style_block
    html += make_html_table("1. GW 벽체", {'48': bgw, '64': bgw+2000}, thicks_gw, gaps, "GW")
    html += make_html_table("2. GW 외벽체", {'48': bgw+diff_gw['ext'], '64': bgw+diff_gw['ext']+2000}, thicks_gw, gaps, "GW")
    html += make_html_table("3. GW 지붕", {'48': bgw+diff_gw['roof'], '64': bgw+diff_gw['roof']+2000}, thicks_gw, gaps, "GW")
    html += make_html_table("4. GW 징크", {'48': bgw+diff_gw['zinc'], '64': bgw+diff_gw['zinc']+2000}, thicks_gw, gaps, "GW")
    html += make_html_table("5. GW 라인메탈", {'48': bgw+diff_gw['line'], '64': bgw+diff_gw['line']+2000}, thicks_gw, gaps, "GW")
    html += make_html_table("6. GW 정메탈", {'48': bgw+diff_gw['jung'], '64': bgw+diff_gw['jung']+2000}, thicks_gw, gaps, "GW")
    
    components.html(html, height=2000, scrolling=True)

# --- URE 탭 ---
with tab_ure:
    if is_admin: st.info(f"관리자 모드: {adm_t_ur}T {adm_p_ur:,}원 기준 역산 중")
    
    gaps = {'gen': gap_ure_gen, 'cert': gap_ure_cert}
    bur = base_ur_wall
    
    html = style_block
    html += make_html_table("1. 우레탄 벽체", {'gen': bur, 'cert': bur+8000}, thicks_ur, gaps, "URE")
    html += make_html_table("2. 우레탄 외벽체", {'gen': bur+diff_ur['ext'], 'cert': bur+diff_ur['ext']+8000}, thicks_ur, gaps, "URE")
    html += make_html_table("3. 우레탄 지붕", {'gen': bur+diff_ur['roof'], 'cert': bur+diff_ur['roof']+8000}, thicks_ur, gaps, "URE")
    html += make_html_table("4. 우레탄 징크", {'gen': bur+diff_ur['zinc'], 'cert': bur+diff_ur['zinc']+8000}, thicks_ur, gaps, "URE")
    html += make_html_table("5. 우레탄 라인메탈", {'gen': bur+diff_ur['line'], 'cert': bur+diff_ur['line']+8000}, thicks_ur, gaps, "URE")
    html += make_html_table("6. 우레탄 정메탈", {'gen': bur+diff_ur['jung'], 'cert': bur+diff_ur['jung']+8000}, thicks_ur, gaps, "URE")
    
    components.html(html, height=2000, scrolling=True)


# ==========================================
# [하단 고정] 카톡복사 & 옵션표
# ==========================================
st.markdown("---")
st.subheader("📌 공통 기준 및 별도 옵션")

if st.sidebar.button("카톡용 텍스트 복사"):
    share_txt = f"[우리 스틸 단가]\nEPS인증(50T): {base_eps_cert:,}\nGW벽체(50T): {base_gw_wall:,}\n우레탄벽체(50T): {base_ur_wall:,}"
    st.sidebar.code(share_txt)

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
