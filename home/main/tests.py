import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

class tests:
    def testdf():
        # 첨부파일 가져와 읽기
        path = "C:\Users\Song\Desktop\SelfStudy\MakeWebpage\Django\DataAnalysis\home\TEST_0307.csv"
        data = pd.read_csv(path)
        return data

data = tests.testdf()
# 데이터프레임의 전체 행 수 추출
peoCount = len(data)

# 중복되지 않는 30% 랜덤 값 리스트로 추출
testPeo = []
for pc in range(round(peoCount*0.3)):
    temp = random.randrange(0,247)
    while temp in testPeo:
        temp = random.randrange(0,247)
    testPeo.append(temp)

# 30%에 해당되지 않는 항목만 데이터프레임으로 추출
trainPeo = data.drop(testPeo)

# 사람들만 따로 데이터프레임으로 생성
people1 = pd.DataFrame({'people':testPeo, 'tt':'test'})
people2 = pd.DataFrame({'people':trainPeo.index, 'tt':'train'})
people = pd.concat([people1, people2])

# 파이그래프로 그래프 그리기
pp =people['tt'].value_counts()
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(aspect="equal"))
def func(pct, allvals):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return "{:.5f}%\n({:d} number of people)".format(pct, absolute)

wedges, texts, autotexts = ax.pie(pp.values, autopct=lambda pct: func(pct, pp.values),
                                  textprops=dict(color="w"))
plt.show()
