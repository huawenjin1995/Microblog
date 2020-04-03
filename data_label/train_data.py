#coding: utf-8
import numpy as np
import jieba
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer, TfidfTransformer
from sklearn import  metrics
from sklearn.naive_bayes import MultinomialNB

# #获取文本矢量
# def get_text_vector(docts):
#     #分词
#     texts = [jieba.cut(text) for text in docts]
#     #转换为列表
#     texts = [list(item) for item in texts]
#     #创建字典，词为key,保证每个key的value不同
#     dictionary = dict()
#     count = 0
#     for word_list in (texts):
#         for word in word_list:
#             if word not in dictionary:
#                 dictionary[word] = count
#                 count += 1
#     total_words = len(dictionary.keys())        #词总数
#     #为语料库中出现的所有单词分配了一个唯一的整数id
#     train_array = []
#     for word_list in (texts):
#         text_array = [0 for i in range(total_words)]
#         for word in word_list:
#             text_array[dictionary[word]] += 1
#         train_array.append(text_array)
#     return np.array(train_array)

#***基于sklearn文本训练
def NaiveBayes(train_docts, label, target_docts):
    """
    朴素贝叶斯进行文本分类
    :return: None
    """
    # 进行特征提取：词频，TFIDF
    count_vect = CountVectorizer()
    tfidf_transformer = TfidfTransformer()
    X_trainCounts = count_vect.fit_transform(train_docts)
    X_testCounts = count_vect.transform(target_docts)
    X_trainTfidf = tfidf_transformer.fit_transform(X_trainCounts)
    X_testTfidf = tfidf_transformer.transform(X_testCounts)
    # 利用训练集训练出一个服从高斯分布的贝叶斯分类器模型
    clf = MultinomialNB().fit(X_trainTfidf, label)
    # 利用sklearn模块中的metrics评估分类器效果
    predicted = clf.predict(X_testTfidf)
    # print(metrics.classification_report([1], predicted))
    # print("accurary\t" + str(np.mean(predicted == newsTest.target)))
    return predicted

# def get_text_vector(docts):
#     # 分词
#     texts = [list(jieba.cut(text)) for text in docts]
#     dictionary = corpora.Dictionary(texts)  # 制作词袋
#     corpus = [dictionary.doc2bow(doc) for doc in texts]
#     return corpus



