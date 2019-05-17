
# coding: utf-8

# In[5]:



# coding: utf-8

# In[3]:


import tushare as ts
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ts.set_token('b39331c7d64c76a09b3625a9412f687e20b8fceb8aa9315ffb822dfa')
pro = ts.pro_api()


#给各个因子打分，这里写得不够完整
def backtest(f1,f2,f3,o1,o2,o3,w1,w2,w3):
    def params(year,month,day):
        if int(month)<10:
            if int(day)<10:
                start_date=year+'0'+month+'0'+day
            else:
                start_date=year+'0'+month+day
        else:
            if int(day)<10:
                start_date=year+month+'0'+day
            else:
                start_date=year+month+day
        return start_date
    
    def pool(start_date,end_date,freq,index):
        b={'上证50指数':'000016.SH','沪深300指数':'000300.SH','中证500指数':'000905.SH'}
        idx=b[index]
        #因为tushare不能自定义间隔，所以只能用每日每周每月三种频率
        if freq=='每天':
            benchmark = pro.index_daily(ts_code=idx, start_date=start_date, end_date=end_date,fields='ts_code,trade_date,close')
        elif freq=='每周':
            benchmark = pro.index_weekly(ts_code=idx, start_date=start_date, end_date=end_date,fields='ts_code,trade_date,close')
        elif freq=='每月':
            benchmark = pro.index_monthly(ts_code=idx, start_date=start_date, end_date=end_date,fields='ts_code,trade_date,close')
        #获取股票池
        if idx=='000300.SH':
            indexlist=[i+'.SH' for i in ts.get_hs300s()['code'].tolist()]
        elif idx =='000016.SH':
            indexlist=[i+'.SH' for i in ts.get_sz50s()['code'].tolist()]
        elif idx=='000905.SH':
            indexlist=[i+'.SH' for i in ts.get_zz500s()['code'].tolist()]
        
        #把回测区间的所有数据都抓取下来
        stock=pd.DataFrame()
        for i in benchmark['trade_date'].tolist():
            stocklist = pro.daily_basic(ts_code='', trade_date=str(i),fields='ts_code,trade_date,turnover_rate,total_mv,pe,pb,ps,close')
        #选取在股票池中的股票
            stocklist = stocklist[stocklist.ts_code.isin(indexlist)]
        #将因子标准化后再排序
            stocklist[['turnover_rate','total_mv','pe','pb','ps']]=stocklist[['turnover_rate','total_mv','pe','pb','ps']].apply(lambda x:(x-x.mean()))
            stock=pd.concat([stocklist,stock],axis=0)
            
        
    
        #这里想把benchmark在后面和performance merge起来，但是始终有找不出来的bugQAQ
        stock=stock.reset_index()
        benchmark=benchmark.reset_index()
        #benchmark=benchmark.drop(['ts_code'],axis=1)
        #benchmark=benchmark.rename({'close':'benchmark_close'},axis='columns')
    
        return [stock,benchmark]
    
    stock=pool(params(year01.get(),month01.get(),day01.get()),params(year02.get(),month02.get(),day02.get()),freq0.get(),index0.get())[0]
    benchmark=pool(params(year01.get(),month01.get(),day01.get()),params(year02.get(),month02.get(),day02.get()),freq0.get(),index0.get())[1]
    
    if o1=='从小到大':
        stock[f1]=stock[['trade_date',f1]].groupby('trade_date').rank()
    elif o1=='从大到小':
        stock[f1]=stock[['trade_date',f1]].groupby('trade_date').rank(ascending=False)
    
    if o2=='从小到大':
        stock[f2]=stock[['trade_date',f2]].groupby('trade_date').rank()
    elif o2=='从大到小':
        stock[f2]=stock[['trade_date',f2]].groupby('trade_date').rank(ascending=False)
    
    if o3=='从小到大':
        stock[f3]=stock[['trade_date',f3]].groupby('trade_date').rank()
    elif o3=='从大到小':
        stock[f3]=stock[['trade_date',f3]].groupby('trade_date').rank(ascending=False)
    
    #总分：因为权重总是1所以w3似乎是多余的？
    stock['score']=w1*stock[f1]+w2*stock[f2]+(1-w1-w2)*stock[f3]
    
    #打分前20（待确认）
    select_stock=stock[['ts_code','trade_date','close','score']].groupby('trade_date').apply(lambda x:x.nlargest(20,'score'))
    
    #这里待改，不一定是等权重持有
    performance=select_stock[['trade_date','close']].groupby('trade_date').sum(axis=1)/20
    #pic=pd.merge(performance,benchmark,on='trade_date')
    
    
    
    
    #画图，将调仓后的股票和指数进行对比；不过这里暂时只画了所持有的股票组合走势，没有画benchmark
    
    
    figure = plt.Figure(figsize=(5,4), dpi=100)
    ax = figure.add_subplot(111)
    line = FigureCanvasTkAgg(figure, root)
    line.get_tk_widget().pack()
    performance.plot(kind='line', legend=True, ax=ax, color='r',marker='o', fontsize=10)
    ax.set_title('portfolio')

    
    
    #需要增加一些类似于夏普比率、最大回撤率之类的计算

