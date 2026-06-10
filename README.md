# Orbital Trajectory & Telemetry Suite

A two-module Python flight mechanics workbench for simulating and 
solving launch vehicle trajectories and circular orbit insertions. 
Built using SciPy numerical integrators and optimisers, deployed 
as an interactive Streamlit web application.

**Live App:** [orbital-trajectory.streamlit.app](https://orbital-trajectory.streamlit.app)

## Overview

Developed to apply numerical methods coursework (IVPs, BVPs, 
optimisation) directly to an aerospace engineering problem. Models 
a two-burn Hohmann-style ascent: a gravity-turn powered ascent phase, 
ballistic coast to apogee, and a circularisation kick burn.

The physics engine accounts for:
- Variable mass (Tsiolkovsky propellant depletion)
- Dynamic atmospheric drag using a real atmospheric density 
  dataset interpolated across scale heights
- Inverse-square gravitational field
- Gravity-turn thrust vectoring with configurable vertical 
  ascent clearance threshold

## Module 1: Forward Trajectory Simulator (IVP)

<img src="images/ivp-simulator.png" width="80%">

Numerically integrates the equations of motion for a launch vehicle 
under known parameters using `scipy.integrate.solve_ivp` (RK45). 
Outputs a polar trajectory plot, altitude profile, and 
tangential velocity profile.

## Equations of Motion (Polar Coordinates)

$$\frac{dr}{dt} = v_r$$

$$\frac{d\theta}{dt} = \frac{v_\theta}{r}$$

$$\frac{dv_\theta}{dt} = \frac{T_\theta}{m} - \frac{1}{2}\frac{\rho C_d A}{m}v \cdot v_\theta - \frac{v_r v_\theta}{r}$$

$$\frac{dv_r}{dt} = \frac{T_r}{m} - \frac{1}{2}\frac{\rho C_d A}{m}v \cdot v_r - g(r) + \frac{v_\theta^2}{r}$$

$$\frac{dm}{dt} = -\frac{T}{I_{sp} \cdot g_0}$$

**Inputs:** Dry mass, fuel mass, thrust, I_sp, drag coefficient, 
cross-sectional area, vertical ascent threshold, starting altitude

## Module 2: Orbital Insertion Solver (BVP)

<img src="images/bvp-solver.png" width="80%">

Solves the inverse problem: given a target circular orbit altitude, 
find the vehicle parameters that achieve it. Formulated as a 
3-degree-of-freedom boundary value problem and solved using 
`scipy.optimize.least_squares`.

**Three-phase mission architecture:**
1. **Ascent burn** — gravity-turn powered climb to staging altitude
2. **Coast to apogee** — ballistic trajectory with apogee detection event
3. **Apogee kick** — circularisation burn to achieve target tangential velocity

**Boundary conditions:**
- Final altitude = target orbit altitude
- Final tangential velocity = circular orbit speed
- Final radial velocity = 0

**Solvable parameters (leave any 3 blank):**
Dry mass, fuel mass, thrust, pitch-over angle, ascent fuel allocation

**Solver:** `scipy.optimize.least_squares` with dynamic variable
scaling, and physically-motivated initial guesses

## Atmospheric Model

Atmospheric density interpolated from a real altitude-density 
dataset using log-space interpolation (`scipy.interpolate.interp1d`) 
for exponential accuracy across scale heights up to 1000 km.

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| SciPy | ODE integration, optimisation |
| NumPy | Numerical computation |
| Matplotlib | Telemetry plotting |
| Pandas | Atmospheric data loading |
| Streamlit | Interactive web deployment |

## Skills Demonstrated

- Numerical integration of coupled ODEs (IVP)
- Boundary value problem formulation and solution
- Non-linear least-squares optimisation
- Atmospheric and gravitational modelling
- Flight mechanics and orbital mechanics
- Interactive scientific application deployment