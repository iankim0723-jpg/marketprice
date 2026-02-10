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
# [관리자 인증] 사이드바
# ==========================================
with st.sidebar:
    st.header("🔒 관리자 접속")
    admin_pw = st.text_input("비밀번호 입력", type="password")
    
    # 비밀번호: 0723 (변경 가능)
    is_admin = (admin_pw == "0723")

    if is_admin:
        st.success("관리자 모드: 수정 가능")
        st.markdown("---")
        st.header("⚙️ 인상폭(Gap) 설정")
        
        st.subheader("1. EPS Gap")
        gap_eps_gen = st.number_input("EPS 일반 Gap", value=800, step=100)
        gap_eps_nan = st.number_input("EPS 난연 Gap", value=1400, step=100)
        gap_eps_cert = st.number_input("EPS 인증 Gap", value=2500, step=100)
        
        st.markdown("---")
        st.subheader("2. 그라스울 Gap")
        gap_gw_48 = st.number_input("GW 48K Gap", value=2400, step=100)
        gap_gw_64 = st.number_input("GW 64K Gap", value=3200, step=100)
        
        st.markdown("---")
        st.subheader("3. 우레탄 Gap")
        gap_ure_gen = st.number_input("우레탄 일반 Gap", value=4000, step=100)
        gap_ure_cert = st.number_input("우레탄 인증 Gap", value=5000, step=100)
    else:
        # 비로그인 시: 기본 고정값 사용 (수정 불가)
        gap_eps_gen = 800
        gap_eps_nan = 1400
        gap_eps_cert = 2500
        gap_gw_48 = 2400
        gap_gw_64 = 3200
        gap_ure_gen = 4000
        gap_ure_cert = 5000
        st.info("현재 '뷰어 모드'입니다.\n단가 수정을 원하시면 비밀번호를 입력하세요.")

# ==========================================
# [공통 함수] 로직
# ==========================================
def calculate_base_price_from_target(target_price, target_thick, thick_list, gap_price):
    try:
        idx = thick_list.index(target_thick)
        return target_price - (idx * gap_price)
    except ValueError:
        return target_price

def make_html_table(title, base_price_dict, thick_list, gap_dict, material_type="EPS"):
    rows = ""
    for i, t in enumerate(thick_list):
        cols = ""
        if material_type == "EPS":
            p_cert = base_price_dict['cert'] + (i * gap_dict['cert'])
            p_gen05 = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_gen35 = base_price_dict.get('gen35', p_gen05 - 4600)
            p_nan05 = base_price_dict['nan'] + (i * gap_dict['nan'])
            p_nan35 = p_nan05 - 1400
            
            if t < 75: str_cert = "-" 
            else: str_cert = f"{p_cert:,}"
            cols = f"<td>{p_gen35:,}</td> <td>{p_gen05:,}</td> <td>{p_nan35:,}</td> <td>{p_nan05:,}</td> <td style='color:#D4AF37; font-weight:bold;'>{str_cert}</td>"
            
        elif material_type == "GW":
            p_48 = base_price_dict['48'] + (i * gap_dict['48'])
            p_64 = base_price_dict['64'] + (i * gap_dict['64'])
            if t >= 125:
                f30 = f"{p_48 + 5000:,}"
                f60_48 = f"{p_48 + 6000:,}"
                f60_64 = f"{p_64 + 6000:,}"
            else: f30 = f60_48 = f60_64 = "-"
            cols = f"<td>{p_48:,}</td> <td>{p_64:,}</td> <td>{f30}</td> <td>{f60_48}</td> <td>{f60_64}</td>"

        elif material_type == "URE":
            p_gen = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_cert = base_price_dict['cert'] + (i * gap_dict['cert'])
            cols = f"<td>{p_gen:,}</td> <td>{p_cert:,}</td>"

        rows += f"<tr><td>{t}T</td>{cols}</tr>"

    header = ""
    if material_type == "EPS":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">일반 (EPS)</th><th colspan="2">난연 (EPS)</th><th>인증 (기본)</th></tr><tr class="sub-header"><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"""
    elif material_type == "GW":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">그라스울 (불연)</th><th colspan="3">그라스울 (내화)</th></tr><tr class="sub-header"><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"""
    elif material_type == "URE":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">우레탄</th></tr><tr class="sub-header"><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"""

    return f"""<div style="margin-bottom: 40px;"><h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3><table><thead>{header}</thead><tbody>{rows}</tbody></table></div>"""

style_block = """
<style>
    body { background-color: #000000; color: #FFFFFF; font-family: sans-serif; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; border: 1px solid #555; }
    th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 8px; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 6px; color: white; }
    .sub-header th { background-color: #B89630; font-size: 12px; }
    h3 { border-left: 5px solid #D4AF37; padding-left: 10px; }
</style>
"""

