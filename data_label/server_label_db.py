#coding: utf-8
from webapp import db
from data_label.client_db import client_db


db.metadata.clear()
#根据客户要求创建标注用的表
class LabelData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, index=True)
    #根据客户提供的要求创建对应的标签列
    leval= db.Column(db.Integer)                #好评/中评/差评
    cost_perform = db.Column(db.Integer)
    appearance = db.Column(db.Integer)
    applicability = db.Column(db.Integer)

    laber = db.Column(db.String(16), index=True)                #标注者
    is_labled = db.Column(db.Integer, index=True, default=0)    #已经标注过:1

    def get_unlabeled(self):                                     #取一条未标注过的记录
        record = self.query.filter(self.is_labled == 0).first()
        return record

#初始化标注用的表LabelData， 将客户数据表中的id 依次写入LabelData的source_id
def init_LabelData():
    LabelData_sourceid = LabelData.query.filter(LabelData.source_id >= 0).all()
    client_db_id = client_db.get_column('id')                                #客户数据库id列表
    source_id_list = [item.source_id for item in LabelData_sourceid]         #数据标注工作表中的source_id列表
    for source_id in source_id_list:
        client_db_id.remove(source_id)                                       #获取还未插入到工作表中的source_id
    for source_id in client_db_id:
        # print(source_id)
        source_id = LabelData(source_id=source_id, is_labled=0)
        db.session.add(source_id)
    db.session.commit()

#根据表单写数据库
def update_LabelData(record,form, current_user):
    '''

    :param record: LabelData中，要更新的那条纪录
    :param form:表单
    :param current_user: 当前登录的user
    :return:
    '''
    record.leval = form.leval.data
    record.cost_perform = form.cost_perform.data
    record.appearance = form.appearance.data
    record.applicability = form.applicability.data
    record.laber = current_user.username
    record.is_labled = 1
    db.session.commit()

#根据数据库中的记录回填表单
def write_form(record, form):
    form.leval.data = record.leval
    form.cost_perform.data = record.cost_perform
    form.appearance.data = record.appearance
    form.applicability.data = record.applicability





if __name__ == '__main__':
    #删除Lble_Data中的数据
    # idlist = LabelData.query.filter(LabelData.id >= 0).all()
    # for id in idlist:
    #     db.session.delete(id)
    # db.session.commit()

    init_LabelData()
    print(LabelData.get_unlabeled(LabelData))