root = tk.Tk()
root.title('多因子选股')
root.geometry('500x480+500+200')

#step1
step1 = tk.Label(root, text = 'STEP1:构建股票池')
step1.place(x = 10, y = 10)

index_str = tk.Label(root, text = '指数成分：')
index_str.place(x = 10, y = 40)

index0 = tk.StringVar()
index = ttk.Combobox(root, width = 15, textvariable = index0)
index.place(x = 80, y = 40)
index['value'] = ('请选择','上证50指数','沪深300指数','中证500指数')
index.current(0)

#step2
step2 = tk.Label(root, text = 'STEP2:多因子选择及权重设置')
step2.place(x = 10, y = 90)

factor_str = tk.Label(root, text = '排名条件：')
factor_str.place(x = 10, y = 120)
factor_str1 = tk.Label(root, text = '权重打分:')
factor_str1.place(x = 280, y = 120)

factor01 = tk.StringVar(); factor02 = tk.StringVar(); factor03 = tk.StringVar()
order01 = tk.StringVar(); order02 = tk.StringVar(); order03 = tk.StringVar()
weight01 = tk.IntVar(); weight02 = tk.IntVar(); weight03 = tk.IntVar()
factor_list = [factor01, factor02, factor03]
order_list = [order01, order02, order03]
weight_list = [ weight01, weight02, weight03]

for i in range(3):
    factor = ttk.Combobox(root, width = 7, textvariable = factor_list[i])
    factor.place(x = 80, y = 120 + i*30)
    factor['value'] = ('请选择','换手率','市盈率PE','市净率PB','市销率PS','总市值')#因子待确定
    factor.current(0)

    order = ttk.Combobox(root, width = 6, textvariable = order_list[i])
    order.place(x = 170, y = 120 + i*30)
    order['value'] = ('从大到小','从小到大')
    order.current(0)

    weight = ttk.Combobox(root, width = 6, textvariable = weight_list[i])
    weight.place(x = 245+105, y = 120 +i*30)
    weight['value'] = tuple(range(10,110,10))
    weight.current(0)

#step3
step3 = tk.Label(root, text='STEP3:回测设置')
step3.place(x = 10, y = 170+50)

date_str = tk.Label(root, text= '回测时间：')
date_str.place(x = 10, y = 200+50)
freq_str = tk.Label(root, text = '调仓频率：')
freq_str.place(x = 10, y = 230+50)
to = tk.Label(root, text = '至')
to.place(x = 260, y = 250)

year01 = tk.StringVar(); year02 = tk.StringVar()
month01 = tk.StringVar(); month02 = tk.StringVar()
day01 = tk.StringVar() ; day02 = tk.StringVar()
year_list = [year01, year02];month_list = [month01, month02];day_list = [day01, day02]

