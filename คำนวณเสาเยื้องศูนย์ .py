"""
Shallow Foundation Bearing Capacity Calculator
Using Terzaghi's General Shear Failure Formula
Deploy: streamlit run shallow_foundation_terzaghi.py
"""

import streamlit as st
import math
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Terzaghi Bearing Capacity",
    page_icon="🏗️",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  { font-size:1.8rem; font-weight:600; color:#0C447C; }
    .sub-title   { font-size:0.9rem; color:#6b7280; margin-top:-0.3rem; }
    .result-box  { background:#EAF3DE; border-left:4px solid #3B6D11;
                   padding:1rem 1.2rem; border-radius:8px; margin-top:0.5rem; }
    .result-qult { font-size:2rem; font-weight:700; color:#0C447C; }
    .result-qall { font-size:2rem; font-weight:700; color:#3B6D11; }
    .warn-box    { background:#FAEEDA; border-left:4px solid #854F0B;
                   padding:0.8rem 1rem; border-radius:8px; }
    .factor-card { background:#F1EFE8; border-radius:8px;
                   padding:0.6rem 0.8rem; text-align:center; }
    hr.section   { border:none; border-top:1px solid #D3D1C7; margin:1.2rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Terzaghi bearing capacity factors ────────────────────────────────────────
def terzaghi_factors(phi_deg: float) -> tuple[float, float, float]:
    """
    Compute Nc, Nq, Nγ using Terzaghi's original formulation.
    For φ = 0: Nc = 5.71, Nq = 1.0, Nγ = 0.0
    """
    if phi_deg == 0:
        return 5.71, 1.0, 0.0
    phi = math.radians(phi_deg)
    Nq = math.exp(math.pi * math.tan(phi)) * math.tan(math.pi / 4 + phi / 2) ** 2
    Nc = (Nq - 1) / math.tan(phi)
    Ng = 2 * (Nq + 1) * math.tan(phi)          # Meyerhof approximation used with Terzaghi
    return Nc, Nq, Ng


# ── Bearing capacity calculation ──────────────────────────────────────────────
def calculate_bearing_capacity(
    B: float, L: float, Df: float,
    c: float, phi: float, gamma: float, FS: float
) -> dict:
    """
    Returns q_ult and q_all (kPa) plus intermediate values.
    Foundation type is detected automatically:
      • Square  : B/L ≥ 0.95
      • Strip   : B/L < 0.15
      • Rectangle: otherwise (shape factors applied)
    """
    Nc, Nq, Ng = terzaghi_factors(phi)
    ratio = B / L

    if ratio >= 0.95:
        foundation_type = "Square"
        q_ult = 1.3 * c * Nc + gamma * Df * Nq + 0.4 * gamma * B * Ng
        sc, sq, sg = 1.3, 1.0, 0.4   # embedded in formula above — shown for reference
    elif ratio < 0.15:
        foundation_type = "Strip (continuous)"
        q_ult = c * Nc + gamma * Df * Nq + 0.5 * gamma * B * Ng
        sc = sq = sg = 1.0
    else:
        foundation_type = "Rectangular"
        sc = 1 + 0.2 * (B / L)
        sq = 1 + 0.1 * (B / L)
        sg = 1 - 0.1 * (B / L)
        q_ult = c * Nc * sc + gamma * Df * Nq * sq + 0.5 * gamma * B * Ng * sg

    q_all = q_ult / FS
    overburden = gamma * Df

    return {
        "foundation_type": foundation_type,
        "Nc": Nc, "Nq": Nq, "Ng": Ng,
        "sc": sc if foundation_type == "Rectangular" else None,
        "sq": sq if foundation_type == "Rectangular" else None,
        "sg": sg if foundation_type == "Rectangular" else None,
        "overburden_kPa": overburden,
        "q_ult_kPa": q_ult,
        "q_all_kPa": q_all,
    }


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🏗️ Terzaghi Bearing Capacity</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Shallow Foundation — General Shear Failure</p>', unsafe_allow_html=True)

st.markdown("---")

# Input columns
col_geo, col_soil = st.columns(2)

with col_geo:
    st.subheader("Foundation Geometry")
    B  = st.number_input("B — width (m)",   min_value=0.1, value=1.5, step=0.1, format="%.2f")
    L  = st.number_input("L — length (m)",  min_value=0.1, value=2.0, step=0.1, format="%.2f")
    Df = st.number_input("Dₓ — depth (m)",  min_value=0.1, value=1.0, step=0.1, format="%.2f")
    FS = st.number_input("FS — factor of safety", min_value=1.0, value=3.0, step=0.5, format="%.1f")

with col_soil:
    st.subheader("Soil Parameters")
    c     = st.number_input("c — cohesion (kPa)",       min_value=0.0,  value=10.0, step=1.0,  format="%.1f")
    phi   = st.number_input("φ — friction angle (°)",   min_value=0.0,  max_value=45.0, value=30.0, step=1.0, format="%.1f")
    gamma = st.number_input("γ — unit weight (kN/m³)",  min_value=1.0,  value=18.0, step=0.5,  format="%.1f")

st.markdown("---")

# Buttons
btn_col1, btn_col2, _ = st.columns([1, 1, 3])
calc_clicked  = btn_col1.button("⚡ Calculate", use_container_width=True, type="primary")
clear_clicked = btn_col2.button("🗑️ Clear",     use_container_width=True)

if clear_clicked:
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if calc_clicked:
    if phi > 45 or phi < 0:
        st.error("Friction angle φ must be between 0° and 45°.")
    elif B <= 0 or L <= 0 or Df <= 0:
        st.error("All dimensions must be greater than zero.")
    elif FS < 1:
        st.error("Factor of safety must be ≥ 1.")
    else:
        res = calculate_bearing_capacity(B, L, Df, c, phi, gamma, FS)

        st.subheader("Results")

        # Main metrics
        m1, m2 = st.columns(2)
        m1.metric(
            label="q_ult — Ultimate Bearing Capacity",
            value=f"{res['q_ult_kPa']:,.2f} kPa",
        )
        m2.metric(
            label="q_all — Allowable Bearing Capacity",
            value=f"{res['q_all_kPa']:,.2f} kPa",
        )

        if res["q_all_kPa"] < 50:
            st.markdown(
                '<div class="warn-box">⚠️ Allowable bearing capacity is low. '
                'Review soil parameters or increase foundation dimensions.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Bearing capacity factors
        st.subheader("Bearing Capacity Factors (Terzaghi)")
        f1, f2, f3 = st.columns(3)
        f1.metric("NꜲ", f"{res['Nc']:.3f}")
        f2.metric("Nᴬ", f"{res['Nq']:.3f}")
        f3.metric("Nᵧ", f"{res['Ng']:.3f}")

        # Foundation type & shape factors
        st.info(f"**Foundation type detected:** {res['foundation_type']}")
        if res["sc"] is not None:
            st.caption(
                f"Shape factors applied — "
                f"sᶜ = {res['sc']:.3f} | sᴬ = {res['sq']:.3f} | sᵧ = {res['sg']:.3f}"
            )

        st.markdown("---")

        # Summary table
        st.subheader("Summary")
        summary = pd.DataFrame({
            "Parameter": [
                "B (m)", "L (m)", "Dₓ (m)",
                "c (kPa)", "φ (°)", "γ (kN/m³)",
                "FS", "Foundation type",
                "Nᶜ", "Nᴬ", "Nᵧ",
                "Overburden q₀ (kPa)",
                "q_ult (kPa)", "q_all (kPa)",
            ],
            "Value": [
                B, L, Df,
                c, phi, gamma,
                FS, res["foundation_type"],
                f"{res['Nc']:.3f}", f"{res['Nq']:.3f}", f"{res['Ng']:.3f}",
                f"{res['overburden_kPa']:.2f}",
                f"{res['q_ult_kPa']:.2f}", f"{res['q_all_kPa']:.2f}",
            ],
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)

        # Formula reference
        with st.expander("📐 Formula reference"):
            st.markdown(r"""
**Terzaghi General Shear Failure:**

| Foundation | q_ult formula |
|---|---|
| **Strip** | $c N_c + \gamma D_f N_q + 0.5 \, \gamma B N_\gamma$ |
| **Square** | $1.3 \, c N_c + \gamma D_f N_q + 0.4 \, \gamma B N_\gamma$ |
| **Rectangle** | $c N_c s_c + \gamma D_f N_q s_q + 0.5 \, \gamma B N_\gamma s_\gamma$ |

**Bearing capacity factors:**

$$N_q = e^{\pi \tan\phi} \cdot \tan^2\!\!\left(45° + \frac{\phi}{2}\right)$$

$$N_c = \frac{N_q - 1}{\tan\phi} \quad (\phi > 0°) \quad | \quad N_c = 5.71 \; (\phi = 0°)$$

$$N_\gamma = 2(N_q + 1)\tan\phi$$

**Rectangular shape factors (Meyerhof):**
$s_c = 1 + 0.2(B/L)$, $s_q = 1 + 0.1(B/L)$, $s_\gamma = 1 - 0.1(B/L)$

**Allowable capacity:**
$$q_{all} = \frac{q_{ult}}{FS}$$
            """)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Reference: Terzaghi (1943) | For educational and preliminary design use only.")
