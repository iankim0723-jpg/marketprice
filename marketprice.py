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
    /* Expander 헤더 스타일 */
    .streamlit-expanderHeader { background-color: #222 !important; color: #D4AF37 !important; font-weight: bold; border: 1px solid #444; }
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
        # 1. EPS 계산
        if material_type == "EPS":
            p_gen05 = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_gen35 = base_price_dict.get('gen35', p_gen05 - 4600)
            p_nan05 = base_price_dict['nan'] + (i * gap_dict['nan'])
            p_nan35 = p_nan05 - 1400
            
            if t < 75: p_cert = "-"
            else: p_cert = f"{base_price_dict['cert'] + ((i-1) * gap_dict['cert']):,}"

            cols = f"<td>{p_gen35:,}</td> <td>{p_gen05:,}</td> <td>{p_nan35:,}</td> <td>{p_nan05:,}</td> <td>{p_cert}</td>"
            
        # 2. GW 계산
        elif material_type == "GW":
            p_48 = base_price_dict['48'] + (i * gap_dict['48'])
            p_64 = base_price_dict['64'] + (i * gap_dict['64'])
            if t >= 125:
                f30 = f"{p_48 + 5000:,}"
                f60_48 = f"{p_48 + 6000:,}"
                f60_64 = f"{p_64 + 6000:,}"
            else: f30 = f60_48 = f60_64 = "-"
            cols = f"<td>{p_48:,}</td> <td>{p_64:,}</td> <td>{f30}</td> <td>{f60_48}</td> <td>{f60_64}</td>"

        # 3. URE 계산
        elif material_type == "URE":
            p_gen = base_price_dict['gen'] + (i * gap_dict['gen'])
            p_cert = base_price_dict['cert'] + (i * gap_dict['cert'])
            cols = f"<td>{p_gen:,}</td> <td>{p_cert:,}</td>"

        rows += f"<tr><td>{t}T</td>{cols}</tr>"

    # 헤더 설정
    header = ""
    if material_type == "EPS":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">일반 (EPS)</th><th colspan="2">난연 (EPS)</th><th>인증</th></tr><tr class="sub-header"><th>0.35T</th><th>0.5T</th><th>0.35T</th><th>0.5T</th><th>0.5T</th></tr>"""
    elif material_type == "GW":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">그라스울 (불연)</th><th colspan="3">그라스울 (내화)</th></tr><tr class="sub-header"><th>48K</th><th>64K</th><th>48K(30분)</th><th>48K(60분)</th><th>64K(60분)</th></tr>"""
    elif material_type == "URE":
        header = """<tr><th rowspan="2">두께</th><th colspan="2">우레탄</th></tr><tr class="sub-header"><th>일반 (0.5T)</th><th>인증 (0.5T)</th></tr>"""

    return f"""<div style="margin-bottom: 40px;"><h3 style="color: #D4AF37; margin-bottom: 5px;">{title}</h3><table><thead>{header}</thead><tbody>{rows}</tbody></table></div>"""


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
    with st.expander("💰 EPS 기준 단가 설정 (접기/펼치기)", expanded=True):
        st.info("각 품목의 [50T 일반 0.5T 기준가]를 입력하세요.")
        c1, c2, c3 = st.columns(3)
        with c1: p_wall = st.number_input("EPS 벽체 50T", value=14
