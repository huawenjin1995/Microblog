#coding: utf-8
import json, random, os
import hashlib
import requests
from flask_babel import _
from webapp import app


#利用百度翻译API提供文本翻译
def translate(text, source_language, dest_language):
    if 'BD_TRANSLATOR_KEY' not in app.config or not app.config['BD_TRANSLATOR_KEY']:
        return _('Error: the translation server is not configured.')
    url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    appid = '20200321000402156'
    salt = random.randint(32768, 65536)     #生成一个随机数
    sign = appid + text +str(salt) + app.config['BD_TRANSLATOR_KEY']
    m = hashlib.new('md5')
    m.update(sign.encode(encoding='utf-8'))
    msign = m.hexdigest()                   #得到原始签名的MD5值

    data= {
        'q': text,
        'from':source_language or 'auto',
        'to':dest_language,
        'appid':appid,
        'salt':salt,
        'sign':msign
    }
    r = requests.get(url, params=data)
    if r.status_code != 200:
        return _('Error: the translation server failed.')
    # print(json.loads(r.content.decode('utf-8')))
    return json.loads(r.content.decode('utf-8'))['trans_result'][0]['dst']


if __name__ == '__main__':
    result = translate('我命由我不由天','', 'spa')
    print(result)
    print(type(result))