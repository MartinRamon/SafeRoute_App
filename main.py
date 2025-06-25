# main.py
import streamlit as st
from streamlit_option_menu import option_menu
# Importa todos tus módulos desde la carpeta 'paginas'
# Asegúrate de que estos archivos .py existen en la carpeta 'paginas/'
from paginas import presentacion, analisis_categorico, analisis_sustancias, mapa_calor, rutas, lesividad, tipo_accidente

st.set_page_config(page_title="SafeRoute - Seguridad Vial Inteligente", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            font-size: 28px !important;
            text-align: left !important;
        }

        /* Eliminar el header superior de Streamlit (para evitar huecos) */
        header {
            visibility: hidden;
        }

        /* Título SafeRoute */
        .menu-header {
            background-color: #2c3e50;
            color: white;
            padding: 2.5rem 0;
            font-size: 56px;
            font-weight: 900;
            text-align: center;
            width: 100%;
            margin-bottom: 0;
        }

        .stApp {
            background-color: white;
        }

        .block-container {
            padding-top: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        .css-18ni7ap {
            max-width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* ---------- BARRA LATERAL ---------- */
        section[data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
        padding: 1rem 1rem 1.5rem 1rem;
        height: 100vh;
        margin-top: 0 !important;
        text-align: left;
    }

        /* Título dentro del sidebar (como “Filtros…”) */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            font-size: 36px !important;
            font-weight: 900 !important;
            color: white !important;
            margin-bottom: 1.2rem !important;
        }

        /* Etiquetas: Rango horario, Sexo, etc. */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] p {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: white !important;
            margin-bottom: 0.5rem !important;
        }

        /* Componentes de entrada */
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] select,
        section[data-testid="stSidebar"] textarea {
            font-size: 26px !important;
            padding: 0.8rem !important;
        }

        /* Espaciado entre componentes */
        section[data-testid="stSidebar"] > div > div {
            margin-bottom: 1.8rem !important;
        }

        button[kind="primary"] {
            font-size: 26px !important;
            padding: 0.7rem 1.5rem !important;
        }

        .stForm {
            background-color: transparent;
            border: none;
        }

        .stForm > div {
            box-shadow: none !important;
            border: none !important;
        }

        .nav-container {
            background-color: #2c3e50 !important;
        }

        .nav-link {
            background-color: #2c3e50 !important;
        }

        .nav-link:hover {
            background-color: #3a3a47 !important;
        }

        h1 {
            font-size: 42px !important;
            font-weight: 800;
            color: #2c3e50;
        }

    </style>
""", unsafe_allow_html=True)


# ---------- ENCABEZADO ----------
st.markdown('<div class="menu-header">SafeRoute</div>', unsafe_allow_html=True)

# ---------- MENÚ HORIZONTAL CENTRADO Y ELEGANTE ----------
selected = option_menu(
    menu_title=None,
    options=[
        "Presentation",
        "Accidents Heatmap",
        "Routes",
        "Categorical Analysis",
        "Substance Use Analysis", # <-- AÑADIDO
        "Injury Severity Prediction",
        "Accident Type Prediction"
    ],
    icons=[
        "house", "map", "geo-alt", "bar-chart-steps", "eyedropper", "graph-up", "exclamation-triangle" # <-- ICONOS ACTUALIZADOS
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0",
            "margin": "0 auto",
            "background-color": "#2c3e50",
            "width": "90%", # Ajustado para que quepan más opciones
            "display": "flex",
            "justify-content": "center",
            "border-radius": "8px"
        },
        "nav-link": {
            "font-size": "22px", # Ligeramente más pequeño
            "color": "white",
            "padding": "20px 25px", # Ajustado
            "margin": "0px",
            "text-align": "center"
        },
        "nav-link-selected": {
            "background-color": "#1abc9c",
            "color": "white"
        },
        "icon": {"color": "white", "font-size": "26px"},
    }
)

# ---------- ENRUTAMIENTO A LAS PÁGINAS ----------
if selected == "Presentation":
    presentacion.mostrar()
elif selected == "Accidents Heatmap":
    mapa_calor.mostrar()
elif selected == "Routes":
    rutas.mostrar()
elif selected == "Categorical Analysis":
    analisis_categorico.mostrar()
elif selected == "Substance Use Analysis": # <-- AÑADIDO
    analisis_sustancias.mostrar()
elif selected == "Injury Severity Prediction":
    lesividad.mostrar()
elif selected == "Accident Type Prediction":
    tipo_accidente.mostrar()