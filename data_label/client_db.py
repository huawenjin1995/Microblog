#coding: utf-8
from config import host, username, password, charset, database, table, data_name
import mysql.connector
from webapp import app
import hashlib


#对客户提供的数据库进行操作,host, username, password, charset,
# database, table, data_name均为连接客户数据库需要的参数
class DB_Client():
    def __init__(self):
        self.connect = mysql.connector.connect(host=host, user=username,
                                password=password, charset=charset)

        self.db = self.connect.cursor()
        self.db.execute('use  %s;' %database)

    def commit(self):
        self.connect.commit()

    def get_column(self, column=data_name):
        self.db.execute("select %s from %s;" %(column,table))
        result = self.db.fetchall()      #result: ((0,),(1,),(2,),...)
        return [item[0] for item in result]

    #根据'id'获取一条待标注数据
    def get_one_data(self, id, column=data_name):
        self.db.execute("select %s from %s where id=%d limit 1;" % (column, table, id))
        result = self.db.fetchall()  # result: ((0,),(1,),(2,),...)
        return [item[0] for item in result]


    def close(self):
        self.connect.close()


client_db = DB_Client()             #实例化客户数据库


if __name__ == '__main__':
    client_db.db.execute('drop table if exists Evaluations;')
    try:
        Evaluations = '''
        CREATE TABLE Evaluations
        (
          id        int             NOT NULL auto_increment primary key,
          data      varchar(16000)  NOT NULL ,
          data_md5  varchar(128)    NOT NULL unique
        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''

        client_db.db.execute(Evaluations)
    except Exception as e:
        app.logger.info(e)

    data_md5_list = client_db.get_column('data_md5')           #获取插入的行号列表
    sql = "INSERT INTO Evaluations(data, data_md5) VALUES ('%s', '%s')"

    with open('../test.txt') as file:
        for line in file:
            if line.strip():
                string = line[0] + line[int(len(line)/2)] +line[len(line)-1]
                data_md5 = hashlib.md5(string.encode(encoding='utf8')).hexdigest()
                if data_md5 not in data_md5_list:                          #未插入的行
                    try:
                        client_db.db.execute(sql % (line,data_md5))        #开始插入记录
                    except:
                        pass
        client_db.commit()

    id_list = client_db.get_column('id')
    evaluation = client_db.get_column('data')
    client_db.close()
    print(id_list)
    print(evaluation)


