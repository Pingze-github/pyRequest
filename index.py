
import sys
import time
import re
import json
import requests
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QTabWidget,QPushButton,QTextEdit,QLineEdit,QLabel,QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,QThread,pyqtSignal,Qt
from PyQt5.QtGui import QIcon,QFont,QFontDatabase

# 超时
# 请求详细信息
# 支持多方法
# TODO 支持参数
# 编码问题
# TODO 美化、字体\
# TODO AUTO模式，自动控制http方法
# TODO 增加记录
# TODO 增加侧边栏
# TODO 解决不报错问题

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


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.__render()
        self.show()
        self.requestThread = RequestThread(self)

    def __render(self):
        self.setWindowTitle('PyRequest')
        self.__renderSelf()
        self.__renderComponents()

    def __renderSelf(self):
        self.layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon('./assets/icon.ico'))
        self.resize(900, 600)

    def __renderComponents(self):
        # input
        self.reqMethodCombo = QComboBox()
        self.reqMethodCombo.addItems(['GET', 'POST'])
        self.reqUrlInput = QLineEdit()
        self.reqUrlInput.setText('http://www.duoyi.com')
        self.reqButton = QPushButton()
        self.reqButton.setText('SEND')
        self.reqButton.clicked.connect(self.__request)
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.reqMethodCombo)
        inputLayout.addWidget(self.reqUrlInput)
        inputLayout.addWidget(self.reqButton)
        # body&query
        self.queryEdit = QTextEdit()
        self.bodyEdit = QTextEdit()
        queryLayout = QVBoxLayout()
        queryLayout.addWidget(QLabel('Query'))
        queryLayout.addWidget(self.queryEdit)
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(QLabel('Body'))
        bodyLayout.addWidget(self.bodyEdit)
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
        self.resStats = QTextEdit()
        self.resText = QTextEdit()
        self.resText.setText('init')
        self.resJSON = QTextEdit()
        self.resView = QWebEngineView()
        resTab.addTab(self.resStats, 'stats')
        resTab.addTab(self.resText, 'text')
        resTab.addTab(self.resJSON, 'json')
        resTab.addTab(self.resView, 'view')
        return resTab

    def __setRes(self, res):
        self.resStats.setPlainText(res['stats'])
        self.resText.setPlainText(res['text'])
        try :
            jsonstr = json.dumps(json.loads(res['text']), indent=2, ensure_ascii=False)
            self.resJSON.setPlainText(jsonstr)
        except Exception as e:
            print(e)
            self.resJSON.setPlainText('Not a JSON string')
        self.resView.setHtml(res['text'])

    def __paramParser(self, paramText):
        param = {}
        paramLines = str.split(paramText, '\n')
        for line in paramLines:
            items = str.split(line)
            if len(items) == 2:
                param[str(items[0])] = str(items[1])
        return param

    def __request(self):
        self.__clearAll()
        bodyRaw = self.bodyEdit.toPlainText()
        self.body = self.__paramParser(bodyRaw)
        queryRaw = self.queryEdit.toPlainText()
        self.query = self.__paramParser(queryRaw)
        self.resView.setHtml('')
        # self.resView.setUrl(QUrl(self.reqUrlInput.text()))
        self.requestThread.finishSignal.connect(self.__setRes)
        self.requestThread.start()

    def __clearAll(self):
        self.resStats.setText('Requesting...')
        self.resText.setText('Requesting...')
        self.resView.setHtml('Requesting...')
        self.resJSON.setText('Requesting...')

    def keyPressEvent(self, event):
        print(event.key())
        if event.key() in (16777268, 16777220, 16777221):
            self.__request()


app = QApplication(sys.argv)

fontId = QFontDatabase.addApplicationFont('./assets/MSYHMONO.ttf')
fontFamilies = QFontDatabase.applicationFontFamilies(fontId)
font = QFont()
font.setFamily(fontFamilies[0])
font.setPixelSize(12)
app.setFont(font)

window = Window()

sys.exit(app.exec_())