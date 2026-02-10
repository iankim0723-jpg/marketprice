import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io

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
    </style>
    """, unsafe_allow_html=True)

st.title("WOORI PRICE MASTER")

# ==========================================
# [사이드바] 구간 변동폭(Gap) 설정
# ==========================================
with st.sidebar:
    st.header("⚙️ 구간(Gap) 설정")
    st.info("25T 단위 두께 증가 시 추가 금액")
    
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

# ==========================================
# [함수] HTML 테이블 생성기
# ==========================================
def make_html_table(title, base_price_dict, thick_list, gap_dict, material_type="EPS"):
    rows = ""
    for i, t in enumerate(thick_list):
        cols = ""
        if material_type == "EPS":
            p_gen05 = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_gen35 = base_price_dict.get('gen35', p_gen05 - 4600)
            p_nan05 = base_price_dict['nan'] + (i * gap_dict['nan'])
            p_nan35 = p_nan05 - 1400
            
            if t < 75: p_cert = "-"
            else: p_cert = f"{base_price_dict['cert'] + ((i-1) * gap_dict['cert']):,}"

            cols = f"<td>{p_gen35:,}</td> <td>{p_gen05:,}</td> <td>{p_nan35:,}</td> <td>{p_nan05:,}</td> <td>{p_cert}</td>"
            
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
        header = """<tr><th rowspan="2">두께</th><th colspan="2">일반 (EPS)</th><th colspan="2">난연 (EPS)</th><th>인증</th></tr><tr class="sub-header"><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"""
    elif material_type == "GW":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">그라스울 (불연)</th><th colspan="3">그라스울 (내화)</th></tr><tr class="sub-header"><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"""
    elif material_type == "URE":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">우레탄</th></tr><tr class="sub-header"><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"""

    return f"""<div style="margin-bottom: 40px;"><h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3><table><thead>{header}</thead><tbody>{rows}</tbody></table></div>"""

# ==========================================
# [기능] 엑셀 데이터 생성
# ==========================================
def generate_excel_data(all_prices, all_gaps):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # EPS 데이터 예시
        data = []
        for i, t in enumerate([50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]):
             p_gen = all_prices['eps_wall'] + (i * all_gaps['eps']['gen'])
             data.append({"두께": f"{t}T", "EPS벽체(일반)": p_gen})
        pd.DataFrame(data).to_excel(writer, sheet_name='단가표', index=False)
    return output.getvalue()


# ==========================================
# [메인] 화면 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

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

# --- EPS 탭 ---
with tab_eps:
    st.info("각 품목의 [50T 일반 0.5T 기준가]를 입력하세요.")
    c1, c2, c3 = st.columns(3)
    with c1: p_wall = st.number_input("EPS 벽체 50T", value=14000)
    with c2: p_ext = st.number_input("EPS 외벽체 50T", value=16400)
    with c3: p_roof = st.number_input("EPS 지붕 50T", value=16900)
    c4, c5, c6 = st.columns(3)
    with c4: p_zinc = st.number_input("EPS 징크 50T", value=18500)
    with c5: p_line = st.number_input("EPS 라인메탈 50T", value=28700)
    with c6: p_jung = st.number_input("EPS 정메탈 50T", value=38300)

    gaps_eps = {'gen': gap_eps_gen, 'nan': gap_eps_nan, 'cert': gap_eps_cert}
    thicks = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
    
    html_content = style_block
    html_content += make_html_table("1. EPS 벽체", {'gen': p_wall, 'nan': p_wall+1400, 'cert': p_wall+8800}, thicks, gaps_eps)
    html_content += make_html_table("2. EPS 외벽체", {'gen': p_ext, 'nan': p_ext+1400, 'cert': p_ext+8800}, thicks, gaps_eps)
    html_content += make_html_table("3. EPS 지붕", {'gen': p_roof, 'nan': p_roof+1400, 'cert': p_roof+8800}, thicks, gaps_eps)
    html_content += make_html_table("4. EPS 징크", {'gen': p_zinc, 'nan': p_zinc+1400, 'cert': p_zinc+8800}, thicks, gaps_eps)
    html_content += make_html_table("5. EPS 라인메탈", {'gen': p_line, 'nan': p_line+1400, 'cert': p_line+8800}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)
    html_content += make_html_table("6. EPS 정메탈", {'gen': p_jung, 'nan': p_jung+1400, 'cert': p_jung+8800}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)

    components.html(html_content, height=2000, scrolling=True)

