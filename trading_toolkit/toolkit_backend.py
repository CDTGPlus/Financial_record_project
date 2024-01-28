import pandas as pd 
import yfinance as yf


class MACD:

    def __init__(self,df,balance=10000):
        # self.df = yf.download(symbol, start=start_date, end=end_date)
        self.df = df
        self.balance = balance

    
    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        # Calculate the short-term exponential moving average
        short_ema = self.df['Close'].ewm(span=short_window, adjust=False).mean()

        # Calculate the long-term exponential moving average
        long_ema = self.df['Close'].ewm(span=long_window, adjust=False).mean()

        # Calculate the MACD line
        self.df['MACD'] = short_ema - long_ema

        # Calculate the signal line
        self.df['Signal_Line'] = self.df['MACD'].ewm(span=signal_window, adjust=False).mean()


    def generate_signals(self):
        # Create a 'Position' column for signals (1 for Buy, -1 for Sell, 0 for Hold)
        self.df['Position'] = 0

        # Generate Buy signals
        self.df.loc[self.df['MACD'] > self.df['Signal_Line'], 'Position'] = 1

        # Generate Sell signals
        self.df.loc[self.df['MACD'] < self.df['Signal_Line'], 'Position'] = -1

    def backtest_strategy(self):
        balance = self.balance
        position = 0

        # Iterate through the DataFrame to simulate trading
        for i in range(1, len(self.df)):
            if self.df['Position'][i] == 1 and self.df['Position'][i - 1] != 1:  # Buy signal
                position = balance / self.df['Close'][i]
                balance = 0
            elif self.df['Position'][i] == -1 and self.df['Position'][i - 1] != -1:  # Sell signal
                balance = position * self.df['Close'][i]
                position = 0

        # Calculate the final balance if still holding a position
        final_balance = balance + position * self.df['Close'].iloc[-1]

        return final_balance
        

class RSI:

    def __init__(self,df,balance=10000):
        self.df = df
        self.rsi_values = self.calculate_rsi(self.df['Close'])
        self.df['RSI'] = self.rsi_values
        self.df['Signal'] = self.generate_signals(self.rsi_values)
        self.balance = balance

    # Calculate RSI
    def calculate_rsi(self,prices, period=14):
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # Generate Trading Signals
    def generate_signals(self,rsi_values):
        signals = []
        for rsi in rsi_values:
            if rsi > 70:
                signals.append('SELL')
            elif rsi < 30:
                signals.append('BUY')
            else:
                signals.append('HOLD')
        return signals  

    def backtest_rsi(self):
        balance = self.balance
        position = 0
        for i in range(len(self.df)):
            if self.df['Signal'][i] == 'BUY' and position == 0:
                position = balance / self.df['Close'][i]
                balance = 0
            elif self.df['Signal'][i] == 'SELL' and balance == 0:
                balance = position * self.df['Close'][i]
                position = 0

        final_balance = balance + (position * self.df['Close'][-1])

        return final_balance
    

class OBV:

    def __init__(self,df,balance=10000):
        self.df = df
        self.calculate_obv(self.df)
        self.generate_obv_signals(self.df)
        self.balance = balance


    def calculate_obv(self,df):
        # Calculate OBV
        df['Daily_Return'] = df['Close'].pct_change()
        df['Direction'] = df['Daily_Return'].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
        df['OBV'] = df['Direction'] * df['Volume']
        df['Cumulative_OBV'] = df['OBV'].cumsum()

    def generate_obv_signals(self,df):
        df['Signal'] = 0  # 0 indicates no action
        df.loc[df['Cumulative_OBV'] > df['Cumulative_OBV'].shift(1), 'Signal'] = 1  # Buy signal
        df.loc[df['Cumulative_OBV'] < df['Cumulative_OBV'].shift(1), 'Signal'] = -1  # Sell signal

    def backtest_obv(self):
        # Execute the strategy
        balance = self.balance
        shares = 0

        for index, row in self.df.iterrows():
            if row['Signal'] == 1:  # Buy
                shares_to_buy = balance // row['Close']
                shares += shares_to_buy
                balance -= shares_to_buy * row['Close']
            elif row['Signal'] == -1:  # Sell
                balance += shares * row['Close']
                shares = 0

        # If there are remaining shares, sell them at the last price
        balance += shares * self.df.iloc[-1]['Close']

        return balance 