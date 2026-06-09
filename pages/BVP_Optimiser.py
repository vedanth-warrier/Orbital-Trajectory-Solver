import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", page_title="BVP Optimiser")
st.title("Orbital Insertion Dashboard")

st.markdown("""
Welcome to the Orbital Insertion Dashboard. 

This page is designed for you to figure out what you need to get your vehicle to your desired orbit!
When entering the solvable inputs below, you must leave 2 degrees of freedom (2 variables blank), and the
optimiser will calculate those values for you!
""")

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

# Getting orbit parameters
# # 1. Initialize Session State Variables
if 'orb_h_km' not in st.session_state:
    st.session_state.orb_h_km = 250.0
if 'orb_v_ms' not in st.session_state:
    st.session_state.orb_v_ms = np.sqrt(G * M_e / (R_e + 250000.0))

# 2. Define Physics Callback Functions
def update_v():
    h_m = st.session_state.orb_h_km * 1000
    st.session_state.orb_v_ms = np.sqrt(G * M_e / (R_e + h_m))

def update_h():
    v = st.session_state.orb_v_ms
    st.session_state.orb_h_km = ((G * M_e / v**2) - R_e) / 1000

# 3. Build UI Layout
col_inputs, col_plot = st.columns([1, 2])

with col_inputs:
    st.subheader("Orbit Parameters")
    st.number_input("Orbit Altitude (km)", min_value=150.0, step=10.0, 
                    key='orb_h_km', on_change=update_v)
    orb_h = st.session_state.orb_h_km * 1000  
    
    st.number_input("Orbital Velocity (m/s)", min_value=0.0, max_value=7818.310843797251, step=10.0, 
                    key='orb_v_ms', on_change=update_h)
    orb_v = st.session_state.orb_v_ms

    # Getting Fixed/Required Inputs
    st.subheader("Fixed Parameters")
    st.markdown("You must input all of these values.")
    A = st.number_input("Cross Sectional Area (m^2)", value=12.0, step=1.0, min_value=0.0)
    Cd = st.number_input("Drag Coeff", value=0.4, step=0.1, min_value=0.0)
    I_sp = st.number_input("I_sp (s)", value=400.0, step=10.0, min_value=0.01)
    vert = st.number_input("Vertical Ascent Threshold (m)", value=15000.0, step=500.0, max_value=orb_h, min_value=10.0)

    # Getting solvable inputs
    st.subheader("Solvable Inputs")
    st.markdown("You must leave 2 of these blank.")
    m_d = st.number_input("Dry Mass (kg)", value=None, step=500.0, min_value=0.01)
    m_f = st.number_input("Fuel Mass (kg)", value=None, step=1000.0, min_value=0.01)
    T = st.number_input("Thrust (N)", value=None, step=50000.0, min_value=0.01)
    pitch = st.number_input("Pitch Over Angle (0 -> π/2)", value=None, step=0.1, min_value=0.001, max_value=np.pi/2)

    blank_count = [m_d, m_f, T, pitch].count(None)
    is_valid = (blank_count==2)

    if blank_count < 2:
        st.error("Leave 2 values blank")
    elif blank_count > 2:
        st.error("Fill in 2 values")

    execute = st.button("Run BVP Optimiser", width='stretch')

solution_trajectory = None

if is_valid and execute:
    solution_trajectory = 0
    pass

with col_plot:
    # Reverting to standard sizing for future trajectory overlay
    fig = plt.figure(figsize = (8.9,12))
    gs = fig.add_gridspec(2,2, height_ratios=[2,1])
    theta = np.linspace(0, 2*np.pi, 100)
    
    ax1 = fig.add_subplot(gs[0,:], projection = 'polar')
    ax1.plot(theta, np.full(100, R_e + orb_h), color='crimson', linewidth=2, label="Target Orbit")
    ax1.fill(theta, np.full(100, R_e), color='dodgerblue', alpha=0.3, label="Earth")
    ax1.set_rlabel_position(225)  
    ax1.tick_params(axis='y', labelsize=8, colors='gray')
    ax1.set_ylim(0, (R_e + orb_h) * 1.05)
    ax1.set_title("Target Orbit Profile", pad=15)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc="lower left", fontsize='small')

    ax2 = fig.add_subplot(gs[1,0])
    ax2.set_xlabel("Time (s)", fontweight='bold')
    ax2.set_ylabel("Altitude (m)", fontweight='bold')
    ax2.set_title("Altitude Profile")
    ax2.grid(True, linestyle='--', alpha=0.7)

    ax3 = fig.add_subplot(gs[1,1])
    ax3.set_xlabel("Time (s)", fontweight='bold')
    ax3.set_ylabel("Tangential Velocity (m/s)", fontweight='bold')
    ax3.set_title("Velocity Profile")
    ax3.grid(True, linestyle='--', alpha=0.7)

    if solution_trajectory != None:
        ax1.plot(theta, np.full(100, 2*R_e), color = 'gold')
        ax1.set_ylim(0, (R_e) * 2.1)
    
    # Allowing Streamlit to natively stretch the plot to fill the right column
    st.pyplot(fig)

st.divider()