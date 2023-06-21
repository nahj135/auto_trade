import time
import pyupbit
import numpy as np

class VirtualAutoTrader:
    def __init__(self, ticker, strategy, start_balance):
        self.ticker = ticker
        self.start_balance = start_balance
        self.balance = start_balance
        self.strategy = strategy
        self.positions = {}
        self.transaction_fee = 0.0005 
        self.total_num_buy = 0 
        self.total_num_sell = 0 

    def get_data(self):
        self.data = pyupbit.get_ohlcv(self.ticker, interval="minute1", count=200)

    def get_eval_balance(self, ticker, price):
        if ticker not in self.positions:
            return self.balance
        else:
            return (self.balance + self.positions[ticker] * price)

    def get_balance(self):
        return self.balance

    def buy(self, ticker, price):
        krw = self.get_balance()
        if krw <= 1000:
            return 
        
        quantity = (self.balance / price) * (1 - self.transaction_fee) # 거래수수료 제외 
        self.balance -= quantity * price # 잔고 변화 
        self.positions[ticker] = quantity
        print(f'Bought {quantity} {ticker} at {price} KRW. Current balance: {self.balance} KRW')
        self.total_num_buy += 1


    def sell(self, ticker, price):
        if ticker not in self.positions:
            return
        quantity = self.positions[ticker]
        self.balance += (quantity * price) * (1 - self.transaction_fee)
        del self.positions[ticker]
        print(f'Sold {quantity} {ticker} at {price} KRW. Current balance: {self.balance} KRW')
        self.total_num_sell += 1

    def run(self):
        cycle = 0
        while True:
            try:
                self.get_data()
                price = pyupbit.get_current_price(self.ticker)
                action = self.strategy(self.data)  # Call the strategy function with the latest data
                if action == 'buy':
                    self.buy(self.ticker, price)
                elif action == 'sell':
                    self.sell(self.ticker, price)
                time.sleep(1)  # To prevent exceeding the call rate limit

                if cycle % 10 == 0 :
                    print(f'[{cycle}]Balance:', self.balance)
                    print(f'[{cycle}]Positions:', self.positions)
                    print(f'[{cycle}]Total:', self.get_eval_balance(self.ticker, price))                
                
                if cycle == 1000:
                    eval = self.get_eval_balance(self.ticker, price)
                    ratio = (eval - self.start_balance) / (self.start_balance)
                    print(f'DONE Start {self.start_balance} Final {eval}')
                    print(f'Rate {ratio}')
                    break

                cycle += 1 

            except Exception as e:
                print("EXCEPTION")
                print(e)
                time.sleep(1)

# Example strategy function
def simple_moving_average_strategy(data, short_window=5, long_window=10):
    data['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    data['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()
    if data['short_mavg'][-1] > data['long_mavg'][-1]:
        return 'buy'
    else:
        return 'sell'

if __name__ == "__main__":
    at = VirtualAutoTrader("KRW-BTC", simple_moving_average_strategy, 10000000)
    at.run() 
