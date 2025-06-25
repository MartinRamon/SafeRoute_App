# paginas/analisis_categorico.py
import streamlit as st
import pandas as pd
import numpy as np
import re
import unicodedata
from scipy.stats import chi2_contingency
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# --- Funciones de Limpieza y Preprocesamiento ---
@st.cache_data
def clean_string_for_names(text):
    if pd.isna(text) or not isinstance(text, str):
        return str(text) if not pd.isna(text) else np.nan
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r'[^a-z0-9_]', '', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

@st.cache_data
def load_and_clean_data(file_path="./datos/Datos_accidentalidad.csv"): # <-- ¡NOMBRE DEL ARCHIVO CORREGIDO AQUÍ!
    try:
        df = pd.read_csv(file_path, sep=",", encoding="utf-8")
        st.success(f"File '{file_path}' loaded succesfully. Incial observations: {len(df)}")
    except FileNotFoundError:
        st.error(f"¡Error! The file '{file_path}' was not found. Make sure the file is in the right directory.")
        return None
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return None

    df.columns = [clean_string_for_names(col) for col in df.columns]

    categorical_cols_to_clean = [
        'tipo_accidente', 'estado_meteorologico', 'cod_distrito',
        'tipo_vehiculo', 'tipo_persona', 'rango_edad', 'sexo',
        'lesividad', 'positiva_alcohol', 'positiva_droga',
        'mes', 'dia_semana'
    ]

    for col in categorical_cols_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'': np.nan, 'nan': np.nan, 'NA': np.nan, 'unknown': np.nan, '-': np.nan})
            
            if col == 'positiva_alcohol':
                df[col] = df[col].str.lower().replace({'n': 'n', 's': 's'}).fillna('n')
            elif col == 'positiva_droga':
                df[col] = df[col].astype(str).str.lower().str.strip()
                df[col] = df[col].apply(lambda x: 's' if str(x) == '10' else ('n' if str(x)=='n' else np.nan)).fillna('n')
            
            if col in ['positiva_alcohol', 'positiva_droga']:
                df[col] = pd.Categorical(df[col], categories=['n', 's'])
            elif col == 'mes':
                df[col] = df[col].astype(str)
                df[col] = pd.Categorical(df[col], categories=[str(i) for i in range(1,13)])
            elif col == 'dia_semana':
                df[col] = df[col].astype(str)
                df[col] = pd.Categorical(df[col], categories=[str(i) for i in range(7)])
            else:
                df[col] = df[col].astype('category')
            
            if df[col].isnull().any():
                df[col].fillna(df[col].mode()[0], inplace=True)
            
            if col not in ['mes', 'dia_semana']: # Estas columnas ya se han limpiado a 'str' antes de convertirse a Categorical
                df[col] = df[col].apply(lambda x: clean_string_for_names(x) if pd.notna(x) else x)
            df[col] = df[col].astype('category')
        
    if 'fecha' in df.columns and 'hora' in df.columns:
        df['fecha_parsed'] = pd.to_datetime(df['fecha'], format="%d/%m/%Y", errors='coerce')
        if 'mes' not in df.columns or df['mes'].isnull().any():
            df['mes'] = df['fecha_parsed'].dt.month.astype(str).fillna(df['fecha_parsed'].dt.month.mode()[0]).apply(clean_string_for_names)
            # CORRECCIÓN DE INDEXACIÓN AQUÍ
            df['mes'] = pd.Categorical(df['mes'], categories=[clean_string_for_names(str(i)) for i in range(1,13)]) 
        if 'dia_semana' not in df.columns or df['dia_semana'].isnull().any():
            df['dia_semana'] = df['fecha_parsed'].dt.dayofweek.astype(str).fillna(df['fecha_parsed'].dt.dayofweek.mode()[0]).apply(clean_string_for_names)
            # CORRECCIÓN DE INDEXACIÓN AQUÍ
            df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=[clean_string_for_names(str(i)) for i in range(7)])
    
    for col in df.select_dtypes(include='object').columns:
        if df[col].isnull().any():
            df[col].fillna('desconocido', inplace=True)

    return df

