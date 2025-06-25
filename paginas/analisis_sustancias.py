# paginas/analisis_sustancias.py
# ==============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==============================================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import statsmodels.api as sm

# Estilo visual para los gráficos
sns.set_theme(style="whitegrid", palette="viridis")

# ==============================================================================
# 2. FUNCIÓN DE ANÁLISIS AUTOMÁTICO
# ==============================================================================
def analizar_y_mostrar_en_app(df, var_fila, var_col, texto_interpretacion):
    """
    Perform the analysis and display the results and graphs directly in the Streamlit app.
    Include a customized interpretation text..
    """
    st.header(f"Analysis: '{var_fila.replace('_', ' ').title()}' vs '{var_col.replace('_', ' ').title()}'")

    if var_fila not in df.columns or var_col not in df.columns:
        st.error(f"Error: One or both columns ('{var_fila}', '{var_col}') not found.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Data Tables")
        contingency_table = pd.crosstab(df[var_fila], df[var_col])
        st.write("**Contingency Table (Counts):**")
        st.dataframe(contingency_table)

        st.write("**Column-wise Percentages:**")
        percentages = pd.crosstab(df[var_fila], df[var_col], normalize='columns').apply(lambda r: r*100, axis=0).round(2)
        st.dataframe(percentages.astype(str) + '%')

    with col2:
        st.subheader("Chi-Square Test")
        try:
            chi2, p_value, dof, _ = chi2_contingency(contingency_table)
            st.metric(label="P-Value", value=f"{p_value:.4f}")

            if p_value < 0.05:
                st.success("Statistically Significant Association!")
                tabla_obj = sm.stats.Table(contingency_table)
                residuos_corregidos = tabla_obj.standardized_resids

                fig_heatmap, ax_heatmap = plt.subplots()
                sns.heatmap(residuos_corregidos, annot=True, fmt=".2f", cmap="coolwarm_r", center=0, ax=ax_heatmap)
                ax_heatmap.set_title(f'Residuals Heatmap')
                st.pyplot(fig_heatmap)
            else:
                st.info("No evidence of significant association.")
        except ValueError as e:
            st.error(f"Error calculating Chi-Square: {e}.")

    st.subheader("Proportion Chart")
    probyciones = pd.crosstab(df[var_col], df[var_fila], normalize='index')

    fig_bar, ax_bar = plt.subplots(figsize=(12, 5))
    probyciones.plot(kind='bar', stacked=True, colormap='viridis', ax=ax_bar)
    ax_bar.set_title(f'Proportion of "{var_fila.replace("_", " ").title()}" by "{var_col.replace("_", " ").title()}"')
    ax_bar.set_ylabel('Proportion')
    ax_bar.set_xlabel(var_col.replace("_", " ").title())
    ax_bar.tick_params(axis='x', rotation=45)
    ax_bar.legend(title=var_fila.replace("_", " ").title())
    st.pyplot(fig_bar)

    # --- ZONA DE INTERPRETACIÓN ---
    st.subheader("✍️ Analysis Interpretation")
    st.markdown(texto_interpretacion) # Mostramos el texto personalizado

    st.markdown("---")