# ==========================================
# [메인] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# --- 1. EPS 탭 ---
with tab_eps:
    st.subheader("EPS 단가표 (인증 기준)")

    # [관리자 모드] -> 입력창 보임
    if is_admin:
        col_sel, col_inp, col_type = st.columns([1, 1.5, 1])
        thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
        
        with col_sel:
            target_t_eps = st.selectbox("기준 두께", thicks_eps, index=2) # 100T
        with col_inp:
            target_p_eps = st.number_input(f"EPS 벽체 {target_t_eps}T 단가", value=22800, step=100)
        with col_type:
            price_type = st.radio("가격 기준", ["인증 (기본)", "일반"], index=0, horizontal=True)
            
        # 품목별 차액 설정
        with st.expander("🔧 가격 상세 설정 (인증↔일반 차이 등)", expanded=False):
            manual_diff = st.number_input("인증 - 일반 차액 (50T 기준)", value=6300, step=100)
            c1, c2, c3 = st.columns(3)
            diff_eps_ext = c1.number_input("외벽체 추가금", value=2400)
            diff_eps_roof = c2.number_input("지붕 추가금", value=2900)
            diff_eps_zinc = c3.number_input("징크 추가금", value=4500)
            c4, c5 = st.columns(2)
            diff_eps_line = c4.number_input("라인메탈 추가금", value=14700)
            diff_eps_jung = c5.number_input("정메탈 추가금", value=24300)
            
        # 계산 로직
        if price_type == "인증 (기본)":
            base_eps_cert = calculate_base_price_from_target(target_p_eps, target_t_eps, thicks_eps, gap_eps_cert)
            base_cert = base_eps_cert
            base_gen = base_cert - manual_diff
        else:
            base_eps_gen_input = calculate_base_price_from_target(target_p_eps, target_t_eps, thicks_eps, gap_eps_gen)
            base_gen = base_eps_gen_input
            base_cert = base_gen + manual_diff

    # [일반 모드] -> 고정값 사용 (수정 불가)
    else:
        # ★ 여기에 대표님이 원하는 '고정 단가'를 입력해두시면 됩니다 ★
        # 현재는 예시로 넣어둔 값입니다. 나중에 이 코드 숫자를 바꾸시면 영구 고정됩니다.
        base_cert = 17800 # 인증 50T 기준값 (예시)
        base_gen = 11500  # 일반 50T 기준값 (예시)
        
        diff_eps_ext = 2400
        diff_eps_roof = 2900
        diff_eps_zinc = 4500
        diff_eps_line = 14700
        diff_eps_jung = 24300
        thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]

    # 출력
    gaps_eps = {'gen': gap_eps_gen, 'nan': gap_eps_nan, 'cert': gap_eps_cert}
    html_content = style_block
    html_content += make_html_table("1. EPS 벽체", {'gen': base_gen, 'nan': base_gen+1400, 'cert': base_cert}, thicks_eps, gaps_eps)
    html_content += make_html_table("2. EPS 외벽체", {'gen': base_gen+diff_eps_ext, 'nan': base_gen+diff_eps_ext+1400, 'cert': base_cert+diff_eps_ext}, thicks_eps, gaps_eps)
    html_content += make_html_table("3. EPS 지붕", {'gen': base_gen+diff_eps_roof, 'nan': base_gen+diff_eps_roof+1400, 'cert': base_cert+diff_eps_roof}, thicks_eps, gaps_eps)
    html_content += make_html_table("4. EPS 징크", {'gen': base_gen+diff_eps_zinc, 'nan': base_gen+diff_eps_zinc+1400, 'cert': base_cert+diff_eps_zinc}, thicks_eps, gaps_eps)
    html_content += make_html_table("5. EPS 라인메탈", {'gen': base_gen+diff_eps_line, 'nan': base_gen+diff_eps_line+1400, 'cert': base_cert+diff_eps_line}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)
    html_content += make_html_table("6. EPS 정메탈", {'gen': base_gen+diff_eps_jung, 'nan': base_gen+diff_eps_jung+1400, 'cert': base_cert+diff_eps_jung}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)

    components.html(html_content, height=2000, scrolling=True)


