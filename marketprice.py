import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOORI PRICE MASTER", layout="wide")

# 2. 스타일 (테이블 깨짐 방지 및 디자인)
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
# [사이드바] 구간 변동폭(Gap) 설정 (재질별 공통)
# ==========================================
with st.sidebar:
    st.header("⚙️ 구간(Gap) 설정")
    st.info("두께가 한 단계(25T) 올라갈 때마다 더해지는 금액입니다.")
    
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
# [함수] HTML 테이블 생성기 (코드 중복 제거)
# ==========================================
def make_html_table(title, base_price_dict, thick_list, gap_dict, material_type="EPS"):
    # base_price_dict: {'일반': 10000, '난연': 12000...}
    # gap_dict: {'일반': 800...}
    
    rows = ""
    for i, t in enumerate(thick_list):
        # 1. 가격 계산
        # 50T는 인덱스 0. 두께 단계(i)만큼 갭을 더함
        cols = ""
        
        # 품목별 컬럼 생성
        if material_type == "EPS":
            # EPS 컬럼: 일반0.35, 일반0.5, 난연0.35, 난연0.5, 인증
            # 기준가 + (인덱스 * 갭)
            p_gen05 = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_gen35 = base_price_dict.get('gen35', p_gen05 - 4600) # 0.35T 기본차액 가정
            p_nan05 = base_price_dict['nan'] + (i * gap_dict['nan'])
            p_nan35 = p_nan05 - 1400 # 난연 차액 가정
            
            # 인증은 75T부터 (인덱스 1부터)
            if t < 75: p_cert = "-"
            else: p_cert = f"{base_price_dict['cert'] + ((i-1) * gap_dict['cert']):,}"

            cols = f"""
                <td>{p_gen35:,}</td> <td>{p_gen05:,}</td>
                <td>{p_nan35:,}</td> <td>{p_nan05:,}</td>
                <td>{p_cert}</td>
            """
            
        elif material_type == "GW":
            # GW 컬럼: 48K, 64K, 내화(30/60)
            p_48 = base_price_dict['48'] + (i * gap_dict['48'])
            p_64 = base_price_dict['64'] + (i * gap_dict['64'])
            
            # 내화 (125T 이상)
            if t >= 125:
                f30 = f"{p_48 + 5000:,}" # 내화 할증 예시
                f60_48 = f"{p_48 + 6000:,}"
                f60_64 = f"{p_64 + 6000:,}"
            else: f30 = f60_48 = f60_64 = "-"
            
            cols = f"""
                <td>{p_48:,}</td> <td>{p_64:,}</td>
                <td>{f30}</td> <td>{f60_48}</td> <td>{f60_64}</td>
            """

        elif material_type == "URE":
            # 우레탄 컬럼: 일반, 인증
            p_gen = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_cert = base_price_dict['cert'] + (i * gap_dict['cert'])
            cols = f"<td>{p_gen:,}</td> <td>{p_cert:,}</td>"

        # 비고 (공통 로직)
        rem = ""
        if t==75: rem="유니스톤"
        elif t==100: rem="유니스톤, 코르텐"
        elif t==260: rem="0.6T 변경 별도"

        rows += f"<tr><td>{t}T</td>{cols}<td class='remark'>{rem}</td></tr>"

    # 헤더 생성
    header = ""
    if material_type == "EPS":
        header = """
        <tr>
            <th rowspan="2">두께</th> <th colspan="2">일반 (EPS)</th> <th colspan="2">난연 (EPS)</th> <th>인증</th> <th rowspan="2">비고</th>
        </tr>
        <tr class="sub-header">
            <th>0.35T</th> <th>0.5T</th> <th>0.35T</th> <th>0.5T</th> <th>0.5T</th>
        </tr>"""
    elif material_type == "GW":
        header = """
        <tr>
            <th rowspan="2">두께</th> <th colspan="2">그라스울 (불연)</th> <th colspan="3">그라스울 (내화)</th> <th rowspan="2">비고</th>
        </tr>
        <tr class="sub-header">
            <th>48K</th> <th>64K</th> <th>48K(30분)</th> <th>48K(60분)</th> <th>64K(60분)</th>
        </tr>"""
    elif material_type == "URE":
        header = """
        <tr>
            <th rowspan="2">두께</th> <th colspan="2">우레탄</th> <th rowspan="2">비고</th>
        </tr>
        <tr class="sub-header">
            <th>일반 (0.5T)</th> <th>인증 (0.5T)</th>
        </tr>"""

    return f"""
    <div style="margin-bottom: 30px;">
        <h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3>
        <table>
            <thead>{header}</thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """


# ==========================================
# [메인] 탭 구성
# ==========================================
tab_eps, tab_gw, tab_ure = st.tabs(["🟦 EPS 단가표", "🟨 그라스울 단가표", "🟥 우레탄 단가표"])

