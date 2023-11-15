import ccxt
import pandas as pd
from datetime import datetime

# 创建币安交易所对象
#exchange = ccxt.binance()
# 创建个人的欧易（OKEx）交易所对象
exchange = ccxt.okex()
# 定义日期范围
start_date = '2022-11-09'
end_date = '2023-04-30'
timeframe = '1d'


# 定义日期范围的起始和结束时间戳
start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp()) * 1000
end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) * 1000

# 获取币安交易所的所有交易对
markets = exchange.load_markets()

# 存储结果的列表
results = []

# 遍历所有交易对
for symbol in markets:
    # 过滤只保留USDT交易对
    if symbol.endswith('/USDT'):

        # 存储结果的列表
        results1 = []

        # 定义起始时间戳
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp()) * 1000
        # 循环请求数据
        while True:
            # 获取最新的500条K线数据
            candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=start_timestamp, limit=500)
            # 如果没有返回数据，则退出循环
            if len(candles) == 0:
                break

            # 将数据添加到结果列表中
            results1.extend(candles)
            if len(candles) >= 2:
                # 更新起始时间戳，以便下一次请求
                start_timestamp = candles[-1][0] + (candles[-1][0] - candles[-2][0])
            else:
                break

            # 如果已经达到结束日期，则退出循环
            if datetime.fromtimestamp(start_timestamp // 1000).strftime('%Y-%m-%d') > end_date:
                break

        # 过滤指定日期范围内的K线数据
        filtered_candles = [candle for candle in results1 if
                            start_date <= datetime.fromtimestamp(candle[0] // 1000).strftime('%Y-%m-%d') <= end_date]
        if len(filtered_candles) > 0:
            # 获取最高价的日期和价格
            max_price = max(filtered_candles, key=lambda x: x[2])
            max_price_date = datetime.fromtimestamp(max_price[0] // 1000).strftime('%Y-%m-%d')
            max_price_value = max_price[2]

            # 获取最高价之前的最低价和日期
            max_price_index = filtered_candles.index(max_price)
            if max_price_index > 0:
                min_price = min(filtered_candles[:max_price_index], key=lambda x: x[3])
                min_price_date = datetime.fromtimestamp(min_price[0] // 1000).strftime('%Y-%m-%d')
                min_price_value = min_price[3]

                # 计算涨幅
                price_change = (max_price_value - min_price_value) / min_price_value * 100

                # 将结果添加到列表中
                results.append({
                    'Symbol': symbol,
                    'Lowest Price': min_price_value,
                    'Lowest Price Date': min_price_date,
                    'Highest Price': max_price_value,
                    'Highest Price Date': max_price_date,
                    'Price Change': price_change
                })

# 创建DataFrame
df = pd.DataFrame(results)
# 保存数据到Excel文件
df.to_excel('price_analysis.xlsx', index=False)

