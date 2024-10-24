# from breeze_connect import BreezeConnect
# import urllib
# breeze = BreezeConnect(api_key="77%U3I71634^099gN232777%316Q~v4=")
# breeze.generate_session(api_secret="9331K77(I8_52JG2K73$5438q95772j@",
#                         session_token="48394703")
from breeze_ import *
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta, time as t
import csv, re, time, math
import time

import warnings
warnings.filterwarnings("ignore")

time_1 = t(9, 15)  # 9:17 AM IST -> 3:47 AM UTC
time_2 = t(3, 20)  # 3:01 PM IST -> 9:31 AM UTC
order = 0
expiry = '2024-10-24'
fut_expiry = '2024-10-31'

SL = 5

while True:
    now = datetime.now()
    if order == 0 and t(9, 35)<=t(datetime.now().time().hour, datetime.now().time().minute)<t(9, 46) and now.second == 0 :
        today = datetime.now().strftime("%Y-%m-%d")
        #yesterday = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        for j in range(0,5):
            try:
                data = breeze.get_historical_data_v2(interval="5minute",
                                                     from_date= f"{today}T00:00:00.000Z",
                                                     to_date= f"{today}T17:00:00.000Z",
                                                     stock_code="NIFTY",
                                                     exchange_code="NFO",
                                                     product_type="futures",
                                                     expiry_date=f'{fut_expiry}T07:00:00.000Z',
                                                     right="others",
                                                     strike_price="0")
                break
            except:
                pass
        
        olhc = data['Success']
        olhc = pd.DataFrame(olhc)
        olhc['datetime'] = pd.to_datetime(olhc['datetime'])
        olhc = olhc[(olhc['datetime'].dt.time >= pd.to_datetime('09:15').time()) &
                       (olhc['datetime'].dt.time <= pd.to_datetime('15:29').time())]
        
        candles_3 = olhc.iloc[-4:-1]
        resistance = candles_3['high'].max()
        support = candles_3['low'].min()
        last_row = olhc.iloc[-1]
        
        if last_row['close'] > resistance :
            atm_strike = round(last_row['close']/50) * 50
            
            strikes = [atm_strike-50, atm_strike-100, atm_strike-150, atm_strike-200, atm_strike-250, atm_strike-300, atm_strike-350, atm_strike-400, atm_strike-450, atm_strike-500, atm_strike-550, atm_strike-600, atm_strike-650, atm_strike-700, atm_strike-750, atm_strike-800, atm_strike-850, atm_strike-900, atm_strike-950, atm_strike-1000, atm_strike-1050, atm_strike-1100]
            
            ltps = []

            for strike in strikes:
                for j in range(0, 5):
                    try:
                        leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="put",
                                                        strike_price=strike)
                        break
                    except:
                        pass
    
                leg_df = leg['Success']
                leg_df = pd.DataFrame(leg_df)
                ltp_value = float(leg_df['ltp'])
                ltps.append({'strike_price': strike, 'ltp': ltp_value})
                    

            target_ltp = 25
            closest_strike_pe = None
            min_diff = float('inf')

            for ltp_data in ltps:
                ltp = ltp_data['ltp']
                diff = abs(ltp - target_ltp)
                if diff < min_diff:
                    min_diff = diff
                    closest_strike_pe = ltp_data['strike_price']
            for j in range(0,5):
                try:
                    option_data = breeze.get_historical_data_v2(interval="5minute",
                                                        from_date= f"{today}T07:00:00.000Z",
                                                        to_date= f"{today}T17:00:00.000Z",
                                                        stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f"{expiry}T07:00:00.000Z",
                                                        right="put",
                                                        strike_price=closest_strike_pe)
                    break
                except:
                    pass
            
            option_data = option_data['Success']
            option_data = pd.DataFrame(option_data)
            
            cand = option_data.iloc[-4:-1]
            sup = cand['low'].min()
            last = option_data.iloc[-1]
            
            if last['close'] <= sup :
                initial_point = 0
                order = 1
                SL = 5
                time = datetime.now().strftime('%H:%M:%S')
                entry_premium = last['close']
                tsl = entry_premium + SL
            
                print('SELL', closest_strike_pe, 'PUT at', entry_premium)
                
                csv_file = "Directional_selling.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, time, closest_strike_pe, 'PE', 'Sell', entry_premium])
                        
            else:
                print(now, 'No decay in option chart')
        else:
            print(now, 'Market in range')
                        
        if last_row['close'] < support :
            atm_strike = round(last_row['close']/50) * 50
            
            strikes = [atm_strike+50, atm_strike+100, atm_strike+150, atm_strike+200, atm_strike+250, atm_strike+300, atm_strike+350, atm_strike+400, atm_strike+450, atm_strike+500, atm_strike+550, atm_strike+600, atm_strike+650, atm_strike+700, atm_strike+750, atm_strike+800, atm_strike+850, atm_strike+900, atm_strike+950, atm_strike+1000, atm_strike+1050, atm_strike+1100]
            
            ltps = []


            for strike in strikes:
                for j in range(0, 5):
                    try:
                        leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="call",
                                                        strike_price=strike)
                        break
                    except:
                        pass
    
                leg_df = leg['Success']
                leg_df = pd.DataFrame(leg_df)
                ltp_value = float(leg_df['ltp'])
                ltps.append({'strike_price': strike, 'ltp': ltp_value})
                    

            target_ltp = 25
            closest_strike_ce = None
            min_diff = float('inf')

            for ltp_data in ltps:
                ltp = ltp_data['ltp']
                diff = abs(ltp - target_ltp)
                if diff < min_diff:
                    min_diff = diff
                    closest_strike_ce = ltp_data['strike_price']
            for j in range(0,5):
                try:
                    option_data = breeze.get_historical_data_v2(interval="5minute",
                                                        from_date= f"{today}T07:00:00.000Z",
                                                        to_date= f"{today}T17:00:00.000Z",
                                                        stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f"{expiry}T07:00:00.000Z",
                                                        right="call",
                                                        strike_price=closest_strike_ce)
                    break
                except:
                    pass
            
            option_data = option_data['Success']
            option_data = pd.DataFrame(option_data)
            
            cand = option_data.iloc[-4:-1]
            sup = cand['low'].min()
            last = option_data.iloc[-1]
            
            if last['close'] <= sup :
                initial_point = 0
                order = -1
                SL = 5
                time = datetime.now().strftime('%H:%M:%S')
                entry_premium = last['close']
                tsl = entry_premium + SL
                print('SELL', closest_strike_ce, 'CALL at', entry_premium)
                
                csv_file = "Directional_selling.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, time, closest_strike_ce, 'CE', 'Sell', entry_premium])
                        
            else:
                print(now, 'no decay in option chart')
        else:
            print(now, 'Market in range')
                        
                
                
    if order == 0 and t(9, 16)<t(datetime.now().time().hour, datetime.now().time().minute)<t(15, 30) and now.second == 0 :
        today = datetime.now().strftime("%Y-%m-%d")
        #yesterday = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        for j in range(0,5):
            try:
                data = breeze.get_historical_data_v2(interval="5minute",
                                                     from_date= f"{today}T00:00:00.000Z",
                                                     to_date= f"{today}T17:00:00.000Z",
                                                     stock_code="NIFTY",
                                                     exchange_code="NFO",
                                                     product_type="futures",
                                                     expiry_date=f'{fut_expiry}T07:00:00.000Z',
                                                     right="others",
                                                     strike_price="0")
                break
            except:
                pass
        
        olhc = data['Success']
        olhc = pd.DataFrame(olhc)
        olhc['datetime'] = pd.to_datetime(olhc['datetime'])
        olhc = olhc[(olhc['datetime'].dt.time >= pd.to_datetime('09:15').time()) &
                       (olhc['datetime'].dt.time <= pd.to_datetime('15:29').time())]
        
        candles_3 = olhc.iloc[-7:-1]
        resistance = candles_3['high'].max()
        support = candles_3['low'].min()
        last_row = olhc.iloc[-1]
        
        if last_row['close'] > resistance :
            atm_strike = round(last_row['close']/50) * 50
            
            strikes = [atm_strike-50, atm_strike-100, atm_strike-150, atm_strike-200, atm_strike-250, atm_strike-300, atm_strike-350, atm_strike-400, atm_strike-450, atm_strike-500, atm_strike-550, atm_strike-600, atm_strike-650, atm_strike-700, atm_strike-750, atm_strike-800, atm_strike-850, atm_strike-900]
            
            ltps = []

            for strike in strikes:
                for j in range(0,5):
                    try:
                        leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="put",
                                                        strike_price=strike)
                        break
                    except:
                        pass
    
                leg_df = leg['Success']
                leg_df = pd.DataFrame(leg_df)
                ltp_value = float(leg_df['ltp'])
                ltps.append({'strike_price': strike, 'ltp': ltp_value})
                    

            target_ltp = 25
            closest_strike_pe = None
            min_diff = float('inf')

            for ltp_data in ltps:
                ltp = ltp_data['ltp']
                diff = abs(ltp - target_ltp)
                if diff < min_diff:
                    min_diff = diff
                    closest_strike_pe = ltp_data['strike_price']

            for j in range(0,5):
                try:
                    option_data = breeze.get_historical_data_v2(interval="5minute",
                                                        from_date= f"{today}T07:00:00.000Z",
                                                        to_date= f"{today}T17:00:00.000Z",
                                                        stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f"{expiry}T07:00:00.000Z",
                                                        right="put",
                                                        strike_price=closest_strike_pe)
                    break
                except:
                    pass
            
            option_data = option_data['Success']
            option_data = pd.DataFrame(option_data)
            
            cand = option_data.iloc[-7:-1]
            sup = cand['low'].min()
            last = option_data.iloc[-1]
            
            if last['close'] <= sup :
                initial_point = 0
                order = 1
                SL = 5
                time = datetime.now().strftime('%H:%M:%S')
                entry_premium = last['close']
                tsl = entry_premium + SL
            
                print('SELL', closest_strike_pe, 'PUT at', entry_premium)
                
                csv_file = "Directional_selling.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, time, closest_strike_pe, 'PE', 'Sell', entry_premium])
                        
            else:
                print(now, 'No decay in option chart')
        else:
            print(now, 'Market in range')
                        
        if last_row['close'] < support :
            atm_strike = round(last_row['close']/50) * 50
            
            strikes = [atm_strike+50, atm_strike+100, atm_strike+150, atm_strike+200, atm_strike+250, atm_strike+300, atm_strike+350, atm_strike+400, atm_strike+450, atm_strike+500, atm_strike+550, atm_strike+600, atm_strike+650, atm_strike+700, atm_strike+750, atm_strike+800, atm_strike+850, atm_strike+900]
            
            ltps = []


            for strike in strikes:
                for j in range(0,5):
                    try:
                        leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="call",
                                                        strike_price=strike)
                        break
                    except:
                        pass
    
                leg_df = leg['Success']
                leg_df = pd.DataFrame(leg_df)
                ltp_value = float(leg_df['ltp'])
                ltps.append({'strike_price': strike, 'ltp': ltp_value})
                    

            target_ltp = 25
            closest_strike_ce = None
            min_diff = float('inf')

            for ltp_data in ltps:
                ltp = ltp_data['ltp']
                diff = abs(ltp - target_ltp)
                if diff < min_diff:
                    min_diff = diff
                    closest_strike_ce = ltp_data['strike_price']

            for j in range(0,5):
                try:
                    option_data = breeze.get_historical_data_v2(interval="5minute",
                                                        from_date= f"{today}T07:00:00.000Z",
                                                        to_date= f"{today}T17:00:00.000Z",
                                                        stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f"{expiry}T07:00:00.000Z",
                                                        right="call",
                                                        strike_price=closest_strike_ce)
                    break
                except:
                    pass
            
            option_data = option_data['Success']
            option_data = pd.DataFrame(option_data)
            
            cand = option_data.iloc[-7:-1]
            sup = cand['low'].min()
            last = option_data.iloc[-1]
            
            if last['close'] <= sup :
                initial_point = 0
                order = -1
                SL = 5
                time = datetime.now().strftime('%H:%M:%S')
                entry_premium = last['close']
                tsl = entry_premium + SL
                print('SELL', closest_strike_ce, 'CALL at', entry_premium)
                
                csv_file = "Directional_selling.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, time, closest_strike_ce, 'CE', 'Sell', entry_premium])
                        
            else:
                print(now, 'no decay in option chart')
        else:
            print(now, 'Market in range')
            
            
                    
    if order == 1 :
        import time
        time.sleep(20)
        for j in range(0, 5):
            try:
                leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                    exchange_code="NFO",
                                                    product_type="options",
                                                    expiry_date=f'{expiry}T06:00:00.000Z',
                                                    right="put",
                                                    strike_price=closest_strike_pe)
                break
            except:
                pass
        leg = leg['Success']
        leg = pd.DataFrame(leg)
        leg_cmp = float(leg['ltp'])
        
        pnl_per = (entry_premium - leg_cmp)/entry_premium * 100
        pnl = (entry_premium - leg_cmp)
        print('pnl is:', pnl)
        
        if (entry_premium - leg_cmp) > initial_point :
            initial_point = (entry_premium - leg_cmp)
            tsl = leg_cmp + SL
            
        if (leg_cmp >= tsl) or (t(datetime.now().time().hour, datetime.now().time().minute) == t(15,20)) or pnl_per < -25 :
            order = 0
            exit_premium = -(leg_cmp)
            time = datetime.now().strftime('%H:%M:%S')
            print('Trailing SL hits: PnL is', (entry_premium - leg_cmp))
            
            csv_file = "Directional_selling.csv"
            try:
                with open(csv_file, 'x', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
            except FileExistsError:
                pass
                with open(csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([today, time, closest_strike_pe, 'PE', 'Buy', exit_premium])
                        
            
        
        if pnl_per > 25 :
            print('target hits,', pnl_per,'% profit achieved')
            
        elif pnl_per < -25 :
            print('SL hits, 25% loss booked')
            
            

                
            
    if order == -1:
        import time
        time.sleep(20)
        for j in range(0,5):
            try:
                leg1 = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                    exchange_code="NFO",
                                                    product_type="options",
                                                    expiry_date=f'{expiry}T06:00:00.000Z',
                                                    right="call",
                                                    strike_price=closest_strike_ce)
                break
            except:
                pass
        leg1 = leg1['Success']
        leg1 = pd.DataFrame(leg1)
        leg1_cmp = float(leg1['ltp'])
        
        
        pnl_per = (entry_premium - leg1_cmp)/entry_premium * 100
        pnl = (entry_premium - leg1_cmp)
        print('pnl is:', pnl)
        
        if (entry_premium - leg1_cmp) > initial_point :
            initial_point = (entry_premium - leg1_cmp)
            tsl = leg1_cmp + SL
            
        if (leg1_cmp >= tsl) or (t(datetime.now().time().hour, datetime.now().time().minute) == t(15,20)) or pnl_per < -25 :
            order = 0
            exit_premium = -(leg1_cmp)
            time = datetime.now().strftime('%H:%M:%S')
            print('Trailing SL hits: PnL is', (entry_premium - leg1_cmp))
            csv_file = "Directional_selling.csv"
            try:
                with open(csv_file, 'x', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Time', 'Strike', 'CE/PE', 'Buy/Sell', 'Premium'])
            except FileExistsError:
                pass
                with open(csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([today, time, closest_strike_ce, 'CE', 'Buy', exit_premium])
                        
            
        
        if pnl_per > 25 :
            
            print('target hits,', pnl_per,'% profit achieved')
            
        elif pnl_per < -25 :
            print('SL hits, 25% loss booked')
            
        
        
