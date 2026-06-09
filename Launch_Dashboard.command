#!/bin/bash
cd "$(dirname "$0")"
streamlit run Orbital_Trajectory_Solver.py --server.headless true &
sleep 2
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --app=http://localhost:8501