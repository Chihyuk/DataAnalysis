import pymysql
from sqlalchemy import create_engine

class sql:
    def connectDB(under_ip, df):
        db_connection_str = 'mysql+pymysql://root:1234@localhost/dataAnal'
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
        df.to_sql(name=under_ip, con=db_connection, if_exists='replace',index=False)  

    
    def selectDB(under_ip, df):
        ...