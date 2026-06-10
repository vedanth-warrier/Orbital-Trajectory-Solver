import streamlit as st

st.set_page_config(
    page_title="Flight Dynamics & Telemetry Suite",
    page_icon="🚀",
    layout="wide"
)

# Premium Style Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global Font & Theme overrides */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}

/* Custom glowing titles */
.title-container {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
    background: radial-gradient(circle at center, rgba(255, 75, 75, 0.06) 0%, rgba(0, 0, 0, 0) 70%);
    border-radius: 24px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 75, 75, 0.12);
}

.gradient-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #FF4B4B, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.8rem;
    letter-spacing: -1px;
}

.subtitle-text {
    font-size: 1.35rem;
    color: #A0AEC0;
    max-width: 800px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Page Link buttons styling override */
div[data-testid="stPageLink"] {
    width: 100%;
}

div[data-testid="stPageLink"] a {
    background: linear-gradient(135deg, rgba(255, 75, 75, 0.08) 0%, rgba(255, 126, 95, 0.08) 100%) !important;
    border: 1px solid rgba(255, 75, 75, 0.25) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.8rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 0.5rem !important;
}

div[data-testid="stPageLink"] a:hover {
    background: linear-gradient(135deg, #FF4B4B 0%, #FF7E5F 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 8px 24px rgba(255, 75, 75, 0.35) !important;
    transform: translateY(-2px) !important;
    color: #FFFFFF !important;
}

/* Info Cards block styling */
.hero-card {
    background: rgba(26, 32, 44, 0.4);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    margin-bottom: 1rem;
}

.hero-card:hover {
    transform: translateY(-6px);
    border-color: rgba(255, 75, 75, 0.35);
    box-shadow: 0 12px 30px rgba(255, 75, 75, 0.08);
    background: rgba(26, 32, 44, 0.6);
}

.card-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.card-desc {
    color: #CBD5E0;
    font-size: 1.05rem;
    line-height: 1.7;
    margin-bottom: 2rem;
}

.footer-text {
    text-align: center;
    color: #718096;
    font-size: 0.95rem;
    margin-top: 4rem;
}
</style>
""", unsafe_allow_html=True)

# 2. Build the Landing Interface
st.markdown("""
<div class="title-container">
    <div class="gradient-title">🚀 Orbital Trajectory & Telemetry Suite</div>
    <div class="subtitle-text">
        An advanced flight dynamics workspace containing high-fidelity numerical integrators and solvers 
        for flight path simulations and boundary-conditioned circular orbit insertions.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# 3. Create Explicit Page Redirections
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="hero-card">
        <div class="card-title">☄️ Forward Trajectory Simulator (IVP)</div>
        <div class="card-desc">
            Simulate launch vehicle profiles using high-fidelity numerical integration. 
            Implements launch tower vertical ascent clearance logic, dynamic atmospheric density, 
            aerodynamic drag coefficients, and gravity turn profiles under known vehicle parameters.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/Forward_Trajectory_Simulator.py", label="Open Trajectory Simulator", icon="☄️")

with col2:
    st.markdown("""
    <div class="hero-card">
        <div class="card-title">🎯 Orbital Insertion Solver (BVP)</div>
        <div class="card-desc">
            Mathematically solve for circular orbit insertion parameters. 
            Uses a multi-variable boundary value solver (3 degrees of freedom) to optimize ascent fuel allocation, 
            liftoff thrust-to-weight ratios, and pitch angles, automatically satisfying final altitude and velocity boundary conditions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/Orbital_Insertion_Solver.py", label="Open Insertion Solver", icon="🎯")

st.markdown("""
<div class="footer-text">
    Precision Aerospace Flight Mechanics Workbench • Powered by SciPy & Streamlit
</div>
""", unsafe_allow_html=True)