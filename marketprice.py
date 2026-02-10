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
# [사이드바] Gap 설정
# ==========================================
with st.sidebar:
    st.header("⚙️ 인상폭(Gap) 설정")
    st.info("두께 단계별 인상 금액")
    
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
# [공통 함수] 기준가 역산 로직
# ==========================================
def calculate_base_price_from_target(target_price, target_thick, thick_list, gap_price):
    """
    사용자가 입력한 두께(target_thick)와 가격(target_price)을 통해
    50T(Index 0)의 기준가를 역산해내는 함수
    """
    try:
        idx = thick_list.index(target_thick) # 선택한 두께가 몇 번째인지 확인
        # 공식: 50T가격 = 입력가격 - (순서 * 갭)
        base_price = target_price - (idx * gap_price)
        return base_price
    except ValueError:
        return target_price # 에러 시 그대로 반환

# ==========================================
# [공통 함수] HTML 테이블 생성
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
    st.subheader("EPS 기준 단가 설정")
    
    # 1) 기준 두께와 가격 입력 (핵심 기능)
    col_sel, col_inp = st.columns([1, 2])
    thicks_eps = [50, 75, 100, 125, 150, 155, 175, 200, 225, 250, 260]
    
    with col_sel:
        target_t_eps = st.selectbox("기준 두께 선택", thicks_eps, index=0) # 기본 50T
    with col_inp:
        target_p_eps = st.number_input(f"EPS 벽체 {target_t_eps}T 단가 입력", value=14000, step=100)

    # 2) 50T 역산 (핵심 로직)
    base_eps = calculate_base_price_from_target(target_p_eps, target_t_eps, thicks_eps, gap_eps_gen)
    
    if target_t_eps != 50:
        st.caption(f"💡 {target_t_eps}T가 {target_p_eps:,}원일 때, 50T 원가는 {base_eps:,}원으로 자동 계산됨")

    # 3) 품목별 차액 설정
    with st.expander("🔧 품목별 추가금 설정 (벽체 대비)", expanded=False):
        c1, c2, c3 = st.columns(3)
        diff_eps_ext = c1.number_input("외벽체 추가금", value=2400)
        diff_eps_roof = c2.number_input("지붕 추가금", value=2900)
        diff_eps_zinc = c3.number_input("징크 추가금", value=4500)
        c4, c5 = st.columns(2)
        diff_eps_line = c4.number_input("라인메탈 추가금", value=14700)
        diff_eps_jung = c5.number_input("정메탈 추가금", value=24300)

    # 4) 출력
    gaps_eps = {'gen': gap_eps_gen, 'nan': gap_eps_nan, 'cert': gap_eps_cert}
    
    html_content = style_block
    html_content += make_html_table("1. EPS 벽체", {'gen': base_eps, 'nan': base_eps+1400, 'cert': base_eps+8800}, thicks_eps, gaps_eps)
    html_content += make_html_table("2. EPS 외벽체", {'gen': base_eps+diff_eps_ext, 'nan': base_eps+diff_eps_ext+1400, 'cert': base_eps+diff_eps_ext+8800}, thicks_eps, gaps_eps)
    html_content += make_html_table("3. EPS 지붕", {'gen': base_eps+diff_eps_roof, 'nan': base_eps+diff_eps_roof+1400, 'cert': base_eps+diff_eps_roof+8800}, thicks_eps, gaps_eps)
    html_content += make_html_table("4. EPS 징크", {'gen': base_eps+diff_eps_zinc, 'nan': base_eps+diff_eps_zinc+1400, 'cert': base_eps+diff_eps_zinc+8800}, thicks_eps, gaps_eps)
    html_content += make_html_table("5. EPS 라인메탈", {'gen': base_eps+diff_eps_line, 'nan': base_eps+diff_eps_line+1400, 'cert': base_eps+diff_eps_line+8800}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)
    html_content += make_html_table("6. EPS 정메탈", {'gen': base_eps+diff_eps_jung, 'nan': base_eps+diff_eps_jung+1400, 'cert': base_eps+diff_eps_jung+8800}, [100, 125, 150, 175, 200, 225, 250], gaps_eps)

    components.html(html_content, height=2000, scrolling=True)


# --- 2. GW 탭 ---
with tab_gw:
    st.subheader("그라스울 기준 단가 설정")
    
    col_sel, col_inp = st.columns([1, 2])
    thicks_gw = [50, 75, 100, 125, 138, 150, 184, 200, 220, 250]
    
    with col_sel:
        target_t_gw = st.selectbox("기준 두께 선택 (GW)", thicks_gw, index=0)
    with col_inp:
        # 기본값 16,300 (지붕 220T 35500원 역산값 - 벽체 기준 추정)
        target_p_gw = st.number_input(f"GW 벽체 {target_t_gw}T 단가 입력", value=13800, step=100)

    base_gw = calculate_base_price_from_target(target_p_gw, target_t_gw, thicks_gw, gap_gw_48)

    if target_t_gw != 50:
        st.caption(f"💡 {target_t_gw}T가 {target_p_gw:,}원일 때, 50T 원가는 {base_gw:,}원으로 자동 계산됨")

    with st.expander("🔧 품목별 추가금 설정 (벽체 대비)", expanded=False):
        c1, c2, c3 = st.columns(3)
        diff_gw_ext = c1.number_input("GW 외벽체 추가금", value=2500)
        diff_gw_roof = c2.number_input("GW 지붕 추가금", value=2500)
        diff_gw_zinc = c3.number_input("GW 징크 추가금", value=4900)
        c4, c5 = st.columns(2)
        diff_gw_line = c4.number_input("GW 라인메탈 추가금", value=6300)
        diff_gw_jung = c5.number_input("GW 정메탈 추가금", value=15100)

    gaps_gw = {'48': gap_gw_48, '64': gap_gw_64}
    
    html_content = style_block
    html_content += make_html_table("1. GW 벽체", {'48': base_gw, '64': base_gw+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("2. GW 외벽체", {'48': base_gw+diff_gw_ext, '64': base_gw+diff_gw_ext+2000}, thicks_gw, gaps_gw, "GW")
    html_content += make_html_table("3. GW 지붕", {'48': base_gw+diff_gw_roof, '64': base_gw+diff