# 공통 스타일 정의
style_block = """
<style>
    body { background-color: #000000; color: #FFFFFF; font-family: sans-serif; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; border: 1px solid #555; }
    th { background-color: #D4AF37; color: #000000; border: 1px solid #555; padding: 8px; }
    td { background-color: #1A1A1A; border: 1px solid #444; padding: 6px; color: white; }
    .sub-header th { background-color: #B89630; font-size: 12px; }
    .remark { color: #FF6B6B; font-size: 11px; }
    h3 { border-left: 5px solid #D4AF37; padding-left: 10px; }
</style>
"""

# --- 1. EPS 탭 ---
with tab_eps:
    st.info("각 품목의 [50T 일반 0.5T 기준가]를 입력하세요. (인증은 75T 시작가)")
    
    # 입력창 배치 (6개 품목)
    c1, c2, c3 = st.columns(3)
    with c1: p_wall = st.number_input("EPS 벽체 50T", value=14000)
    with c2: p_ext = st.number_input("EPS 외벽체(골/V70) 50T", value=16400)
    with c3: p_roof = st.number_input("EPS 지붕 50T", value=16900)
    
    c4, c5, c6 = st.columns(3)
    with c4: p_zinc = st.number_input("EPS 징크 50T", value=18500)
    with c5: p_line = st.number_input("EPS 라인메탈 50T(계산용)", value=28700) # 실제 100T부터지만 50T 로직 적용
    with c6: p_jung = st.number_input("EPS 정메탈 50T(계산용)", value=38300)

    # 인증 시작가 (별도 입력 혹은 +알파) -> 여기선 단순화 위해 인증 시작가는 일반+8000원으로 자동 가정 (조절 가능)
    # 실제로는 품목마다 인증 갭이 다르지만, 편의상 '벽체 인증' 값을 기준으로 잡거나 각각 입력받아야 함.
    # 복잡도를 줄이기 위해 '일반' 입력값에 +8800원을 더해 인증 시작가로 자동 설정합니다.
    
    gaps = {'gen': gap_eps_gen, 'nan': gap_eps_nan, 'cert': gap_eps_cert}
    thicks = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
    
    # HTML 조립
    html_content = style_block
    
    # 1) EPS 벽체
    html_content += make_html_table("1. EPS 벽체", 
        {'gen': p_wall, 'nan': p_wall+1400, 'cert': p_wall+8800}, thicks, gaps)
    
    # 2) EPS 외벽체 (250/500/1000/V70/V45)
    html_content += make_html_table("2. EPS 외벽체 (250/500/1000골, V70, V45)", 
        {'gen': p_ext, 'nan': p_ext+1400, 'cert': p_ext+8800}, thicks, gaps)
    
    # 3) EPS 지붕
    html_content += make_html_table("3. EPS 지붕 (3골/4골)", 
        {'gen': p_roof, 'nan': p_roof+1400, 'cert': p_roof+8800}, thicks, gaps)

    # 4) EPS 징크
    html_content += make_html_table("4. EPS 징크 (ZK-2, ZK-3)", 
        {'gen': p_zinc, 'nan': p_zinc+1400, 'cert': p_zinc+8800}, thicks, gaps)

    # 5) EPS 라인메탈 (보통 100T부터지만 표시는 다 함)
    html_content += make_html_table("5. EPS 라인메탈 (메지 1000 고정)", 
        {'gen': p_line, 'nan': p_line+1400, 'cert': p_line+8800}, [100, 125, 150, 175, 200, 225, 250], gaps)

    # 6) EPS 정메탈
    html_content += make_html_table("6. EPS 정메탈 (L드가공 별도)", 
        {'gen': p_jung, 'nan': p_jung+1400, 'cert': p_jung+8800}, [100, 125, 150, 175, 200, 225, 250], gaps)

    components.html(html_content, height=2000, scrolling=True)


# --- 2. 그라스울 탭 ---
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

    gaps = {'48': gap_gw_48, '64': gap_gw_64}
    thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
    
    html_content = style_block
    # 64K는 48K + 2000원 가정
    html_content += make_html_table("1. GW 벽체", {'48': p_gw_wall, '64': p_gw_wall+2000}, thicks_gw, gaps, "GW")
    html_content += make_html_table("2. GW 외벽체", {'48': p_gw_ext, '64': p_gw_ext+2000}, thicks_gw, gaps, "GW")
    html_content += make_html_table("3. GW 지붕", {'48': p_gw_roof, '64': p_gw_roof+2000}, thicks_gw, gaps, "GW")
    html_content += make_html_table("4. GW 징크", {'48': p_gw_zinc, '64': p_gw_zinc+2000}, thicks_gw, gaps, "GW")
    html_content += make_html_table("5. GW 라인메탈", {'48': p_gw_line, '64': p_gw_line+2000}, thicks_gw, gaps, "GW")
    html_content += make_html_table("6. GW 정메탈", {'48': p_gw_jung, '64': p_gw_jung+2000}, thicks_gw, gaps, "GW")
    
    components.html(html_content, height=2000, scrolling=True)


