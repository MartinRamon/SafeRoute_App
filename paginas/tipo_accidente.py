# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 17:48:22 2025

@author: agime
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib

def mostrar():
    st.title("🔍 Type of Accident Prediction")
    st.markdown("Fill in the fields and the model will predict the most probable type of accident.")

    model = joblib.load("modelos/modelo_xgb_accidentes_final.pkl")
    encoder = joblib.load("modelos/label_encoder_accidentes_final.pkl")

    st.sidebar.subheader("Context before boarding the vehicle")

    hora = st.sidebar.slider("Time of the day", 0.0, 23.99, 12.0, 0.25, format="%.2f")
    sexo = st.sidebar.selectbox("Gender", ['Hombre', 'Mujer'])
    estado = st.sidebar.selectbox("Weather conditons", ['Despejado', 'Nublado', 'Lluvia débil', 'Lluvia intensa', 'Granizo', 'Niebla', 'Viento fuerte', 'Otros'])
    vehiculo = st.sidebar.selectbox("Type of vechicle", ['Turismo', 'Motocicleta', 'Bicicleta', 'Camión', 'Autobús', 'Furgoneta', 'Otros'])
    persona = st.sidebar.selectbox("Type of person", ['Conductor', 'Pasajero', 'Peatón'])
    edad = st.sidebar.selectbox("Age Range", ['0-15', '16-25', '26-40', '41-65', '66+'])
    alcohol = st.sidebar.selectbox("Positive for alcohol?", ['No', 'Sí'])
    droga = st.sidebar.selectbox("Positive for drugs?", ['No', 'Sí'])

    if st.button("Predict Type of Accident"):
        # Convertir hora_num en hora_rango
        if hora <= 6:
            hora_rango = "Noche"
        elif hora <= 12:
            hora_rango = "Mañana"
        elif hora <= 18:
            hora_rango = "Tarde"
        else:
            hora_rango = "Noche (tarde)"
        
        entrada = pd.DataFrame([{
            'hora_rango': hora_rango,
            'sexo': sexo,
            'estado_meteorológico': estado,
            'tipo_vehiculo': vehiculo,
            'tipo_persona': persona,
            'rango_edad': edad,
            'positiva_alcohol': 1 if alcohol == "Sí" else 0,
            'positiva_droga': 1 if droga == "Sí" else 0
        }])



        proba = model.predict_proba(entrada)[0]
        pred_idx = np.argmax(proba)
        tipo_predicho = encoder.inverse_transform([pred_idx])[0]

        st.success(f"Predicted Type of Accident: **{tipo_predicho}**")

        st.markdown("#### Probability distribution:")
        for i, tipo in enumerate(encoder.classes_):
            st.write(f"{tipo}: {proba[i]*100:.2f}%")
