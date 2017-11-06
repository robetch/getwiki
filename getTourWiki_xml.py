# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 12:42:14 2017

@author: wanglei
"""
#import chardet
import urllib
from urllib import request
import re,os
import xml.dom.minidom as dom
import xlrd

try: 
  import xml.etree.cElementTree as ET 
except ImportError: 
  import xml.etree.ElementTree as ET


#这部分目录的变量需要修改
path = "E:\\study\\python\\html\\tour\\"
urlfile = r'TourCities-201710_ja.xls'
####中日韩各国启示行号 如英文的为：0 日文的为：2  韩文的为：1
offset=1




ENCODE = r'utf-8'
interURL={
0:r'https://en.wikipedia.org/wiki/',
1:r'https://ko.wikipedia.org/wiki/',
2:r'https://ja.wikipedia.org/wiki/'
}

urlhead = interURL[offset]

print(urlhead)
ridlist = ['Gallery','See also','Notes','References','External links']

def goRun():
    file = path + urlfile
    count = 0
    #urlists = geturllist(file,count,offset)
    counpath = ""
    #while urlists[2] != "":
    while True:
        urlists = geturllist(file,count,offset)
        if urlists == None:
            break;
        if urlists[2] == "":
            continue
        
        tmppath = urlists[1].strip()
        citypath = urlists[2].strip()
        if tmppath != "":
            counpath = tmppath
        ulist = urlists[3:]
        writefile(counpath,citypath,ulist)
        count += 4

def getTourMain(url):
    #book = createXml()
    print(url)
    if url.strip() == "" :
        return None
    doc = dom.Document()

    #开始做网页的页面抓取
    html = getTourInfo(url)

    if html != "" :
    ##获得页面的数据标题信息
        findhtml = re.findall(r'<div class="toctitle">([\s\S]*?)(</div>)([\s\S]*?)(\2)',html)
        if not findhtml:
            ###如果页面数据比较少的情况
            doc.appendChild(getNoTocCont(html))

        else:
            ###如果页面数据比较多的情况
            roothtml = ET.fromstring(findhtml[0][2])
            node = getTocCont(roothtml,html)
            doc.appendChild(node)

    else:
        print("Con't find url:" + url)

    return doc

def getNoTocCont(html):
    root = dom.Document().createElement("root")
    findhtml = re.findall(r'<h[\d].*?id="([\S]+)".*?>(.+?)<',html)
    for node in findhtml:
        if node[0][:1] == "p" or re.sub(r'</?\w+[^>]*>',"",node[1]) in ridlist:
            continue
        else:
            locHref = node[0]
            nodeName = node[0]
            #print(locHref)
            firstnode = createNode(locHref,html,nodeName)
        root.appendChild(firstnode)
    
    return root

def getTocCont(tochtml,html):
    root = dom.Document().createElement("root")
    #nodeDict={'name':'ijfaie','text':'parei'}
    #node = appendNode(nodeDict)
    #doc.appendChild(root)

    tocdoc = tochtml
    for node in tocdoc.findall("./li"):
        if node[0][1].text in ridlist:
            continue
        #nodeName = node[0][1].text
        #locHref = node[0].attrib["href"][1:]
        #h2node = createNode(locHref,html,nodeName)
        h2node = createNode(node[0].attrib["href"][1:],html,node[0][1].text)
        for subh3 in node.findall("./ul/li"):
            if subh3[0][1].text in ridlist:
                continue
            #nodeName = subh3[0][1].text
            #locHref = subh3[0].attrib["href"][1:]
            #h3node = createNode(locHref,html,nodeName)
            h3node = createNode(subh3[0].attrib["href"][1:],html,subh3[0][1].text)
            h2node.appendChild(h3node)
            for subh4 in subh3.findall("./ul/li"):
                if subh4[0][1].text in ridlist:
                    continue
                h4node = createNode(subh4[0].attrib["href"][1:],html,subh4[0][1].text)
                h3node.appendChild(h4node)
                for subh5 in subh4.findall("./ul/li"):
                    if subh5[0][1].text in ridlist:
                        continue
                    h5node = createNode(subh5[0].attrib["href"][1:],html,subh5[0][1].text)
                    h4node.appendChild(h5node)
                
        root.appendChild(h2node)

    return root

def createNode(locId,html,nodeName):
    curId = locId.replace(" ","_")
    #strtmp = r'<(h[\d])>.*?id="' + curId + r'".*?</\1>(.*?)<h[\d]>'
    strtmp = r'<(h[\d]).*?id="'+curId+r'".*?</\1>([\s\S]*?)<h[\d]>'
    
    #patternSee = re.compile(strtmp,re.M|re.I|re.S)
    patternSee = re.compile(strtmp,re.M|re.I)
    ptnDelTag = re.compile(r'</?\w+[^>]*>')

    nodeDict={'name':nodeName}
    findhtml = patternSee.findall(html)    

    resTour = ""
    if findhtml != None:
        resTour = findhtml[0][1]
        #print(resTour)
        resTour = ptnDelTag.sub("",resTour)
        #print(resTour)
        resTour = re.sub(r'\t+',"",resTour)
        resTour = re.sub("\\n+","\\n",resTour)
        #print(resTour)
        nodeDict['text'] = resTour

    return appendNode(nodeDict)

def appendNode(nodeDict):
    doc = dom.Document()
    node = doc.createElement(nodeDict['name'])
    #if nodeDict.has_key('attrname'):
    if 'attrname' in nodeDict.keys():
        node.setAttribute(nodeDict['attrname'],nodeDict['attrvalue'])
    if 'text' in nodeDict.keys():
        node.appendChild(doc.createTextNode(nodeDict['text']))

    return node


def getPicList(url):
    picList = []
    html = getTourInfo(url)
    findimg = re.findall(r'<img.*?src="(.*?)".*?srcset="(.*?)".*?/',html,re.S|re.I|re.M)
    #print(findimg)
    for imgs in findimg:
        if imgs[0][-3:].lower() in ["jpg","jpeg"]:
            if len(imgs) > 1:
                img = imgs[1]
                img = img.split(",")[-1]
                img = img.strip().split(' ')[0]
                #print(img)
            else :
                img = imgs[0]
            if not re.match(r'^http:.*',img,re.I):
                img = "https:" + img
            picList.append(img)

    return picList

def downloadfile(piclist,path):
    for url in piclist:
        filename = path + "\\" + request.unquote(url.split("/")[-1])
        #print(filename)
        try:
            request.urlretrieve(url,filename)
        except:
            print("download picture is ERROR!")
            return False
    return True

def getTourInfo(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'# 将user_agent写入头信息
    headers = {'User-Agent' : user_agent, 'connection': 'keep-alive'}
    htmlcode = ""
    try:
        req = request.Request(url,data=None,headers=headers)
        #print("test")
        resp = request.urlopen(req)
        htmlcode = resp.read().decode(ENCODE)
        
        '''
        charset = chardet.detect(resp)['encoding']
        print(charset)
        if charset==None:
            print("charset is None")
            charset='utf-8'
        
        htmlcode = str(resp.read().decode(charset,'ignore'))[2:-1]
        '''
    except urllib.error.URLError as e:
        print("URLINFO err:" + str(e.reason))
        return ""
        
    return htmlcode

def geturllist(file,rows,offset):
    #打开文件
    try:
        workbook = xlrd.open_workbook(file)
        #根据sheet索引或者名称获取sheet内容
        sheet = workbook.sheet_by_name("中日韩")
        '''
        # 获取单元格内容
        print sheet.cell(1,0).value.encode('utf-8')
        print sheet.cell_value(1,0).encode('utf-8') 
        print sheet.row(1)[0].value.encode('utf-8')
        # 获取单元格内容的数据类型
        print sheet.cell(1,0).ctype
        # sheet的名称，行数，列数
        nname = sheet.name
        nrows = sheet.nrows #行数
        ncols = sheet.ncols #列数
        print(nrows,ncols)
        '''
        urllist = sheet.row_values(rows+offset)
        urllist[1] = sheet.cell(rows+1,1).value.strip()
        urllist[2] = sheet.cell(rows+1,2).value.strip()
        
        #对后续的网页进行格式转化和url的bytes转换
        for i in range(len(urllist)):
            urllist[i] = str(urllist[i]).strip().replace(" ","_")
            if i > 2 and urllist[i] != "":
                urllist[i] = urlhead + request.quote(urllist[i])

    except:
        return None
    return urllist
    
def writefile(countrypath,citypath,urllist):
    ulist = urllist
    curpath = path + "data\\" + countrypath + "\\" + citypath + "\\"
    if any(ulist):
        for url in ulist:
            if url.strip() == "":
                continue
            #将页面中的文本进行抓取
            xmlfile = url.split("/")[-1]+".xml"
            #xmlfile = url.split("/")[-1]+".txt"
            filename = curpath + request.unquote(xmlfile)
            doc = getTourMain(url)
            if doc != None:
                if not os.path.exists(curpath):
                    #print(curpath)
                    os.makedirs(curpath)

                with open(filename,'w+',encoding=ENCODE) as fp:
                    #存成xml文件
                    doc.writexml(fp, addindent="\t", newl="\n", encoding=ENCODE)
                    
                    #存成txt文件
                    '''
                    rstext = ""
                    for node in doc.childNodes:
                        for node1 in node.childNodes:
                            #print(node1.nodeName)
                            rstext += node1.nodeName + ":"
                            for node2 in node1.childNodes:
                                if node2.nodeType == 1:
                                    #print(node2.nodeName)
                                    rstext += node2.nodeName + ":"
                                    for node3 in node2.childNodes:
                                        #print(node3.data)
                                        rstext += node3.data
                                elif node2.nodeType == 3:
                                    #print(node2.data)
                                    rstext += node2.data
                    fp.write(rstext)
                    '''

            else:
                print(filename + ": can't catch DATA so don't create!")
            
            #开始对页面的图片进行下载
            '''
            piclist = getPicList(url)
            if piclist:
                picpath = curpath + request.unquote(url.split("/")[-1])
                if not os.path.exists(picpath):
                    os.makedirs(picpath)
                downloadfile(piclist,picpath)
            '''

#这个脚本可以临时跑少量网页的数据
def gotest():
    counpath = "China"
    citypath = "Beijing"
    #name = r'Cloisonné'
    #url = 'https://en.wikipedia.org/wiki/' + name
    #print(urllib.request.quote(url))
    #ulist = ['https://en.wikipedia.org/wiki/Beijing']
    ulist = [
    'https://ja.wikipedia.org/wiki/%E6%96%B0%E5%A4%A9%E5%9C%B0',
    'https://ja.wikipedia.org/wiki/%E7%B4%AB%E7%A6%81%E5%9F%8E',
    'https://ja.wikipedia.org/wiki/%E4%BA%BA%E6%B0%91%E5%A4%A7%E4%BC%9A%E5%A0%82'
    ]
    
    writefile(counpath,citypath,ulist)
    

if __name__ == "__main__" :
    #url = r'https://en.wikivoyage.org/wiki/Beijing'
    #url = r'https://en.wikivoyage.org/wiki/Tokyo'
    #url = r'https://en.wikipedia.org/wiki/Badaling'
    #url = r'https://en.wikipedia.org/wiki/Amerikamura'
    #getTourMain(url)
    #file = path + urlfile
    #geturllist(file,0)
    #gotest()
    goRun()

