
import sys
import time
import re
import json
from urllib.parse import urlparse
from collections import OrderedDict
import requests
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QTabWidget,QPushButton,QTextEdit,QLineEdit,QLabel,QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,QThread,pyqtSignal,Qt
from PyQt5.QtGui import QIcon,QFont,QFontDatabase

# 超时
# 请求详细信息
# 支持多方法
# 支持动态body/query
# TODO 支持Headers
# 编码问题
# 美化、字体
# TODO 增加记录
# TODO 增加侧边栏
# TODO debug 报错
# 成功打包icon和字体
# TODO 增加菜单
# 增加查看快捷键
# url和query联动
# TODO 尾部状态栏
# TODO Request标签页 自动切换

def jsonPretty(jstr):
    return json.dump(json.loads(jstr), indent=2)

class RequestThread(QThread):
    finishSignal = pyqtSignal(dict)

    def __init__(self, window):
        super().__init__()
        self._window = window
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
    def __request(self, options):
        response = requests.request(options['method'], options['url'], headers=options['headers'], data=window.body, params=window.query)
        return response
    def run(self):
        start = time.time()
        url = self._window.reqUrlInput.text()
        text = ''
        try:
            print('Request Sending:', url)
            method = window.reqMethodCombo.currentText()
            print(method)
            response = self.__request({
                'url': url,
                'method': method,
                'headers': self.headers
            })
            charsetPatt = re.compile('charset=["\']{0,1}([A-Za-z0-9\-]+)["\']', re.IGNORECASE)
            matches = charsetPatt.search(str(response.text))
            if matches :
                response.encoding = matches.group(1)
            text = response.text
            print(response.__getattribute__('encoding'))
            print(response.status_code)
            print(response.headers)
            print(response.cookies)
            stats = 'Status: Success \n'
            stats += '{}: {}\n'.format('Code', response.status_code)
            stats += '{}: {:.3f}s\n'.format('ResponseTime', time.time() - start)
            stats += '{}: {}\n'.format('Encoding', response.encoding)
            stats += '{}: {}\n'.format('Headers', json.dumps(dict(response.headers), indent=2))
            print('Request Success:', response.url)
        except Exception as e:
            #print('Request Failed:', e)
            stats = 'Status: Failed \n' + 'Error: ' + str(e)
        print('请求耗时：', time.time() - start)
        sigData = {
            'url': url,
            'text': text,
            'stats': stats
        }
        self.finishSignal.emit(sigData)

def formatParamParse(paramText):
    param = OrderedDict()
    paramLines = str.split(paramText, '\n')
    for line in paramLines:
        items = str.split(line)
        if len(items) == 2:
            param[str(items[0])] = str(items[1])
    return param

def formatParamStringify(param):
    paramFormat = ''
    for k in param:
        paramFormat += '{} {}\n'.format(k, param[k])
    return paramFormat

def paramParse(paramStr):
    paramPats = str.split(paramStr, '&')
    param = OrderedDict()
    for paramPat in paramPats:
        equalIndex = paramPat.find('=')
        if equalIndex > 0:
            param[paramPat[:equalIndex]] = paramPat[equalIndex+1:]
    return param

def urlencodeFromMap(m):
    us = ''
    for k in m:
        us += k + '=' + str(m[k]) + '&'
    return us[:-1]



