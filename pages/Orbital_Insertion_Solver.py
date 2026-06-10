# Import necessary computational, optimisation, and GUI libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import streamlit as st

# Configure the Streamlit page properties to wide-mode and set the browser title
st.set_page_config(layout="wide", page_title="Orbital Insertion Solver (BVP)")

# Premium Style Injection using CSS
# Applies custom typography, custom inputs, custom page links, button gradients, and hides the default sidebar navigation
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
    padding-top: 1rem;
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

/* Premium Button style overrides for form submission buttons */
div[data-testid="stButton"] button {
    background: linear-gradient(90deg, #FF4B4B, #FF8A00) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(255, 75, 75, 0.25) !important;
}

/* Hover glow effect and slight lift for primary button */
div[data-testid="stButton"] button:hover {
    box-shadow: 0 6px 20px rgba(255, 75, 75, 0.45) !important;
    transform: translateY(-2px) !important;
}

/* Button active state correction */
div[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
}

/* Hide Streamlit Sidebar completely */
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
st.markdown('<div class="page-title">🎯 Orbital Insertion Solver (BVP)</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Resolve orbital boundary-value problems (BVP) using a fast gradient-based numerical solver. Input your environmental parameters, leave exactly three solvable inputs blank, and execute the solver to target your desired stable parking orbit.</div>', unsafe_allow_html=True)

# --- PHYSICAL CONSTANTS DEFINITION ---
G = 6.67430e-11  # Universal Gravitational Constant (m^3 kg^-1 s^-2)
M_e = 5.9722e24  # Earth Mass (kg)
R_e = 6.371e6   # Earth Mean Radius (meters)
p_0  = 1.225  # Sea level atmospheric density (kg/m^3)
g_0 = 9.80665  # Standard gravity (m/s^2)

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

# --- DYNAMIC INTERACTIVE ORBIT INPUT CALLBACKS ---
# Initialise session state default parameters if not already present
if 'orb_h_km' not in st.session_state:
    st.session_state.orb_h_km = 250.0
if 'orb_v_ms' not in st.session_state:
    st.session_state.orb_v_ms = np.sqrt(G * M_e / (R_e + 250000.0))

# Callback to update orbital velocity (based on circular speed formula) when altitude changes
def update_v():
    h_m = st.session_state.orb_h_km * 1000
    st.session_state.orb_v_ms = np.sqrt(G * M_e / (R_e + h_m))

# Callback to update orbital altitude (based on circular speed formula) when velocity changes
def update_h():
    v = st.session_state.orb_v_ms
    st.session_state.orb_h_km = ((G * M_e / v**2) - R_e) / 1000

# --- GUI WIDGET CONTROL INTERFACE ---
# Divide the interface into columns for input parameters and telemetry plots
col_inputs, col_plot = st.columns([1, 2])

# Render input forms in the left column
with col_inputs:
    # Placeholders to show messages at the top of the page without scrolling
    msg_placeholder = st.empty()
    validation_placeholder = st.empty()

    st.subheader("Orbit Parameters")
    st.number_input("Orbit Altitude (km)", min_value=150.0, step=10.0, 
                    key='orb_h_km', on_change=update_v)
    orb_h = st.session_state.orb_h_km * 1000  # Convert altitude from km to meters
    
    st.number_input("Orbital Velocity (m/s)", min_value=0.0, max_value=7818.310843797251, step=10.0, 
                    key='orb_v_ms', on_change=update_h)
    orb_v = st.session_state.orb_v_ms
    # Estimate transfer orbit coast time to apogee (half period of Hohmann orbit)
    t_coast_est = np.pi * np.sqrt((R_e + 0.5 * orb_h)**3 / (G * M_e))
    coast_time_limit = max(10000.0, 3.0 * t_coast_est)

    st.subheader("Fixed Parameters")
    st.markdown("You must input all of these values.")
    v_thetai = st.number_input("Initial Tangential Velocity (m/s)", value = 386.7, step = 10.0, min_value=0.0)
    A = st.number_input("Cross Sectional Area (m^2)", value=12.0, step=1.0, min_value=0.0)
    Cd = st.number_input("Drag Coeff", value=0.4, step=0.1, min_value=0.0)
    I_sp = st.number_input("I_sp (s)", value=400.0, step=10.0, min_value=0.01)
    vert = st.number_input("Vertical Ascent Threshold (m)", value=15000.0, step=500.0, max_value=orb_h, min_value=10.0)

    st.subheader("Solvable Inputs")
    st.markdown("You must leave 3 of these blank.")

    # --- INJECT PENDING UPDATES BEFORE WIDGETS RENDER ---
    # Rerouting updated session state outputs back into input form defaults after successful run
    if 'update_pending' in st.session_state and st.session_state.update_pending:
        st.session_state.md_key = st.session_state.new_md
        st.session_state.mf_key = st.session_state.new_mf
        st.session_state.t_key = st.session_state.new_t
        st.session_state.pitch_key = st.session_state.new_pitch
        st.session_state.alloc_key = st.session_state.new_alloc
        st.session_state.update_pending = False

    # Input forms for solvable variables (defaults to None to mark as blank/solvable)
    m_d = st.number_input("Dry Mass (kg)", value=None, step=500.0, min_value=0.01, max_value=999999.0, key='md_key')
    m_f = st.number_input("Fuel Mass (kg)", value=None, step=1000.0, min_value=0.01, max_value=9999999.0, key='mf_key')
    alloc_ui = st.number_input("Ascent Fuel Allocation (1 -> 99%)", value=None, step=5.0, min_value=1.0, max_value=99.0, key='alloc_key')
    alloc_perc = alloc_ui / 100.0 if alloc_ui is not None else None
    T = st.number_input("Thrust (N)", value=None, step=50000.0, min_value=0.01, max_value=999999999.0, key='t_key')
    pitch = st.number_input("Pitch Over Angle (0 -> π/2)", value=None, step=0.1, min_value=0.0, max_value=np.pi/2, key='pitch_key')
    
    # Calculate how many solvable parameters are left blank to check degrees of freedom
    blank_count = [m_d, m_f, T, pitch, alloc_ui].count(None)
    is_valid = (blank_count==3)

    # Print error messages based on blank count validation
    if blank_count < 3:
        st.error("Leave 3 values blank")
    elif blank_count > 3:
        st.error("Fill in 3 values")

    # Render button to trigger solver execution
    execute = st.button("Run BVP Optimiser", width='stretch')

    # Display solver outcomes dynamically in top placeholders
    if 'bvp_error' in st.session_state and st.session_state.bvp_error:
        msg_placeholder.error(st.session_state.bvp_error)
    elif 'bvp_success' in st.session_state and st.session_state.bvp_success:
        msg_placeholder.success(st.session_state.bvp_success)

# --- DIFFERENTIAL EQUATIONS OF MOTION WITH VEHICLE MASS SWITCH ---
def vehicle_dynamics(t, state, thrust, pitch, dry_m):
    r, theta, v_r, v_theta, m = state 
    v = np.sqrt(v_r**2 + v_theta**2) 

    # Active thrust is zero if vehicle is completely out of fuel (m <= dry_m)
    current_T = thrust if m > dry_m else 0.0
    
    # State derivatives for coordinates
    dt_r = v_r
    dt_theta = v_theta/r

    # Gravity Turn Logic:
    # Maintain vertical flight until radial clearance threshold is achieved (r - R_e < vert)
    if (v == 0) or (r - R_e < vert and v_r >=0):
        thrust_theta = 0
        thrust_r = current_T
    else:
        # Tilt and align thrust vector based on pitch angle configuration
        thrust_theta = current_T * np.cos(pitch)
        thrust_r = current_T * np.sin(pitch)

    # Dynamics equations representing aerodynamic drag, planetary gravity, and centripetal terms
    dt_vtheta = thrust_theta/m - (1/2)*(p(r)*Cd*A/m)*v*v_theta - v_r*v_theta/r
    dt_vr = thrust_r/m - (1/2)*(p(r)*Cd*A/m)*v*v_r - g(r) + v_theta**2/(r)
    # Depletion rate of propellant mass
    dt_m = -current_T/(I_sp*g_0)
    
    return np.array([dt_r, dt_theta, dt_vr, dt_vtheta, dt_m])

# --- SOLVER INTEGRATION TERMINATION EVENTS ---
# Solver Event: Terminate integration if vehicle crashes back to Earth
def ground_impact(t, state, thrust, pitch, dry_m):
    if t < 0.1:
        return 1.0 # Prevent immediate trigger on the launchpad at t=0
    return state[0] - R_e
ground_impact.terminal = True
ground_impact.direction = -1

# Solver Event: Terminate integration if radial velocity goes to zero (apogee reached during coast)
def apogee_reached(t, state, thrust, pitch, dry_m):
    return state[2] 
apogee_reached.terminal = True
apogee_reached.direction = -1

# Solver Event: Terminate integration if propellant burn limits are reached
def mass_cutoff(t, state, thrust, pitch, dry_m):
    return state[4] - dry_m
mass_cutoff.terminal = True
mass_cutoff.direction = -1

# Solver Event: Terminate integration during apogee kick if orbital speed is achieved
def target_velocity_reached(t, state, thrust, pitch, dry_m):
    # Only allow early cutoff if we are above 90% of the target altitude
    if state[0] - R_e < 0.9 * orb_h:
        return 1.0
    return state[3] - orb_v
target_velocity_reached.terminal = True
target_velocity_reached.direction = 1

# --- BOUNDARY VALUE PROBLEM EVALUATOR ---
# Evaluates target boundary errors under current variable guesses
def bvp_objective(guess):
    # Retrieve variable mappings
    current_params = unknowns.copy()
    current_params[blank_vars[0]] = guess[0]
    current_params[blank_vars[1]] = guess[1]
    current_params[blank_vars[2]] = guess[2]

    # Map parameters
    dry_m = current_params['m_d']
    total_fuel = current_params['m_f']
    thrust = current_params['T']
    pitch = current_params['pitch']
    alloc = current_params['alloc']

    # Distribute propellant allocations between Ascent Burn and Circularisation Kick phases
    mf_ascent = total_fuel * alloc
    mf_kick = total_fuel * (1.0 - alloc)

    # Launch pad state vector: [R_e, 0 rad, 0 m/s, tangential speed, total mass]
    state_i = np.array([R_e, 0.0, 0.0, v_thetai, dry_m + total_fuel])

    # --- PHASE 1: ASCENT BURN ---
    sol_1 = sp.integrate.solve_ivp(
        vehicle_dynamics, (0, 3600), state_i, 
        rtol=1e-5, atol=1e-7,
        events=[ground_impact, mass_cutoff], args=(thrust, pitch, dry_m + mf_kick)
    )
    # Boundary check: Did the vehicle crash during ascent phase?
    if sol_1.y[0][-1] <= R_e + 10: 
        peak_r = np.max(sol_1.y[0])
        peak_v = np.max(sol_1.y[3])
        impact_vr = sol_1.y[2][-1]  # Capture radial velocity at the moment of impact
        
        # Scale the natural errors by 100. This maintains the correct 
        # mathematical slope while making the crash zone highly punitive.
        error_r_crash = 100.0 * (peak_r - (R_e + orb_h)) / orb_h
        error_v_crash = 100.0 * (peak_v - orb_v) / orb_v
        error_vr_crash = 100.0 * (impact_vr / 1000.0) 
        return [error_r_crash, error_v_crash, error_vr_crash]

    # --- PHASE 2: COAST TO APOGEE ---
    state_2_initial = sol_1.y[:, -1]
    sol_2 = sp.integrate.solve_ivp(
        vehicle_dynamics, (sol_1.t[-1], sol_1.t[-1] + coast_time_limit), state_2_initial, 
        rtol=1e-5, atol=1e-7,
        events=[ground_impact, apogee_reached], args=(0.0, 0.0, 0.0)
    )
    # Boundary check: Did the vehicle crash during coast phase?
    if sol_2.y[0][-1] <= R_e + 10: 
        peak_r = np.max(sol_2.y[0])
        peak_v = np.max(sol_2.y[3])
        impact_vr = sol_2.y[2][-1]
        
        error_r_crash = 100.0 * (peak_r - (R_e + orb_h)) / orb_h
        error_v_crash = 100.0 * (peak_v - orb_v) / orb_v
        error_vr_crash = 100.0 * (impact_vr / 1000.0)
        return [error_r_crash, error_v_crash, error_vr_crash]

    # --- PHASE 3: APOGEE KICK ---
    state_3_initial = sol_2.y[:, -1]
    sol_3 = sp.integrate.solve_ivp(
        vehicle_dynamics, (sol_2.t[-1], sol_2.t[-1] + 3600), state_3_initial, 
        events=[ground_impact, mass_cutoff, target_velocity_reached], args=(thrust, 0.0, dry_m), 
        rtol=1e-5, atol=1e-7
    )
    # Boundary check: Did the vehicle crash during circularisation burn phase?
    if sol_3.y[0][-1] <= R_e + 10: 
        peak_r = np.max(sol_3.y[0])
        peak_v = np.max(sol_3.y[3])
        impact_vr = sol_3.y[2][-1]
        
        error_r_crash = 100.0 * (peak_r - (R_e + orb_h)) / orb_h
        error_v_crash = 100.0 * (peak_v - orb_v) / orb_v
        error_vr_crash = 100.0 * (impact_vr / 1000.0)
        return [error_r_crash, error_v_crash, error_vr_crash]

    # --- THE FINAL ERROR CALCULATION ---
    r_final = sol_3.y[0][-1]
    v_r_final = sol_3.y[2][-1]       # EXTRACT RADIAL VELOCITY
    v_theta_final = sol_3.y[3][-1]

    # Calculate normalised errors to pass back to the optimiser
    error_r_norm = (r_final - (R_e + orb_h)) / orb_h
    error_vtheta_norm = (v_theta_final - orb_v) / orb_v
    
    # Normalise radial velocity against a baseline so it scales evenly with the other errors
    error_vr_norm = v_r_final / 1000.0  

    # Return the 3-element vector. 
    # least_squares is perfectly happy solving an overdetermined system (3 equations, 2 unknowns)
    return [error_r_norm, error_vtheta_norm, error_vr_norm]

# --- MAIN GRADIENT OPTIMISER PIPELINE ---
if is_valid and execute:
    st.session_state.bvp_error = None
    st.session_state.bvp_success = None
    
    # Define mapping of parameters and extract variables to solve
    unknowns = {'m_d': m_d, 'm_f': m_f, 'T': T, 'pitch': pitch, 'alloc': alloc_perc}
    blank_vars = [i for i, j in unknowns.items() if j == None]

    # --- DYNAMIC INITIAL GUESS LOGIC FOR LEAST_SQUARES ---
    known_md = m_d if m_d is not None else 5000.0
    known_mf = m_f if m_f is not None else 50000.0
    known_T = T if T is not None else 1500000.0
    known_pitch = pitch if pitch is not None else 0.8
    known_alloc = alloc_perc if alloc_perc is not None else 0.90

    # Mathematically guarantee a launch TWR > 1.0 for the initial guess
    if T is None:
        T_guess = (known_md + known_mf) * g_0 * 1.5
        mf_guess = known_mf
        md_guess = known_md
    else:
        T_guess = known_T
        max_launch_mass = T_guess / g_0
        if m_f is None and m_d is not None:
            if m_d >= max_launch_mass:
                mf_guess = 1000.0
                md_guess = m_d
            else:
                mf_guess = (T_guess / (g_0 * 1.5)) - m_d
                if mf_guess < 10.0:
                    mf_guess = 0.5 * (max_launch_mass - m_d)
                md_guess = m_d
        elif m_d is None and m_f is not None:
            if m_f >= max_launch_mass:
                md_guess = 1000.0
                mf_guess = m_f
            else:
                md_guess = (T_guess / (g_0 * 1.5)) - m_f
                if md_guess < 10.0:
                    md_guess = 0.5 * (max_launch_mass - m_f)
                mf_guess = m_f
        elif m_d is None and m_f is None:
            target_launch_mass = T_guess / (g_0 * 1.5)
            md_guess = target_launch_mass * 0.1
            mf_guess = target_launch_mass * 0.9
        else:
            md_guess = m_d
            mf_guess = m_f

    # Create the initial guess mapping vector
    guess_map = {
        'm_d': md_guess,
        'm_f': mf_guess,
        'T': T_guess,
        'pitch': known_pitch,
        'alloc': known_alloc
    }
    
    # Pack initial guesses for the 3 blank variables
    guess = [guess_map[blank_vars[0]], guess_map[blank_vars[1]], guess_map[blank_vars[2]]]

    # Setup parameter bounds maps to prevent non-physical solver values (e.g. negative mass/thrust)
    bounds_map = {
        'm_d': (0.01, 999999.0), 
        'm_f': (0.01, 9999999.0), 
        'T': (100.0, 99999999.0), 
        'pitch': (0.0, np.pi/2),
        'alloc': (0.01, 0.99)
    }
    
    # Pack solver bounds coordinates
    lower_bounds = [bounds_map[blank_vars[0]][0], bounds_map[bounds_map[blank_vars[1]] == None or blank_vars[1]][0], bounds_map[blank_vars[2]][0]]
    # Fix a minor dictionary key check to retrieve indices cleanly
    lower_bounds = [bounds_map[blank_vars[0]][0], bounds_map[blank_vars[1]][0], bounds_map[blank_vars[2]][0]]
    upper_bounds = [bounds_map[blank_vars[0]][1], bounds_map[blank_vars[1]][1], bounds_map[blank_vars[2]][1]]
    solver_bounds = (lower_bounds, upper_bounds)

    # Scale the variables to normalise differences between values (e.g., thrust in millions vs. pitch in fractions of a radian)
    custom_scale = np.maximum(np.abs(guess), 1.0)

    # Warn users if solving large orbits
    spinner_message = "Running Fast Gradient Solver..."
    if orb_h >= 5000000.0:
        spinner_message += " (Note: Large orbits may take a few minutes to solve)"

    # Solve the BVP equations using Trust Region Reflective (trf) non-linear least-squares
    with st.spinner(spinner_message):
        guess_final = sp.optimize.least_squares(
            bvp_objective, 
            guess, 
            bounds=solver_bounds,
            method='trf',
            x_scale=custom_scale,     # Dynamically scales variables so 1,000,000 N and 0.5 rad are weighted equally
            diff_step=1e-3,    # Forces the solver to take larger test steps (e.g., 1000 N) to punch through numerical noise
            ftol=1e-6,  
            xtol=1e-6,  
            gtol=1e-6,
            max_nfev=3000
        )
    
    # Stop execution and output message if solver failed to converge
    if not guess_final.success:
        st.session_state.bvp_error = f"❌ Solver Failed: {guess_final.message}"
        st.session_state.bvp_success = None
        st.stop()

    # Retrieve optimal parameters
    unknowns[blank_vars[0]] = guess_final.x[0]
    unknowns[blank_vars[1]] = guess_final.x[1]
    unknowns[blank_vars[2]] = guess_final.x[2]
    
    final_dry_m = unknowns['m_d']
    final_mf_ascent = unknowns['m_f'] * unknowns['alloc']
    final_mf_kick = unknowns['m_f'] * (1.0 - unknowns['alloc'])
    final_T = unknowns['T']
    final_pitch = unknowns['pitch']

    state_final_1 = np.array([R_e, 0.0, 0.0, v_thetai, final_dry_m + unknowns['m_f']])

    # --- HIGH FIDELITY FORWARD PROPAGATION OF THE OPTIMAL RUN ---
    # Phase 1: Ascent Burn
    sol_final_1 = sp.integrate.solve_ivp(
        vehicle_dynamics, (0, 3600), state_final_1, max_step=2.0,  
        events=[ground_impact, mass_cutoff], args=(final_T, final_pitch, final_dry_m + final_mf_kick),
        rtol = 1e-10, atol = 1e-12
    )
    
    # Phase 2: Coasting
    sol_final_2 = sp.integrate.solve_ivp(
        vehicle_dynamics, (sol_final_1.t[-1], sol_final_1.t[-1] + coast_time_limit), sol_final_1.y[:, -1], max_step=10.0, 
        events=[apogee_reached, ground_impact], args=(0.0, 0.0, 0.0),
        rtol = 1e-10, atol = 1e-12
    )

    # Phase 3: Apogee Kick 
    sol_final_3 = sp.integrate.solve_ivp(
        vehicle_dynamics, (sol_final_2.t[-1], sol_final_2.t[-1] + 3600), sol_final_2.y[:, -1], max_step=1.0,
        events=[mass_cutoff, ground_impact, target_velocity_reached], args=(final_T, 0.0, final_dry_m),
        rtol = 1e-10, atol = 1e-12
    )

    # Phase 4: Orbital Confirmation (Simulate for 3 orbits to verify stability)
    t_orbit = np.pi * np.sqrt((R_e + orb_h)**3 / (G * M_e)) * 3
    sol_final_4 = sp.integrate.solve_ivp(
        vehicle_dynamics, (sol_final_3.t[-1], sol_final_3.t[-1] + t_orbit), sol_final_3.y[:, -1], max_step=20.0, 
        events=ground_impact, args=(0.0, 0.0, final_dry_m),
        rtol = 1e-10, atol = 1e-12
    )

    # Extract orbital telemetry values at apogee insertion point
    r_final = sol_final_3.y[0][-1]
    v_theta_final = sol_final_3.y[3][-1]
    v_r_final = sol_final_3.y[2][-1]

    # Calculate actual differences vs target values
    err_alt_km = (r_final - (R_e + orb_h)) / 1000.0
    err_vtheta_ms = v_theta_final - orb_v
    err_vr_ms = v_r_final

    # Calculate analytical perigee altitude of the resulting orbit
    h_momentum = r_final * v_theta_final
    energy = 0.5 * (v_r_final**2 + v_theta_final**2) - (G * M_e / r_final)
    
    # If orbit is bound (closed), calculate perigee altitude
    if energy < 0:
        semi_major_axis = -G * M_e / (2.0 * energy)
        eccentricity_sq = 1.0 + (2.0 * energy * h_momentum**2) / (G * M_e)**2
        eccentricity = np.sqrt(max(0.0, eccentricity_sq))
        r_perigee = semi_major_axis * (1.0 - eccentricity)
        alt_perigee_km = (r_perigee - R_e) / 1000.0
        is_escape = False
    else:
        # Unbound orbit (parabolic or hyperbolic escape trajectory)
        if energy > 0:
            semi_major_axis = -G * M_e / (2.0 * energy)
            eccentricity_sq = 1.0 + (2.0 * energy * h_momentum**2) / (G * M_e)**2
            eccentricity = np.sqrt(max(0.0, eccentricity_sq))
            r_perigee = semi_major_axis * (1.0 - eccentricity)
        else:
            r_perigee = h_momentum**2 / (2.0 * G * M_e)
        alt_perigee_km = (r_perigee - R_e) / 1000.0
        is_escape = True

    # Ensure orbit perigee is above 100 km, did not crash, and did not escape
    crashed_in_orbit = (sol_final_4.y[0][-1] <= R_e + 10) or (alt_perigee_km < 100.0) or is_escape
    
    # Evaluate physical constraints and format user alerts
    if guess_final.cost > 0.0001 or crashed_in_orbit:
        if crashed_in_orbit:
            if is_escape:
                msg = "⚠️ **Physical Impossibility: Escape Trajectory**. The vehicle exceeded escape velocity (energy >= 0), causing it to shoot out of orbit."
            elif alt_perigee_km < 100.0:
                msg = f"⚠️ **Physical Impossibility: Orbit Decayed/Unstable**. The resulting orbit has a perigee inside the atmosphere (**{alt_perigee_km:.2f} km**), causing it to decay rapidly and crash back to Earth during orbital confirmation."
            else:
                msg = "⚠️ **Physical Impossibility: Orbit Decayed/Unstable**. The vehicle crashed back to Earth during orbital confirmation."
        else:
            msg = "⚠️ **Physical Impossibility**: The optimiser could not reach the target orbit with these constraints."

        st.session_state.bvp_error = (
            f"{msg} Displaying the closest trajectory found. (Error Cost: {guess_final.cost:.6f})\n\n"
            f"**Final Insertion Telemetry (Apogee Kick End):**\n"
            f"* Altitude: **{(r_final - R_e)/1000.0:.2f} km** (Error: {err_alt_km:+.2f} km)\n"
            f"* Tangential Velocity: **{v_theta_final:.2f} m/s** (Error: {err_vtheta_ms:+.2f} m/s)\n"
            f"* Radial Velocity: **{v_r_final:.2f} m/s**"
        )
        if energy < 0:
            st.session_state.bvp_error += f"\n* Calculated Perigee Altitude: **{alt_perigee_km:.2f} km**"
        st.session_state.bvp_success = None
    else:
        st.session_state.bvp_success = (
            f"🎯 **Orbit Insertion Successful!** (Error Cost: {guess_final.cost:.6f})\n\n"
            f"**Final Insertion Telemetry (Apogee Kick End):**\n"
            f"* Altitude: **{(r_final - R_e)/1000.0:.2f} km** (Error: {err_alt_km:+.2f} km)\n"
            f"* Tangential Velocity: **{v_theta_final:.2f} m/s** (Error: {err_vtheta_ms:+.2f} m/s)\n"
            f"* Radial Velocity: **{v_r_final:.2f} m/s**"
        )
        if energy < 0:
            st.session_state.bvp_success += f"\n* Calculated Perigee Altitude: **{alt_perigee_km:.2f} km**"
        st.session_state.bvp_error = None

    # Load calculated parameters back to session state variables
    st.session_state.new_md = float(unknowns['m_d'])
    st.session_state.new_mf = float(unknowns['m_f'])
    st.session_state.new_t = float(unknowns['T'])
    st.session_state.new_pitch = float(unknowns['pitch'])
    st.session_state.new_alloc = float(unknowns['alloc'] * 100.0)
    st.session_state.update_pending = True

    # Concatenate vectors to plot entire timeline
    st.session_state.plot_t = np.concatenate((sol_final_1.t, sol_final_2.t, sol_final_3.t, sol_final_4.t))
    st.session_state.plot_y = np.concatenate((sol_final_1.y, sol_final_2.y, sol_final_3.y, sol_final_4.y), axis=1)

    # Force Streamlit page refresh
    st.rerun()

# --- TELEMETRY DASHBOARD PLOTTING ---
with col_plot:
    # Setup canvas matching Streamlit dark mode configurations
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 12))
    fig.patch.set_facecolor('#0E1117') # Match Streamlit background
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Subplot 1: Polar Spatial Path displaying physical trajectory
    ax1 = fig.add_subplot(gs[0, :], projection='polar')
    ax1.set_facecolor('#1E2530')
    # Draw circular line of the Target Orbit boundary
    ax1.plot(theta, np.full(100, R_e + orb_h), color='#FF4B4B', linewidth=2, linestyle='--', label="Target Orbit")
    # Draw Earth disk
    ax1.fill(theta, np.full(100, R_e), color='#3182CE', alpha=0.25, label="Earth")
    ax1.set_rlabel_position(225)  
    ax1.tick_params(axis='y', labelsize=8, colors='#718096')
    ax1.tick_params(axis='x', colors='#A0AEC0')
    ax1.set_ylim(0, (R_e + orb_h) * 1.05)
    ax1.set_title("Orbital Path (True Scale)", pad=15, color='#FFFFFF', fontweight='bold', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.3, color='#4A5568')

    # Subplot 2: Altitude vs Time Profile
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('#1E2530')
    ax2.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax2.set_ylabel("Altitude (m)", fontweight='bold', color='#A0AEC0')
    ax2.set_title("Altitude Profile", color='#FFFFFF', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax2.tick_params(colors='#718096')

    # Subplot 3: Velocity vs Time Profile
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#1E2530')
    ax3.set_xlabel("Time (s)", fontweight='bold', color='#A0AEC0')
    ax3.set_ylabel("Tangential Velocity (m/s)", fontweight='bold', color='#A0AEC0')
    ax3.set_title("Velocity Profile", color='#FFFFFF', fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.3, color='#4A5568')
    ax3.tick_params(colors='#718096')

    # Plot simulated path results if they exist in state
    if 'plot_t' in st.session_state:
        ax1.plot(st.session_state.plot_y[1], st.session_state.plot_y[0], color='#48BB78', label='Simulated Trajectory', linewidth=2.5)
        ax1.set_ylim(0, max(max(st.session_state.plot_y[0]), (R_e + orb_h))*1.05)
        ax2.plot(st.session_state.plot_t, st.session_state.plot_y[0]-R_e, color='#ED8936', linewidth=2)
        ax3.plot(st.session_state.plot_t, st.session_state.plot_y[3], color='#48BB78', linewidth=2)
    
    # Legend settings
    ax1.legend(loc="lower left", fontsize='small', facecolor='#1A202C', edgecolor=(1.0, 1.0, 1.0, 0.1))
    fig.tight_layout()
    st.pyplot(fig)

st.divider()