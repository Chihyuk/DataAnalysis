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
    # 초기값 지정
    # sel_val = 0.7
    # inputfile = None
    global sel_val
    global inputfile
    data = {}

    # ip 가져오기
    ip = get_client_ip(req)
   
    if req.method == 'POST':
        if 'sel_val' in req.POST:
            # 선택한 퍼센트 가져오기
            sel_val = req.POST.get('sel_val')
            sel_val = float(sel_val)
            
        if 'inputfile' in req.FILES:
            # 첨부 파일 가져오기
            inputfile = req.FILES['inputfile']

            # 첨부파일 저장하기
            fs = FileSystemStorage()
            filename = f"temp/{ip}.csv"
            filename = fs.save(filename, inputfile)

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
        trainDf, testDf, people = makeTrainTest(df, sel_val)

        # FusionCharts에 사용할 data json 형태 만들기
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

        data['output'] = chartObj.render()

        # 인덱스명만 추출
        index = df.columns.tolist()
        # X로 시작하는 것들만 추출
        matching = [i for i in index if i.startswith("X")] 
        # html에서 사용할 수 있도록 딕셔너리 안에 리스트로 저장
        data['index'] = matching

        # selected의 이름을 가진 버튼이 선택된 경우
        if 'selected_index' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_index = req.POST.getlist('selected_index')
            # 받아온 인자들로만 데이터프레임 만들기
            selectMatch_index = df[selected_index]
            data['selectMatch_index'] = selectMatch_index


        # 범주 찾기
        exist = 0                                                           # 유일 값이 있는지 확인하기 위한 변수
        cat = {}                                                            # 해당 value_count 담기
        for i in range(len(df.columns)):
            if df.iloc[:,i].count() != 0:                                   # 값이 0이 아닌 것들 중
                for j in range(len(df.iloc[:,i].value_counts().values)):    # 값 분류한 만큼 for문을 돌려서
                    if df.iloc[:,i].value_counts().values[j] == 1:          # 값 중 유일 값을 가지고 있는 경우 중단시키기
                        exist = 1
                        break
                if exist == 0:                                              # 유일 값을 가지고 있지 않은 경우
                    if df.iloc[:,i].value_counts().count() != 1:            # 하나만 존재하는 것 제외
                        cat[i] = df.iloc[:,i].value_counts()
            exist = 0                                                       # exist 초기화

        nameCat = []                                                        # 이름으로 HTML에 보여주기 위해 이름만 list로 저장
        for c in cat:
            nameCat.append(cat[c].name)                     

        data['category'] = nameCat                                          # 범주에 해당되는 값의 컬럼 번호를 리스트형으로 전달
        # selected_category의 이름을 가진 버튼이 선택된 경우
        if 'selected_category' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_category_name = req.POST.get('selected_category')
            selected_category_no = list(cat.keys())[nameCat.index(selected_category_name)]      # 이름으로 컬럼 번호 찾기
            print(list(cat[selected_category_no].index), list(cat[selected_category_no].values))

            data['selected_category_label'] = list(cat[selected_category_no].index)
            data['selected_category_data'] = list(cat[selected_category_no].values)

        return render(req, 'pie.html', data)
 

def MakeChart(dataJson):
    # "data": [{"label" : "asdf", "value" : "zxcv"}, {"label" : "asdf", "value" : "zxcv"},]}

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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



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


def chartjs(req):
    labels = ['a', 'b', 'c']
    data = [100, 200, 300]
    return render(req, 'chartjs.html', {
        'labels': labels,
        'data': data,
    })