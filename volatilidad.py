import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import time

# Título de la aplicación
st.title("Volatilidad en Tiempo Real")

# Dividir los controles en 3 columnas
col1, col2, col3 = st.columns(3)

# Entrada para el ticker (activo a monitorear)
with col1:
    ticker = st.text_input("Ticker del activo:", "GGAL")
    
    # Parámetro para la cantidad de registros a graficar (debajo del ticker)
    num_records = st.number_input("Cantidad de registros a graficar:", min_value=1, value=100)

# Parámetros para las ventanas deslizantes (para medir volatilidad con diferentes periodos)
with col2:
    window1 = st.number_input("Ventana 1 (periodos para volatilidad):", min_value=1, value=14)
    window2 = st.number_input("Ventana 2 (periodos para volatilidad):", min_value=1, value=26)
    window3 = st.number_input("Ventana 3 (periodos para volatilidad):", min_value=1, value=50)

# Parámetros para seleccionar el periodo y el intervalo
with col3:
    period = st.selectbox(
        "Periodo de datos:",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    )

    interval = st.selectbox(
        "Intervalo de datos:",
        ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"]
    )

# Parámetro para la actualización automática
update_interval = st.slider("Intervalo de actualización (segundos):", min_value=10, max_value=600, value=60)

# Loop para actualizar la aplicación en tiempo real
while True:
    # Descargar datos basados en el periodo y el intervalo seleccionados
    data = yf.download(ticker, period=period, interval=interval, progress=False)

    # Verificar que el número de registros no supere el máximo disponible
    max_records = len(data)
    if num_records > max_records:
        num_records = max_records

    # Reducir los datos a la cantidad solicitada
    data = data.tail(num_records)

    # Calcular los retornos logarítmicos para la volatilidad
    data['Log Return'] = (data['Adj Close'] / data['Adj Close'].shift(1)).apply(lambda x: np.log(x))

    # Calcular la volatilidad como la desviación estándar de los retornos
    data['Volatility1'] = data['Log Return'].rolling(window=window1).std() * np.sqrt(252)
    data['Volatility2'] = data['Log Return'].rolling(window=window2).std() * np.sqrt(252)
    data['Volatility3'] = data['Log Return'].rolling(window=window3).std() * np.sqrt(252)

    # Crear el gráfico interactivo usando Plotly
    fig = go.Figure()

    # Añadir la volatilidad con diferentes ventanas
    fig.add_trace(go.Scatter(x=data.index, y=data['Volatility1'], mode='lines', name=f'Volatilidad ({window1} periodos)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Volatility2'], mode='lines', name=f'Volatilidad ({window2} periodos)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Volatility3'], mode='lines', name=f'Volatilidad ({window3} periodos)', line=dict(color='green')))

    # Configurar el layout del gráfico con la leyenda alineada a la izquierda y sobre el gráfico
    fig.update_layout(
        title=f'Volatilidad para {ticker} en Intervalo de {interval}',
        xaxis_title='Fecha',
        yaxis_title='Volatilidad',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hovermode='x unified'
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # Esperar el tiempo especificado antes de actualizar
    time.sleep(update_interval)

    # Refrescar la aplicación
    st.rerun()
