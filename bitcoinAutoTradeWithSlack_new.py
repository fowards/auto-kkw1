import time
import pyupbit
import datetime
import requests

access = "Bxvsn0XODvSlkNyQVwiVYQsLFYWLWFyJ7WBFiWxW"
secret = "2rDFWt1pfFTW7sSSMxfd9MfLKQMS6tsiTxZ4RW76"
myToken = "xoxb-2355206505509-2381871754192-6zTkCmq4XPzw3kCUOPZnv7yJ1"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

    


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "autotrade start")




buy_result = 0
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(minutes=1)
        print("start time : " +str(start_time))
        print("end time : " +str(end_time))

        if start_time < now < end_time - datetime.timedelta(seconds=5):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            
            revised_price = round(current_price/1000*0.999)*1000
            
           # if target_price < current_price :
            krw = get_balance("KRW")
            print(krw)

            if krw > 5000:
                    buy_result = upbit.buy_limit_order("KRW-BTC",revised_price,0.9*krw/current_price)
                    print(buy_result)
                    post_message(myToken,"#crypto", "BTC buy : " +str(buy_result))
                   
                                    
        else:
            btc = get_balance("BTC")
            print(btc)
            get_order = upbit.get_order("KRW-BTC")
            print(get_order)
            if len(get_order) != 0:
                cancel_result = upbit.cancel_order(get_order[0]['uuid'])
                print(cancel_result)
            if btc > 0.00008:
                
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                print(sell_result)
                post_message(myToken,"#crypto", "BTC buy : " +str(sell_result))

              
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#crypto", e)
        time.sleep(1)
  