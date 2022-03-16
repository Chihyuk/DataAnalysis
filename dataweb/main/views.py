import mimetypes
import os
import time
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
from django.http import FileResponse
from sklearn.model_selection import train_test_split

# Include the `fusioncharts.py` file which has required functions to embed the charts in html page
# from .fusioncharts import FusionCharts

# 초기값 설정
global sel_val
global inputfile
global selected_category_name
global selected_category_no
global selected_index
sel_val = 0.7

# 초기화시켜줄 메소드
def reset():
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    sel_val = 0.7                       # 기본 초기값
    inputfile = None                    # 입력한 첨부파일
    selected_category_name = None       # 선택한 카테고리명
    selected_category_no = None         # 선택한 카테고리 번호
    selected_index = None               # 선택한 컬럼

def index(req):
    # 시간 측정
    start = time.time()

    # 값 불러와 사용
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index

    # 리턴할 값 모음
    data = {}  

    # ip 가져오기
    ip = get_client_ip(req)
    data['ip'] = ip

    # input data
    try:
        # 첨부 파일 가져오기
        if 'inputfile' in req.FILES:
            inputfile = req.FILES['inputfile']

            # temp폴더에 IP주소명으로 첨부파일 저장하기
            fs = FileSystemStorage()
            filename = f"./temp/{ip}.csv"

            # 만약 해당 경로에 같은 이름의 파일이 있는 경우 삭제
            if os.path.isfile(filename):
                os.remove(filename)

            # 파일 저장
            filename = fs.save(filename, inputfile)

            # 이전에 입력한 항목 초기화
            reset()

        # csv 첨부파일 경로 지정
        path = f"temp/{ip}.csv"
        # path = "temp/58.238.38.231.csv"

        # 지정한 경로에 있는 csv 파일을 읽어오기
        df = pd.read_csv(path)
    except:
        # input data가 없으면 초기화하고 내용 없이 return
        reset()
        return render(req, 'index.html', data)

    # train percent 적용
    try:
        # 선택한 train set 퍼센트 가져오기
        if 'sel_val' in req.POST:
            sel_val = req.POST.get('sel_val')
            sel_val = float(sel_val)

        # 선택한 train set 퍼센트 유지
        data['sel_val'] = sel_val
    except:
        print("train set 설정 중 error 발생")

    # train set, test set 나눈 뒤 파이차트 생성
    try:
        # 입력받은 퍼센트로 입력받은 csv 파일을 train, test set과 그래프로 표현할 데이터로 나누기
        x_train, x_valid, y_train, y_valid, people = makeTrainTest(df, sel_val)
        # chart.js로 파이차트 그리기
        data['selected_train_label'] = list(people['set'].value_counts().index)
        data['selected_train_data'] = list(people['set'].value_counts().values)
    except:
        print("train test set 생성 중 error 발생")

    # 범주 생성
    try:    
        # 범주를 담을 딕셔너리
        cat = {}
        # dataframe column 만큼 for문 돌리기
        for i in range(len(df.columns)):
            # dataframe 모든 row와 i번째 해당하는 column의 value_count(중복된 값이 몇개 있는지 파악)
            vc = df.iloc[:,i].value_counts()
            # distinct 값이 1개 초과 10개 이하일 경우 & 오름차순 했을 떄 첫 번째 리스트 값이 1이상인 경우 저장
            if vc.count() > 1 and vc.sort_values().values[0] > 1:           
                cat[i] = vc

        # 범주 이름으로 보여주기 위해 이름만 list로 저장
        nameCat = []                                                        
        for c in cat:
            nameCat.append(cat[c].name)                     

        # 범주에 해당되는 값의 범주 이름을 리스트형으로 전달
        data['category'] = nameCat        
    except:
        print("범주 생성 중 error 발생")                                  

    # 컬럼명 추출
    try:
        # 컬럼명만 추출
        index = df.columns.tolist()
        # 컬럼 리스트 생성
        data['index'] = index
    except:
        print("컬럼명 추출 중 error 발생")

    # 범주 선택 시 histogram 생성
    try:
        # selected_category의 이름을 가진 버튼이 선택된 경우 (범주)
        if 'selected_category' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_category_name = req.POST.get('selected_category')
            # 이름으로 컬럼 번호 찾기
            selected_category_no = list(cat.keys())[nameCat.index(selected_category_name)]      
    except:
        print("선택한 범주 데이터를 가져오는 중 error 발생")
    else:
        try:
            # 버튼 선택한 기록이 있는 경우
            if selected_category_name != None and selected_category_no != None:
                data['selected_category_name'] = selected_category_name
                data['selected_category_label'] = list(cat[selected_category_no].index)
                data['selected_category_data'] = list(cat[selected_category_no].values)
                data['selected_category_historgram_data'] = list(df[selected_category_name])
            else:
                # 기록이 없는 경우 None 전달
                data['selected_category_name'] = None
                data['selected_category_label'] = None
                data['selected_category_data'] = None
                data['selected_category_historgram_data'] = None
        except:
            selected_category_name = None
            selected_category_no = None
            print("선택한 버튼 데이터를 html로 옮기는 중 error 발생")

    # 선택된 컬럼으로 데이터프레임 생성 및 저장
    try:
        # selected_index의 이름을 가진 버튼이 선택된 경우 (컬럼)
        if 'selected_index' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_index = req.POST.getlist('selected_index')

        # 선택된 컬럼이 있었거나 있는 경우
        if selected_index != None:
            # 받아온 인자들로만 데이터프레임 만들기
            selectMatch_index = df[selected_index]
            # 선택한 컬럼은 html로 전달
            data['selectMatch_index'] = selected_index

            # ip 주소 .을 _로 바꾸기
            d_ip = str(ip).replace('.', '_')
            # 행 번호는 없이 바꾼 이름으로 csv 파일 저장 
            selectMatch_index.to_csv(f'make/{d_ip}.csv', index = False)
            # 데이터프레임 다운 버튼 활성화
            data['download_btn'] = "데이터프레임 다운로드"
        else:
            # 컬럼이 선택되지 않은 경우
            data['selectMatch_index'] = None
            data['download_btn'] = None
    except:
        print("데이터프레임을 만드는 중 error 발생")

    print("time : ", time.time() - start)
    return render(req, 'index.html', data)

# 사용자 ip 얻어오기
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# 데이터프레임을 인자값으로 받아서 원하는 퍼센트로 train test set 만들기
def makeTrainTest(df, pct):    
    start = time.time()
    data = df.iloc[:,1:-1]
    target = df.iloc[:,0]
    x_train, x_valid, y_train, y_valid = train_test_split(data, target, test_size=pct, shuffle=True)
    
    people1 = pd.DataFrame({'people':y_train.index, 'set':'Train'})
    people2 = pd.DataFrame({'people':y_valid.index, 'set':'Test'})
    people = pd.concat([people1, people2])

    print("time2-0-4 : ", time.time() - start)                          
    return x_train, x_valid, y_train, y_valid, people

# 다운로드 버튼 누를경우 작동되는 메소드
def downloadFile(req):
    ip = get_client_ip(req)
    d_ip = str(ip).replace('.', '_')

    filename = f'{d_ip}.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

def downloadTrainFile(req):
    ip = get_client_ip(req)
    d_ip = str(ip).replace('.', '_')

    filename = f'{d_ip}test.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

def downloadTestFile(req):
    ip = get_client_ip(req)
    d_ip = str(ip).replace('.', '_')

    filename = f'{d_ip}train.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

def am(req):
    return render(req, 'amchart.html')


def hc(req):
    return render(req, 'highcharts.html')