def mostrar():
    st.title("📊 Association Analysis Between Categorical Variables")
    st.markdown("Explore frequencies, contingency tables and statistical significance (Chi-Square test) between two categorical variables in your dataset.")

    data = load_and_clean_data("./datos/Datos_accidentalidad.csv") # <-- ¡NOMBRE DEL ARCHIVO CORREGIDO AQUÍ!

    if data is not None:
        categorical_cols = data.select_dtypes(include='category').columns.tolist()
        
        excluded_cols = ['num_expediente', 'fecha', 'hora', 'localizacion', 'numero', 
                         'distrito', 'fecha_parsed', 'coordenada_x_utm', 'coordenada_y_utm',
                         'coordenada_cluster', 
                         'hora_numerica', 'hora_sin', 'hora_cos', 'mes_sin', 'mes_cos',
                         'source_file']
        
        available_categorical_cols = [col for col in categorical_cols if col not in excluded_cols]

        if len(available_categorical_cols) < 2:
            st.warning("Not enough categorical variables for the Chi-Square test.")
        else:
            st.sidebar.header("Variable Selection")
            variable1 = st.sidebar.selectbox("Select Variable 1 (Rows)", available_categorical_cols, index=0)
            
            available_for_var2 = [col for col in available_categorical_cols if col != variable1]
            variable2 = st.sidebar.selectbox("Select Variable 2 (Columns)", available_for_var2, index=0 if available_for_var2 else None)

            if variable1 and variable2:
                st.subheader(f"Association Analysis: '{variable1.replace('_', ' ').title()}' vs. '{variable2.replace('_', ' ').title()}'")

                st.markdown("#### 1. Frequency Tables")
                
                st.write(f"**Absolute and Relative Frequency for '{variable1.replace('_', ' ').title()}':**")
                freq_v1 = data[variable1].value_counts(dropna=False)
                freq_v1_perc = data[variable1].value_counts(dropna=False, normalize=True) * 100
                freq_df_v1 = pd.DataFrame({'Count': freq_v1, 'Percentage (%)': freq_v1_perc}).sort_values(by='Count', ascending=False)
                st.dataframe(freq_df_v1)

                st.write(f"**Absolute and Relative Frequency for '{variable2.replace('_', ' ').title()}':**")
                freq_v2 = data[variable2].value_counts(dropna=False)
                freq_v2_perc = data[variable2].value_counts(dropna=False, normalize=True) * 100
                freq_df_v2 = pd.DataFrame({'Count': freq_v2, 'Percentage (%)': freq_v2_perc}).sort_values(by='Count', ascending=False)
                st.dataframe(freq_df_v2)

                st.markdown("#### 2. Contingency Tables")
                
                st.write(f"**Contingency Table (Observed Count):**")
                contingency_table = pd.crosstab(data[variable1], data[variable2], dropna=False)
                st.dataframe(contingency_table)

                st.write(f"**Contingency Table (Percentage by column):**")
                contingency_perc_col = pd.crosstab(data[variable1], data[variable2], normalize='columns', dropna=False) * 100
                st.dataframe(contingency_perc_col.round(2).astype(str) + '%')

                st.write(f"**Contingency Table (Percentage by row):**")
                contingency_perc_row = pd.crosstab(data[variable1], data[variable2], normalize='index', dropna=False) * 100
                st.dataframe(contingency_perc_row.round(2).astype(str) + '%')

                st.markdown("#### 3. Visualizations")

                # Gráfico de Barras Agrupadas
                st.write(f"**Bar graph: {variable2.replace('_', ' ').title()} by {variable1.replace('_', ' ').title()}**")
                fig_bar, ax_bar = plt.subplots(figsize=(12, 7))
                sns.countplot(data=data, x=variable1, hue=variable2, palette='viridis', ax=ax_bar)
                ax_bar.set_title(f'Distribution of {variable2.replace("_", " ").title()} by {variable1.replace("_", " ").title()}')
                ax_bar.set_xlabel(variable1.replace("_", " ").title())
                ax_bar.set_ylabel('Count')
                ax_bar.tick_params(axis='x', rotation=45)
                plt.setp(ax_bar.get_xticklabels(), ha='right')
                ax_bar.legend(title=variable2.replace("_", " ").title(), bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                st.pyplot(fig_bar)

                # Mapa de Calor de la Tabla de Contingencia (Recuentos)
                st.write(f"**Heatmap of: {variable1.replace('_', ' ').title()} vs. {variable2.replace('_', ' ').title()} (Counts)**")
                
                fig_width = max(8, min(20, len(contingency_table.columns) * 0.8 + 2)) 

                fig_height = max(6, min(15, len(contingency_table.index) * 0.6 + 2))
                fig_heatmap, ax_heatmap = plt.subplots(figsize=(fig_width, fig_height))
                
                annot_kws = {"fontsize": 8}
                if len(contingency_table.columns) * len(contingency_table.index) > 50:
                    annot_kws = {"fontsize": min(8, max(4, int(200 / (len(contingency_table.columns) * len(contingency_table.index))**0.5)))}
                
                sns.heatmap(contingency_table, 
                            annot=True, 
                            fmt='d', 
                            cmap='YlGnBu', 
                            linewidths=.5, 
                            linecolor='gray', 
                            cbar_kws={'label': 'Count'}, 
                            ax=ax_heatmap,
                            annot_kws=annot_kws
                           )
                ax_heatmap.set_title(f'Heatmap of{variable1.replace("_", " ").title()} vs. {variable2.replace("_", " ").title()}')
                ax_heatmap.set_xlabel(variable2.replace("_", " ").title())
                ax_heatmap.set_ylabel(variable1.replace("_", " ").title())
                ax_heatmap.tick_params(axis='x', rotation=45)
                plt.setp(ax_heatmap.get_xticklabels(), ha='right')
                ax_heatmap.tick_params(axis='y', rotation=0)
                
                plt.tight_layout()
                st.pyplot(fig_heatmap)


                # --- 4. Prueba Chi-Cuadrado de Independencia ---
                st.markdown("#### 4. Chi-Square Test of Independence")
                st.markdown("The Chi-Square test evaluates if there is a statistically significant association between the two categorical variables. A p-value < 0.05 (for a 5% significance level) suggests that there is an association..")

                contingency_table_clean = contingency_table.loc[(contingency_table.sum(axis=1) != 0), (contingency_table.sum(axis=0) != 0)]
                
                if contingency_table_clean.empty or contingency_table_clean.shape[0] < 2 or contingency_table_clean.shape[1] < 2:
                    st.warning("The contingency table is too small or empty after removing rows/columns with zeros. The Chi-Square test cannot be performed..")
                else:
                    try:
                        chi2, p_value, dof, expected_freqs = chi2_contingency(contingency_table_clean)

                        st.write(f"**CHi-Square Statistic (χ²):** `{chi2:.4f}`")
                        st.write(f"** Degrees of freedom (gl):** `{dof}`")
                        st.write(f"**P-value:** `{p_value:.4f}`")

                        if p_value < 0.05:
                            st.success("Result: ¡STATISTICALLY SIGNIFICANT Association! (p < 0.05)")
                            st.markdown("This means there is evidence that the distribution of one variable depends on the other.")
                            
                            st.markdown("##### Corrected Standardized Residuals Anlaysis")
                            st.info("Values > |1.96| suggest a stronger specific association (positive or negative) in that cell. A large positive residual indicates that the combination occurs more than expected; a large negative residual, less than expected..")
                            
                            try:
                                table_obj = sm.stats.Table(contingency_table_clean)
                                residuos_corregidos = table_obj.standardized_resids
                                st.dataframe(residuos_corregidos.round(2))
                            except Exception as e:
                                st.warning(f"Error calculating corrected standardized residuals: {e}. This can occur with tables that have rows/columns of zeros after filtering..")

                        else:
                            st.info("Result: There is no evidence of significative association.(p >= 0.05)")
                            st.markdown("This means that the variables appear to be independent of each other.")

                    except ValueError as ve:
                        st.error(f"Error performing the Chi-Square test: {ve}. This can occur if the contingency table has rows or columns with only zeros (e.g., a category with no observations after filtering).")
            else:
                st.warning("Please, select two variables to start the analysis.")
    else:
        st.error("Could not load or preprocess the data file. Please check the path and format of the file 'Datos_accidentalidad.csv' in the 'datos/' folder..")