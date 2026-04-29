"""
Terzaghi Bearing Capacity Calculator — Streamlit Version
Deploy: streamlit run terzaghi_streamlit.py
No extra packages needed beyond: pip install streamlit pandas
"""

import streamlit as st
import math
import pandas as pd
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Terzaghi Bearing Capacity",
    page_icon="🏗️",
    layout="wide",
)

# ══════════════════════════════════════════════════════════════
#  CUSTOM CSS  — Engineering Blueprint Dark Theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: #0F1923;
    color: #C8DCF0;
}
.stApp { background: #0F1923; }
.block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1200px; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Banner ── */
.banner {
    background: linear-gradient(135deg, #0D1B2A 0%, #162230 100%);
    border: 1px solid #1E3A5F;
    border-left: 4px solid #00C2FF;
    border-radius: 8px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
}
.banner-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.6rem; font-weight: 700;
    color: #00C2FF; letter-spacing: 2px;
    margin: 0;
}
.banner-sub {
    font-size: 0.8rem; color: #4A7EA5;
    margin-top: 2px; letter-spacing: 1px;
}
.banner-time {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem; color: #2A5070;
}

/* ── Section headers ── */
.sec-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem; color: #00C2FF;
    letter-spacing: 3px;
    border-bottom: 1px solid #1E3A5F;
    padding-bottom: 6px; margin: 1.5rem 0 1rem 0;
}