# --- 3. 우레탄 탭 ---
with tab_ure:
    st.info("각 품목의 [50T 일반 기준가]를 입력하세요.")
    c1, c2, c3 = st.columns(3)
    with c1: p_ur_wall = st.number_input("URE 벽체 50T", value=24500)
    with c2: p_ur_ext = st.number_input("URE 외벽체 50T", value=25500)
    with c3: p_ur_roof = st.number_input("URE 지붕 50T", value=26500)
    
    c4, c5, c6 = st.columns(3)
    with c4: p_ur_zinc = st.number_input("URE 징크 50T", value=30500)
    with c5: p_ur_line = st.number_input("URE 라인메탈 50T", value=35500) # 가정
    with c6: p_ur_jung = st.number_input("URE 정메탈 50T", value=45500) # 가정

    gaps = {'gen': gap_ure_gen, 'cert': gap_ure_cert}
    thicks_ur = [50, 75, 100, 125, 150]
    
    html_content = style_block
    # 인증은 일반 + 8000원 가정
    html_content += make_html_table("1. 우레탄 벽체", {'gen': p_ur_wall, 'cert': p_ur_wall+8000}, thicks_ur, gaps, "URE")
    html_content += make_html_table("2. 우레탄 외벽체", {'gen': p_ur_ext, 'cert': p_ur_ext+8000}, thicks_ur, gaps, "URE")
    html_content += make_html_table("3. 우레탄 지붕", {'gen': p_ur_roof, 'cert': p_ur_roof+8000}, thicks_ur, gaps, "URE")
    html_content += make_html_table("4. 우레탄 징크", {'gen': p_ur_zinc, 'cert': p_ur_zinc+8000}, thicks_ur, gaps, "URE")
    html_content += make_html_table("5. 우레탄 라인메탈", {'gen': p_ur_line, 'cert': p_ur_line+8000}, thicks_ur, gaps, "URE")
    html_content += make_html_table("6. 우레탄 정메탈", {'gen': p_ur_jung, 'cert': p_ur_jung+8000}, thicks_ur, gaps, "URE")
    
    components.html(html_content, height=2000, scrolling=True)


# ==========================================
# [하단] 공통 비고 사항 (고정)
# ==========================================
st.markdown("---")
st.subheader("📌 공통사항 및 내화인증 기준")

footer_html = """
<style>
    .footer-table { width: 100%; border-collapse: collapse; color: white; font-size: 13px; text-align: center; }
    .footer-table th { background-color: #333; color: #D4AF37; border: 1px solid #555; padding: 8px; }
    .footer-table td { background-color: #1A1A1A; border: 1px solid #444; padding: 8px; }
    .warning { color: #FF6B6B; font-weight: bold; }
</style>

<div style="display: flex; gap: 20px; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 300px;">
        <h4 style="color: #D4AF37;">📋 공통 추가 비용</h4>
        <table class="footer-table">
            <tr><th>항목</th><th>비용/내용</th></tr>
            <tr><td>보호필름</td><td>+300원 / m</td></tr>
            <tr><td>특이색상</td><td>+500원 / m (오렌지, 검정, 노랑 등)</td></tr>
            <tr><td>캐노피/행가</td><td>50T: 20,500원 / 75T: 21,900원</td></tr>
            <tr><td>인증단가</td><td>그 외 구간별(25T기준) 인증단가 -1,100원</td></tr>
        </table>
    </div>

    <div style="flex: 1; min-width: 300px;">
        <h4 style="color: #D4AF37;">🔥 내화 확인서 기준</h4>
        <table class="footer-table">
            <tr><th>타입</th><th>두께</th><th>밀도</th><th>성능</th><th>하지여부</th><th>비고</th></tr>
            <tr><td rowspan="2">벽체</td><td>125T~</td><td>48K~</td><td>1.0시간</td><td>무하지</td><td>발포패드</td></tr>
            <tr><td>150T~</td><td>48K~</td><td>1.5시간</td><td>-</td><td>-</td></tr>
            <tr><td rowspan="3">외벽</td><td>100T~</td><td>48K~</td><td>0.5시간</td><td>하지1700↓</td><td>발포패드</td></tr>
            <tr><td>125T~</td><td>48K~</td><td>1.0시간</td><td>무하지</td><td>-</td></tr>
            <tr><td>150T~</td><td>48K~</td><td>1.0시간</td><td>-</td><td>발포패드</td></tr>
            <tr><td>지붕</td><td>184T~</td><td>48K~</td><td>0.5시간</td><td>하지1200↓</td><td>발포패드</td></tr>
        </table>
    </div>
</div>
"""
components.html(footer_html, height=400)