# --- GW 탭 ---
with tab_gw:
    st.info("각 품목의 [50T 48K 기준가]를 입력하세요.")
    c1, c2, c3 = st.columns(3)
    with c1: p_gw_wall = st.number_input("GW 벽체 50T", value=20400)
    with c2: p_gw_ext = st.number_input("GW 외벽체 50T", value=22900)
    with c3: p_gw_roof = st.number_input("GW 지붕 50T", value=22900)
    c4, c5, c6 = st.columns(3)
    with c4: p_gw_zinc = st.number_input("GW 징크 50T", value=25300)
    with c5: p_gw_line = st.number_input("GW 라인메탈 50T", value=26700)
    with c6: p_gw_jung = st.number_input("GW 정메탈 50T", value=35500)

    gaps_gw = {'48': gap_gw_48, '64': gap_gw_64}
    thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
    
    html_content = style_block
    html_content += make_html_table("1. GW 벽체", {'48': p_gw_wall, '64': p_gw_wall+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("2. GW 외벽체", {'48': p_gw_ext, '64': p_gw_ext+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("3. GW 지붕", {'48': p_gw_roof, '64': p_gw_roof+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("4. GW 징크", {'48': p_gw_zinc, '64': p_gw_zinc+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("5. GW 라인메탈", {'48': p_gw_line, '64': p_gw_line+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("6. GW 정메탈", {'48': p_gw_jung, '64': p_gw_jung+2000}, thicks_gw, gaps_gw, "GW")
    
    components.html(html_content, height=2000, scrolling=True)

# --- URE 탭 ---
with tab_ure:
    st.info("각 품목의 [50T 일반 기준가]를 입력하세요.")
    c1, c2, c3 = st.columns(3)
    with c1: p_ur_wall = st.number_input("URE 벽체 50T", value=24500)
    with c2: p_ur_ext = st.number_input("URE 외벽체 50T", value=25500)
    with c3: p_ur_roof = st.number_input("URE 지붕 50T", value=26500)
    c4, c5, c6 = st.columns(3)
    with c4: p_ur_zinc = st.number_input("URE 징크 50T", value=30500)
    with c5: p_ur_line = st.number_input("URE 라인메탈 50T", value=35500)
    with c6: p_ur_jung = st.number_input("URE 정메탈 50T", value=45500)

    gaps_ure = {'gen': gap_ure_gen, 'cert': gap_ure_cert}
    thicks_ur = [50, 75, 100, 125, 150]
    
    html_content = style_block
    html_content += make_html_table("1. 우레탄 벽체", {'gen': p_ur_wall, 'cert': p_ur_wall+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("2. 우레탄 외벽체", {'gen': p_ur_ext, 'cert': p_ur_ext+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("3. 우레탄 지붕", {'gen': p_ur_roof, 'cert': p_ur_roof+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("4. 우레탄 징크", {'gen': p_ur_zinc, 'cert': p_ur_zinc+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("5. 우레탄 라인메탈", {'gen': p_ur_line, 'cert': p_ur_line+8000}, thicks_ur, gaps_ure, "URE")
    html_content += make_html_table("6. 우레탄 정메탈", {'gen': p_ur_jung, 'cert': p_ur_jung+8000}, thicks_ur, gaps_ure, "URE")
    
    components.html(html_content, height=2000, scrolling=True)


# ==========================================
# [기능] 엑셀 다운로드 & 카톡 복사
# ==========================================
all_prices = {'eps_wall': p_wall} 
all_gaps_excel = {'eps': gaps_eps} # 약식 데이터 (실제 사용 시 확장 필요)
excel_data = generate_excel_data(all_prices, all_gaps_excel)

st.sidebar.markdown("---")
st.sidebar.header("📥 내보내기")
st.sidebar.download_button("엑셀 다운로드", excel_data, "WOORI_PRICE.xlsx")

share_txt = f"""[우리 스틸 단가표]
EPS 벽체 50T: {p_wall:,}원
GW 벽체 50T: {p_gw_wall:,}원"""
if st.sidebar.button("카톡용 텍스트"):
    st.sidebar.code(share_txt)


# ==========================================
# [하단 고정] 공통 기준 & 별도 옵션 (안전한 문자열 방식)
# ==========================================
st.markdown("---")
st.subheader("📌 공통 기준 및 별도 옵션")

# ★ 중요: 여기는 f-string(f"...")을 쓰지 않고 일반 문자열("""...""")을 써서 에러를 방지합니다.
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
    .note { color: #aaa; font-size: 11px; }
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
            <tr><td colspan="3" class="note">*기본색상: 은회색 헤어라인 / 골드</td></tr>

            <tr><td>정메탈</td><td>측면/두걱 가공</td><td style="color:#D4AF37;">별도 견적</td></tr>
        </table>
    </div>
</div>
"""
components.html(footer_html, height=800, scrolling=True)
