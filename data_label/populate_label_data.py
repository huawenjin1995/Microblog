#coding: utf-8
from config import host, username, password, charset, database, table, data_name
import mysql.connector
from webapp import app
import hashlib


#host, username, password, charset,database, table, data_name均为连接数据库需要的参数
class DB_LABEL():
    def __init__(self):
        self.connect = mysql.connector.connect(host=host, user=username,
                                password=password, charset=charset)

        self.db = self.connect.cursor()
        self.db.execute('use  %s;' %database)

    def create_table(self, create_sql):
        '''

        :param create_sql:创建表的SQL语句
        :return: 成功返回1，数据表已存在返回0， 失败返回-1
        '''
        try:
            db_label.db.execute(create_sql)
            return 1
        except Exception as e:
            app.logger.info(e)
            if e == 'Table' + create_sql + 'already exists':
                return 0
            else:
                return -1


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


db_label = DB_LABEL()             #实例化客户数据库


if __name__ == '__main__':
    # db_label.db.execute('drop table if exists Evaluations;')
    Evaluations = '''
    CREATE TABLE Evaluations
    (
      id        int             NOT NULL auto_increment primary key,
      label     int             NOT NULL,
      review    varchar(16000)  NOT NULL,
      data_md5  varchar(128)    NOT NULL unique
    )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''

    if db_label.create_table(Evaluations) >= 0:          #创建数据表成功
        print('table is exists')

    data_md5_set = set(db_label.get_column('data_md5'))           #获取插入的md5集合，即已经插入的文本
    sql = '''INSERT INTO Evaluations(label, review, data_md5) VALUES ("%s", "%s", "%s")'''

    with open('../新浪微博_4类情感/review.csv') as file:
        for line in file:
            if line.strip() and line[0].isdigit():
                label = int(line[0])
                review = line[2:].replace('\"','')          #去掉文本中的'',否则插入会报语法错误
                #获取每条文本的md5值
                string = ''
                for i in range(len(review)):
                    if i % 4 == 0:
                        string += review[i]
                data_md5 = hashlib.md5(string.encode(encoding='utf8')).hexdigest()

                if data_md5 not in data_md5_set:                                        #未插入的行
                    try:
                        db_label.db.execute(sql % (label,review,data_md5))              #开始插入记录
                    except Exception as e:
                        app.logger.info(e)

        db_label.commit()

    id_list = db_label.get_column('id')
    evaluation = db_label.get_column('review')
    db_label.close()
    print(len(id_list))



