# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import joblib

def mostrar():
    st.title("🔍 Injury Severity Prediction in Accidents")
    st.markdown("---")
    st.markdown("Enter the accident details and the system will estimate its severity.")

    model = joblib.load("modelos/modelo_xgb_agrupado.pkl")
    encoder = joblib.load("modelos/label_encoder_xgb_agrupado.pkl")

    st.sidebar.subheader("Context before boarding the vehicle")

    hora = st.sidebar.slider("Time of the day", 0.0, 23.99, 12.0, 0.25, format="%.2f")
    sexo = st.sidebar.selectbox("Gender", ['Hombre', 'Mujer'])
    meteo = st.sidebar.selectbox("Weather condition", ['Despejado', 'Nublado', 'Lluvia débil', 'Lluvia intensa', 'Granizo', 'Niebla', 'Viento fuerte', 'Otros'])
    vehiculo = st.sidebar.selectbox("Type of vehicle", ['Turismo', 'Motocicleta', 'Bicicleta', 'Camión', 'Autobús', 'Furgoneta', 'Otros'])
    persona = st.sidebar.selectbox("Type of person", ['Conductor', 'Pasajero', 'Peatón'])
    edad = st.sidebar.selectbox("Age range", ['0-15', '16-25', '26-40', '41-65', '66+'])
    alcohol = st.sidebar.selectbox("Positive for alcohol?", ['No', 'Sí'])
    droga = st.sidebar.selectbox("Positive for drugs?", ['No', 'Sí'])

    if st.button("🧠 Predict"):
        datos = pd.DataFrame([{
            'hora_num': hora,
            'sexo': sexo,
            'estado_meteorológico': meteo,
            'tipo_vehiculo': vehiculo,
            'tipo_persona': persona,
            'rango_edad': edad,
            'positiva_alcohol': alcohol,
            'positiva_droga': droga
        }])

        proba = model.predict_proba(datos)[0]
        clase = encoder.inverse_transform([np.argmax(proba)])[0]

        st.success(f"**Injury Severity**: {clase}")
        st.markdown("#### Probability distribution:")
        for i, c in enumerate(encoder.classes_):
            st.write(f"{c}: {proba[i]*100:.2f}%")
