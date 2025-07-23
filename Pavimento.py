import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import log10

# Configuración de la página
st.set_page_config(
    page_title="Diseño de Pavimentos - Método AASHTO",
    page_icon="🛣️",
    layout="wide"
)

# Título principal
st.title("🛣️ Diseño de Pavimentos - Método AASHTO")
st.markdown("---")

# Sidebar para selección de tipo de pavimento
st.sidebar.title("Configuración")
tipo_pavimento = st.sidebar.selectbox(
    "Tipo de Pavimento",
    ["Pavimento Flexible (Asfáltico)", "Pavimento Rígido (Concreto)"]
)

# Función para calcular número estructural (SN) - Pavimento Flexible
def calcular_sn_flexible(W18, ZR, So, delta_PSI, MR):
    """
    Calcula el Número Estructural (SN) para pavimento flexible
    """
    try:
        # Ecuación AASHTO 1993 para pavimento flexible
        # log10(W18) = ZR*So + 9.36*log10(SN+1) - 0.20 + log10(ΔPSI/(4.2-1.5))/(0.40 + 1094/(SN+1)^5.19) + 2.32*log10(MR) - 8.07
        
        # Método iterativo para resolver SN
        SN = 1.0  # Valor inicial
        tolerance = 0.001
        max_iterations = 100
        
        for i in range(max_iterations):
            # Cálculo del lado derecho de la ecuación
            term1 = log10(delta_PSI / (4.2 - 1.5))
            term2 = 0.40 + 1094 / ((SN + 1) ** 5.19)
            term3 = 2.32 * log10(MR) - 8.07
            
            right_side = ZR * So + 9.36 * log10(SN + 1) - 0.20 + (term1 / term2) + term3
            
            # Diferencia con W18
            diff = log10(W18) - right_side
            
            if abs(diff) < tolerance:
                break
                
            # Ajuste de SN
            SN += diff * 0.1
            
            if SN < 0:
                SN = 0.1
        
        return max(SN, 1.0)
    except:
        return 3.0

# Función para calcular espesor de losa (D) - Pavimento Rígido
def calcular_espesor_rigido(W18, ZR, So, delta_PSI, Sc, J, Cd, Ec, k):
    """
    Calcula el espesor de losa (D) para pavimento rígido
    """
    try:
        # Método iterativo para resolver D
        D = 8.0  # Valor inicial en pulgadas
        tolerance = 0.01
        max_iterations = 100
        
        for i in range(max_iterations):
            # Cálculo de términos de la ecuación AASHTO
            term1 = log10(delta_PSI / (4.5 - 1.5))
            term2 = 1.0 + (1.624 * 10**7) / ((D + 1)**8.46)
            term3 = (0.75 - 1.132) * log10(215.63 * J * (D**0.75 - 1.132))
            term4 = log10((Sc * Cd * (D**0.75 - 1.132)) / (18.42 * (Ec/k)**0.25))
            
            right_side = ZR * So + 7.35 * log10(D + 1) - 0.06 + (term1 / term2) + term3 + term4
            
            # Diferencia con W18
            diff = log10(W18) - right_side
            
            if abs(diff) < tolerance:
                break
                
            # Ajuste de D
            D += diff * 0.5
            
            if D < 4:
                D = 4.0
        
        return max(D, 6.0)
    except:
        return 8.0

