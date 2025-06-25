# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 17:32:18 2025

@author: Usuario
"""

import streamlit as st
import pandas as pd
import openrouteservice
import folium
import time
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
from shapely.geometry import Point, LineString

def mostrar():
    st.title("🚦 SafeRoute: Find the safeness of your route in Madrid")
    st.markdown("---")
    st.markdown("Select the **street** and the **number** for origin and destiantion within Madrid.")

    # ---------- Cargar listado de calles ----------
    try:
        calles_df = pd.read_csv("datos/VialesVigentes_procesado.csv", encoding='latin-1', sep=';')
        lista_calles = sorted(calles_df["VIA_COMPLETA"].dropna().unique().tolist())
    except Exception as e:
        st.error(f"❌ Error loading street file: {e}")
        return

    # ---------- Cargar datos de accidentes ----------
    try:
        acc_df = pd.read_csv("datos/Datos_accidentalidad.csv", low_memory=False)

        def safe_to_float(x):
            try:
                return float(str(x).replace(',', '.'))
            except:
                return None

        acc_df = acc_df.dropna(subset=['coordenada_x_utm', 'coordenada_y_utm']).copy()
        acc_df['coordenada_x_utm'] = acc_df['coordenada_x_utm'].apply(safe_to_float)
        acc_df['coordenada_y_utm'] = acc_df['coordenada_y_utm'].apply(safe_to_float)
        acc_df = acc_df.dropna(subset=['coordenada_x_utm', 'coordenada_y_utm'])

        transformer = Transformer.from_crs("epsg:25830", "epsg:4326", always_xy=True)
        acc_df['lon'], acc_df['lat'] = transformer.transform(
            acc_df['coordenada_x_utm'].values, acc_df['coordenada_y_utm'].values
        )
    except Exception as e:
        st.error(f"❌ Error processing accidents file: {e}")
        return

    # ---------- Inicializar servicios ----------
    geolocator = Nominatim(user_agent="safe_route_app")
    ors_client = openrouteservice.Client(key="5b3ce3597851110001cf6248ab8202387c5c4077aefc78dff4efb321")  # Sustituye con tu API key

    # ---------- Inicializar estado ----------
    for key in ["coords", "riesgos", "origen_coords", "destino_coords"]:
        if key not in st.session_state:
            st.session_state[key] = None

    # ---------- Función geocodificación ----------
    def geocode_address(address):
        try:
            location = geolocator.geocode(address + ", Madrid, España", timeout=5)
            if location:
                return location.latitude, location.longitude
        except GeocoderTimedOut:
            time.sleep(1)
            return geocode_address(address)
        except Exception:
            return None
        return None

    # ---------- Función cálculo riesgos ----------


# Función optimizada con índice espacial
    def calcular_riesgos_por_tramos_km(coords, acc_coords, tramo_km=1.0, buffer_m=100):
        linea_ruta = LineString(coords)
        tramo_grados = tramo_km / 111.3  # ≈ 1 km en grados
    
        # Crear puntos de tramos a lo largo de la ruta
        puntos_tramo = []
        d = 0.0
        while d < linea_ruta.length:
            puntos_tramo.append(linea_ruta.interpolate(d))
            d += tramo_grados
    
        # Crear índice espacial con los puntos de accidentes
        acc_points = [Point(lon, lat) for lon, lat in acc_coords]
        rtree = STRtree(acc_points)
    
        # Calcular riesgos para cada punto de tramo usando el índice
        riesgos = []
        for p in puntos_tramo:
            nearby = rtree.query(p.buffer(buffer_m / 111320))  # buffer en grados
            count = len(nearby)
    
            if count > 100:
                riesgos.append(1.0)  # Alto riesgo
            elif count >= 50:
                riesgos.append(0.6)  # Medio riesgo
            else:
                riesgos.append(0.2)  # Bajo riesgo
    
        # Construir tramos visuales entre los puntos
        tramos = []
        for i in range(len(puntos_tramo) - 1):
            tramos.append([puntos_tramo[i], puntos_tramo[i + 1]])
    
        return tramos, riesgos


    # ---------- Formulario ----------
    with st.form("form_ruta_segura"):
        col1, col2 = st.columns(2)
        with col1:
            calle_origen = st.selectbox("📍 Origin Street", lista_calles)
            numero_origen = st.text_input("Number (Optional)", placeholder="Ej: 45", key="num_origen")
            origen_text = f"{calle_origen} {numero_origen}"
        with col2:
            calle_destino = st.selectbox("🏁 Destination Street", lista_calles)
            numero_destino = st.text_input("Number (Optional)", placeholder="Ej: 12", key="num_destino")
            destino_text = f"{calle_destino} {numero_destino}"

        calcular = st.form_submit_button("🚗 Calculate Safe Route")

    # ---------- Cálculo ruta ----------
    if calcular:
        origen_coords = geocode_address(origen_text)
        destino_coords = geocode_address(destino_text)

        if origen_coords and destino_coords:
            try:
                route = ors_client.directions(
                    coordinates=[(origen_coords[1], origen_coords[0]), (destino_coords[1], destino_coords[0])],
                    profile='driving-car',
                    format='geojson'
                )
                coords = route['features'][0]['geometry']['coordinates']
                tramos, riesgos = calcular_riesgos_por_tramos_km(
                    coords, list(zip(acc_df["lon"], acc_df["lat"])), buffer_m=100
                )

                st.session_state.coords = tramos
                st.session_state.riesgos = riesgos
                st.session_state.origen_coords = origen_coords
                st.session_state.destino_coords = destino_coords

                st.success("✅ Route succesfully calculated.")
            except Exception as e:
                st.error(f"❌ Error calculating the route: {e}")
        else:
            st.warning("⚠️ One or both directions could not be localizated.")

    # ---------- Mostrar mapa ----------
    if st.session_state.coords and st.session_state.riesgos:
        map_center = [
            (st.session_state.origen_coords[0] + st.session_state.destino_coords[0]) / 2,
            (st.session_state.origen_coords[1] + st.session_state.destino_coords[1]) / 2
        ]
        m = folium.Map(location=map_center, zoom_start=13)

        for i, tramo in enumerate(st.session_state.coords):
            start = tramo[0]
            end = tramo[1]
            latlon_start = [start.y, start.x]
            latlon_end = [end.y, end.x]

            riesgo = st.session_state.riesgos[i]
            color = "green" if riesgo == 0.2 else "orange" if riesgo == 0.6 else "red"
            tooltip = f"Risk: {'Low' if riesgo == 0.2 else 'Mid' if riesgo == 0.6 else 'High'}"

            folium.PolyLine(
                [latlon_start, latlon_end],
                color=color,
                weight=5,
                tooltip=tooltip
            ).add_to(m)

        folium.Marker(
            location=st.session_state.origen_coords,
            popup="Start",
            icon=folium.Icon(color="blue")
        ).add_to(m)

        folium.Marker(
            location=st.session_state.destino_coords,
            popup="Finish",
            icon=folium.Icon(color="purple")
        ).add_to(m)

        st_folium(m, width=1000, height=600)
