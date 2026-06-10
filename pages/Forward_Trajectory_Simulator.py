import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import streamlit as st

st.set_page_config(layout='wide', page_title="Forward Trajectory Simulator")

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
.page-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #FF4B4B, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.5px;
}

.page-subtitle {
    font-size: 1.15rem;
    color: #A0AEC0;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Input boxes premium borders */
div[data-baseweb="input"] {
    background-color: #1E2530 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    transition: all 0.3s ease;
}
div[data-baseweb="input"]:focus-within {
    border-color: #FF4B4B !important;
    box-shadow: 0 0 0 1px #FF4B4B !important;
}

/* Sidebar / Control panel styling */
div[data-testid="stVerticalBlock"] > div:has(div[data-testid="element-container"]) {
    /* background: rgba(26, 32, 44, 0.2); */
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">☄️ Forward Trajectory Simulator (IVP)</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Simulate rocket flight path parameters in real time. Input your vehicle details to calculate and plot the 2D gravity turn profile, dynamic drag, and velocity updates.</div>', unsafe_allow_html=True)

# Defining Universal Gravitational Constant
G = 6.67430e-11  # m^3 kg^-1 s^-2

# Defining Earth Constants
M_e = 5.9722e24  # Earth Mass in kg
R_e = 6.371e6   # Earth Radius in meters
p_0  = 1.225  # Sea level atmospheric density in kg/m^3
g_0 = 9.80665  # Standard gravity in m/s^2
def g(h):  # Standard pure gravity in m/s^2
    return G * M_e / (h)**2

# Defining Atmospheric Density as a function of altitude
@st.cache_data
def load_atmosphere():
    density = pd.read_csv('atm_density.csv')  
    altitudes = density['Altitude (m)'].values  
    densities = density['Density (kg/m^3)'].values  
    return sp.interpolate.interp1d(altitudes, np.log(densities), fill_value="extrapolate")

log_densities_interpolated = load_atmosphere()  # Interpolating the log of densities for better accuracy
def p(h):  # Function to return atmospheric density at a given altitude h
    if h-R_e > 1000000:  # If altitude is greater than 1000 km, we can assume the density is negligible
        return 0
    if h-R_e < 0:
        h = R_e
    return np.exp(log_densities_interpolated(h-R_e))  # Returning the interpolated density value at altitude h


# Getting Vehicle Parameters
# --- TOP CONTROL BAR (THE GUI INTERFACE) ---
col_inputs, col_plot = st.columns([1, 2])

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


theta = 0
v_ri = 0   # Assuming initial velocity in normal-direction is zero
r_i = R_e  # Assuming initial position in normal-direction is the Earth's surface

# Creating Initial State Vector
state_i = np.array([r_i, theta, v_ri, v_thetai, m_d + m_f])  # Initial state vector [x, y, v_x, v_y, mass]

# Note the differential equations are as follows:
# d/dt(v_x) = T*v_x/(m*v) - (1/2)*(p(y)*C_d*A/m)*v*v_x
# d/dt(v_y) = T*v_y/(m*v) - (1/2)*(p(y)*C_d*A/m)*v*v_y - g(y) + v_x**2/(R_e+y)
# d/dt(m) = - T / (I_sp * g_0) if m > m_d else 0

# Also note that the derivative of the state vector is as follows:
# d/dt(state) = [d/dt(x), d/dt(y), d/dt(v_x), d/dt(v_y), d/dt(m)]
# Hence, the right hand side of the DE can be defined as follows:
def vehicle_dynamics(t, state):
    r, theta, v_r, v_theta, m = state  # Unpacking the state vector
    v = np.sqrt(v_r**2 + v_theta**2)  # Calculating the velocity magnitude

    current_T = T if m > m_d else 0.0
    
    dt_r = v_r
    dt_theta = v_theta/r

    if (v == 0) or (r - R_e < vert and v_r >=0):
        thrust_theta = 0
        thrust_r = current_T
    else:
        thrust_theta = current_T * v_theta/v
        thrust_r = current_T * v_r/v

    dt_vtheta = thrust_theta/m - (1/2)*(p(r)*Cd*A/m)*v*v_theta - v_r*v_theta/r
    dt_vr = thrust_r/m - (1/2)*(p(r)*Cd*A/m)*v*v_r - g(r) + v_theta**2/(r)
    dt_m = -current_T/(I_sp*g_0)
    return np.array([dt_r, dt_theta, dt_vr, dt_vtheta, dt_m])

# Funtion for handling ground impact
def ground_impact(t, state):
    return state[0] - R_e
ground_impact.terminal = True
ground_impact.direction = -1

# Now we can use scipy to solve the differential equation and give all the state_vectors for the first t seconds
solution = sp.integrate.solve_ivp(
    vehicle_dynamics, 
    (0,t_sim), 
    state_i, 
    t_eval = np.linspace(0,t_sim,int(t_sim)*50),
    events = ground_impact
    )

# Now to plot the trajectory
# Initialize a wider figure for better subplot spacing
fig = plt.figure(figsize=(16, 6))
fig.suptitle("Launch Telemetry Dashboard", fontsize=16, fontweight='bold')

# Plot 1: Spatial Trajectory (True Physical Scale)
with col_plot:
    # Apply premium dark plot theme matching Streamlit dark mode
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 9.5))
    fig.patch.set_facecolor('#0E1117') # Match Streamlit background
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])

    # Top Plot: Spatial Trajectory
    ax1 = fig.add_subplot(gs[0, :], projection='polar')
    ax1.set_facecolor('#1E2530')
    ax1.plot(solution.y[1], solution.y[0], color='#FF4B4B', linewidth=2.5, label="Trajectory")
    theta_earth = np.linspace(0, 2*np.pi, 100)
    ax1.set_rlabel_position(225)  
    ax1.tick_params(axis='y', labelsize=8, colors='#718096')
    ax1.tick_params(axis='x', colors='#A0AEC0')
    ax1.fill(theta_earth, np.full(100, R_e), color='#3182CE', alpha=0.25, label="Earth")
    ax1.set_ylim(0, np.max(solution.y[0]) * 1.05) 
    ax1.set_title("Spatial Path (True Scale)", pad=15, color='#FFFFFF', fontweight='bold', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax1.legend(loc="lower left", fontsize='small', facecolor='#1A202C', edgecolor=(1.0, 1.0, 1.0, 0.1))

    # Bottom Left Plot: Altitude Profile
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('#1E2530')
    ax2.plot(solution.t, solution.y[0]-R_e, color='#ED8936', linewidth=2)
    ax2.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax2.set_ylabel("Altitude (m)", fontweight='bold', color='#A0AEC0')
    ax2.set_title("Altitude Profile", color='#FFFFFF', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax2.tick_params(colors='#718096')

    # Bottom Right Plot: Velocity Profile
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#1E2530')
    ax3.plot(solution.t, solution.y[3], color='#48BB78', linewidth=2)
    ax3.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax3.set_ylabel("Tangential Velocity (m/s)", fontweight='bold', color='#A0AEC0')
    ax3.set_title("Velocity Profile", color='#FFFFFF', fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax3.tick_params(colors='#718096')

    fig.tight_layout()
    st.pyplot(fig)

st.divider()