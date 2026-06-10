# Import necessary computational and GUI libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import streamlit as st

# Configure the Streamlit page properties to wide-mode and set the browser title
st.set_page_config(layout='wide', page_title="Forward Trajectory Simulator")

# Premium Style Injection using CSS
# Applies custom typography, custom inputs, custom page links, and hides the default sidebar navigation
st.markdown("""
<style>
/* Import the Outfit font family from Google Fonts for a clean, technical look */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Apply global font-family styling to page elements */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* Format all header elements with a high font-weight */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}

/* CSS class for glowing headers with a vibrant orange-red linear gradient fill */
.page-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #FF4B4B, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.5px;
}

/* CSS class for subtitles and descriptions */
.page-subtitle {
    font-size: 1.15rem;
    color: #A0AEC0;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Style input widgets with custom background, borders, and rounding */
div[data-baseweb="input"] {
    background-color: #1E2530 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    transition: all 0.3s ease;
}
/* Focus indicator glowing effect for input widgets */
div[data-baseweb="input"]:focus-within {
    border-color: #FF4B4B !important;
    box-shadow: 0 0 0 1px #FF4B4B !important;
}

/* Sidebar / Control panel container overrides */
div[data-testid="stVerticalBlock"] > div:has(div[data-testid="element-container"]) {
    /* background: rgba(26, 32, 44, 0.2); */
}

/* Disable and hide the default Streamlit sidebar container completely */
[data-testid="stSidebar"] {
    display: none !important;
}
/* Disable and hide the collapsed sidebar indicator arrow toggle */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Back to Dashboard page link button styling */
div[data-testid="stPageLink"] a {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.85rem !important;
    color: #A0AEC0 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    text-decoration: none !important;
    transition: all 0.3s ease !important;
    display: inline-flex !important;
    width: auto !important;
    margin-bottom: 1.5rem !important;
}
/* Hover animation (glow border and slight leftward slide) for the back button */
div[data-testid="stPageLink"] a:hover {
    border-color: #FF4B4B !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 10px rgba(255, 75, 75, 0.15) !important;
    transform: translateX(-3px) !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Render Navigation and Headers
st.page_link("Orbital_Trajectory_Solver.py", label="Back to Dashboard", icon="🏠")
st.markdown('<div class="page-title">☄️ Forward Trajectory Simulator (IVP)</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Simulate rocket gravity-turn based flight path parameters in real time. Input your vehicle details to calculate and plot the 2D gravity turn profile, dynamic drag, and velocity updates.</div>', unsafe_allow_html=True)

# --- PHYSICAL CONSTANTS DEFINITION ---
G = 6.67430e-11  # Universal Gravitational Constant (m^3 kg^-1 s^-2)
M_e = 5.9722e24  # Earth Mass (kg)
R_e = 6.371e6   # Earth Mean Radius (meters)
p_0  = 1.225  # Sea-level atmospheric density (kg/m^3)
g_0 = 9.80665  # Standard acceleration due to gravity at Earth's surface (m/s^2)

# Function to calculate local gravity (m/s^2) as a function of radial distance h from Earth center
def g(h):
    return G * M_e / (h)**2

# --- ATMOSPHERIC DENSITY MODELLING ---
# Cache the data loading to optimise webpage load times
@st.cache_data
def load_atmosphere():
    # Read the altitude vs density reference data from CSV
    density = pd.read_csv('atm_density.csv')  
    altitudes = density['Altitude (m)'].values  
    densities = density['Density (kg/m^3)'].values  
    # Interpolate using log(density) for exponential accuracy across scale heights
    return sp.interpolate.interp1d(altitudes, np.log(densities), fill_value="extrapolate")

# Load and instantiate the interpolator
log_densities_interpolated = load_atmosphere()

# Function to evaluate atmospheric density (kg/m^3) at a given radial distance h
def p(h):
    # Above 1000 km altitude, atmospheric density is virtually zero
    if h-R_e > 1000000:
        return 0
    # Keep altitude boundary at sea level if coordinate goes underground
    if h-R_e < 0:
        h = R_e
    # Return exponentiated value from the log-density interpolator
    return np.exp(log_densities_interpolated(h-R_e))


# --- GUI WIDGET CONTROL INTERFACE ---
# Divide the interface into columns for input parameters and telemetry plots
col_inputs, col_plot = st.columns([1, 2])

# Render input forms in the left column
with col_inputs:
    st.subheader("Vehicle Parameters")
    m_d = st.number_input("Dry Mass (kg)", value=10000.0, step=500.0)
    m_f = st.number_input("Fuel Mass (kg)", value=100000.0, step=1000.0)
    A = st.number_input("Cross Sectional Area (m^2)", value=12.0, step=1.0)
    Cd = st.number_input("Drag Coeff", value=0.4, step=0.1)
    I_sp = st.number_input("I_sp (s)", value=400.0, step=10.0)
    T = st.number_input("Thrust (N)", value=3000000.0, step=50000.0)

    st.subheader("Initial & Environment Conditions")
    t_sim = st.number_input("Simulation Length (s)", value=3000.0, step=50.0)
    vert = st.number_input("Vertical Ascent Threshold (m)", value=15000.0, step=500.0)
    v_thetai = st.number_input("Initial Tangential Vel (m/s)", value=386.7, step=10.0)
    r_i = st.number_input("Starting Altitude (km)", value=0.0, step=100.0)*1000 + R_e


# --- INITIAL CONDITIONS SETUP ---
theta = 0  # Initial polar angle coordinate
v_ri = 0   # Initial velocity in radial direction is zero (at launch start or launchpad clearance)

# Create the initial state vector: [radial distance, polar angle, radial velocity, tangential velocity, mass]
state_i = np.array([r_i, theta, v_ri, v_thetai, m_d + m_f])


# --- DIFFERENTIAL EQUATIONS OF MOTION ---
# Mathematical descriptions:
# d/dt(v_theta) = T_theta/m - 1/2 * (p * C_d * A / m) * v * v_theta - v_r * v_theta / r
# d/dt(v_r) = T_r/m - 1/2 * (p * C_d * A / m) * v * v_r - g(r) + v_theta^2 / r
# d/dt(m) = -T / (I_sp * g_0) if fuel remains else 0
def vehicle_dynamics(t, state):
    r, theta, v_r, v_theta, m = state  # Unpack the 5-state vector
    v = np.sqrt(v_r**2 + v_theta**2)  # Compute total velocity magnitude

    # Active thrust is zero if vehicle is completely out of fuel (m <= m_d)
    current_T = T if m > m_d else 0.0
    
    # State derivatives for coordinates
    dt_r = v_r
    dt_theta = v_theta/r

    # Gravity Turn Logic:
    # Maintain vertical flight until radial clearance threshold is achieved (r - R_e < vert)
    if (v == 0) or (r - R_e < vert and v_r >=0):
        thrust_theta = 0
        thrust_r = current_T
    else:
        # Tilt and align thrust vector with the velocity vector (gravity turn)
        thrust_theta = current_T * v_theta/v
        thrust_r = current_T * v_r/v

    # Equations of motion under gravitational pull, aerodynamics (drag), and coordinate system accelerations
    dt_vtheta = thrust_theta/m - (1/2)*(p(r)*Cd*A/m)*v*v_theta - v_r*v_theta/r
    dt_vr = thrust_r/m - (1/2)*(p(r)*Cd*A/m)*v*v_r - g(r) + v_theta**2/(r)
    
    # Propellant mass depletion rate
    dt_m = -current_T/(I_sp*g_0)
    
    return np.array([dt_r, dt_theta, dt_vr, dt_vtheta, dt_m])

# Solver Event: Terminate integration if vehicle crashes back to Earth
def ground_impact(t, state):
    return state[0] - R_e
ground_impact.terminal = True
ground_impact.direction = -1


# --- NUMERICAL INTEGRATION RUN ---
# Solve the system of ordinary differential equations (Initial Value Problem)
solution = sp.integrate.solve_ivp(
    vehicle_dynamics, 
    (0,t_sim), 
    state_i, 
    t_eval = np.linspace(0,t_sim,int(t_sim)*50),
    events = ground_impact
)


# --- TELEMETRY DASHBOARD PLOTTING ---
# Main canvas setup
fig = plt.figure(figsize=(16, 6))
fig.suptitle("Launch Telemetry Dashboard", fontsize=16, fontweight='bold')

with col_plot:
    # Apply dark mode theme configurations matching Streamlit dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 9.5))
    fig.patch.set_facecolor('#0E1117') # Set background patch color to match app background
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])

    # Top Plot: Polar Spatial Trajectory displaying the actual physical path
    ax1 = fig.add_subplot(gs[0, :], projection='polar')
    ax1.set_facecolor('#1E2530') # Set polar plot face color matching panel backgrounds
    ax1.plot(solution.y[1], solution.y[0], color='#FF4B4B', linewidth=2.5, label="Trajectory")
    theta_earth = np.linspace(0, 2*np.pi, 100)
    ax1.set_rlabel_position(225)  
    ax1.tick_params(axis='y', labelsize=8, colors='#718096')
    ax1.tick_params(axis='x', colors='#A0AEC0')
    # Fill in Earth area
    ax1.fill(theta_earth, np.full(100, R_e), color='#3182CE', alpha=0.25, label="Earth")
    ax1.set_ylim(0, np.max(solution.y[0]) * 1.05) 
    ax1.set_title("Spatial Path (True Scale)", pad=15, color='#FFFFFF', fontweight='bold', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    # Render legend with transparent border
    ax1.legend(loc="lower left", fontsize='small', facecolor='#1A202C', edgecolor=(1.0, 1.0, 1.0, 0.1))

    # Bottom Left Plot: Altitude vs Time Profile
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('#1E2530')
    ax2.plot(solution.t, solution.y[0]-R_e, color='#ED8936', linewidth=2)
    ax2.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax2.set_ylabel("Altitude (m)", fontweight='bold', color='#A0AEC0')
    ax2.set_title("Altitude Profile", color='#FFFFFF', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax2.tick_params(colors='#718096')

    # Bottom Right Plot: Velocity vs Time Profile
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#1E2530')
    ax3.plot(solution.t, solution.y[3], color='#48BB78', linewidth=2)
    ax3.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax3.set_ylabel("Tangential Velocity (m/s)", fontweight='bold', color='#A0AEC0')
    ax3.set_title("Velocity Profile", color='#FFFFFF', fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax3.tick_params(colors='#718096')

    # Apply layout constraints and render the plot in Streamlit
    fig.tight_layout()
    st.pyplot(fig)

st.divider()