# --- 2. GW 탭 ---
with tab_gw:
    st.subheader("그라스울 단가표")
    
    if is_admin:
        col_sel, col_inp = st.columns([1, 2])
        thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
        
        with col_sel:
            target_t_gw = st.selectbox("기준 두께 (GW)", thicks_gw, index=0)
        with col_inp:
            target_p_gw = st.number_input(f"GW 벽체 {target_t_gw}T 단가", value=13800, step=100)

        base_gw = calculate_base_price_from_target(target_p_gw, target_t_gw, thicks_gw, gap_gw_48)

        with st.expander("🔧 품목별 추가금 설정", expanded=False):
            c1, c2, c3 = st.columns(3)
            diff_gw_ext = c1.number_input("GW 외벽체 추가금", value=2500)
            diff_gw_roof = c2.number_input("GW 지붕 추가금", value=2500)
            diff_gw_zinc = c3.number_input("GW 징크 추가금", value=4900)
            c4, c5 = st.columns(2)
            diff_gw_line = c4.number_input("GW 라인메탈 추가금", value=6300)
            diff_gw_jung = c5.number_input("GW 정메탈 추가금", value=15100)
    else:
        # 일반 모드 고정값
        base_gw = 13800 
        diff_gw_ext = 2500
        diff_gw_roof = 2500
        diff_gw_zinc = 4900
        diff_gw_line = 6300
        diff_gw_jung = 15100
        thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]

    gaps_gw = {'48': gap_gw_48, '64': gap_gw_64}
    
    html_content = style_block
    html_content += make_html_table("1. GW 벽체", {'48': base_gw, '64': base_gw+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("2. GW 외벽체", {'48': base_gw+diff_gw_ext, '64': base_gw+diff_gw_ext+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("3. GW 지붕", {'48': base_gw+diff_gw_roof, '64': base_gw+diff_gw_roof+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("4. GW 징크", {'48': base_gw+diff_gw_zinc, '64': base_gw+diff_gw_zinc+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("5. GW 라인메탈", {'48': base_gw+diff_gw_line, '64': base_gw+diff_gw_line+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("6. GW 정메탈", {'48': base_gw+diff_gw_jung, '64': base_gw+diff_gw_jung+2000}, thicks_gw, gaps_gw, "GW")
    
    components.html(html_content, height=2000, scrolling=True)


# --- 3. URE 탭 ---
with tab_ure:
    st.subheader("우레탄 단가표")
    
    if is_admin:
        col_sel, col_inp = st.columns([1, 2])
        thicks_ur = [50, 75, 100, 125, 150]
        
        with col_sel:
            target_t_ure = st.selectbox("기준 두께 (URE)", thicks_ur, index=0)
        with col_inp:
            target_p_ure = st.number_input(f"URE 벽체 {target_t_ure}T 단가", value=24500, step=100)

        base_ure = calculate_base_price_from_target(target_p_ure, target_t_ure, thicks_ur, gap_ure_gen)

        with st.expander("🔧 품목별 추가금 설정", expanded=False):
            c1, c2, c3 = st.columns(3)
            diff_ur_ext = c1.number_input("URE 외벽체 추가금", value=1000)
            diff_ur_roof = c2.number_input("URE 지붕 추가금", value=2000)
            diff_ur_zinc = c3.number_input("URE 징크 추가금", value=6000)
            c4, c5 = st.columns(2)
            diff_ur_line = c4.number_input("URE 라인메탈 추가금", value=11000)
            diff_ur_jung = c5.number_input("URE 정메탈 추가금", value=21000)
    else:
        # 일반 모드 고정값
        base_ure = 24500
        diff_ur_ext = 1000
        diff_ur_roof = 2000
        diff_ur_zinc = 6000
        diff_ur_line = 11000
        diff_ur_jung = 21000
        thicks_ur = [50, 75, 100, 125, 150]

    gaps_ure = {'gen': gap_ure_gen, 'cert': gap_ure_cert}
    
    html_content = style_block
    html_content += make_html_table("1. 우레탄 벽체", {'gen': base_ure, 'cert': base_ure+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("2. 우레탄 외벽체", {'gen': base_ure+diff_ur_ext, 'cert': base_ure+diff_ur_ext+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("3. 우레탄 지붕", {'gen': base_ure+diff_ur_roof, 'cert': base_ure+diff_ur_roof+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("4. 우레탄 징크", {'gen': base_ure+diff_ur_zinc, 'cert': base_ure+diff_ur_zinc+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("5. 우레탄 라인메탈", {'gen': base_ure+diff_ur_line, 'cert': base_ure+diff_ur_line+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("6. 우레탄 정메탈", {'gen': base_ure+diff_ur_jung, 'cert': base_ure+diff_ur_jung+8000}, thicks_ur, gaps_ure, "URE")
    
    components.html(html_content, height=2000, scrolling=True)


# ==========================================
# [하단 고정] 공통 기준 & 별도 옵션
# ==========================================
st.markdown("---")
st.subheader("📌 공통 기준 및 별도 옵션")

share_txt = f"""[우리 스틸 기준 단가]
EPS 인증: {base_cert:,}원 기준
GW 48K: {base_gw:,}원 기준"""
if st.sidebar.button("카톡용 텍스트 복사"):
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
