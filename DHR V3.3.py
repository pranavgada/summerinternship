#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import pandas as pd
import math
from datetime import timedelta
import matplotlib.pyplot as plt
#pd.set_option("max_row", None)


# In[5]:


data = pd.read_csv("banknifty5min.csv")
data.datetime = pd.to_datetime(data.datetime)
data.head()


# In[6]:


def get_cpr(data):
    pdh = data.high.max()
    pdl = data.low.min()
    pdc = data.close.values[-1]
    cpr = (pdh+pdl+pdc)/3
    return pdh, pdl,pdc,cpr


# In[7]:


def get_entry_exit(df, index, ent, pdh, cpr):
    
    #stoploss is 0.1% above prev day high   
    entry_price = df.low.values[ent]
    entry_time = df.datetime.values[index]
    exit_price = df.open.values[-1]
    exit_time = df.datetime.values[-1]
    
    stop_loss = 1.001 * pdh
    oneR = entry_price-(pdh-entry_price)
    
    if cpr<entry_price :
        target = max(cpr,oneR)
    else:
        target = oneR
    
    low_cl = entry_price
    i = 0
    for close in df.loc[index:]["close"]:
        if close >= stop_loss:
            exit_price = stop_loss
            exit_time = df.datetime.values[index+i]
            break
            
        elif close < low_cl:
            low_cl = close
            stop_loss = 1.001*pdh - (entry_price - close)
            
        else:
            pass
        
        i+=1
        
    fun_tgt = target
    fun_sl = 1.001 * pdh
    
    return entry_time, exit_time, entry_price, exit_price, fun_sl, fun_tgt, low_cl


# In[8]:


date_df = pd.DataFrame({"Date": data.datetime.dt.date.unique()})


# In[9]:


#%%pixie_debugger -b get_entry_exit
entry_time = []
exit_time = []
entry_price = []
exit_price = []
prevdh = []
f_open = []
f_high = []
f_low = []
f_close = []
f_lowcl = []
TGT = []
SL = []
c1 = []
c2 = []
c3 = []

for i in range(len(data.datetime.dt.date.unique())-1):
    
    prev_day = data[data.datetime.dt.date.values == date_df.Date[i]].reset_index(drop = True)
    df = data[data.datetime.dt.date.values == date_df.Date[i+1]].reset_index(drop = True)
    pdh, pdl, pdc, cpr = get_cpr(prev_day)
    flag = True

    for i in range(3):

        if (df.high.values[i] > pdh)&flag:

            for j in range(i,i+4):

                if (df.close.values[j] < pdh)&flag:

                    for k in range(j,75):

                        if df.low.values[k] < df.low.values[j]:
                            ent, ext, enp, exp, sl, tgt, lowcl = get_entry_exit(df, k, j, pdh, cpr)
                            entry_time.append(ent)
                            entry_price.append(enp)
                            exit_price.append(exp)
                            exit_time.append(ext)

                            prevdh.append(pdh)
                            f_open.append(df.open.values[i])
                            f_high.append(df.high.values[i])
                            f_low.append(df.low.values[j])
                            f_close.append(df.close.values[j])
                            TGT.append(tgt)
                            SL.append(sl)
                            c1.append(df.datetime.dt.time.values[i])
                            c2.append(df.datetime.dt.time.values[j])
                            c3.append(df.datetime.dt.time.values[k])
                            f_lowcl.append(lowcl)

                            flag = False
                            break

                        else:
                            pass
                else:
                    pass
        else:
            pass


# In[10]:


final_data = pd.DataFrame({"entry_time":entry_time,
                          "entry_price":entry_price,
                          "exit_time":exit_time,
                          "exit_price":exit_price,
                          "prevdayhigh":prevdh,
                          "fc_open":f_open,
                          "fc_high":f_high,
                          "ec_low":f_low,
                          "ec_close":f_close,
                          "Condition1":c1,
                          "Condition2":c2,
                          "Condition3":c3,
                          "Target":TGT,
                           "Low Cl":f_lowcl,
                           "SL":SL})


# In[11]:


final_data['profit'] = final_data.entry_price>final_data.exit_price
final_data['pc_change'] = (1-(final_data['exit_price']/final_data['entry_price']))
final_data.entry_time = pd.to_datetime(final_data.entry_time)
final_data


# In[20]:


final_data.to_excel('DHR_V3.3.xlsx')


# In[13]:


equity_curve = pd.DataFrame({"date":data.datetime.dt.date.unique()})


# Brokerage Formula:
# 
# Turnover x 7 x 0.00001 + 50
# 
# Slippages:
# 
# 0.001% of Turnover

# In[18]:


net_pos = []
sandb = []
entry_pr = []
exit_pr = []
nlots = []
profit = []
t_o = []
ppl = []



net_pos.append(100000)
sandb.append(0)
entry_pr.append(0)
exit_pr.append(0)
nlots.append(0)
profit.append(0)
t_o.append(0)
ppl.append(0)
j = 0


for i in range(len(date_df)-1):
    
    if j<len(final_data):
        
        if (equity_curve.date.values[i+1]==final_data.entry_time.dt.date.values[j]):
            
            lots = int(net_pos[i]*5/(final_data.entry_price[j]*20))
            turnover = (final_data.entry_price[j]+final_data.exit_price[j])*20
            profpl = (final_data.entry_price[j]-final_data.exit_price[j])*20
            sab = lots*(0.00008*turnover+50)
            net_profit = profpl*lots-sab
            
            net_pos.append(net_pos[i] + net_profit)
            entry_pr.append(final_data.entry_price[j])
            exit_pr.append(final_data.exit_price[j])
            sandb.append(sab)
            nlots.append(lots)
            profit.append(net_profit)
            t_o.append(turnover)
            ppl.append(profpl)
            j+=1
                    
        else:
            
            net_pos.append(net_pos[i])
            sandb.append(0)
            entry_pr.append(0)
            exit_pr.append(0)
            nlots.append(0)
            profit.append(0)
            t_o.append(0)
            ppl.append(0)
            
    else:
        
        net_pos.append(net_pos[i])
        sandb.append(0)
        entry_pr.append(0)
        exit_pr.append(0)
        nlots.append(0)
        profit.append(0)
        t_o.append(0)
        ppl.append(0)


# In[19]:


equity_curve['Net_Position'] = net_pos
equity_curve['Entry Price'] = entry_pr
equity_curve['Exit Price'] = exit_pr
equity_curve['Slippage & Brokerage'] = sandb
equity_curve['Lots'] = nlots
equity_curve['Daily Profit'] = profit
equity_curve['Turnover'] = t_o
equity_curve['Prof per lot'] = ppl

equity_curve


# In[21]:


equity_curve.to_excel("DHRv3.3EquityCurve.xlsx")


# In[22]:


equity_curve.plot(x='date',y='Net_Position',figsize = (12,7));


# In[ ]:




