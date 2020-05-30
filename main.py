import ctypes
import inspect
import os.path
import threading
import traceback
from random import randint

import openpyxl
import pandas as pd
from PyQt5.QtWidgets import *
from openpyxl.utils.dataframe import dataframe_to_rows
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import UI
import os
import re
import sys
import time
from model import mainUrl, getCategoryId, xlsHeader


# chrome driver version 83.0.4103.39
# pyinstaller -w -F main.spec main.py
# pyuic5 -x UI.ui -o UI.py

def filterArray(arr: list):
    if len(arr) > 0:
        newArr = list(set(arr))
        newArr = map(str.strip, newArr)
        newArr = list(filter(lambda x: x != '', newArr))
        return newArr
    else:
        return []


def _async_raise(tid, exctype):
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Thread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stoped(self):
        return self._stop_event.is_set()

    def _get_my_tid(self):
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        if hasattr(self, "_thread_id"):
            return self._thread_id

        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        self.raise_exc(SystemExit)


class MyWindowApp(QMainWindow, UI.Ui_dialog):
    browser = ''
    browserUrl = ''
    targetCategory = ""
    targetCategoryId = ""
    productIdList = []
    productList = []
    outputFileName = ''
    th = ''

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.onClickButton)
        self.comboBox.currentIndexChanged.connect(self.onChangeSelect)

    def log(self, logStr: str):
        self.logForm.append(logStr)
        self.logForm.ensureCursorVisible()

    def onChangeSelect(self, index):
        combo = self.sender()
        if index > 0:
            self.targetCategory = combo.currentText()
            self.targetCategoryId = str(getCategoryId(combo.currentText()))
        else:
            self.targetCategory = ""
            self.targetCategoryId = ""

    def threadStop(self):
        if self.th != '':
            self.th.stop()
            if not self.th.stoped():
                self.th.terminate()
                self.th.join()

            self.th = ''
            self.browserClose()
            self.outputFileName = ''

    def statusChange(self, status: str):
        if status == 'start':
            self.pushButton.setText('중단')
            th = threading.Thread(target=self.statusChange, args=('process',))
            th.setDaemon(True)
            th.start()
        elif status == 'process':
            self.pushButton.setEnabled(False)
            time.sleep(5)
            self.pushButton.setEnabled(True)
        else:
            self.threadStop()
            self.pushButton.setText('시작')
            th = threading.Thread(target=self.statusChange, args=('process',))
            th.setDaemon(True)
            th.start()
            th.join()

    def onClickButton(self):
        # self.productForm.setPlainText('LBPD10016372')
        self.productIdList = []
        self.productList = []
        productInputValue = self.productForm.toPlainText()
        if self.pushButton.text() == '시작':
            self.th = ''
            self.statusChange('start')
            if self.targetCategory:
                self.th = Thread(name=None, target=self.searchByCategory, args=())
            elif productInputValue:
                self.th = Thread(name=None, target=self.searchByProduct, args=(productInputValue,))
            else:
                QMessageBox.about(self, "경고", "카테고리 또는 상품번호를 입력해주세요")
                self.statusChange('end')

            if self.th:
                self.th.setDaemon(True)
                self.th.start()
        else:
            self.statusChange('end')

    def exportExcel(self, rows: list):
        try:
            data = pd.DataFrame(rows, columns=xlsHeader)
            if os.path.isfile(self.outputFileName):
                wb = openpyxl.load_workbook(self.outputFileName)
                sheet = wb.active
                header = False
            else:
                wb = openpyxl.Workbook()
                sheet = wb.active
                header = True

            for r in dataframe_to_rows(data, index=False, header=header):
                sheet.append(r)

            wb.save(self.outputFileName)
        except IOError as e:
            self.log(e)

    def browserConnect(self, url: str):
        if self.browser == '':
            options = Options()
            # options.headless = True
            options.add_argument('window-size=1920x1080')
            options.add_argument('disable-gpu')
            options.add_argument(
                'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, '
                'like Gecko) Chrome/61.0.3163.100 Safari/537.36')
            options.add_argument('lang=ko_KR')
            options.add_argument('--disable-browser-side-navigation')

            if getattr(sys, 'frozen', False):
                driverPath = os.path.join(sys._MEIPASS, "chromedriver.exe")
                browser = webdriver.Chrome(driverPath, options=options)
            else:
                browser = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

            self.browser = browser
            self.browserUrl = url

            self.browser.implicitly_wait(3)
            self.browser.get(url)

        return self.browser

    def browserClose(self):
        if self.browser != '':
            self.browser.quit()
        self.browserUrl = ''
        self.browser = ''

    def searchByProduct(self, productInputValue: str):
        productIdList = productInputValue.split(',')
        self.productIdList = filterArray(productIdList)
        self.searchDetailProductList()

    def searchByCategory(self):
        categoryId = self.targetCategoryId
        url = mainUrl + '/search/render/render.ecn?render=nqapi&platform=pc&collection_id=401&u9=navigate&u8={' \
                        '0}&login=Y&mallId=7 '
        url = url.format(categoryId)
        self.browserConnect(url)

        if self.browser:
            self.log('상품 번호 수집 중...')
            # infinite scroll
            # SCROLL_PAUSE_TIME = 0.75
            # last_height = self.browser.execute_script("return document.body.scrollHeight")
            # while True:
            #     if self.browser:
            #         self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #         time.sleep(SCROLL_PAUSE_TIME)
            #
            #         new_height = self.browser.execute_script("return document.body.scrollHeight")
            #         if new_height == last_height:
            #             break
            #         last_height = new_height

            # pagination
            PAUSE_TIME = 1
            while True:
                if self.browser:
                    time.sleep(PAUSE_TIME)
                    html = self.browser.page_source
                    regex = re.compile("href\=[\"\'].*\/p\/product\/([a-zA-Z0-9]*)\?.*[\"\']")
                    productIdList = regex.findall(html)
                    self.productIdList = self.productIdList + filterArray(productIdList)
                    try:
                        nextBtn = self.browser.find_element_by_css_selector(".srchPaginationNext")
                        nextBtn.click()
                    except NoSuchElementException:
                        break
                else:
                    self.statusChange('end')

            if self.browser:
                self.searchDetailProductList()

    def searchDetailProductList(self):
        self.outputFileName = str(time.time_ns()) + '.xlsx'

        total = len(self.productIdList)
        self.log('수집 할 상품 개수: 총 ' + str(total) + '건')

        if not self.browser:
            self.browserConnect(mainUrl)

        for index, productId in enumerate(self.productIdList):
            if self.browser:
                self.searchDetailProduct(productId)
                self.log('[' + productId + '] ' + str(index + 1) + '/' + str(total))

        self.log("수집 완료")
        self.browserClose()
        self.outputFileName = ''
        self.statusChange('end')

    def searchDetailProduct(self, productId: str):
        try:
            if self.browser:
                time.sleep(randint(1, 3))
                url = mainUrl + '/p/product/' + productId
                self.browser.implicitly_wait(3)
                self.browser.get(url)
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

                try:
                    errorPage = self.browser.find_element_by_css_selector(".commonErrorWrap")
                    if errorPage:
                        raise RuntimeError
                except NoSuchElementException:
                    # START
                    # 상품번호
                    productNo = productId

                    # 상품명
                    productName = ''
                    if self.browser:
                        try:
                            productName = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".productName h1"))).text
                        except TimeoutException:
                            # print(traceback.format_exc())
                            pass

                    # 가격
                    productPrice = ''
                    if self.browser:
                        try:
                            productPrice = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.price span"))).text
                        except TimeoutException:
                            # print(traceback.format_exc())
                            pass

                    # 메인 이미지
                    mainImageSrc = ''
                    if self.browser:
                        try:
                            mainImageSrc = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".imgWrap img"))).get_attribute("src")
                        except TimeoutException:
                            # print(traceback.format_exc())
                            pass

                    # 추가 이미지
                    thumbs = []
                    if self.browser:
                        try:
                            thumbsElement = wait.until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, ".productVisualThumbs"))).get_attribute("innerHTML")
                            regex = re.compile("\<img[^>]*src\=[^\"\']*[\"\']([^\"\']*)[\"\'][^>]*\>")
                            thumbs = regex.findall(thumbsElement)
                        except TimeoutException:
                            # print(traceback.format_exc())
                            pass

                    # 상품 설명
                    productDescription = ''
                    if self.browser:
                        try:
                            src = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "#m2-prd-frame"))).get_attribute('src')

                            if src:
                                self.browser.implicitly_wait(3)
                                self.browser.get(src)
                                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                                productDescription = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#m2root"))).get_attribute(
                                    'innerHTML')
                                print(productDescription)
                        except TimeoutException:
                            # print(traceback.format_exc())
                            pass

                    # 상품 수집 끝
                    product = {}
                    for v in xlsHeader:
                        product[v] = ''

                    product = {
                        '판매자상품코드': productNo,
                        '제품명': productName,
                        '판매가': productPrice,
                        '기본이미지': mainImageSrc,
                        '상세설명': productDescription,
                        '추가이미지': ",".join([thumb.replace('67x67', '555x555') for thumb in thumbs]),
                        '상태(S2고정)': 'S2',
                        '재고(100고정)': '200',
                        '무게(0.5g고정)': '0.3',
                        '국내/해외(2고정)': '2',
                        '신제품(1고정)': '1',
                        '제조국': 'KOREA',
                        '성인제품(N고정)': 'N',
                        '발송일(3고정)': '4',

                        '옵션': '',
                        'keyword': '',
                        '3차카테고리': '',
                    }

                    self.exportExcel([product])
                    self.productList.append(product)
                    # END

        except BaseException as e:
            self.log('[' + productId + '] 오류 발생')
            print(traceback.format_exc())
            time.sleep(randint(1, 3))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindowApp()
    myWindow.show()
    app.exec_()