# ==============================================================================
# 3. EJECUCIÓN PRINCIPAL DE LA PÁGINA
# ==============================================================================
def mostrar():
    st.title("📊 Dashboard for Accidentality and Substance Use Analysis")
    st.write("""
    This section analyzes and explores relationships between alcohol/drug use,
    demographic factors, and accident characteristics.
    """)

    file_path = 'datos/Datos_accidentalidad.csv' # RUTA CORREGIDA

    try:
        @st.cache_data
        def cargar_y_limpiar_datos(path):
            df = pd.read_csv(path, sep=',', on_bad_lines='skip', low_memory=False)

            # Limpieza de datos
            df['positiva_droga'] = df['positiva_droga'].fillna(0).map({1.0: 'S', 0: 'N', '1': 'S', '0':'N'}).fillna('N')
            df['positiva_alcohol'] = df['positiva_alcohol'].astype(str).str.strip().replace({'nan': 'N', 'S':'S', 'N':'N'}).fillna('N')
            df_limpio = df.dropna(subset=['sexo', 'rango_edad', 'tipo_accidente', 'tipo_vehiculo']).copy()
            df_limpio = df_limpio[df_limpio['sexo'].isin(['Hombre', 'Mujer'])]

            top_accidentes = df_limpio['tipo_accidente'].value_counts().nlargest(5).index
            df_limpio['tipo_accidente_simplificado'] = df_limpio['tipo_accidente'].apply(lambda x: x if x in top_accidentes else 'Otro')

            return df_limpio

        df_limpio = cargar_y_limpiar_datos(file_path)

        st.sidebar.header("Substance Analysis")
        st.sidebar.success(f"Data loaded and processed: {df_limpio.shape[0]} records ready for analysis.")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Analyses Performed:")
        st.sidebar.write("1. Drug Use vs. gender")
        st.sidebar.write("2. Alcohol Use vs. Age Range")
        st.sidebar.write("3. Alcohol Use vs. Drug Use")
        st.sidebar.write("4. Accident Type vs. Alcohol Use")


        # --- INICIAMOS LOS ANÁLISIS ---

        texto_analisis_1 = """
        ****Key Conclusions:****  
        *   There is a clear significant relationship (p < 0.05) between drug use and male gender in traffic accidents.  
        *   The residuals heatmap shows that men have a significantly higher propensity to test positive for drugs compared to women, with an 11.5% higher rate than that of women.

        ****Insights and Next Steps:****  
        *   This finding suggests that drug and driving awareness campaigns could have a greater impact if focused on the male audience, as well as highlighting the clear relationship between drug and alcohol use while driving.

        """
        analizar_y_mostrar_en_app(df_limpio, var_fila='positiva_droga', var_col='sexo', texto_interpretacion=texto_analisis_1)

        texto_analisis_2 = """
        ****Key Conclusions:****  
        *   Given the p-value < 0.05, there is a significant association between age range and alcohol consumption.  
        *   The bar chart shows that men have a significantly higher rate of positive alcohol tests among young adults (18-24 years) and early adults (25-34 years) compared to older age groups.  
        *   The age ranges 25-34 and 35-44 show the highest proportions of positive alcohol tests.  
        *   The residuals heatmap indicates that men aged 25-34 have a significantly higher propensity to test positive for alcohol, with 10% more than women of the same age.

        ****Insights and Next Steps:****  
        *   Prevention policies should focus on these age groups, possibly with more frequent breathalyzer checks in nightlife areas frequented by this demographic profile.

        """
        analizar_y_mostrar_en_app(df_limpio, var_fila='positiva_alcohol', var_col='rango_edad', texto_interpretacion=texto_analisis_2)

        texto_analisis_3 = """
        ****Key Conclusions:****  
        *   There is a strong positive correlation with a p-value less than 0.05. Individuals who test positive for drugs are much more likely to also test positive for alcohol, and vice versa.

        ****Insights and Next Steps:****  
        *   This indicates a pattern of poly-substance use. Detection tests should ideally be conducted for both substances simultaneously, as a positive result for one is a strong indicator of the possible presence of the other.

        """
        analizar_y_mostrar_en_app(df_limpio, var_fila='positiva_alcohol', var_col='positiva_droga', texto_interpretacion=texto_analisis_3)

        texto_analisis_4 = """
        ****Key Conclusions:****  
        *   Alcohol consumption appears to be significantly more associated with 'Run-off-road' and 'Other' types of accidents than with frontal-lateral collisions.  
        *   Additionally, collisions with fixed obstacles stand out as an accident type with a high proportion of positive alcohol tests, which makes complete sense and is clearly observed in the residuals heatmap as the most notable difference.

        ****Insights and Next Steps:****  
        *   Accident investigations involving run-off-road incidents should prioritize breathalyzer testing as one of the most probable causes.

        """
        analizar_y_mostrar_en_app(df_limpio, var_fila='positiva_alcohol', var_col='tipo_accidente_simplificado', texto_interpretacion=texto_analisis_4)

    except FileNotFoundError:
        st.error(f"ERROR: File not found '{file_path}'. Make sure it's in the folder 'datos/'.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")