# Función para generar gráfico de sensibilidad
def generar_grafico_sensibilidad(tipo, parametros_base):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Análisis de Sensibilidad - {tipo}', fontsize=14, fontweight='bold')
    
    if tipo == "Pavimento Flexible (Asfáltico)":
        W18_base, ZR_base, So_base, delta_PSI_base, MR_base = parametros_base
        
        # Gráfico 1: Variación de W18
        W18_range = np.logspace(4, 7, 20)
        SN_W18 = [calcular_sn_flexible(w, ZR_base, So_base, delta_PSI_base, MR_base) for w in W18_range]
        ax1.semilogx(W18_range, SN_W18, 'b-', linewidth=2)
        ax1.set_xlabel('W₁₈ (ESALs)')
        ax1.set_ylabel('Número Estructural (SN)')
        ax1.set_title('SN vs W₁₈')
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Variación de MR
        MR_range = np.linspace(3000, 20000, 20)
        SN_MR = [calcular_sn_flexible(W18_base, ZR_base, So_base, delta_PSI_base, mr) for mr in MR_range]
        ax2.plot(MR_range, SN_MR, 'r-', linewidth=2)
        ax2.set_xlabel('Módulo de Resiliencia (psi)')
        ax2.set_ylabel('Número Estructural (SN)')
        ax2.set_title('SN vs Módulo de Resiliencia')
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Variación de ΔPSI
        delta_PSI_range = np.linspace(1.5, 4.5, 20)
        SN_delta = [calcular_sn_flexible(W18_base, ZR_base, So_base, d, MR_base) for d in delta_PSI_range]
        ax3.plot(delta_PSI_range, SN_delta, 'g-', linewidth=2)
        ax3.set_xlabel('ΔPSI')
        ax3.set_ylabel('Número Estructural (SN)')
        ax3.set_title('SN vs ΔPSI')
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Variación de Confiabilidad
        R_range = np.linspace(50, 99.99, 20)
        ZR_range = [-0.674, -0.841, -1.036, -1.282, -1.555, -1.881, -2.326, -2.576, -3.090, -3.719]
        R_vals = [50, 60, 70, 80, 85, 90, 95, 97.5, 99, 99.9]
        ZR_interp = np.interp(R_range, R_vals, ZR_range)
        SN_R = [calcular_sn_flexible(W18_base, zr, So_base, delta_PSI_base, MR_base) for zr in ZR_interp]
        ax4.plot(R_range, SN_R, 'm-', linewidth=2)
        ax4.set_xlabel('Confiabilidad (%)')
        ax4.set_ylabel('Número Estructural (SN)')
        ax4.set_title('SN vs Confiabilidad')
        ax4.grid(True, alpha=0.3)
        
    else:  # Pavimento Rígido
        W18_base, ZR_base, So_base, delta_PSI_base, Sc_base, J_base, Cd_base, Ec_base, k_base = parametros_base
        
        # Gráfico 1: Variación de W18
        W18_range = np.logspace(4, 7, 20)
        D_W18 = [calcular_espesor_rigido(w, ZR_base, So_base, delta_PSI_base, Sc_base, J_base, Cd_base, Ec_base, k_base) for w in W18_range]
        ax1.semilogx(W18_range, D_W18, 'b-', linewidth=2)
        ax1.set_xlabel('W₁₈ (ESALs)')
        ax1.set_ylabel('Espesor de Losa (pulg)')
        ax1.set_title('Espesor vs W₁₈')
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Variación de k
        k_range = np.linspace(50, 500, 20)
        D_k = [calcular_espesor_rigido(W18_base, ZR_base, So_base, delta_PSI_base, Sc_base, J_base, Cd_base, Ec_base, k) for k in k_range]
        ax2.plot(k_range, D_k, 'r-', linewidth=2)
        ax2.set_xlabel('Módulo de Reacción k (psi/pulg)')
        ax2.set_ylabel('Espesor de Losa (pulg)')
        ax2.set_title('Espesor vs Módulo k')
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Variación de Sc
        Sc_range = np.linspace(400, 800, 20)
        D_Sc = [calcular_espesor_rigido(W18_base, ZR_base, So_base, delta_PSI_base, sc, J_base, Cd_base, Ec_base, k_base) for sc in Sc_range]
        ax3.plot(Sc_range, D_Sc, 'g-', linewidth=2)
        ax3.set_xlabel('Módulo de Rotura Sc (psi)')
        ax3.set_ylabel('Espesor de Losa (pulg)')
        ax3.set_title('Espesor vs Módulo de Rotura')
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Variación de Ec
        Ec_range = np.linspace(3000000, 6000000, 20)
        D_Ec = [calcular_espesor_rigido(W18_base, ZR_base, So_base, delta_PSI_base, Sc_base, J_base, Cd_base, ec, k_base) for ec in Ec_range]
        ax4.plot(Ec_range/1000000, D_Ec, 'm-', linewidth=2)
        ax4.set_xlabel('Módulo Elástico Ec (x10⁶ psi)')
        ax4.set_ylabel('Espesor de Losa (pulg)')
        ax4.set_title('Espesor vs Módulo Elástico')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# Interfaz principal