class Window(QWidget):
    query = {}
    reqStatsObj = {}

    def __init__(self):
        super().__init__()
        self.__render()
        self.show()
        self.reqUrlInput.setFocus()
        self.requestThread = RequestThread(self)

    # 渲染组件
    def __render(self):
        self.setWindowTitle('PyRequest')
        self.__renderSelf()
        self.__renderComponents()
        self.reqUrlInput.textEdited.emit(self.reqUrlInput.text())
        self.queryEdit.textChanged.emit()
        self.bodyEdit.textChanged.emit()

    def __renderSelf(self):
        self.layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon('assets/icon.ico'))
        self.resize(900, 600)

    def __renderComponents(self):
        # input
        self.reqMethodCombo = QComboBox()
        self.reqMethodCombo.addItems(['GET', 'POST'])
        self.reqMethodCombo.currentTextChanged.connect(self.__methodChange)
        self.reqUrlInput = QLineEdit()
        self.reqUrlInput.setText('http://www.duoyi.com')
        self.reqUrlInput.textEdited.connect(self.__urlChanged)
        self.reqButton = QPushButton()
        self.reqButton.setText('SEND')
        self.reqButton.clicked.connect(self.__request)
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.reqMethodCombo)
        inputLayout.addWidget(self.reqUrlInput)
        inputLayout.addWidget(self.reqButton)
        # body&query
        self.queryLabel = QLabel('Query')
        self.queryEdit = QTextEdit()
        # self.queryEdit.grabKeyboard()
        self.queryEdit.textChanged.connect(self.__queryEditChanged)
        self.bodyLabel = QLabel('Body')
        self.bodyEdit = QTextEdit()
        self.bodyEdit.textChanged.connect(self.__bodyEditChanged)
        queryLayout = QVBoxLayout()
        queryLayout.addWidget(self.queryLabel)
        queryLayout.addWidget(self.queryEdit)
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(self.bodyLabel)
        bodyLayout.addWidget(self.bodyEdit)
        self.bodyEdit.hide()
        self.bodyLabel.hide()
        paramLayout = QHBoxLayout()
        paramLayout.addLayout(queryLayout)
        paramLayout.addLayout(bodyLayout)
        self.layout.addLayout(inputLayout)
        self.layout.addLayout(paramLayout)
        # response
        self.resTab = self.__createResTab()
        self.layout.addWidget(self.resTab)

    def __createResTab(self):
        resTab = QTabWidget()
        self.reqStats = QTextEdit()
        self.resStats = QTextEdit()
        self.resText = QTextEdit()
        self.resJSON = QTextEdit()
        self.resView = QWebEngineView()
        resTab.addTab(self.reqStats, 'req')
        resTab.addTab(self.resStats, 'res')
        resTab.addTab(self.resText, 'text')
        resTab.addTab(self.resJSON, 'json')
        resTab.addTab(self.resView, 'view')
        return resTab

    # 处理返回
    def __setRes(self, res):
        self.resTab.setCurrentIndex(1)
        self.resStats.setPlainText(res['stats'])
        self.resText.setPlainText(res['text'])
        try :
            jsonstr = json.dumps(json.loads(res['text']), indent=2, ensure_ascii=False)
            self.resJSON.setPlainText(jsonstr)
        except Exception as e:
            print(e)
            self.resJSON.setPlainText('Not a JSON string')
        self.resView.setHtml(res['text'])

    # 发起请求
    def __request(self):
        self.__clearAll()
        bodyRaw = self.bodyEdit.toPlainText()
        self.body = formatParamParse(bodyRaw)
        self.resView.setHtml('')
        # self.resView.setUrl(QUrl(self.reqUrlInput.text()))
        self.requestThread.finishSignal.connect(self.__setRes)
        self.requestThread.start()

    # 清空返回栏
    def __clearAll(self):
        self.resStats.setText('Requesting...')
        self.resText.setText('Requesting...')
        self.resView.setHtml('Requesting...')
        self.resJSON.setText('Requesting...')

    # 方法切换
    def __methodChange(self, text):
        if text == 'GET':
            self.bodyEdit.hide()
            self.bodyLabel.hide()
        else:
            self.bodyEdit.show()
            self.bodyLabel.show()

    # 快捷键
    def keyPressEvent(self, event):
        print(event.key())
        key = event.key()
        if key in (16777268, 16777220, 16777221):
            self.__request()
        if key >= 49 and key <= 53:
            self.resTab.setCurrentIndex(key - 49)
        if key == 71:
            self.reqMethodCombo.setCurrentText('GET')
        if key == 80:
            self.reqMethodCombo.setCurrentText('POST')
        if key == 87:
            if (self.reqMethodCombo.currentText() == 'GET'):
                self.reqMethodCombo.setCurrentText('POST')
            elif (self.reqMethodCombo.currentText() == 'POST'):
                self.reqMethodCombo.setCurrentText('GET')

    # query/body/reqStats 联动
    def __queryEditChanged(self):
        queryRaw = self.queryEdit.toPlainText()
        self.__querySetFromFormat(queryRaw)

    def __bodyEditChanged(self):
        bodyRaw = self.bodyEdit.toPlainText()
        self.__reqStatsChanged({'body': formatParamParse(bodyRaw)})

    def __urlChanged(self, url):
        self.__querySetFromUrl(url)

    def __querySetFromFormat(self, queryRaw):
        query = formatParamParse(queryRaw)
        self.query = query
        self.__reqStatsChanged({'query': query})
        queryStr = urlencodeFromMap(query)
        if queryStr:
            url = self.reqUrlInput.text()
            urlParts = urlparse(url)
            url = '{}://{}{}?{}'.format(urlParts.scheme, urlParts.netloc, urlParts.path, queryStr)
            self.reqUrlInput.setText(url)
            self.__reqStatsChanged({'url': url})

    def __querySetFromUrl(self, url):
        queryStr = urlparse(url).query
        query = paramParse(queryStr)
        self.__reqStatsChanged({'url': url})
        self.__reqStatsChanged({'query': query})
        queryFormat = formatParamStringify(query)
        self.queryEdit.blockSignals(True)
        self.queryEdit.setPlainText(queryFormat)
        self.queryEdit.blockSignals(False)

    def __reqStatsChanged(self, things):
        for k in things:
            thing = things[k]
            self.reqStatsObj[k] = thing
        reqStatsStr = json.dumps(self.reqStatsObj, indent=2, ensure_ascii=False)
        self.reqStats.setPlainText(reqStatsStr)


def getfont():
    fontId = QFontDatabase.addApplicationFont('assets/MSYHMONO.ttf')
    if fontId != -1:
        fontFamilies = QFontDatabase.applicationFontFamilies(fontId)
        font = QFont()
        font.setFamily(fontFamilies[0])
        font.setPixelSize(12)
        return font

app = QApplication(sys.argv)

font = getfont()
if font:
    app.setFont(font)

window = Window()

sys.exit(app.exec_())