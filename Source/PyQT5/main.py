import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Ui_insideWid import Ui_InsideWidget  # 导入UI文件中生成的类

def main():
    app = QApplication(sys.argv)  # 创建应用程序对象

    # 创建第一个窗口
    window1 = QMainWindow()
    ui1 = Ui_InsideWidget()
    ui1.setupUi(window1,1)
    window1.show()

    # 创建第二个窗口
    window2 = QMainWindow()
    ui2 = Ui_InsideWidget()
    ui2.setupUi(window2,2)
    window2.show()

    sys.exit(app.exec_())  # 进入事件循环

if __name__ == "__main__":
    main()