import numpy as np
import pandas as pd
import streamlit as st 
import plotly.graph_objects as go
from sktime.forecasting.arima import ARIMA
from datetime import datetime, timedelta
from sktime.forecasting.base import ForecastingHorizon

ALL = "All Cumulaive Series - No Forecast"
CASES = "Total Cases"
DEATHS = "Total Deaths"
INFECTED = "Total Infected"
RECOVERED = "Total Recovered"


# change the directory path in according to the location
# of the entire project
path_file = '/content/drive/MyDrive/PBL_sem2/ohuinea.txt'


@st.cache(allow_output_mutation=True)
def make_forecast(selection, df, start_date, fh_interval):
    """Takes a name from the selection and makes a forecast plot."""

    if selection == CASES:
        title = "Daily Cases"
        y_label = "Cases"

    if selection == DEATHS:
        title = "Daily Deaths"
        y_label = "Deaths"

    if selection == INFECTED:
        title = "Daily Recoveries"
        y_label = "Recoveries"

    if selection == RECOVERED:
        title = "Daily Recoveries"
        y_label = "Recoveries"

    # Setting the forecasting horizon and the main forecaster
    fh = ForecastingHorizon(
        pd.PeriodIndex(pd.date_range(start_date, periods=fh_interval, freq="D")), is_relative=False
    )

    # Initialise forecaster
    forecaster = ARIMA(
        order=(2, 1, 2), seasonal_order=(1, 0, 1, 7), suppress_warnings=True
    )

    # Fit chosen forecaster with train data
    forecaster.fit(df)

    # Code for confidence interval prediction
    alpha = 0.05  
    df_pred, df_pred_ints = forecaster.predict(fh, return_pred_int=True, alpha=alpha)
    new_pd = pd.concat([df_pred_ints["upper"], df_pred_ints["lower"][::-1]])

    # Trace creation
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index.strftime('%Y-%m-%d'), 
                             y=df.values, 
                             line_color='rgb(0, 64, 255)',
                             mode='lines+markers', 
                             name='actual data'))
    fig.add_trace(go.Scatter(x=df_pred.index.strftime('%Y-%m-%d'), 
                             y=df_pred.values, 
                             line_color='rgb(255, 102, 0)',
                             mode='lines+markers', 
                             name='prediction'))
    fig.add_trace(go.Scatter(x=new_pd.index.strftime('%Y-%m-%d'),
                             y=new_pd.values,
                             fill='toself',
                             fillcolor='rgba(255, 102, 0, 0.2)',
                             line_color='rgba(255 , 255, 255, 0)',
                             showlegend=True,
                             name='confidence interval'))
    fig.update_layout(title=title,
                      xaxis_title="Date",
                      yaxis_title=y_label)
    
    return fig


def plot_graph(selected_series, y, start_date, input_fh):
    """Plots the graph indicated by the user."""
    plotly_fig = make_forecast(selected_series, y, start_date, input_fh)
    st.plotly_chart(plotly_fig)


def make_dataframe(path):
    """Reads the content of txt file and creates a dataframe
    based on the recordings provided."""

    with open(path, 'r') as f:
        ugly_data = eval(f.readline())

    # initialise dataframe
    dataframe = {
        'cases':[], 
        'deaths':[], 
        'infected':[], 
        'recoveries':[], 
        'timestamp':[]
    }

    fields = ['cases', 'deaths', 'infected', 'recoveries']

    # for each entry extract extract all necessary data
    date = datetime.today()
    cases = 0
    for d in ugly_data:
        for field in fields:
            dataframe[field].append(int(d[field]))
        dataframe['timestamp'].append(date.strftime("%Y-%m-%d"))
        date += timedelta(days=1)

    # here we do the transformation dict -> DataFrame
    cases = pd.DataFrame(dataframe)
    cases.index = pd.PeriodIndex(cases['timestamp'], freq='D')
    cases.index.name = None
    cases = cases.drop('timestamp', axis=1)

    return cases


st.write("# COVID-19 Forecast")

cases = make_dataframe(path_file)
data_time = cases.index.to_timestamp()
fin_date = datetime.strptime("2022-12-31", "%Y-%m-%d")
default_date = data_time[1]


selected_series = st.selectbox("Select data to forecast:", (ALL, CASES, DEATHS, INFECTED, RECOVERED))


if selected_series in [CASES, DEATHS, INFECTED, RECOVERED]:

    # Selection bar for start date
    start_date = st.date_input(
        "Select start date for forecasting:",
        default_date,
        min_value=default_date,
        max_value=fin_date,
    )

    # Setting the slider for forecasting length
    fh_length = st.slider("Days", 1, 100, 10)
    
    st.write("Forecasting interval: " + str(fh_length) + " days")
    
    # Output the plot based on the user choice
    if selected_series == CASES:
        cases_cases = cases['cases']
        plot_graph(selected_series, cases_cases, start_date, fh_length)
    
    elif selected_series == DEATHS:
        deaths = cases['deaths']
        plot_graph(selected_series, deaths, start_date, fh_length)
    
    elif selected_series == INFECTED:
        infected = cases['infected']
        plot_graph(selected_series, infected, start_date, fh_length)
    
    else:
        recovered = cases['recoveries']
        plot_graph(selected_series, recovered, start_date, fh_length)
        
else:
    # init plotly figure
    fig = go.Figure()
    
    # add traces
    fig.add_trace(go.Scatter(x=cases.index.strftime('%Y-%m-%d'), 
                            y=cases["cases"], 
                            mode='lines+markers', 
                            name='cases'))
    fig.add_trace(go.Scatter(x=cases.index.strftime('%Y-%m-%d'), 
                            y=cases["deaths"], 
                            mode='lines+markers', 
                            name='deaths'))
    fig.add_trace(go.Scatter(x=cases.index.strftime('%Y-%m-%d'), 
                            y=cases["infected"], 
                            mode='lines+markers', 
                            name='infected'))
    fig.add_trace(go.Scatter(x=cases.index.strftime('%Y-%m-%d'), 
                            y=cases["recoveries"], 
                            line_color='rgb(0, 64, 255)',
                            mode='lines+markers', 
                            name='recoveries'))
    
    # change titles to the plot and xaxis, yaxis
    fig.update_layout(title='Daily Series',
                    xaxis_title='Date',
                    yaxis_title='Number of people')
    
    # display the plot
    st.plotly_chart(fig)
