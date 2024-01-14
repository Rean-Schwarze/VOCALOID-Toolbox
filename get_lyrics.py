import re

import docx
import requests
from docx.enum.text import WD_ALIGN_PARAGRAPH  # 设置对象居中、对齐等。
from docx.oxml.ns import qn
from pyncm import apis
from pyncm.apis.login import LoginViaAnonymousAccount
from pyqqmusicapi import QQMusic

from common.config import cfg

qqmusic_api = QQMusic()


# 获取QQ音乐搜索结果
async def qqmusic_search(keyword):
    try:
        data = await qqmusic_api.search.query(keyword)
    except Exception as e:
        print(e)
        return False, e
    reslut = []
    # 获取所需要的信息，重新封装为字典，然后加入列表中
    for d in data:
        id = d['info']['id']
        mid = d['info']['mid']
        title = d['info']['title']
        album = d['album']['name']
        singers = d['singer']
        artist = ''
        for i in range(len(singers)):
            artist += singers[i]['name']
            if i != (len(singers) - 1):
                artist += '/'
        song_json = {'id': id, 'mid': mid, 'title': title, 'album': album, 'artist': artist}
        reslut.append(song_json)
    return True, reslut


# 获取QQ音乐平台歌曲的歌词
async def qqmusic_get_lyric(id, mid):
    headers = {
        'authority': 'u.y.qq.com',
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://y.qq.com',
        'referer': 'https://y.qq.com/',
        'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    }
    lyric_url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&musicid={}&format=json".format(id)

    referer = "https://y.qq.com/n/yqq/song/{}.html".format(mid)
    headers['referer'] = referer

    response = requests.get(lyric_url, headers=headers)
    if response.status_code == 200:
        # 将response解析为json
        res_json = response.json()
        lyric_lrc = res_json['lyric']
        # 处理歌词格式
        lyric = process_lyric(lyric_lrc)
        return True, lyric
    else:
        return False, ''


# 处理歌词格式
def process_lyric(lyric):
    # 返回的单词格式有两种
    # lrc歌词时间示例：[00&#58;10&#46;37]→[00:10.371]
    # 使用正则表达式寻找
    re_lyric = re.findall(r'[[0-9]+&#[0-9]+;[0-9]+&#[0-9]+;[0-9]+].*', lyric)
    # 获取的lrc歌词有时间
    if re_lyric:
        lyric = re_lyric[0]
        # 处理字符
        lyric = lyric.replace("&#32;", " ")
        lyric = lyric.replace("&#40;", "(")
        lyric = lyric.replace("&#41;", ")")
        lyric = lyric.replace("&#45;", "-")
        lyric = lyric.replace("&#38;apos&#59;", "'")
        lyric = lyric.replace("&#46;", ".")
        lyric = lyric.replace("&#58;", ":")
        lyric = lyric.replace("&#13;", "")  # Carriage Return，光标回到本行开头
        lyric = lyric.replace("&#10;", "\n")  # Line Feed，光标前往下一行
        return lyric
        #
        # result = []
        # for sentence in re.split(u"[[0-9]+&#[0-9]+;[0-9]+&#[0-9]+;[0-9]+]", lyric):
        #     # 去除首尾的空格/换行符
        #     if sentence.strip() != "":
        #         result.append(sentence)
        # if format != '.lrc':
        #     return "\n".join(result)
        # else:
        #     return "".join(result)
    # 获取的lrc歌词没有时间
    else:
        lyric = lyric.replace("&#32;", " ")
        lyric = lyric.replace("&#40;", "(")
        lyric = lyric.replace("&#41;", ")")
        lyric = lyric.replace("&#45;", "-")
        lyric = lyric.replace("&#13;", "")  # Carriage Return，光标回到本行开头
        lyric = lyric.replace("&#10;", "\n")  # Line Feed，光标前往下一行
        lyric = lyric.replace("&#38;apos&#59;", "'")
        return lyric


# 获取网易云音乐搜索结果
def netease_search(keyword):
    # url = 'https://autumnfish.cn/search'
    # params = {'keywords': keyword}
    url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&type=1&offset=0&total=true'
    params = {'s': keyword, 'limit': 50}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # 将response解析为json
            res_json = response.json()
            data = res_json['result']['songs']
            result = []
            for d in data:
                id = d['id']
                title = d['name']
                artists = d['artists']
                artist = ''
                # 处理为xxx/xxx/...的格式
                for i in range(len(artists)):
                    artist += artists[i]['name']
                    if i != (len(artists) - 1):
                        artist += '/'
                album = d['album']['name']
                duration = d['duration']
                song_json = {'id': str(id), 'title': title, 'artist': artist, 'album': album, 'duration': duration}
                result.append(song_json)
            return True, result
        else:
            return False, ''
    except Exception:
        return False, ''


# 获取网易云音乐平台歌曲的歌词
def netease_get_lyric(id):
    LoginViaAnonymousAccount()
    data = apis.track.GetTrackLyrics(id)
    lyric_lrc = data['lrc']['lyric']  # 无需处理，直接使用
    return True, lyric_lrc


# 将lrc格式的歌词中所有时间去掉
def convert_lrc_to_others(lyric_lrc):
    lyric = []
    for sentence in re.split(u"[[0-9]+:[0-9]+.[0-9]+]", lyric_lrc):
        lyric.append(sentence)
    return True, "".join(lyric)


# 保存歌词到文件中
def save_to_file(lyric, title, bpm, C, b, key, format, artist=''):
    note = b
    if note == '♮':
        note = ''
    if format == '.lrc':
        path = cfg.get(cfg.dataFolder) + '/' + artist + ' - ' + title + format
    else:
        path = cfg.get(cfg.dataFolder) + '/' + title + '_' + bpm + '_' + C + note + ' ' + key + format
    if format != '.docx':
        with open(path, 'w') as f:
            f.write(lyric)
    else:
        doc = docx.Document()
        doc.styles['Normal'].font.name = '等线'  # 设置字体
        doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), u'等线')
        paragraph = doc.add_paragraph(lyric)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER  # 居中对齐
        doc.save(path)
