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
from django.core.files.storage import FileSystemStorage

# Include the `fusioncharts.py` file which has required functions to embed the charts in html page
from .fusioncharts import FusionCharts


global sel_val
global inputfile
sel_val = 0.7
inputfile = None

def pie(req):
    # 초기값 지정
    global sel_val
    global inputfile
    data = {}

    # ip 가져오기
    ip = get_client_ip(req)

    # 원하는 pct 가져와 sel_val 적용
    findPct(req)
    # 첨부파일 받아와 inputfile 적용 및  ip 이름으로 저장
    findSaveInputFile(req, ip)

    # 버튼 유지
    data['sel_val'] = sel_val
    
    # csv 첨부파일 경로 지정
    path = f"temp/{ip}.csv"

    try:
        # 지정한 경로에 있는 csv 파일을 읽어오기
        df = pd.read_csv(path)
    except:
        # 없으면 내용 없이 return
        return render(req, 'pie.html', data)
    else:
        # 입력받은 퍼센트로 입력받은 csv 파일을 train, test set과 그래프로 표현할 데이터로 나누기
        trainDf, testDf, peopleDf = makeTrainTest(df, sel_val)

        # train, test set과 그래프로 표현할 데이터를 넣어 FusionCharts 만들기
        chartObj = makeChart(peopleDf)
        data['output'] = chartObj.render()

        # 인덱스명만 추출
        index = df.columns.tolist()
        # X로 시작하는 것들만 추출
        matching = [i for i in index if i.startswith("X")] 
        # html에서 사용할 수 있도록 딕셔너리 안에 리스트로 저장
        data['index'] = matching

        # POST 중 selected 의 이름을 가진 요소가 있을 경우
        if 'selected' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected = req.POST.getlist('selected')
            # 받아온 인자들로만 데이터프레임 만들기
            selectMatch = df[selected]
            data['selectMatch'] = selectMatch

            return render(req, 'pie.html', data)

        return render(req, 'pie.html', data)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def findPct(req):
    if 'sel_val' in req.POST:
        global sel_val
        # 선택한 퍼센트 가져오기
        sel_val = req.POST.get('sel_val')
        sel_val = float(sel_val)

def findSaveInputFile(req, ip):
    if 'inputfile' in req.FILES:
        global inputfile
        # 첨부 파일 가져오기
        inputfile = req.FILES['inputfile']

        # 첨부파일 저장하기
        fs = FileSystemStorage()
        filename = f"temp/{ip}.csv"
        filename = fs.save(filename, inputfile)

# def makeDf(path):

def makeChart(peopleDf):
    # FusionCharts에 사용할 data json 형태 만들기
    dataJson = '"data": ['
    for i in range(len(peopleDf['set'].value_counts().index)):        # 인덱스의 갯수만큼 for 문 돌리기
        dataJson = dataJson + '{"label" : "'
        index = peopleDf['set'].value_counts().index[i]
        values = str(peopleDf['set'].value_counts().values[i])
        dataJson = dataJson + index + '", "value" : "' + values + '" },'
    dataJson = dataJson + "]}"

    # FusionCharts에 사용할 chart json ("subcaption" : "값"   --> 이렇게 subcaption 추가 가능)
    chartJson = """{
    "chart": {
        "caption": "Train, Test Set",
        "showpercentvalues": "1",
        "defaultcenterlabel": "Train, Test",
        "aligncaptionwithcanvas": "0",
        "captionpadding": "0",
        "decimals": "1",
        "plottooltext": "<b>$percentValue</b> of our TEST_0307.csv are on <b>$label</b>",
        "centerlabel": "# Users: $value",
        "theme": "fusion"
    }, """

    chartObj = FusionCharts('doughnut2d', 'ex1', '600', '400', 'chart-1', 'json', chartJson + dataJson)

    return chartObj

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
    people1 = pd.DataFrame({'peopleDf':trainDf.index, 'set':'Train'})
    people2 = pd.DataFrame({'peopleDf':testDf.index, 'set':'Test'})
    peopleDf = pd.concat([people1, people2])

    return trainDf, testDf, peopleDf
