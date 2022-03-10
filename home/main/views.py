from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import csv
from django.shortcuts import render
from django.http import HttpResponse
import datetime

# Include the `fusioncharts.py` file which has required functions to embed the charts in html page
from .fusioncharts import FusionCharts


def index(req):
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

        return render(req, 'index.html', data)

    return render(req, 'index.html', data)

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
    trainDf = df.loc[testRd].sort_index()
    # train df 생성
    testDf = df.drop(testRd)

    # 그래프 그리기 위해 test인 사람과 train인 사람 라벨링하여 df로 만들기
    people1 = pd.DataFrame({'people':trainDf.index, 'set':'Train'})
    people2 = pd.DataFrame({'people':testDf.index, 'set':'Test'})
    people = pd.concat([people1, people2])

    return trainDf, testDf, people


def getposttest(req):
    if req.method == 'POST':
        return render(req, 'post_list.html', {'POST':'POST방식입니다!!'})
    if req.method == 'GET':
        return render(req, 'post_list.html', {'GET':'GET방식입니다!!'})


global sel_val
global inputfile
sel_val = 0.7
inputfile = None

def pie(req):
    # global sel_val
    # global inputfile
    sel_val = 0.7
    inputfile = None
    data = {}
    # select value 초기값 설정            
    if req.method == 'POST':
        if 'sel_val' in req.POST:
            # 버튼으로 선택한 것들을 받아오기
            sel_val = req.POST.get('sel_val')
            sel_val = float(sel_val)
            # req.set_cookie('sel_val', sel_val, max_age=None)
            
        if 'inputfile' in req.FILES:
            # 첨부 파일 가져오기
            inputfile = req.FILES['inputfile']
            print('inputfile : ', inputfile)
            # req.session['inputfile'] = inputfile
            # req.set_cookie('inputfile', inputfile, max_age=None)
            

    # 버튼 유지
    data['sel_val'] = sel_val
    
    # csv 첨부파일 가져와 읽기
    # path = 'C:/Users/Song/Desktop/SelfStudy/MakeWebpage/Django/DataAnalysis/home/TEST_0307.csv'
    if inputfile != None :
        path = inputfile
        df = pd.read_csv(path)

        # train, test set
        trainDf, testDf, people = makeTrainTest(df, sel_val)

        # # data json 형태 만들기
        dataJson = '"data": ['
        for i in range(len(people['set'].value_counts().index)):        # 인덱스의 갯수만큼 for 문 돌리기
            dataJson = dataJson + '{"label" : "'
            index = people['set'].value_counts().index[i]
            values = str(people['set'].value_counts().values[i])
            dataJson = dataJson + index + '", "value" : "' + values + '" },'
        dataJson = dataJson + "]}"

        chartJson = """{
        "chart": {
            "caption": "Train, Test Set",
            "subcaption": "TEST_0307.csv",
            "showpercentvalues": "1",
            "defaultcenterlabel": "Train, Test",
            "aligncaptionwithcanvas": "0",
            "captionpadding": "0",
            "decimals": "1",
            "plottooltext": "<b>$percentValue</b> of our TEST_0307.csv are on <b>$label</b>",
            "centerlabel": "# Users: $value",
            "theme": "fusion"
        }, """

        chartObj = FusionCharts( 'doughnut2d', 'ex1', '600', '400', 'chart-1', 'json', chartJson + dataJson)

        data['output'] = chartObj.render()

    return render(req, 'pie.html', data)


def set_cookie(response, key, value, days_expire = 7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)



def input(req):
    data={}
    if req.method == 'POST':
        # 첨부 파일 가져오기
        inputfile = req.POST.get('file')
        print('inputfile : ', inputfile)
    return render(req, 'input.html', data)


def amchart(req):
    data={}
    return render(req, 'amchart.html', data)