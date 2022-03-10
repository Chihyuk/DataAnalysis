from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import csv
# from . import tests

def index(req):
    return render(req, 'index.html')

def index_save(req):
    data = {}

    # 첨부파일 가져와 읽기
    path = 'C:/Users/Song/Desktop/SelfStudy/MakeWebpage/Django/DataAnalysis/home/TEST_0307.csv'
    df = pd.read_csv(path)

    # 인덱스명만 추출
    index = df.columns.tolist()
    # X로 시작하는 것들만 추출
    matching = [i for i in index if i.startswith("X")] 
    # html에서 사용할 수 있도록 딕셔너리 안에 리스트로 저장
    data['index'] = matching

    # 해당 메소드를 요청한 방법이 POST인 경우
    if req.method == 'POST':
        data['POST'] = 'POST방식입니다!!'
        
        # 버튼으로 선택한 것들을 받아오기
        selected = req.POST.getlist('selected')
        # 받아온 인자들로만 데이터프레임 만들기
        selectMatch = df[selected]
        data['selectMatch'] = selectMatch

        return render(req, 'index_save.html', data)

    return render(req, 'index_save.html', data)

def makeTrainTest(df, pct):      # 데이터프레임을 인자값으로 받아서 원하는 퍼센트로 train test set 만들기
    # 데이터프레임의 전체 행 수 추출
    peoCount = len(df)

    # 중복되지 않는 pct 랜덤 값 추출
    testRd = []
    for pc in range(round(peoCount*pct)):
        temp = random.randrange(0,peoCount-1)
    while temp in testRd:
        temp = random.randrange(0,peoCount-1)
    testRd.append(temp)

    # test df 생성
    testDf = df.loc[testRd].sort_index()
    # train df 생성
    trainDf = df.drop(testRd)

    # 그래프 그리기 위해 test인 사람과 train인 사람 라벨링하여 df로 만들기
    people1 = pd.DataFrame({'people':trainDf.index, 'set':'test'})
    people2 = pd.DataFrame({'people':trainDf.index, 'set':'train'})
    people = pd.concat([people1, people2])

    # pie chart 생성
    pp = people['set'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(aspect="equal"))
    def func(pct, allvals):
        absolute = int(np.round(pct/100.*np.sum(allvals)))
        return "{:.5f}%\n({:d} number of people)".format(pct, absolute)

    wedges, texts, autotexts = ax.pie(pp.values, autopct=lambda pct: func(pct, pp.values),
                                    textprops=dict(color="w"))
    plt.show()


def getposttest(req):
    if req.method == 'POST':
        return render(req, 'post_list.html', {'POST':'POST방식입니다!!'})
    if req.method == 'GET':
        return render(req, 'post_list.html', {'GET':'GET방식입니다!!'})