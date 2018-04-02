'''Get song urls by singers' name.
    Using Multi-Thread. '''
__author__ = 'GhostAnderson'

import bs4
import os
import requests
import base64
import binascii
from Crypto.Cipher import AES
import json
import threading
import queue

header = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en,zh;q=0.8,zh-CN;q=0.6,en-US;q=0.4',
    'Connection':'keep-alive',
    'Content-Type':'application/x-www-form-urlencoded',
    'Origin':'https://music.163.com',
    'Referer':'https://music.163.com/song',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

def createSecretKey(size):  
    return binascii.hexlify(os.urandom(size))[:16]  

def aesEncrypt(text, secKey):  
    pad = 16 - len(text) % 16  
    text = text + chr(pad) * pad  
    encryptor = AES.new(secKey, 2, '0102030405060708')  
    ciphertext = encryptor.encrypt(text)  
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')  
    return ciphertext  

def rsaEncrypt(text, pubKey, modulus):  
    text = text[::-1]  
    rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))  
    return format(rs, 'x').zfill(256)  

def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return data

class NetEaseAPI:

    @staticmethod
    def getMusicURL(id):

        Song_Info = {"ids": "[{}]".format(id),
                    "br": "999000",
                    "csrf_token": ''}

        returnText = requests.post("http://music.163.com/weapi/song/enhance/player/url?csrf_token=",data = encrypted_request(Song_Info),headers = header)
        return json.loads(returnText.content)['data'][0]['url']
    
    @staticmethod
    def search(s, stype=1, offset=0, total='true', limit=100):  
    #搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*
        
        action = 'http://music.163.com/api/search/get/web'
        data = {  
            's': s,  
            'type': stype,  
            'offset': offset,  
            'total': total,  
            'limit': limit  
        }
        searchResult = requests.post(action,data = data,headers = header).text
        with open('res.txt','w') as f:
            f.write(searchResult)
        searchResult = json.loads(searchResult)['result']['songs']
        songList = []


        for song in searchResult:

            songList.append((song['name'],song['id'],song['artists'][0]['name']))

        
        return songList


class downloader(threading.Thread):
    
    def init(self,songList = []):

        self.songList = songList

    def run(self):

        for song in self.songList:

            print('Now Downloading {} ...'.format(song[0]))
            mp3file = requests.get(NetEaseAPI.getMusicURL(song[1]))

            with open('Music\\{}.mp3'.format(song[0]),'wb') as f:

                f.write(mp3file.content)

def main():

    name = '周杰伦'
    counter = 0
    temp = []
    for i in NetEaseAPI.search(name,stype = 1):

        temp.append(i)
        counter+=1

        if(counter == 10):
            
            tempd = downloader()
            tempd.init(temp)
            tempd.start()
            temp = []
            counter = 0

def downloadSpecifiedMusic(SingerName,SongName):

    songList = NetEaseAPI.search(SongName)
    for i in songList:
        if i[2] == SingerName:
            
            mp3file = requests.get(NetEaseAPI.getMusicURL(i[1]))
            with open('SourceMusic\\{}-{}.mp3'.format(SongName,SingerName),'wb')as f:

                f.write(mp3file.content)
            
            break



if __name__ == '__main__':
    main()