'''
(这部分没debug出来，实际会遇到用户选择2月31日的情况，怎么处理？？)
#不同月份有不同日期
def getday1():
    if month01.get() in ('1月', '3月', '5月', '7月', '8月', '10月', '12月'):
        day1['value'] = tuple(str(i)+'日' for j in range(1, 32))#若出现2月31日
    else:
        if month01.get() != '2月':
            day1['value'] = tuple(str(i)+'日' for j in range(1, 32))
        else:
            year = int(year01.get()[:4])
            if (year ==0 and year % 100 != 0) or (year % 400 == 0):
                day1['value'] = tuple(str(i)+'日' for j in range(1, 30))
            else:
                day1['value'] = tuple(str(i)+'日' for j in range(1, 29))           
    root.after(500,getday1())

def getday2():
    if month02.get() in ('1月', '3月', '5月', '7月', '8月', '10月', '12月'):
        day2['value'] = tuple(str(i)+'日' for j in range(1, 32))#若出现2月31日
    else:
        if month02.get() != '2月':
            day2['value'] = tuple(str(i)+'日' for j in range(1, 32))
        else:
            year = int(year02.get()[:4])
            if (year ==0 and year % 100 != 0) or (year % 400 == 0):
                day2['value'] = tuple(str(i)+'日' for j in range(1, 30))
            else:
                day2['value'] = tuple(str(i)+'日' for j in range(1, 29))           
    root.after(500,getday2())
'''

for i in range(2):
    year = ttk.Combobox(root, width = 6, textvariable = year_list[i])
    year.place(x = 80+200*i, y = 200+50)
    #year['value'] = tuple(str(j)+'年' for j in range(2000, 2020))#时间待确定
    year['value'] = tuple(str(j) for j in range(2000, 2020))
    year.current(0)

    month = ttk.Combobox(root, width = 3, textvariable = month_list[i])
    month.place(x = 155+200*i, y = 200+50)
    month['value'] = tuple(str(j) for j in list(range(1, 13)))
    month.current(0)
 
    day = ttk.Combobox(root, width = 3, textvariable = day_list[i])
    day.place(x = 210+200*i, y = 200+50)
    day['value'] = tuple(str(j) for j in range(1, 32))
    day.current(0)


#调仓频率
freq0 = tk.StringVar()
freq = ttk.Combobox(root, width = 9, textvariable = freq0)
freq.place(x = 80, y = 230+50)
freq['value'] = ('每天','每周','每月')
freq.current(0)

#Buttons

f={'换手率':'turnover_rate','市盈率PE':'pe','市净率PB':'pb','市销率PS':'ps','总市值':'total_mv'}


backtest_button = tk.Button( root, text = '开始回测', width = 18, height = 2, command = lambda: backtest(f[factor01.get()],f[factor02.get()],f[factor03.get()],order01.get(),order02.get(),order03.get(),weight01.get(),weight02.get(),weight03.get()))# 函数写好了再设置command
backtest_button.place(x = 170, y = 340)


report_button = tk.Button( root, text = '生成报告', width = 18, height = 2)#, command = report 函数写好了再设置command
report_button.place(x = 170, y = 400)


root.mainloop()


'''
变量汇总:

(1)股票池指数 【str类型】
index0.get() 
取值：('请选择','中证50指数','沪深300指数','中证500指数','中证1000指数)

(2)因子 【str类型】
factor01.get()
factor02.get()
factor03.get()
取值：('请选择',1,2,3,4) (因子待确定)

(3)对应因子的排序 【str类型】
order01.get()
order02.get()
order03.get()
取值：('从大到小','从小到大')

(4)对应因子的权重 【int类型】
weight01.get()
weight02.get()
weight03.get()
取值：(10,20,30,40,50,60,70,80,90,100)

(5)回测时间：包括起始年日月和结束的年日月 【str类型】
year01.get()
year02.get()
month01.get()
month02.get()
day01.get()
day02.get()
取值：2000-2019年  1-12月  1-31日
**这里要注意判断一些无效时间，如2月31日。

(6)调仓频率 【str类型】
freq0.get()
取值：('每天','每周','每月')

'''

