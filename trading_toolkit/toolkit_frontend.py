import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import toolkit_backend

page_icon = ':moneybag:'
st.set_page_config(page_title='Trading Tool Kit',page_icon=':moneybag:')

#user enters ticker symbol, start_date, and end_date. Yfinance api retrieves stock data based on parameters
#user selects technical indicator and enter initial investment budget
st.title('Technical Trading Tool :chart_with_upwards_trend:')
ticker = st.text_input('Enter Ticker Sysmbol for Desired Stock')
start = st.date_input('Start', value = pd.to_datetime('2021-01-01'))
end = st.date_input('End', value=pd.to_datetime('today'))
budget = st.number_input('Enter initial investment:',min_value=0)

option = st.selectbox('Select Indicator',('Moving Average Convergence Divergence (MACD)',
                                          'Relative Strength Index (RSI)',
                                          'On-Balance Volume (OBV)'))

#return revenue based on technical indicator, else return no data found for given stock sticker symbol
#graph return of the stock and technical analysis oscillator
if ticker:
    try:
        stock = yf.download(ticker, start=start, end=end)

        if option == 'Moving Average Convergence Divergence (MACD)':
            
            print('OK')
            data = toolkit_backend.MACD(stock,budget)
            data.calculate_macd()
            data.generate_signals()
            rev = data.backtest_strategy()
            print(rev)
            st.write('Estimated return $:{:.2f}'.format(rev))
            fig1 = px.line(data.df, x= data.df.index, y='Close')
            st.plotly_chart(fig1)
            n_data = data.df[['MACD','Signal_Line']]
            fig2 = px.line(n_data, x=n_data.index ,y=n_data.columns)
            st.plotly_chart(fig2)
            st.table(data.df.tail(10))
                
        elif option == 'Relative Strength Index (RSI)':
            
            data = toolkit_backend.RSI(stock,budget)
            rev = data.backtest_rsi()
            print(rev)
            st.write('Estimated return $:{:.2f}'.format(rev))
            fig1 = px.line(data.df, x=data.df.index, y= 'Close')
            st.plotly_chart(fig1)
            fig2 = px.line(x=data.df.index, y=data.df.RSI)
            # Add labels to axes
            fig2.update_layout(xaxis_title='Date',yaxis_title='Value',title='RSI Technical Indicator')
            # Add dotted horizontal lines at 30 and 70
            fig2.add_shape(type='line',x0=data.df.index.min(),x1=data.df.index.max(),y0=30,y1=30,line=dict(color='red', dash='dash'))
            fig2.add_shape(type='line',x0=data.df.index.min(),x1=data.df.index.max(),y0=70,y1=70,line=dict(color='red', dash='dash'))
            st.plotly_chart(fig2)
            st.table(data.df.tail(10))

        elif option == 'On-Balance Volume (OBV)':
            data = toolkit_backend.OBV(stock,budget)
            rev = data.backtest_obv()
            print(rev)
            st.write('Estimated return $:{:.2f}'.format(rev))
            fig1 = px.line(data.df, x=data.df.index, y= 'Close')
            st.plotly_chart(fig1)
            fig2 = px.line(data.df, x=data.df.index, y= 'Cumulative_OBV')
            st.plotly_chart(fig2)
            st.table(data.df.tail(10))
    except:
        st.write('Asset for trading ticker not found! :milky_way:')
            

st.cache_data.clear()