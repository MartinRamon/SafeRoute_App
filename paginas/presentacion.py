# paginas/presentacion.py
import streamlit as st # <-- AÑADIDO

def mostrar():
    st.markdown("""
    <p style='font-size: 24px; text-align: justify; line-height: 1.7em;'>
    <b>SafeRoute</b> is a comprehensive platform designed to analyze, visualize, and predict traffic accidents in urban environments.
    Its goal is to provide intelligent tools to improve mobility and road safety by applying data science, geographic visualization techniques,
    and machine learning models on real data from the city of Madrid.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-size: 30px;'>🧭 Main Features</h2>", unsafe_allow_html=True) # Corregido font-size

    st.markdown("""
    <div style='font-size: 20px; line-height: 1.6em; text-align: justify;'>

    🔥 <b>Heatmap:</b> Visualizes the areas with the highest density of accidents, filtering by time of day, weather conditions, vehicle type, person type, etc.

    🗺️ <b>Safe Routes:</b> Shows the level of danger on the route between two locations so users can decide whether to avoid those segments.

    📊 <b>Data Analysis:</b> Graphically examines the dataset, allowing exploration of patterns based on key variables such as gender, age, accident type, or vehicle.

    ⚠️ <b>Injury Severity Prediction:</b> Estimates the severity of an accident (minor, serious, or fatal) based on pre-accident conditions.

    🚨 <b>Accident Type Prediction:</b> Predicts whether a collision, run-over, crash, or another incident will occur based on the user profile.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-size: 30px;'>🧠 Target Audience</h2>", unsafe_allow_html=True) # Corregido font-size

    st.markdown("""
    <div style='font-size: 24px; text-align: justify; line-height: 1.7em;'>
    SafeRoute is aimed at urban mobility officials, road safety technicians, data analysts, and citizens interested in understanding their city's road environment.
    It adds value to both strategic planning and citizen awareness and informed decision-making.
    </div>
    """, unsafe_allow_html=True)