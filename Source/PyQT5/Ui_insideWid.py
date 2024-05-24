from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QWidget

class Ui_InsideWidget(QWidget):
    def setupUi(self, InsideWidget,eid:int):
        self.eid = eid
        InsideWidget.setObjectName("InsideWidget")
        InsideWidget.resize(222, 289)
        self.Direction = QtWidgets.QGraphicsView(InsideWidget)
        self.Direction.setGeometry(QtCore.QRect(90, 10, 41, 31))
        self.Direction.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Direction.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Direction.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Direction.setObjectName("Direction")
        self.f1 = QtWidgets.QPushButton(InsideWidget)
        self.f1.setGeometry(QtCore.QRect(90, 110, 41, 41))
        self.f1.setObjectName("f1")
        self.f1.clicked.connect(self.on_button_clicked)
        self.open = QtWidgets.QPushButton(InsideWidget)
        self.open.setGeometry(QtCore.QRect(20, 230, 41, 41))
        self.open.setObjectName("open")
        self.f2 = QtWidgets.QPushButton(InsideWidget)
        self.f2.setGeometry(QtCore.QRect(90, 160, 41, 41))
        self.f2.setObjectName("f2")
        self.LCD = QtWidgets.QLCDNumber(InsideWidget)
        self.LCD.setGeometry(QtCore.QRect(90, 40, 41, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LCD.sizePolicy().hasHeightForWidth())
        self.LCD.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.LCD.setFont(font)
        self.LCD.setSmallDecimalPoint(False)
        self.LCD.setDigitCount(1)
        self.LCD.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.LCD.setObjectName("LCD")
        self.f3 = QtWidgets.QPushButton(InsideWidget)
        self.f3.setGeometry(QtCore.QRect(90, 210, 41, 41))
        self.f3.setObjectName("f3")
        self.close = QtWidgets.QPushButton(InsideWidget)
        self.close.setGeometry(QtCore.QRect(160, 230, 41, 41))
        self.close.setAutoDefault(True)
        self.close.setDefault(False)
        self.close.setFlat(False)
        self.close.setObjectName("close")
        self.label = QtWidgets.QLabel(InsideWidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 71, 41))
        self.label.setObjectName("label")

        self.retranslateUi(InsideWidget)
        QtCore.QMetaObject.connectSlotsByName(InsideWidget)

    def retranslateUi(self, InsideWidget):
        _translate = QtCore.QCoreApplication.translate
        InsideWidget.setWindowTitle(_translate("InsideWidget", "Elevator#"+str(self.eid)))
        self.f1.setText(_translate("InsideWidget", "3"))
        self.open.setText(_translate("InsideWidget", "<|>"))
        self.f2.setText(_translate("InsideWidget", "2"))
        self.f3.setText(_translate("InsideWidget", "1"))
        self.close.setText(_translate("InsideWidget", ">|<"))
        self.label.setText(_translate("InsideWidget", "ElevatorId"))
    def on_button_clicked(self):
        # 当按钮被点击时，执行的操作
        print("button is pressed!")

