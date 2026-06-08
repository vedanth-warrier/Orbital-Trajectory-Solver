import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd

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
density = pd.read_csv('atm_density.csv')  # reading atmospheric density data from a CSV file
altitudes = density['Altitude (m)'].values  # Altitude values in meters
densities = density['Density (kg/m^3)'].values  # Corresponding density values in kg/m^3
log_densities_interpolated = sp.interpolate.interp1d(
    altitudes, 
    np.log(densities), 
    fill_value="extrapolate"
    )  # Interpolating the log of densities for better accuracy
def p(h):  # Function to return atmospheric density at a given altitude h
    if h-R_e > 1000000:  # If altitude is greater than 1000 km, we can assume the density is negligible
        return 0
    if h-R_e < 0:
        h = R_e
    return np.exp(log_densities_interpolated(h-R_e))  # Returning the interpolated density value at altitude h


# Getting Vehicle Parameters
m_d = float(input("Enter the dry mass of the vehicle in kg: "))
m_f = float(input("Enter the fuel mass of the vehicle in kg: "))
A = float(input("Enter the cross-sectional area of the vehicle in m^2: "))
Cd = float(input("Enter the drag coefficient of the vehicle: "))
I_sp = float(input("Enter the specific impulse of the vehicle in seconds: "))
T = float(input("Enter the thrust of the vehicle in Newtons: "))

# Initial Conditions
t = float(input("Enter the desired length of the simulation in s: "))
vert = float(input("Enter the desired length of initial pure vertical ascent in m: "))
v_thetai = float(input("Enter the initial tangetial velocity in m/s: "))
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
    (0,t), 
    state_i, 
    t_eval = np.linspace(0,t,int(t)*50),
    events = ground_impact
    )

# Now to plot the trajectory
print("Integration successful?", solution.success)

# Initialize a wider figure for better subplot spacing
plt.figure(figsize=(16, 6))
plt.suptitle("Launch Telemetry Dashboard", fontsize=16, fontweight='bold')

# Plot 1: Spatial Trajectory (True Physical Scale)
ax1 = plt.subplot(1, 3, 1, projection='polar')
ax1.plot(solution.y[1], solution.y[0], color='crimson', linewidth=2, label="Trajectory")
theta_earth = np.linspace(0, 2*np.pi, 100)
ax1.fill(theta_earth, np.full(100, R_e), color='dodgerblue', alpha=0.3, label="Earth")
ax1.set_ylim(0, np.max(solution.y[0]) * 1.05) 
ax1.set_title("Spatial Path (True Scale)", pad=15)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_yticklabels([]) 
ax1.legend(loc="lower left", fontsize='small')

# Plot 2: Telemetry - Altitude vs Time
ax2 = plt.subplot(1, 3, 2)
ax2.plot(solution.t, solution.y[0]-R_e, color='darkorange', linewidth=2)
ax2.set_xlabel("Time (s)", fontweight='bold')
ax2.set_ylabel("Altitude (m)", fontweight='bold')
ax2.set_title("Altitude Profile")
ax2.grid(True, linestyle='--', alpha=0.7)

# Plot 3: Telemetry - Tangential Velocity vs Time
ax3 = plt.subplot(1, 3, 3)
ax3.plot(solution.t, solution.y[3], color='forestgreen', linewidth=2)
ax3.set_xlabel("Time (s)", fontweight='bold')
ax3.set_ylabel("Tangential Velocity (m/s)", fontweight='bold')
ax3.set_title("Velocity Profile")
ax3.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()