import pandas as pd
import pyupbit
import numpy as np
from datetime import datetime, time, date, timedelta
from calendar import monthrange
from time import sleep
from pytz import timezone

#access = "ACCESS"
#secret = "SECRET"
print(pyupbit)
upbit = pyupbit.Upbit(access,secret)

def get_upbit_ohlcv(now, ticker, year, month):
    df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

    # 해당 년월 1일부터
    from_date = date(year, month, 1)

    # 해당 년월 마지막 일(28일, 30일, 31일)
    end_day = monthrange(year, month)[1]
    to_date = date(year, month, end_day)

    # 해당 년월 마지막 일자가 현재 프로그램 수행일자보다 큰 경우
    if to_date >= now.date():
        to_date = now.date()
        end_day = to_date.day
    
    # 해당 년월 1일부터 말일(또는 프로그램 수행일자)까지 데이터 수집 실시
    for day in range(1, end_day+1):
        cnt = 200 # default
        base_time = datetime.combine(from_date, time(3, 20, 0))
       # base_time -= timedelta(hours=6, minutes=14)
       # print(base_time)
        for i in range(8):
            try:
                df_temp = pyupbit.get_ohlcv(ticker, interval='minute1', count=cnt, to=base_time)
                #print(i, 'base_time:', base_time, 'shape:', df_temp.shape)
                df = pd.concat([df, df_temp], axis=0)
                if i == 6:
                    base_time += timedelta(hours=0, minutes=40)
                else:
                    base_time += timedelta(hours=3, minutes=20)
            except Exception as e:
                print('Exception:', e)
        from_date = from_date + timedelta(days=1)
        sleep(0.5)
    return df

start_year = 2023
end_year = 2024
start_month = 3
end_month = 5

# my_ticker = "KRW-BTC"
# my_interval = "minutes1"
# df = pd.DataFrame()
# for year in range (start_year, end_year):
#     for month in range(start_month, end_month):

#         # 해당 년월 마지막 일(28일, 30일, 31일)
#         end_day = monthrange(year, month)[1]

#         now = datetime.now()

#         df = pd.concat([df,get_upbit_ohlcv(now, ticker=my_ticker, year=year, month=month)])
        
# df.reset_index(inplace=True)
# df.drop_duplicates('index', inplace=True)
# # df = df[(datetime.combine(date(year, month, 1), time(0, 0, 0)) <= df['index']) & (df['index'] < datetime.combine(date(year, month, end_day), time(23, 59, 59)))]

# fileName = '{}_{}_{}_{}_{}_ohlcv.csv'.format(start_year, start_month, end_year-1, end_month-1, my_ticker)
# df.to_csv('./data/'+fileName, index=False)

        
fileName = './data/2023_3_2023_4_ohlcv.csv'
df2 = pd.read_csv(fileName)
print(df2)

# 전략 백테스트 함수
def backtest_strategy(data, initial_capital):
    # 전략 구현
    positions = np.zeros(len(data))
    # for i in range(1, len(data)):
    #     if data['close'][i] > data['close'][i-1]:
    #         positions[i] = 1  # 매수
    #     else:
    #         positions[i] = 0  # 매도
    for i in range(1, len(data)):
        if data['close'][i] > data['high'][i-1]:  # 상승 돌파 시 매수
            positions[i] = 1
        elif data['close'][i] < data['low'][i-1]:  # 하락 돌파 시 매도
            positions[i] = 0
        else:
            positions[i] = positions[i-1]  # 이전 포지션 유지

    # 수익률 계산
    returns = data['close'] / data['close'].shift(1) - 1
    shifted_positions = pd.Series(positions).shift(1)  # 이전 포지션을 담은 Series 생성
    strategy_returns = returns * shifted_positions.values  # 수정된 부분

    print(returns)
    print(strategy_returns)

    # 누적 수익률 계산
    cumulative_returns = (1 + strategy_returns).cumprod()
    print(cumulative_returns)
    # 자산 계산
    asset_values = initial_capital * cumulative_returns

    # 최저 자산, 최고 자산, MDD 계산
    min_asset_value = asset_values.min()
    max_asset_value = asset_values.max()
    peak = max_asset_value / initial_capital
    drawdown = ((max_asset_value - min_asset_value) / max_asset_value)

    # 결과 출력
    print("시작 자산:", initial_capital)
    print("최종 자산:", asset_values.iloc[-1])
    print("누적 수익률:", cumulative_returns.iloc[-1])
    print("최저 자산:", min_asset_value)
    print("최고 자산:", max_asset_value)
    print("MDD:", drawdown)
    print("Peak:", peak)

# 전략 백테스트 실행
initial_capital = 1000000  # 시작 자산 설정
backtest_strategy(df2, initial_capital)