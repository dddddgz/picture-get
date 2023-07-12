import re
import requests
import time
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from bs4 import BeautifulSoup
from pyperclip import copy
from os import mkdir
from ntpath import isdir

form_class = uic.loadUiType("picture_get.ui")[0]

class PictureGet(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
        }
        self.options = [self.s1, self.s2, self.s3, self.s4]
        self.cur_url = ""
        self.css_selector = ""
        self.flag = False
        self.frame2.setVisible(False)
        self.frame3.setVisible(False)
        self.label3.setVisible(False)
        self.exp.setEnabled(False)
        self.confirm.clicked.connect(self.confirmURL)
        self.css.clicked.connect(self.myExpression)
        self.doac.clicked.connect(self.select)
        self.stop.clicked.connect(self.stopParse)
        self.copyua.clicked.connect(self.copyUserAgent)
        if not isdir("images"):
            mkdir("images")
    
    def confirmURL(self):
        url = self.url.text()
        self.cur_url = url
        if url and re.match(r"^https?://", url):
            self.frame2.setVisible(True)
        else:
            self.label3.setVisible(True)
        if not self.css.isChecked():
            if re.match(r"^https?://(www.)?bilibili.com/read/cv.*$", url):
                self.s1.setChecked(True)
            elif re.match(r"^(https?://(www.)?fishc.com.cn|http://bbs.fishc.(com|org))/(thread-\d+-1-1.html|forum.php\?.*?mod=viewthread.*?&.*?tid=\d+.*?)$", url):
                self.s2.setChecked(True)
            elif re.match(r"^https?://blog.csdn.net/.*?/article/details/.*?$", url):
                self.s3.setChecked(True)
            else:
                self.s4.setChecked(True)
        
    def myExpression(self):
        if self.s4.isChecked():
            self.css.setChecked(True)
            self.exp.setEnabled(True)
            return
        if self.css.isChecked():
            for option in self.options:
                option.setEnabled(False)
            self.exp.setEnabled(True)
        else:
            for option in self.options:
                option.setEnabled(True)
            self.exp.setEnabled(False)
    
    def select(self):
        self.frame3.setVisible(True)
        if self.s1.isChecked():
            self.css_selector = "#read-article-holder"
        elif self.s2.isChecked():
            self.css_selector = ".t_f"
        elif self.s3.isChecked():
            self.css_selector = "#content_views"
        elif self.s4.isChecked():
            self.css_selector = self.exp.text()
        self.getPage()

    def getPage(self):
        response = requests.get(self.url.text(), headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        try:
            part = soup.select_one(self.css_selector)
        except:
            return
        images = part.findAll("img")
        for i, image in enumerate(images):
            if self.flag:
                break
            try:
                url = image["src"]
            except KeyError:
                url = image["data-src"]
            if url.startswith("//"):
                url = "https:" + url
            elif not url.startswith("https://"):
                url = soup.base["href"] + url
            img = requests.get(url, headers=self.headers)
            with open(f"images/{i + 1}.png", "wb") as f:
                f.write(img.content)
            self.label5.setText(f"共{len(images)}个，已下载{i + 1}个")
            self.dpg.setValue(int((i + 1) / len(images) * 100))
            QApplication.processEvents()
            time.sleep(0.5)
        self.stopParse()
    
    def stopParse(self):
        self.flag = True
        self.stop.setText("已停止")
        self.stop.setEnabled(False)
    
    def copyUserAgent(self):
        copy(self.headers["User-Agent"])


app = QApplication([])
window = PictureGet()
window.show()
app.exec()
