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
    return G * M_e / (R_e + h)**2

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
    if h > 1000000:  # If altitude is greater than 1000 km, we can assume the density is negligible
        return 0
    return np.exp(log_densities_interpolated(h))  # Returning the interpolated density value at altitude h


# Getting Vehicle Parameters
m_d = float(input("Enter the dry mass of the vehicle in kg: "))
m_f = float(input("Enter the fuel mass of the vehicle in kg: "))
A = float(input("Enter the cross-sectional area of the vehicle in m^2: "))
Cd = float(input("Enter the drag coefficient of the vehicle: "))
I_sp = float(input("Enter the specific impulse of the vehicle in seconds: "))
T = float(input("Enter the thrust of the vehicle in Newtons: "))

# Initial Conditions
t = float(input("Enter the desired length of the simulation in s: "))
v_xi = float(input("Enter the initial velocity in x-direction in m/s: "))
v_yi = 0   # Assuming initial velocity in y-direction is zero
x_i = 0   # Assuming initial position in x-direction is zero 
y_i = 250000   # Assuming initial position in y-direction is zero

# Creating Initial State Vector
state_i = np.array([x_i, y_i, v_xi, v_yi, m_d + m_f])  # Initial state vector [x, y, v_x, v_y, mass]

# Note the differential equations are as follows:
# d/dt(v_x) = T*v_x/(m*v) - (1/2)*(p(y)*C_d*A/m)*v*v_x
# d/dt(v_y) = T*v_y/(m*v) - (1/2)*(p(y)*C_d*A/m)*v*v_y - g(y) + v_x**2/(R_e+y)
# d/dt(m) = - T / (I_sp * g_0) if m > m_d else 0

# Also note that the derivative of the state vector is as follows:
# d/dt(state) = [d/dt(x), d/dt(y), d/dt(v_x), d/dt(v_y), d/dt(m)]
# Hence, the right hand side of the DE can be defined as follows:
def vehicle_dynamics(t, state):
    x, y, v_x, v_y, m = state  # Unpacking the state vector
    v = np.sqrt(v_x**2 + v_y**2)  # Calculating the velocity magnitude

    current_T = T if m > m_d else 0.0
    
    dt_x = v_x
    dt_y = v_y

    if v == 0:
        thrust_x = 0
        thrust_y = current_T
    else:
        thrust_x = current_T * v_x/v
        thrust_y = current_T * v_y/v

    dt_vx = thrust_x/m - (1/2)*(p(y)*Cd*A/m)*v*v_x
    dt_vy = thrust_y/m - (1/2)*(p(y)*Cd*A/m)*v*v_y - g(y) + v_x**2/(R_e+y)
    dt_m = -current_T/(I_sp*g_0)
    return np.array([dt_x, dt_y, dt_vx, dt_vy, dt_m])

# Funtion for handling ground impact
def ground_impact(t, state):
    return state[1]
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
plt.subplot(1,3,1)
plt.plot(solution.y[0], solution.y[1], label = "y(x)")
plt.xlabel("x-Displacement (m)")
plt.ylabel("y-Displacement (m)")
plt.grid()
plt.subplot(1,3,2)
plt.plot(solution.t, solution.y[0], label = "x(t)")
plt.xlabel("time (s)")
plt.ylabel("x-Displacement (m)")
plt.grid()
plt.subplot(1,3,3)
plt.plot(solution.t, solution.y[1], label = "y(t)")
plt.xlabel("time (s)")
plt.ylabel("y-Displacement (m)")
plt.grid()
plt.show()