/* ── Panel cards ── */
.panel {
    background: #162230;
    border: 1px solid #1E3A5F;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem; color: #4A7EA5;
    letter-spacing: 2px; margin-bottom: 1rem;
    border-bottom: 1px solid #1E3A5F; padding-bottom: 6px;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin: 1rem 0; }
.metric-card {
    flex: 1;
    background: #0D1B2A;
    border: 1px solid #1E3A5F;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.blue::before  { background: #00C2FF; }
.metric-card.green::before { background: #00E5A0; }
.metric-card.amber::before { background: #FFB340; }

.metric-label {
    font-size: 0.72rem; color: #4A7EA5;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem; font-weight: 700; line-height: 1;
}
.metric-value.blue  { color: #00C2FF; }
.metric-value.green { color: #00E5A0; }
.metric-value.amber { color: #FFB340; }
.metric-unit {
    font-size: 0.75rem; color: #2A5070;
    margin-top: 4px;
}

/* ── Status bar ── */
.status-ok    { background:#0A2010; border-left:4px solid #00C87A; color:#00C87A;
                font-family:'Share Tech Mono',monospace; font-size:0.8rem;
                padding:0.6rem 1rem; border-radius:6px; margin:1rem 0; }
.status-error { background:#200A0A; border-left:4px solid #FF5A5A; color:#FF5A5A;
                font-family:'Share Tech Mono',monospace; font-size:0.8rem;
                padding:0.6rem 1rem; border-radius:6px; margin:1rem 0; }
.status-warn  { background:#201200; border-left:4px solid #FFB340; color:#FFB340;
                font-family:'Share Tech Mono',monospace; font-size:0.8rem;
                padding:0.6rem 1rem; border-radius:6px; margin:1rem 0; }

/* ── Input labels ── */
label { color: #7FA8C9 !important; font-size: 0.85rem !important; }
.stNumberInput input {
    background: #0D1B2A !important;
    border: 1px solid #2A4A6B !important;
    border-radius: 6px !important;
    color: #00C2FF !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1rem !important;
}
.stNumberInput input:focus {
    border-color: #00C2FF !important;
    box-shadow: 0 0 0 2px rgba(0,194,255,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #0D2A4A !important;
    color: #00C2FF !important;
    border: 1px solid #1E5A8A !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-weight: 600 !important; letter-spacing: 1px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #1A4A7A !important;
    border-color: #00C2FF !important;
    transform: translateY(-1px) !important;
}

/* ── Dataframe / Table ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
.stDataFrame table {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    border-collapse: collapse;
}
.stDataFrame thead tr th {
    background: #1A3A5C !important;
    color: #00C2FF !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    padding: 10px 14px !important;
}
.stDataFrame tbody tr:nth-child(even) td { background: #162230 !important; }
.stDataFrame tbody tr:nth-child(odd)  td { background: #1C2B3A !important; }
.stDataFrame tbody tr td { color: #C8DCF0 !important; padding: 8px 14px !important; }

/* ── Formula box ── */
.formula-box {
    background: #0D1B2A;
    border: 1px solid #1E3A5F;
    border-radius: 8px;
    padding: 1.2rem 1.6rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.82rem; color: #4A7EA5;
    line-height: 1.9;
}
.formula-box span { color: #00C2FF; }
.formula-box em   { color: #00E5A0; font-style: normal; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  ENGINEERING CALCULATIONS
# ══════════════════════════════════════════════════════════════
def terzaghi_factors(phi_deg):
    if phi_deg == 0:
        return 5.71, 1.0, 0.0
    phi = math.radians(phi_deg)
    Nq = math.exp(math.pi * math.tan(phi)) * math.tan(math.pi/4 + phi/2)**2
    Nc = (Nq - 1) / math.tan(phi)
    Ng = 2 * (Nq + 1) * math.tan(phi)
    return Nc, Nq, Ng


def calculate(B, L, Df, c, phi, gamma, FS):
    Nc, Nq, Ng = terzaghi_factors(phi)
    ratio = B / L
    sc = sq = sg = None

    if ratio >= 0.95:
        ftype = "Square"
        q_ult = 1.3*c*Nc + gamma*Df*Nq + 0.4*gamma*B*Ng
    elif ratio < 0.15:
        ftype = "Strip"
        q_ult = c*Nc + gamma*Df*Nq + 0.5*gamma*B*Ng
    else:
        ftype = "Rectangular"
        sc = 1 + 0.2*(B/L)
        sq = 1 + 0.1*(B/L)
        sg = 1 - 0.1*(B/L)
        q_ult = c*Nc*sc + gamma*Df*Nq*sq + 0.5*gamma*B*Ng*sg

    q_all = q_ult / FS
    q0    = gamma * Df
    cNc_term   = c * Nc * (sc if sc else 1.0)
    qNq_term   = q0 * Nq * (sq if sq else 1.0)
    gBNg_term  = 0.5 * gamma * B * Ng * (sg if sg else 1.0)

    return dict(
        ftype=ftype, Nc=Nc, Nq=Nq, Ng=Ng,
        sc=sc, sq=sq, sg=sg, q0=q0,
        cNc=cNc_term, qNq=qNq_term, gBNg=gBNg_term,
        q_ult=q_ult, q_all=q_all
    )


def build_table(v, r):
    rows = []

    def add(label, symbol, value, unit, note, section=False):
        rows.append({
            "Parameter": label,
            "Symbol": symbol,
            "Value": value,
            "Unit": unit,
            "Note": note,
        })

    # ── Inputs ──
    add("━━ INPUT PARAMETERS ━━", "", "", "", "")
    add("Width",               "B",      f"{v['B']:.3f}",      "m",       "Foundation width")
    add("Length",              "L",      f"{v['L']:.3f}",      "m",       "Foundation length")
    add("Depth of foundation", "Df",     f"{v['Df']:.3f}",     "m",       "Embedment depth")
    add("Cohesion",            "c",      f"{v['c']:.3f}",      "kPa",     "Soil cohesion")
    add("Friction angle",      "φ",      f"{v['phi']:.3f}",    "°",       "Internal friction angle")
    add("Unit weight",         "γ",      f"{v['gamma']:.3f}",  "kN/m³",   "Bulk unit weight")
    add("Factor of safety",    "FS",     f"{v['FS']:.2f}",     "—",       "Applied to q_ult")
    add("B/L ratio",           "B/L",    f"{v['B']/v['L']:.4f}","—",     "Shape indicator")
    add("Foundation type",     "—",      r['ftype'],           "—",       "Auto-detected by B/L")

    # ── Bearing factors ──
    add("━━ BEARING CAPACITY FACTORS ━━", "", "", "", "Terzaghi (1943)")
    add("Bearing factor Nc",   "Nc",     f"{r['Nc']:.4f}",    "—",       "Nc = (Nq−1)/tanφ")
    add("Bearing factor Nq",   "Nq",     f"{r['Nq']:.4f}",    "—",       "Nq = exp(π·tanφ)·tan²(45+φ/2)")
    add("Bearing factor Nγ",   "Nγ",     f"{r['Ng']:.4f}",    "—",       "Nγ = 2(Nq+1)·tanφ")

    # ── Shape factors ──
    if r["sc"] is not None:
        add("━━ SHAPE FACTORS (Rectangular) ━━", "", "", "", "Meyerhof")
        add("Shape factor sc",  "sc",    f"{r['sc']:.4f}",    "—",       "sc = 1 + 0.2(B/L)")
        add("Shape factor sq",  "sq",    f"{r['sq']:.4f}",    "—",       "sq = 1 + 0.1(B/L)")
        add("Shape factor sγ",  "sγ",    f"{r['sg']:.4f}",    "—",       "sγ = 1 − 0.1(B/L)")

    # ── Stress terms ──
    add("━━ STRESS CONTRIBUTION TERMS ━━", "", "", "", "")
    add("Overburden pressure",  "q₀",    f"{r['q0']:.4f}",    "kPa",     "γ × Df")
    add("Cohesion term",        "c·Nc",  f"{r['cNc']:.4f}",   "kPa",     "Cohesion contribution")
    add("Surcharge term",       "γDf·Nq",f"{r['qNq']:.4f}",   "kPa",     "Surcharge contribution")
    add("Self-weight term",     "0.5γBNγ",f"{r['gBNg']:.4f}", "kPa",     "Self-weight contribution")
    add("Sum check",            "Σ",     f"{r['cNc']+r['qNq']+r['gBNg']:.4f}","kPa","= q_ult")

    # ── Results ──
    add("━━ RESULTS ━━", "", "", "", "")
    add("Ultimate bearing capacity",   "q_ult", f"{r['q_ult']:.4f}", "kPa", "General shear failure")
    add("Allowable bearing capacity",  "q_all", f"{r['q_all']:.4f}", "kPa", "q_ult / FS")

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════
#  UI LAYOUT
# ══════════════════════════════════════════════════════════════

# ── Banner ──
st.markdown(f"""
<div class="banner">
  <div>
    <p class="banner-title">⬛ TERZAGHI BEARING CAPACITY</p>
    <p class="banner-sub">SHALLOW FOUNDATION  //  GENERAL SHEAR FAILURE  //  BEARING CAPACITY CALCULATOR</p>
  </div>
  <div class="banner-time">{datetime.now().strftime("%Y-%m-%d  %H:%M")}</div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ──
st.markdown('<div class="sec-header">▶ INPUT PARAMETERS</div>', unsafe_allow_html=True)

col_geo, col_soil = st.columns([1, 1], gap="large")

with col_geo:
    st.markdown('<div class="panel"><div class="panel-title">// FOUNDATION GEOMETRY</div>', unsafe_allow_html=True)
    B  = st.number_input("B  —  Width (m)",           min_value=0.01, value=1.50, step=0.1,  format="%.2f")
    L  = st.number_input("L  —  Length (m)",          min_value=0.01, value=2.00, step=0.1,  format="%.2f")
    Df = st.number_input("Df  —  Depth (m)",          min_value=0.01, value=1.00, step=0.1,  format="%.2f")
    FS = st.number_input("FS  —  Factor of Safety",   min_value=1.00, value=3.00, step=0.5,  format="%.2f")
    st.markdown('</div>', unsafe_allow_html=True)

with col_soil:
    st.markdown('<div class="panel"><div class="panel-title">// SOIL PARAMETERS</div>', unsafe_allow_html=True)
    c     = st.number_input("c  —  Cohesion (kPa)",       min_value=0.0,  value=10.0, step=1.0,  format="%.2f")
    phi   = st.number_input("φ  —  Friction Angle (°)",   min_value=0.0,  max_value=45.0, value=30.0, step=1.0, format="%.1f")
    gamma = st.number_input("γ  —  Unit Weight (kN/m³)",  min_value=0.1,  value=18.0, step=0.5,  format="%.2f")
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Buttons ──
st.markdown("")
bc1, bc2, bc3, _ = st.columns([1.2, 1, 1.2, 3])
calc_btn   = bc1.button("⚡  CALCULATE",   use_container_width=True)
clear_btn  = bc2.button("✕  CLEAR",        use_container_width=True)

# ── Validate & Calculate ──
if "result" not in st.session_state:
    st.session_state.result = None

if clear_btn:
    st.session_state.result = None
    st.rerun()

if calc_btn:
    errors = []
    if B <= 0 or L <= 0 or Df <= 0:
        errors.append("B, L, Df must be > 0")
    if FS < 1:
        errors.append("FS must be ≥ 1")
    if not (0 <= phi <= 45):
        errors.append("φ must be 0 – 45°")
    if gamma <= 0:
        errors.append("γ must be > 0")

    if errors:
        st.markdown(f'<div class="status-error">⚠  {" | ".join(errors)}</div>',
                    unsafe_allow_html=True)
    else:
        v = dict(B=B, L=L, Df=Df, c=c, phi=phi, gamma=gamma, FS=FS)
        r = calculate(B, L, Df, c, phi, gamma, FS)
        st.session_state.result = (v, r)

# ── Results ──
if st.session_state.result:
    v, r = st.session_state.result

    st.markdown(
        f'<div class="status-ok">✔  [{r["ftype"]} Footing]  '
        f'q_ult = {r["q_ult"]:.2f} kPa  |  q_all = {r["q_all"]:.2f} kPa  |  '
        f'Nc = {r["Nc"]:.3f}  Nq = {r["Nq"]:.3f}  Nγ = {r["Ng"]:.3f}</div>',
        unsafe_allow_html=True
    )

    if r["q_all"] < 50:
        st.markdown(
            '<div class="status-warn">⚠  Low allowable capacity — review parameters or enlarge foundation.</div>',
            unsafe_allow_html=True
        )

    # ── Metric cards ──
    st.markdown('<div class="sec-header">▶ RESULTS</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card blue">
        <div class="metric-label">q_ult — Ultimate Bearing Capacity</div>
        <div class="metric-value blue">{r['q_ult']:.2f}</div>
        <div class="metric-unit">kPa</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">q_all — Allowable Bearing Capacity</div>
        <div class="metric-value green">{r['q_all']:.2f}</div>
        <div class="metric-unit">kPa</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Factor of Safety</div>
        <div class="metric-value amber">{v['FS']:.1f}</div>
        <div class="metric-unit">—</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">Foundation Type</div>
        <div class="metric-value blue" style="font-size:1.4rem;">{r['ftype']}</div>
        <div class="metric-unit">auto-detected</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bearing factors row ──
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card amber">
        <div class="metric-label">Bearing Factor Nc</div>
        <div class="metric-value amber" style="font-size:1.6rem;">{r['Nc']:.4f}</div>
        <div class="metric-unit">cohesion factor</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Bearing Factor Nq</div>
        <div class="metric-value amber" style="font-size:1.6rem;">{r['Nq']:.4f}</div>
        <div class="metric-unit">surcharge factor</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Bearing Factor Nγ</div>
        <div class="metric-value amber" style="font-size:1.6rem;">{r['Ng']:.4f}</div>
        <div class="metric-unit">self-weight factor</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">Overburden q₀</div>
        <div class="metric-value blue" style="font-size:1.6rem;">{r['q0']:.3f}</div>
        <div class="metric-unit">kPa = γ × Df</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Detailed table ──
    st.markdown('<div class="sec-header">▶ DETAILED CALCULATION TABLE</div>', unsafe_allow_html=True)
    df = build_table(v, r)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter",        width="large"),
            "Symbol":    st.column_config.TextColumn("Symbol",           width="small"),
            "Value":     st.column_config.TextColumn("Value",            width="medium"),
            "Unit":      st.column_config.TextColumn("Unit",             width="small"),
            "Note":      st.column_config.TextColumn("Note / Formula",   width="large"),
        }
    )

    # ── Export ──
    st.markdown("")
    csv_data = df.to_csv(index=False, encoding="utf-8")
    export_col, _ = st.columns([1, 3])
    export_col.download_button(
        label="↓  EXPORT CSV",
        data=csv_data,
        file_name=f"terzaghi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── Formula reference ──
    st.markdown('<div class="sec-header">▶ FORMULA REFERENCE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="formula-box">
      <span>Strip       :</span>  q_ult = c·Nc + γ·Df·Nq + 0.5·γ·B·Nγ<br>
      <span>Square      :</span>  q_ult = 1.3·c·Nc + γ·Df·Nq + 0.4·γ·B·Nγ<br>
      <span>Rectangular :</span>  q_ult = c·Nc·sc + γ·Df·Nq·sq + 0.5·γ·B·Nγ·sγ<br>
      <br>
      <em>Nq = exp(π·tanφ) · tan²(45° + φ/2)</em><br>
      <em>Nc = (Nq − 1) / tanφ     [φ=0 → Nc = 5.71]</em><br>
      <em>Nγ = 2(Nq + 1)·tanφ</em><br>
      <br>
      <span>Shape factors (Rectangular) :</span>
      sc = 1 + 0.2(B/L)   sq = 1 + 0.1(B/L)   sγ = 1 − 0.1(B/L)<br>
      <br>
      <em>q_all = q_ult / FS</em>
    </div>
    """, unsafe_allow_html=True)

else:
    # Placeholder when no result yet
    st.markdown("""
    <div style="text-align:center; padding:3rem; color:#2A5070;
                font-family:'Share Tech Mono',monospace; font-size:0.9rem;
                border:1px dashed #1E3A5F; border-radius:10px; margin-top:1rem;">
      ▶  กรอก Input Parameters แล้วกด CALCULATE เพื่อแสดงผล
    </div>
    """, unsafe_allow_html=True)
