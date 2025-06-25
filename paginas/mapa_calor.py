# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from pyproj import Transformer
from streamlit_folium import folium_static

def mostrar():
    st.title("🗺️ Accident Heatmap in Madrid")
    st.markdown("---")
    st.markdown("Visualize the areas with the highest concentration of accidents based on multiple variables.")

    df = pd.read_csv("datos/Datos_accidentalidad.csv", low_memory=False)

    def safe_to_float(x):
        try:
            return float(str(x).replace(',', '.'))
        except:
            return None

    df = df.dropna(subset=['coordenada_x_utm', 'coordenada_y_utm']).copy()
    df['coordenada_x_utm'] = df['coordenada_x_utm'].apply(safe_to_float)
    df['coordenada_y_utm'] = df['coordenada_y_utm'].apply(safe_to_float)
    df = df.dropna(subset=['coordenada_x_utm', 'coordenada_y_utm'])

    transformer = Transformer.from_crs("epsg:25830", "epsg:4326", always_xy=True)
    df['lon'], df['lat'] = transformer.transform(df['coordenada_x_utm'].values, df['coordenada_y_utm'].values)

    df['hora_num'] = pd.to_datetime(df['hora'], errors='coerce').dt.hour.fillna(-1).astype(int)

    with st.sidebar:
        st.subheader("Heatmap Filters")
        hora_range = st.slider("Time interval", 0, 23, (0, 23))
        sexo_opciones = sorted(df['sexo'].dropna().unique())
        sexo_seleccion = st.selectbox("Gender", ["Todos"] + sexo_opciones)
        sexo = sexo_opciones if sexo_seleccion == "Todos" else [sexo_seleccion]

        # Estado meteorológico
        estado_opciones = sorted(df['estado_meteorológico'].dropna().unique())
        estado_seleccion = st.selectbox("Weather condition", ["Todos"] + estado_opciones)
        estado = estado_opciones if estado_seleccion == "Todos" else [estado_seleccion]
        
        # Tipo de vehículo
        vehiculo_opciones = sorted(df['tipo_vehiculo'].dropna().unique())
        vehiculo_seleccion = st.selectbox("Type of vehicle", ["Todos"] + vehiculo_opciones)
        vehiculo = vehiculo_opciones if vehiculo_seleccion == "Todos" else [vehiculo_seleccion]
        
        # Tipo de accidente
        accidente_opciones = sorted(df['tipo_accidente'].dropna().unique())
        accidente_seleccion = st.selectbox("Type of accident", ["Todos"] + accidente_opciones)
        accidente = accidente_opciones if accidente_seleccion == "Todos" else [accidente_seleccion]

        umbral = st.slider("Heat threshold (minimum accidents per spot)", 1, 20, 5)

    df_filtrado = df[
        (df['hora_num'] >= hora_range[0]) & (df['hora_num'] <= hora_range[1]) &
        (df['sexo'].isin(sexo)) &
        (df['estado_meteorológico'].isin(estado)) &
        (df['tipo_vehiculo'].isin(vehiculo)) &
        (df['tipo_accidente'].isin(accidente))
    ]

    heatmap_data = (
        df_filtrado.groupby(['lat', 'lon'])
        .size()
        .reset_index(name='count')
        .query(f'count >= {umbral}')
    )

    heat_data = heatmap_data[['lat', 'lon', 'count']].values.tolist()

    m = folium.Map(location=[40.4168, -3.7038], zoom_start=11, tiles='CartoDB positron')
    HeatMap(
    heat_data,
    radius=12,
    blur=15,
    min_opacity=0.4,
    gradient={0.2: 'blue', 0.6: 'orange', 0.9: 'red'}
        ).add_to(m)

    folium_static(m, width=3750, height=1550)

    st.success(f"{len(heatmap_data)} hotspots have been visualized.")