if tipo_pavimento == "Pavimento Flexible (Asfáltico)":
    st.header("🛣️ Diseño de Pavimento Flexible (Asfáltico)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros de Diseño")
        
        # Tráfico
        W18 = st.number_input(
            "W₁₈ - Número de ESALs de diseño",
            min_value=10000,
            max_value=50000000,
            value=1000000,
            format="%d",
            help="Número acumulado de ejes equivalentes de 18 kips durante el período de diseño"
        )
        
        # Confiabilidad
        R = st.selectbox(
            "Confiabilidad (R) %",
            [50, 60, 70, 75, 80, 85, 90, 95, 97.5, 99, 99.9],
            index=6,
            help="Nivel de confiabilidad del diseño"
        )
        
        # Mapeo de confiabilidad a ZR
        ZR_dict = {50: -0.674, 60: -0.841, 70: -1.036, 75: -1.150, 80: -1.282, 
                   85: -1.555, 90: -1.881, 95: -2.326, 97.5: -2.576, 99: -3.090, 99.9: -3.719}
        ZR = ZR_dict[R]
        
        # Desviación estándar
        So = st.slider(
            "So - Desviación estándar normal",
            min_value=0.30,
            max_value=0.50,
            value=0.45,
            step=0.01,
            help="Desviación estándar normal (0.40-0.50 para pavimentos flexibles)"
        )
        
        # Pérdida de serviciabilidad
        delta_PSI = st.slider(
            "ΔPSI - Pérdida de serviciabilidad",
            min_value=1.5,
            max_value=4.5,
            value=2.0,
            step=0.1,
            help="Diferencia entre serviciabilidad inicial y final"
        )
        
        # Módulo de resiliencia
        MR = st.number_input(
            "MR - Módulo de resiliencia de la subrasante (psi)",
            min_value=1000,
            max_value=50000,
            value=10000,
            help="Módulo de resiliencia efectivo de la subrasante"
        )
    
    with col2:
        st.subheader("Resultados del Diseño")
        
        # Cálculo del número estructural
        SN = calcular_sn_flexible(W18, ZR, So, delta_PSI, MR)
        
        st.metric("Número Estructural (SN)", f"{SN:.2f}")
        
        # Información adicional
        st.info(f"""
        **Parámetros utilizados:**
        - W₁₈: {W18:,} ESALs
        - Confiabilidad: {R}% (ZR = {ZR:.3f})
        - Desviación estándar: {So}
        - ΔPSI: {delta_PSI}
        - MR: {MR:,} psi
        """)
        
        # Recomendaciones de espesores típicos
        st.subheader("Espesores Típicos Recomendados")
        st.write("*Basado en el SN calculado:*")
        
        if SN <= 2.0:
            st.success("**Tráfico Ligero**\n- Carpeta asfáltica: 5-7.5 cm\n- Base granular: 15-20 cm\n- Sub-base: 20-30 cm")
        elif SN <= 4.0:
            st.warning("**Tráfico Medio**\n- Carpeta asfáltica: 7.5-10 cm\n- Base granular: 20-30 cm\n- Sub-base: 30-40 cm")
        else:
            st.error("**Tráfico Pesado**\n- Carpeta asfáltica: 10-15 cm\n- Base granular: 30-40 cm\n- Sub-base: 40-50 cm")

