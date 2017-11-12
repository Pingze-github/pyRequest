
import sys
import time
import re
import json
import requests
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QTabWidget,QPushButton,QTextEdit,QLineEdit,QLabel,QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,QThread,pyqtSignal,Qt
from PyQt5.QtGui import QIcon

# 超时
# 请求详细信息
# 支持多方法
# TODO 支持参数
# 编码问题
# TODO 美化、字体
# TODO AUTO模式，自动控制http方法
# TODO 增加记录
# TODO 增加侧边栏

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
        if options['method'] == 'GET':
            response = requests.get(options['url'], headers=options['headers'])
            return response
        elif options['method'] == 'POST':
            response = requests.post(options['url'], headers=options['headers'])
            return response
    def run(self):
        start = time.time()
        url = self._window.reqUrlInput.text()
        text = ''
        try:
            print('Request Sending:', url)
            method = window.reqMethodCombo.currentText()
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
            stats += '{}: {}\n'.format('Encoding', response.encoding)
            stats += '{}: {}\n'.format('Headers', json.dumps(dict(response.headers), indent=2))
            print('Request Success:', response.url)
        except Exception as e:
            print('Request Failed:', e)
            stats = 'Status: Failed \n' + 'Error:\n' + str(e)
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
        self.reqMethodCombo = QComboBox()
        self.reqMethodCombo.addItems(['GET', 'POST'])
        self.reqUrlInput = QLineEdit()
        self.reqUrlInput.setText('http://www.duoyi.com')
        self.reqButton = QPushButton()
        self.reqButton.setText('SEND')
        self.reqButton.clicked.connect(self.__request)
        self.resTab = self.__createResTab()
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.reqMethodCombo)
        inputLayout.addWidget(self.reqUrlInput)
        inputLayout.addWidget(self.reqButton)
        self.layout.addLayout(inputLayout)
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
        self.resJSON.setPlainText(res['text'])

    def __request(self):
        self.__clearAll()
        self.resView.setHtml('')
        self.resView.setUrl(QUrl(self.reqUrlInput.text()))
        self.requestThread.finishSignal.connect(self.__setRes)
        self.requestThread.start()

    def __clearAll(self):
        self.resStats.setText('Requesting...')
        self.resText.setText('Requesting...')
        self.resView.setHtml('Requesting...')
        self.resJSON.setText('Requesting...')

    def keyPressEvent(self, event):
        if event.key() in (16777220, 16777221):
            self.__request()


app = QApplication(sys.argv)
window = Window()

sys.exit(app.exec_())