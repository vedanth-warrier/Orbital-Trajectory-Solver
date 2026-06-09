import streamlit as st

# 1. Configure the Main Page
st.set_page_config(
    page_title="Orbital Trajectory Suite",
    page_icon="🚀",
    layout="wide"
)

# 2. Build the Landing Interface
st.title("🚀 Orbital Trajectory & Telemetry Suite")

st.markdown("""
Welcome to the Flight Dynamics Dashboard. 

This application is split into two primary computational modules. Please select a module below or use the sidebar navigation to begin.
""")

st.divider()

# 3. Create Explicit Page Redirections
col1, col2 = st.columns(2)

with col1:
    st.subheader("Phase 1: Kinematic IVP Engine")
    st.write("Simulate launch profiles using purely kinematic gravity turns and launch tower clearance logic.")
    # This button redirects to your existing Phase 1 script
    st.page_link("pages/IVP_Engine.py", label="Launch IVP Engine", icon="☄️")

with col2:
    st.subheader("Phase 2: BVP Optimizer")
    st.write("Calculate explicit pitch profiles to mathematically target specific orbital insertion boundaries.")
    # This button redirects to your new Phase 2 script
    st.page_link("pages/BVP_Optimiser.py", label="Launch BVP Optimizer", icon="🎯")

st.divider()

# 4. Footer Information
st.caption("Developed using Python, SciPy, and Streamlit.")