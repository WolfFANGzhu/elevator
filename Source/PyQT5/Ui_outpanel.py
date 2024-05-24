from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(240, 320)
        self.Up = QtWidgets.QPushButton(Form)
        self.Up.setGeometry(QtCore.QRect(80, 130, 51, 51))
        self.Up.setObjectName("Up")
        self.Down = QtWidgets.QPushButton(Form)
        self.Down.setGeometry(QtCore.QRect(80, 210, 51, 51))
        self.Down.setObjectName("Down")
        self.E2 = QtWidgets.QLCDNumber(Form)
        self.E2.setGeometry(QtCore.QRect(140, 20, 51, 51))
        self.E2.setDigitCount(1)
        self.E2.setObjectName("E2")
        self.E1 = QtWidgets.QLCDNumber(Form)
        self.E1.setGeometry(QtCore.QRect(40, 20, 51, 51))
        self.E1.setDigitCount(1)
        self.E1.setObjectName("E1")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.Up.setText(_translate("Form", "Up"))
        self.Down.setText(_translate("Form", "Down"))

