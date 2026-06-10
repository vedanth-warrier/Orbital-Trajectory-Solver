import streamlit as st

# 1. Configure the Main Page properties, title, icon, and wide-mode layout
st.set_page_config(
    page_title="Flight Dynamics & Telemetry Suite",
    page_icon="🚀",
    layout="wide"
)

# 2. Premium Style Injection using CSS
# Injects custom typography, backgrounds, button effects, glassmorphic cards, and hides the default sidebar
st.markdown("""
<style>
/* Import the Outfit font family from Google Fonts for a modern look */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global Font override targeting markdown elements, html, and body */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* Custom header font-weight override for consistent typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}

/* Container class for the main landing page header and radial background glow */
.title-container {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
    background: radial-gradient(circle at center, rgba(255, 75, 75, 0.06) 0%, rgba(0, 0, 0, 0) 70%);
    border-radius: 24px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 75, 75, 0.12);
}

/* Glowing text title with a red-orange gradient fill */
.gradient-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #FF4B4B, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.8rem;
    letter-spacing: -1px;
}

/* Subtitle description text styles */
.subtitle-text {
    font-size: 1.35rem;
    color: #A0AEC0;
    max-width: 800px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Force Streamlit page link blocks to span full card width */
div[data-testid="stPageLink"] {
    width: 100%;
}

/* Design the custom button styling for native Streamlit page links */
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

/* Add vibrant gradient hover effects and lifting animations to page links */
div[data-testid="stPageLink"] a:hover {
    background: linear-gradient(135deg, #FF4B4B 0%, #FF7E5F 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 8px 24px rgba(255, 75, 75, 0.35) !important;
    transform: translateY(-2px) !important;
    color: #FFFFFF !important;
}

/* Frosted glass container card styling for module descriptions */
.hero-card {
    background: rgba(26, 32, 44, 0.4);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    margin-bottom: 1rem;
}

/* Hover effect for glassmorphic cards to lift up and highlight border */
.hero-card:hover {
    transform: translateY(-6px);
    border-color: rgba(255, 75, 75, 0.35);
    box-shadow: 0 12px 30px rgba(255, 75, 75, 0.08);
    background: rgba(26, 32, 44, 0.6);
}

/* Title header text inside card blocks */
.card-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

/* Description paragraph text inside card blocks */
.card-desc {
    color: #CBD5E0;
    font-size: 1.05rem;
    line-height: 1.7;
    margin-bottom: 2rem;
}

/* Footer layout styles */
.footer-text {
    text-align: center;
    color: #718096;
    font-size: 0.95rem;
    margin-top: 4rem;
}

/* Disable and hide the default Streamlit sidebar container completely */
[data-testid="stSidebar"] {
    display: none !important;
}

/* Disable and hide the collapsed sidebar indicator arrow toggle */
[data-testid="collapsedControl"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Build the Landing Interface Header HTML Elements
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

# 4. Create Explicit Page Redirections and Module Cards Layout using Columns
col1, col2 = st.columns(2, gap="large")

# Left Column: Kinematic Initial Value Problem (IVP) Simulation Module
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
    # Redirect button to navigate to the IVP simulator script
    st.page_link("pages/Forward_Trajectory_Simulator.py", label="Open Trajectory Simulator", icon="☄️")

# Right Column: Orbital Boundary Value Problem (BVP) Solver Module
with col2:
    st.markdown("""
    <div class="hero-card">
        <div class="card-title">🎯 Orbital Insertion Solver (BVP)</div>
        <div class="card-desc">
            Mathematically solve for circular orbit insertion parameters. 
            Uses a multi-variable boundary value solver (3 degrees of freedom) to optimise ascent fuel allocation, 
            liftoff thrust-to-weight ratios, and pitch angles, automatically satisfying final altitude and velocity boundary conditions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Redirect button to navigate to the BVP solver script
    st.page_link("pages/Orbital_Insertion_Solver.py", label="Open Insertion Solver", icon="🎯")

# 5. Render Footer Information
st.markdown("""
<div class="footer-text">
    Precision Aerospace Flight Mechanics Workbench • Powered by SciPy & Streamlit
</div>
""", unsafe_allow_html=True)