else:  # Pavimento Rígido
    st.header("🏗️ Diseño de Pavimento Rígido (Concreto)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros de Diseño")
        
        # Tráfico
        W18 = st.number_input(
            "W₁₈ - Número de ESALs de diseño",
            min_value=10000,
            max_value=50000000,
            value=1000000,
            format="%d"
        )
        
        # Confiabilidad
        R = st.selectbox(
            "Confiabilidad (R) %",
            [50, 60, 70, 75, 80, 85, 90, 95, 97.5, 99, 99.9],
            index=6
        )
        
        ZR_dict = {50: -0.674, 60: -0.841, 70: -1.036, 75: -1.150, 80: -1.282, 
                   85: -1.555, 90: -1.881, 95: -2.326, 97.5: -2.576, 99: -3.090, 99.9: -3.719}
        ZR = ZR_dict[R]
        
        # Desviación estándar
        So = st.slider(
            "So - Desviación estándar normal",
            min_value=0.30,
            max_value=0.40,
            value=0.35,
            step=0.01,
            help="Desviación estándar normal (0.30-0.40 para pavimentos rígidos)"
        )
        
        # Pérdida de serviciabilidad
        delta_PSI = st.slider(
            "ΔPSI - Pérdida de serviciabilidad",
            min_value=1.5,
            max_value=4.5,
            value=2.5,
            step=0.1
        )
        
        # Módulo de rotura del concreto
        Sc = st.number_input(
            "S'c - Módulo de rotura del concreto (psi)",
            min_value=400,
            max_value=800,
            value=650,
            help="Módulo de rotura del concreto a los 28 días"
        )
        
        # Coeficiente de transferencia de carga
        J = st.slider(
            "J - Coeficiente de transferencia de carga",
            min_value=2.5,
            max_value=4.5,
            value=3.2,
            step=0.1,
            help="2.5-3.1 con pasadores, 3.6-4.2 sin pasadores"
        )
        
        # Coeficiente de drenaje
        Cd = st.slider(
            "Cd - Coeficiente de drenaje",
            min_value=0.75,
            max_value=1.25,
            value=1.0,
            step=0.05,
            help="0.75-1.25 dependiendo de la calidad del drenaje"
        )
        
        # Módulo elástico del concreto
        Ec = st.number_input(
            "Ec - Módulo elástico del concreto (psi)",
            min_value=3000000,
            max_value=6000000,
            value=4000000,
            help="Módulo elástico del concreto"
        )
        
        # Módulo de reacción de la subrasante
        k = st.number_input(
            "k - Módulo de reacción de la subrasante (psi/pulg)",
            min_value=50,
            max_value=1000,
            value=200,
            help="Módulo de reacción de la subrasante"
        )
    
    with col2:
        st.subheader("Resultados del Diseño")
        
        # Cálculo del espesor de losa
        D = calcular_espesor_rigido(W18, ZR, So, delta_PSI, Sc, J, Cd, Ec, k)
        
        st.metric("Espesor de Losa (D)", f"{D:.1f} pulg", f"{D*2.54:.1f} cm")
        
        # Información adicional
        st.info(f"""
        **Parámetros utilizados:**
        - W₁₈: {W18:,} ESALs
        - Confiabilidad: {R}% (ZR = {ZR:.3f})
        - S'c: {Sc} psi
        - J: {J}
        - k: {k} psi/pulg
        - Ec: {Ec:,} psi
        """)
        
        # Recomendaciones adicionales
        st.subheader("Recomendaciones de Diseño")
        
        if D <= 8:
            st.success("**Espesor Mínimo Aceptable**\nConsiderar refuerzo mínimo")
        elif D <= 12:
            st.warning("**Espesor Moderado**\nDiseño estándar para tráfico medio")
        else:
            st.error("**Espesor Alto**\nConsiderar alternativas o mejoras en la subrasante")

# Sección de gráficos
st.markdown("---")
st.header("📊 Análisis Gráfico")

mostrar_grafico = st.checkbox("Mostrar análisis de sensibilidad", value=False)

if mostrar_grafico:
    if tipo_pavimento == "Pavimento Flexible (Asfáltico)":
        parametros = (W18, ZR, So, delta_PSI, MR)
    else:
        parametros = (W18, ZR, So, delta_PSI, Sc, J, Cd, Ec, k)
    
    fig = generar_grafico_sensibilidad(tipo_pavimento, parametros)
    st.pyplot(fig)
    
    st.info("""
    **Interpretación de los gráficos:**
    - Los gráficos muestran cómo varía el resultado del diseño al cambiar cada parámetro
    - Permite identificar los parámetros más sensibles en el diseño
    - Útil para análisis de optimización y validación del diseño
    """)

# Información adicional
st.markdown("---")
st.subheader("ℹ️ Información del Método AASHTO")

with st.expander("Acerca del Método AASHTO"):
    st.write("""
    **Método AASHTO (American Association of State Highway and Transportation Officials)**
    
    Este método se basa en los resultados del ensayo vial AASHO realizado entre 1958-1960 en Ottawa, Illinois.
    Las ecuaciones utilizadas corresponden a la Guía AASHTO 1993.
    
    **Pavimento Flexible:**
    - Se calcula el Número Estructural (SN) requerido
    - SN se conviestream
    
    rte en espesores de capas usando coeficientes estructurales
    
    **Pavimento Rígido:**
    - Se calcula directamente el espesor de la losa de concreto
    - Considera la transferencia de carga entre losas
    
    **Factores principales:**
    - Tráfico (W₁₈): Número de ejes equivalentes de 18 kips
    - Confiabilidad: Probabilidad de que el pavimento tenga un comportamiento satisfactorio
    - Serviciabilidad: Medida de la comodidad al usuario
    - Propiedades de materiales: Resistencia y rigidez
    """)

st.markdown("---")
st.caption("Desarrollado para diseño de pavimentos según método AASHTO 1993")