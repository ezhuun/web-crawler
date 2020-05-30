# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from model import title, category

class Ui_dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(470, 350)
        Dialog.setMinimumSize(QtCore.QSize(470, 350))
        Dialog.setMaximumSize(QtCore.QSize(470, 350))
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(20, 220, 61, 16))
        self.label_4.setObjectName("label_4")
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 50, 431, 101))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBox.setObjectName("comboBox")

        for i in range(0, len(category) + 1):
            self.comboBox.addItem("")

        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.productForm = QtWidgets.QTextEdit(self.formLayoutWidget)
        self.productForm.setMaximumSize(QtCore.QSize(16777215, 50))
        self.productForm.setObjectName("productForm")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.productForm)
        self.label_5 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_5)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(20, 160, 429, 31))
        self.pushButton.setObjectName("pushButton")
        self.logForm = QtWidgets.QTextEdit(Dialog)
        self.logForm.setGeometry(QtCore.QRect(20, 240, 431, 91))
        self.logForm.setMaximumSize(QtCore.QSize(16777215, 100))
        self.logForm.setReadOnly(True)
        self.logForm.setObjectName("logForm")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 431, 21))
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(0, 200, 470, 16))
        self.line.setMinimumSize(QtCore.QSize(470, 0))
        self.line.setMaximumSize(QtCore.QSize(470, 16777215))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", title + " 크롤링 프로그램"))
        self.label_4.setText(_translate("Dialog", "작업 내역 "))
        self.label_2.setText(_translate("Dialog", "카테고리 "))
        self.comboBox.setItemText(0, _translate("Dialog", "선택하기"))

        for index, categoryName in enumerate(category):
            self.comboBox.setItemText(index + 1, _translate("dialog", categoryName))

        self.label_3.setText(_translate("Dialog", "상품번호 "))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p><span style=\" color:#999999;\">※ 카테고리 선택시 상품번호 무시. 구분자: 콤마(,)</span></p></body></html>"))
        self.pushButton.setText(_translate("Dialog", "시작"))
        self.logForm.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Gulim\'; font-size:9pt; font-weight:400; font-style:normal;\" bgcolor=\"#ededed\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">"+ title +"</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
