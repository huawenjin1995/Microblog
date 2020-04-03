#coding: utf-8
from config import host, username, password, charset, database, table, data_name
import pymysql
from webapp import app
import hashlib
from DBUtils.PooledDB import PooledDB, SharedDBConnection


POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建

    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=3,
    # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，
    #因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，
    #_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never,
    # 1 = default = whenever it is requested, 2 = when a cursor
    #is created, 4 = when a query is executed, 7 = always
    host=host,
    port=3306,
    user=username,
    password=password,
    database=database,
    charset=charset
)


#host, username, password, charset,database, table, data_name均为连接数据库需要的参数
class DB_LABEL():
    def __init__(self):
        self.connect = POOL.connection()

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

    def get_column(self, table,column=data_name, limit=None):
        if not limit:
            self.db.execute("select %s from %s;" %(column,table))
        else:
            self.db.execute("select %s from %s limit %d;" %(column,table, limit))

        result = self.db.fetchall()      #result: ((0,),(1,),(2,),...)
        return [item[0] for item in result]

    #取训练样本
    def get_trian_data(self, table, limit=None):
        '''

        :param limit: 样本数量，默认全部已标注过的
        :return: ([ids],[labels],[datas])
        '''
        if not limit:
            self.db.execute("select id,label, %s  from %s where is_labeled=1;" %(data_name,table))
        else:
            self.db.execute("select id,label, %s from %s where is_labeled=1 limit %d;" %(data_name,table, limit))

        result = self.db.fetchall()      #result: ((0,),(1,),(2,),...)
        return ([item[0] for item in result],[item[1] for item in result],
                [item[2] for item in result]) if result else None

    #根据'id'获取一条待标注数据
    def get_one_data(self,id, table,column=data_name):
        self.db.execute("select %s from %s where id=%d limit 1;" % (column, table, id))
        result = self.db.fetchall()  # result: ((0,),(1,),(2,),...)
        return [item[0] for item in result] if result else None

    #取一条未标注过的数据及其id
    def get_one_unlabeled(self,table=table, column=data_name):
        self.db.execute("select id, %s from %s where is_labeled=0 limit 1;" % (column,table))
        result = self.db.fetchall()  # result: ((id0,colunm0,),(id1,column1,),...)
        return ([item[0] for item in result], [item[1] for item in result]) if result else None

    #获取所有未标注的数据
    def get_all_unlabeled(self,table):
        '''

        :param table: 表名
        :return: 返回([id], [column])
        '''
        self.db.execute("select id , %s from %s where is_labeled=0;" % (data_name,table))
        result = self.db.fetchall()
        return ([item[0] for item in result], [item[1] for item in result]) if result else None

    #获取指定标注者预测与实际标注不符的数据id
    def get_diff_predict(self,username, table):
        self.db.execute("select id from %s where label_user='%s' and label != predict_label;" %(table, username))
        result = self.db.fetchall()
        return ([item[0] for item in result]) if result else None

    #更新label
    def update_one_label(self,id, label, username, table):
        '''
        :param id: 更新的数据的id
        :param form: 表单
        :return: 更新成功返回None,失败返回错误原因
        '''
        new_label = label
        try:
            self.db.execute("update %s set label=%d, label_user='%s', is_labeled=1 where id=%d; " %(table, new_label,username, id))
            self.commit()
        except Exception as e:
            app.logger.info(e)
            return e
        return None

    #批量更新标签
    def update_label_many(self, table, data):
        '''
        :param table: 表名
        :param data:更新一条数据（元组），组成列表:[(label1,id1), (label2,id2),...]
        :return:更新成功返回None,失败返回错误原因
        '''
        sql = "update " + table + " set label=(%d)  where id=(%d);"
        count = 0
        for item in data:
            try:
                self.db.execute(sql %(item[0], item[1]))
                count += 1
                if count % 1000 == 0:
                    self.commit()
            except Exception as e:
                app.logger.info(e)
                return e
        self.commit()
        return None

    #批量更新predict_label
    def update_many_predict_label(self, table, data):
        '''
        :param id: 更新的数据的id
        :param table: 表名
        :return: 更新成功返回None,失败返回错误原因
        '''
        # self.db.execute("update %s set predict_label=%d where id=%d " %(table, predict_label, id))
        sql = "update " + table + " set predict_label=(%d)  where id=(%d);"
        count = 0
        for item in data:
            try:
                self.db.execute(sql % (item[0], item[1]))
                count += 1
                if count % 1000 == 0:
                    self.commit()
            except Exception as e:
                app.logger.info(e)
                return e
        self.commit()
        return None

    #获取总数据量
    def get_counts(self):
        self.db.execute("select count* from %s;" %table)
        result = self.db.fetchall()
        return [item[0] for item in result] if result else None



    def close(self):
        self.connect.close()


db_label = DB_LABEL()             #实例化客户数据库


if __name__ == '__main__':
    # db_label.db.execute('drop table if exists Evaluations;')
    # Evaluations = '''
    # CREATE TABLE Evaluations
    # (
    #   id            int             NOT NULL auto_increment primary key,
    #   label         int             NOT NULL,
    #   review        varchar(16000)  NOT NULL,
    #   data_md5      varchar(128)    NOT NULL unique,
    #   is_labeled    int             default 0,
    #   predict_label int             NULL,
    #   label_user    char(64)        NULL
    # )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
    #
    # if db_label.create_table(Evaluations) >= 0:          #创建数据表成功
    #     print('table is exists')
    #
    # data_md5_set = set(db_label.get_column('data_md5'))           #获取插入的md5集合，即已经插入的文本
    # sql = '''INSERT INTO Evaluations(label, review, data_md5) VALUES ("%s", "%s", "%s")'''
    #
    # with open('../新浪微博_4类情感/review.csv') as file:
    #     for line in file:
    #         if line.strip() and line[0].isdigit():
    #             label = int(line[0])
    #             review = line[2:].replace('\"','')          #去掉文本中的'',否则插入会报语法错误
    #             #获取每条文本的md5值
    #             string = ''
    #             for i in range(len(review)):
    #                 if i % 4 == 0:
    #                     string += review[i]
    #             data_md5 = hashlib.md5(string.encode(encoding='utf8')).hexdigest()
    #
    #             if data_md5 not in data_md5_set:                                        #未插入的行
    #                 try:
    #                     db_label.db.execute(sql % (label,review,data_md5))              #开始插入记录
    #                 except Exception as e:
    #                     app.logger.info(e)
    #
    #     db_label.commit()

    # id_list = db_label.get_column(table='Test',column='id')
    # evaluation = db_label.get_column(table='Test',column='review')
    # db_label.close()
    # print(len(id_list))

    label = db_label.get_one_data(id=5,table='Test',column='label')
    print(label[0])
