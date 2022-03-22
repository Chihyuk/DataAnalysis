import pymysql
from sqlalchemy import create_engine
import mysql.connector
from .SqlCon import SqlCon
import pandas as pd

class SqlQuery:
    @staticmethod
    def insertDB(under_ip, df):
        db_connection_str = 'mysql+pymysql://song:1234@localhost/dataAnal'
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
        df.to_sql(name=under_ip, con=db_connection, if_exists='replace',index=False)  

    @staticmethod
    def selectAllColumn(under_ip):
        cursor = SqlCon.Cursor()
        query = str.format(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'dataAnal' AND TABLE_NAME = '{under_ip}'")
        try: 
            cursor.execute(query)
            row = cursor.fetchall()  
            SqlCon.Commit()
        except:
            return None
        else:
            return row

    @staticmethod
    def selectColumn(under_ip, sel_column):
        cursor = SqlCon.Cursor()
        query = str.format(f"select {sel_column} from {under_ip}")
        try: 
            cursor.execute(query)
            row = cursor.fetchall()   
            SqlCon.Commit()
        except:
            return None
        else:
            return row

    @staticmethod
    def selectColumnType(under_ip, sel_column):
        cursor = SqlCon.Cursor()
        query = str.format(f"show columns from {under_ip} where Field = '{sel_column}'")
        try: 
            cursor.execute(query)
            row = cursor.fetchone()   
            SqlCon.Commit()
        except:
            return None
        else:
            return row

    @staticmethod
    def selectColumnNull(under_ip, sel_column):
        cursor = SqlCon.Cursor()
        query = str.format(f"""
        SELECT COUNT(CASE WHEN PREDICT IS NULL THEN 'NULL' ELSE PREDICT END)
        FROM {under_ip}
        WHERE {sel_column} IS NULL;
        """)
        try: 
            cursor.execute(query)
            row = cursor.fetchone()
            SqlCon.Commit()
        except:
            return None
        else:
            return row

    @staticmethod
    def selectColumnDistinct(under_ip, sel_column):
        cursor = SqlCon.Cursor()
        query = str.format(f"select distinct {sel_column} from {under_ip}")
        try: 
            cursor.execute(query)
            row = cursor.fetchall() 
            SqlCon.Commit()
        except:
            return None
        else:
            return row

    @staticmethod
    def selectColumnValueCounts(under_ip, sel_column):
        cursor = SqlCon.Cursor()
        query = str.format(f"select {sel_column}, count(*) from {under_ip} group by {sel_column} order by {sel_column}")
        try: 
            cursor.execute(query)
            row = cursor.fetchall() 
            SqlCon.Commit()
        except:
            return None
        else:
            return row

# a = SqlQuery.selectColumnValueCounts('127_0_0_1', 'X121')
# print(pd.DataFrame(a))

# selVariableDistinct = SqlQuery.selectColumnDistinct('127_0_0_1', 'X121')
# selVariableDistinctList = [dis[0] for dis in selVariableDistinct]
# print(selVariableDistinctList)