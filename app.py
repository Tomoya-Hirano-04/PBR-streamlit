from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import streamlit as st
import re
import matplotlib.pyplot as plt
import webbrowser

plt.rcParams['font.family'] = 'MS Gothic'

st.title('PBR分析アプリ')

st.write('### PBR（Price Book-value Ratio)とは ###')
st.write(""" 株価が割安か割高かを判断するための指標で、株価純資産倍率といいます。\n
純資産から見た｢株価の割安性｣が示されるため、以下のように判断することができます。\n
『PBRが１より低い』＝市場価格が純資産と比較して安い\n
『PBRが１より高い』＝市場価格が純資産と比較して高い\n
""")

link = "https://quote.jpx.co.jp/jpx/template/quote.cgi?F=tmp/stock_search"

if st.button('株式番号の検索はこちら'):
    webbrowser.open_new_tab(link)

stock_list = st.text_input('株式番号を入力してください（カンマ区切りで複数指定可）', '2201,1301,7203')
stock_list = [int(stock) for stock in stock_list.split(',')]

@st.cache_data
def get_data(stock_list):
    df = pd.DataFrame()
    for stock_text in stock_list:
        url = "https://minkabu.jp/stock/"+str(stock_text)+"/daily_valuation"
        html = requests.get(url)

        # BeautifulSoupのHTMLパーサーを生成
        soup = BeautifulSoup(html.content, "html.parser")

        company_name = soup.find_all('p',{'class': 'md_stockBoard_stockName'})[0].text
        daily_date = soup.find_all('td', {'class': 'tal'})[0].text
        daily_valuation = soup.find_all('td', {'class': 'num'})[3].text

        try:
            daily_valuation = float(soup.find_all('td', {'class': 'num'})[3].text)
        except ValueError:
            daily_valuation = 'PBRが取得できていない企業が含まれています。'

        # 取得したデータを辞書にまとめてDataFrameに追加する
        data = {
            '企業名' : company_name,
            '日付' : daily_date,
            'PBR': daily_valuation
        }
        df_temp = pd.DataFrame(data, index=[0])
        df = pd.concat([df, df_temp], ignore_index=True)

    return df

result = get_data(stock_list)

fig = plt.figure()
ax = fig.add_subplot(111)

pbr = result['PBR'].astype(float)  # PBR
xpos = np.arange(len(pbr))  

cmap = plt.cm.get_cmap('Set3', len(pbr))
colors = [cmap(i) for i in range(len(pbr))]

ax.bar(xpos, pbr, color=colors)
ax.set(xticks=xpos, xticklabels=result['企業名'])
ax.xaxis.label.set_fontname('MS Gothic')
#y軸の範囲を設定
ax.set_ylim(bottom=0, top=result['PBR'].astype(float).max() + 0.5) 

st.pyplot(fig)

