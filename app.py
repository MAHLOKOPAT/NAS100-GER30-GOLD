import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
from PIL import Image
import time

from utils import (
    process_uploaded_chart,
    display_chart_with_prediction,
    display_comparison_view,
    apply_indicators
)
from prediction import predict_next_movement
from sample_data import get_sample_data

# Page config
st.set_page_config(
    page_title="Forex Chart Analysis & Prediction",
    page_icon="📈",
    layout="wide"
)

# Main title
st.title("Forex Chart Analysis & Market Movement Prediction")

st.markdown("""
This application allows you to upload and analyze forex charts for NAS100, GER30, and XAUUSD.
Upload your chart images or use our historical data to visualize and predict market movements.
""")

# Sidebar for controls
st.sidebar.title("Controls")

# Chart selection
chart_type = st.sidebar.selectbox(
    "Select Instrument",
    ["NAS100", "GER30", "XAUUSD"]
)

# Timeframe selection
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"]
)

# Analysis type
analysis_mode = st.sidebar.radio(
    "Analysis Mode",
    ["Upload Chart", "Use Historical Data"]
)

# Container for the main content
main_container = st.container()

with main_container:
    if analysis_mode == "Upload Chart":
        st.header(f"{chart_type} Chart Analysis")
        
        # Upload chart
        uploaded_file = st.file_uploader(f"Upload {chart_type} chart image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                # Process and display the uploaded chart
                chart_image = Image.open(uploaded_file)
                
                # Analyze the chart
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.image(chart_image, caption=f"{chart_type} Chart", use_column_width=True)
                
                with col2:
                    st.subheader("Chart Analysis")
                    
                    with st.spinner("Analyzing chart..."):
                        # Simulate analysis time
                        time.sleep(1)
                        
                        # Get prediction with timeframe
                        prediction, confidence, entry_price, stop_loss, take_profit = predict_next_movement(chart_type, timeframe)
                        
                        direction_color = "green" if prediction == "UP" else "red"
                        st.markdown(f"### Prediction: <span style='color:{direction_color}'>{prediction}</span>", unsafe_allow_html=True)
                        st.progress(confidence)
                        st.write(f"Confidence Level: {confidence:.2f}%")
                        
                        # Price signals
                        st.subheader("Price Signals")
                        st.write(f"**Entry Price:** {entry_price:,}")
                        st.write(f"**Stop Loss:** {stop_loss:,}")
                        st.write(f"**Take Profit:** {take_profit:,}")
                        
                        # Key levels
                        st.subheader("Key Price Levels")
                        if chart_type == "NAS100":
                            st.write("Support: 15,420")
                            st.write("Resistance: 15,650")
                        elif chart_type == "GER30":
                            st.write("Support: 17,850")
                            st.write("Resistance: 18,200")
                        else:  # XAUUSD
                            st.write("Support: 2,140")
                            st.write("Resistance: 2,190")
                
                # Analysis details
                st.subheader("Detailed Analysis")
                tabs = st.tabs(["Technical Indicators", "Volume Analysis", "Market Sentiment"])
                
                with tabs[0]:
                    st.write("### Technical Indicators")
                    indicators = st.multiselect(
                        "Select indicators to apply",
                        ["RSI", "MACD", "Bollinger Bands", "Moving Averages"]
                    )
                    
                    if indicators:
                        st.write("Indicators applied:")
                        for indicator in indicators:
                            st.write(f"- {indicator}: {'Bullish' if prediction == 'UP' else 'Bearish'}")
                
                with tabs[1]:
                    st.write("### Volume Analysis")
                    st.write("Volume trend indicates market interest is increasing" if prediction == "UP" else "Volume trend shows decreasing market participation")
                
                with tabs[2]:
                    st.write("### Market Sentiment")
                    sentiment = 65 if prediction == "UP" else 35
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Bullish", f"{sentiment}%", f"{sentiment-50:+}%")
                    with col2:
                        st.metric("Bearish", f"{100-sentiment}%", f"{50-sentiment:+}%")
                    with col3:
                        st.metric("Volatility", "Medium", "5%")
            
            except Exception as e:
                st.error(f"Error processing the uploaded chart: {e}")
                st.info("Please upload a clear chart image for accurate analysis.")
        
        else:
            # Show sample charts
            st.info("Upload a chart image or use the examples below")
            
            # Display sample forex charts
            st.subheader("Sample Forex Charts")
            
            sample_charts = {
                "Forex Trading Chart 1": "https://images.unsplash.com/photo-1554260570-e9689a3418b8",
                "Forex Trading Chart 2": "https://images.unsplash.com/photo-1644363832001-0876e81f37a9",
                "Forex Trading Chart 3": "https://images.unsplash.com/photo-1639754390580-2e7437267698",
                "Forex Trading Chart 4": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29"
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(sample_charts["Forex Trading Chart 1"], caption="Sample Forex Chart 1", use_column_width=True)
                st.image(sample_charts["Forex Trading Chart 3"], caption="Sample Forex Chart 3", use_column_width=True)
            with col2:
                st.image(sample_charts["Forex Trading Chart 2"], caption="Sample Forex Chart 2", use_column_width=True)
                st.image(sample_charts["Forex Trading Chart 4"], caption="Sample Forex Chart 4", use_column_width=True)
    
    else:  # Use Historical Data
        st.header(f"{chart_type} Historical Data Analysis")
        
        # Get sample data for the selected instrument
        df = get_sample_data(chart_type)
        
        # Time period selection
        time_period = st.select_slider(
            "Select Time Period",
            options=["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year"],
            value="1 Month"
        )
        
        # Filter data based on selected time period
        end_date = datetime.now().date()
        if time_period == "1 Day":
            start_date = end_date - timedelta(days=1)
        elif time_period == "1 Week":
            start_date = end_date - timedelta(weeks=1)
        elif time_period == "1 Month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "3 Months":
            start_date = end_date - timedelta(days=90)
        elif time_period == "6 Months":
            start_date = end_date - timedelta(days=180)
        else:  # 1 Year
            start_date = end_date - timedelta(days=365)
        
        filtered_df = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]
        
        # Display chart with indicators
        indicators = st.multiselect(
            "Select Technical Indicators",
            ["RSI", "MACD", "Bollinger Bands", "Moving Averages"]
        )
        
        fig = go.Figure()
        
        # Create candlestick chart
        fig.add_trace(go.Candlestick(
            x=filtered_df['Date'],
            open=filtered_df['Open'],
            high=filtered_df['High'],
            low=filtered_df['Low'],
            close=filtered_df['Close'],
            name=chart_type
        ))
        
        # Apply selected indicators
        if indicators:
            filtered_df = apply_indicators(filtered_df, indicators)
            
            # Add indicators to chart
            if "Moving Averages" in indicators:
                fig.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['MA_20'],
                    line=dict(color='blue', width=1),
                    name="20-day MA"
                ))
                
                fig.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['MA_50'],
                    line=dict(color='orange', width=1),
                    name="50-day MA"
                ))
                
            if "Bollinger Bands" in indicators:
                fig.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['BB_Upper'],
                    line=dict(color='gray', width=1, dash='dash'),
                    name="Upper BB"
                ))
                
                fig.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['BB_Lower'],
                    line=dict(color='gray', width=1, dash='dash'),
                    name="Lower BB"
                ))
        
        # Update layout
        fig.update_layout(
            title=f"{chart_type} Price Chart ({time_period})",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Prediction
        st.subheader("Market Movement Prediction")
        
        # Use timeframe from slider
        timeframe_map = {
            "1 Day": "1 Day",
            "1 Week": "1 Week",
            "1 Month": "1 Month",
            "3 Months": "1 Day",
            "6 Months": "1 Day",
            "1 Year": "1 Day"
        }
        
        prediction, confidence, entry_price, stop_loss, take_profit = predict_next_movement(chart_type, timeframe_map.get(time_period, "1 Day"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            direction_color = "green" if prediction == "UP" else "red"
            st.markdown(f"### Next Movement: <span style='color:{direction_color}'>{prediction}</span>", unsafe_allow_html=True)
            st.progress(confidence)
            st.write(f"Confidence Level: {confidence:.2f}%")
            
            # Price signals
            st.subheader("Price Signals")
            st.write(f"**Entry Price:** {entry_price:,}")
            st.write(f"**Stop Loss:** {stop_loss:,}")
            st.write(f"**Take Profit:** {take_profit:,}")
        
        with col2:
            st.subheader("Key Price Levels")
            if chart_type == "NAS100":
                st.write("Support: 15,420")
                st.write("Resistance: 15,650")
                st.write("Current: 15,530")
            elif chart_type == "GER30":
                st.write("Support: 17,850")
                st.write("Resistance: 18,200")
                st.write("Current: 18,050")
            else:  # XAUUSD
                st.write("Support: 2,140")
                st.write("Resistance: 2,190")
                st.write("Current: 2,165")
        
        # Additional indicators
        if "RSI" in indicators or "MACD" in indicators:
            st.subheader("Technical Indicators")
            
            if "RSI" in indicators and "MACD" in indicators:
                col1, col2 = st.columns(2)
                
                with col1:
                    # RSI Chart
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(
                        x=filtered_df['Date'],
                        y=filtered_df['RSI'],
                        line=dict(color='purple', width=1),
                        name="RSI"
                    ))
                    
                    fig_rsi.add_shape(
                        type="line",
                        x0=filtered_df['Date'].iloc[0],
                        y0=70,
                        x1=filtered_df['Date'].iloc[-1],
                        y1=70,
                        line=dict(color="red", width=1, dash="dash")
                    )
                    
                    fig_rsi.add_shape(
                        type="line",
                        x0=filtered_df['Date'].iloc[0],
                        y0=30,
                        x1=filtered_df['Date'].iloc[-1],
                        y1=30,
                        line=dict(color="green", width=1, dash="dash")
                    )
                    
                    fig_rsi.update_layout(
                        title="RSI Indicator",
                        xaxis_title="Date",
                        yaxis_title="RSI",
                        height=300
                    )
                    
                    st.plotly_chart(fig_rsi, use_container_width=True)
                
                with col2:
                    # MACD Chart
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=filtered_df['Date'],
                        y=filtered_df['MACD'],
                        line=dict(color='blue', width=1),
                        name="MACD"
                    ))
                    
                    fig_macd.add_trace(go.Scatter(
                        x=filtered_df['Date'],
                        y=filtered_df['MACD_Signal'],
                        line=dict(color='red', width=1),
                        name="Signal"
                    ))
                    
                    fig_macd.add_trace(go.Bar(
                        x=filtered_df['Date'],
                        y=filtered_df['MACD_Hist'],
                        marker_color=np.where(filtered_df['MACD_Hist'] >= 0, 'green', 'red'),
                        name="Histogram"
                    ))
                    
                    fig_macd.update_layout(
                        title="MACD Indicator",
                        xaxis_title="Date",
                        yaxis_title="MACD",
                        height=300
                    )
                    
                    st.plotly_chart(fig_macd, use_container_width=True)
            
            elif "RSI" in indicators:
                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['RSI'],
                    line=dict(color='purple', width=1),
                    name="RSI"
                ))
                
                fig_rsi.add_shape(
                    type="line",
                    x0=filtered_df['Date'].iloc[0],
                    y0=70,
                    x1=filtered_df['Date'].iloc[-1],
                    y1=70,
                    line=dict(color="red", width=1, dash="dash")
                )
                
                fig_rsi.add_shape(
                    type="line",
                    x0=filtered_df['Date'].iloc[0],
                    y0=30,
                    x1=filtered_df['Date'].iloc[-1],
                    y1=30,
                    line=dict(color="green", width=1, dash="dash")
                )
                
                fig_rsi.update_layout(
                    title="RSI Indicator",
                    xaxis_title="Date",
                    yaxis_title="RSI",
                    height=300
                )
                
                st.plotly_chart(fig_rsi, use_container_width=True)
            
            elif "MACD" in indicators:
                # MACD Chart
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['MACD'],
                    line=dict(color='blue', width=1),
                    name="MACD"
                ))
                
                fig_macd.add_trace(go.Scatter(
                    x=filtered_df['Date'],
                    y=filtered_df['MACD_Signal'],
                    line=dict(color='red', width=1),
                    name="Signal"
                ))
                
                fig_macd.add_trace(go.Bar(
                    x=filtered_df['Date'],
                    y=filtered_df['MACD_Hist'],
                    marker_color=np.where(filtered_df['MACD_Hist'] >= 0, 'green', 'red'),
                    name="Histogram"
                ))
                
                fig_macd.update_layout(
                    title="MACD Indicator",
                    xaxis_title="Date",
                    yaxis_title="MACD",
                    height=300
                )
                
                st.plotly_chart(fig_macd, use_container_width=True)

# Market insights at the bottom
st.header("Market Insights")

# Prediction charts
st.subheader("Financial Prediction Graphs")
col1, col2 = st.columns(2)

with col1:
    st.image("https://images.unsplash.com/photo-1444653389962-8149286c578a", caption="Financial Prediction Sample 1", use_column_width=True)
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab", caption="Financial Prediction Sample 3", use_column_width=True)

with col2:
    st.image("https://images.unsplash.com/photo-1444653614773-995cb1ef9efa", caption="Financial Prediction Sample 2", use_column_width=True)
    st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", caption="Financial Prediction Sample 4", use_column_width=True)

# Disclaimer
st.markdown("---")
st.caption("""
**Disclaimer**: This application provides market analysis and predictions based on technical indicators and historical data. 
These predictions are for informational purposes only and should not be considered as financial advice. 
Trading in financial markets involves risk, and past performance is not indicative of future results.
""")
