#coding: utf-8
from webapp import db
from data_label.populate_label_data import db_label
from data_label.train_data import NaiveBayes
import numpy as np
import hashlib
from webapp import celery


#根据表单写数据库
def update_LabelData(record,form):
    '''

    :param record: LabelData中，要更新的那条纪录
    :param form:表单
    :return:
    '''
    record.leval = form.leval.data
    record.is_labled = 1
    db.session.commit()

#根据数据库中的记录回填表单
def write_form(label, form):
    form.level.data = label


#刚开始手动标注标注，然后用手动标注的去预测未标注的
#通过celery在后台进行
@celery.task
def predict_labels(table):
    '''

    :return: 成功返回None
    '''
    table_name = table
    #获取训练数据
    train_data = db_label.get_trian_data(table=table_name)
    #训练样本
    train_docts = train_data[2]
    if len(train_docts) < 1000:
        return "Training Data is Not Enough!"
    #待预测数据
    predict_data = db_label.get_all_unlabeled(table=table_name)
    if not predict_data:
        return "No Data is unlabeled!"
    #训练标签
    label = np.array(train_data[1])
    #待预测数据的id
    predict_ids = predict_data[0]
    #待预测文本
    predict_docts = predict_data[2]
    #预测标签结果
    predict_labels = NaiveBayes(train_docts, label, predict_docts)
    #将预测结果写入数据库
    data = zip(predict_labels,predict_ids)
    data = list(data)
    result = db_label.update_label_many(table=table_name,data=data)
    # return result



#将列表按索引分为奇数部分和偶数部分
def split_list(target_list, lenth):
    odd_list = []       #奇数部分
    even_list = []      #偶数部分
    for i in range(lenth):
        if i % 2 == 0:
            even_list.append(target_list[i])
        if i % 2 == 1:
            odd_list.append(target_list[i])
    return (odd_list, even_list)



#训练样本,获取预测值与实际值不符的文本id
#通过celery在后台运行
@celery.task
def train_datas(flag, table):
    '''
    :param flag: 默认取索引为奇数的数据作为训练样本
    :return: 返回预测与实际不符的数据的id
    '''
    table_name = table
    #获取所有数据
    data = db_label.get_trian_data(table=table_name)
    if not data:
        return "No Data to Train!"
    ids = data[0]                #所有id
    labels = data[1]             #所有标签
    docts = data[2]              #所有文本
    counts = len(labels)          #总数据量
    split_docts = split_list(docts,counts)
    split_labels = split_list(labels, counts)
    split_ids = split_list(ids, counts)

    left_docts = split_docts[0]  #前半部分文本
    left_labels = split_labels[0]  #前半部分标签
    right_docts = split_docts[1]
    right_labels = split_labels[1]
    left_ids = split_ids[0]
    right_ids = split_ids[1]
    if flag:                            #训练样本为前半部分
        train_docts = left_docts
        label = left_labels
        predict_docts = right_docts
        real_labels = right_labels
        predict_ids = right_ids
    else:
        train_docts = right_docts
        label = right_labels
        predict_docts = left_docts
        real_labels = left_labels
        predict_ids = left_ids
    train_label = np.array(label)
    predict_labels = NaiveBayes(train_docts, train_label, predict_docts)
    # dif_id = []                    #预测标签与实际标签不符的id
    # for i in range(len(predict_labels)):
    #     if real_labels[i] != predict_labels[i]:
    #         dif_id.append(predict_ids[i])
    # return dif_id
    #将训练结果保存在predict_label列
    predict_labels = [int(i) for i in predict_labels]
    predict_data = list(zip(predict_labels,predict_ids))
    db_label.update_many_predict_label(table=table_name, data=predict_data)


# #多线程训练数据
# def train_datas(flag=1):
#     Thread(target=train, args=(flag,)).start()






if __name__ == '__main__':
    # db_label.db.execute('drop table if exists Test;')
    # Test = '''
    # CREATE TABLE Test
    # (
    #   id            int             NOT NULL auto_increment primary key,
    #   label         int             NULL,
    #   review        varchar(16000)  NOT NULL,
    #   data_md5      varchar(128)    NOT NULL unique,
    #   is_labeled    int             default 0,
    #   predict_label int             NULL,
    #   label_user    char(64)        NULL
    # )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
    #
    # if db_label.create_table(Test) >= 0:          #创建数据表成功
    #     print('table is exists')
    # label = [0,2,1,3,1,1,0,2]
    # id = [1,2,3,4,5,6,7,8]
    # data = zip(label,id)
    # data = list(data)
    # db_label.update_label_many(table='Test',data=data)

    # dif_id = db_label.get_diff_predict(username='huawenjin', table='Evaluations')
    # print(dif_id)
    task = predict_labels.delay(table="Evaluations")
    print(task.status)