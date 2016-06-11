# -*- Coding:UTF-8 -*-


import re
import os
import requests
from pyquery import PyQuery as pq
from selenium import webdriver

from ConfigParser import ConfigParser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class taobaommscrapy():

    def __init__(self):

        conf = ConfigParser()
        conf.read('conf.ini')
        self.url = 'http://mm.taobao.com/json/request_top_list.htm?page='
        self.login_data = dict(conf.items('account'))
        self.headers = dict(conf.items('header'))
        self.ses = requests.session()

    def getPage(self,ipage):
        try:
            res = self.ses.get(url = self.url+str(ipage), headers = self.headers)
            return res.text.decode('utf-8')
        except requests.exceptions.RequestException:
            print 'open '+self.url+' error'

    def getContent(self,html):

        doc = pq(html)
        ladyname = []
        ladywebpage = []
        for data in doc('a.lady-name'):
            ladyname.append(pq(data).text())
            ladywebpage.append(pq(data).attr('href'))
        #return ladyname
        return ladyname,ladywebpage

    #get url from js with phantomjs and solumn

    def getPersonallink(self,url):

        local_url = 'http:' + url
        driver = webdriver.PhantomJS(executable_path='/usr/bin/phantomjs')
        driver.get(local_url)
        doc = pq(driver.page_source.decode('utf-8'))
        return doc('div.mm-p-domain-info li').find('span').eq(0).text()


    def getPersonalPage(self,url):
        try:
            local_url = 'http:'+url
            res = self.ses.get(url = local_url,headers = self.headers)
            return res.text.decode('utf-8')
        except requests.exceptions.RequestException:
            print 'open PersonalPage error: '+local_url

    def getAllimgurl(self,html):
        doc = pq(html)
        imgurl = []
        for data in doc('img'):
            string = pq(data).attr('src')
            if not string:
                continue
            havehttps = re.search(r'http',string)
            if not havehttps:
                imgurl.append(pq(data).attr('src'))

        return imgurl

    def saveImg(self,imgurl,fileName):
        try:
            res = self.ses.get(url = imgurl)
            data = res.content
            with open(fileName,'wb') as f:
                f.write(data)
        except requests.exceptions.RequestException:
            print 'open image url error'



    #
    def mkdir(self, path):
        path = path.strip()
        #
        isExists = os.path.exists(path)
        if not isExists:
            #
            os.makedirs(path)
            return True
        else:
            print path+'dir exists'
            return False

    def scrapyOnePage(self,ipage):

        html = self.getPage(ipage)
        lady = self.getContent(html)
        ladyname = lady[0]
        ladyurl = lady[1]

        for i in range(len(ladyname)):
            self.mkdir(ladyname[i])

            personlink = self.getPersonallink(ladyurl[i])


            html = self.getPersonalPage(personlink)
            allImagUrl = self.getAllimgurl(html)

            k = 0
            for item in allImagUrl:
                imgurl = 'http:'+item.strip()

                k += 1
                fileName = ladyname[i] + "/" + str(k) + '.jpg'
                IsfileExists = os.path.exists(fileName)
                if IsfileExists:
                    print 'The'+str(k)+' picture for '+ ladyname[i]+' already exists'
                else:
                    print 'The'+str(k)+' picture for '+ ladyname[i]+' is saving'
                    self.saveImg(imgurl,fileName)


MM = taobaommscrapy()
MM.scrapyOnePage(2)

#lady = MM.getContent()
#print lady[0][:]

#html = MM.getPersonalPage(MM.getPersonallink(lady[1][0]))

#allImgUrl = MM.getAllimgurl(html)

#imgurl = 'http:'+allImgUrl[1]
#print imgurl
#fileName = '1.jpg'
#MM.saveImg(imgurl, fileName)

#print len(allImgUrl)
#for item in MM.getAllimgurl(html):
#    print item
