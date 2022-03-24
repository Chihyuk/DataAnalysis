# #SqlCon.py
# import mysql.connector
# class SqlCon:
#     hostlink = 'localhost'
#     conn = mysql.connector.connect(host = hostlink, port = '3306', user='song', password='1234', database='News_Summary')  # 해당 인자도 다 변수로 사용할 수 있으면 좋다

#     @staticmethod
#     def Cursor():
#         return SqlCon.conn.cursor()

#     @staticmethod
#     def Close():
#         SqlCon.conn.close()

#     @staticmethod
#     def Commit():
#         SqlCon.conn.commit()

# try:
#     SqlCon.Cursor()
# except:
#     print("연결안댐")