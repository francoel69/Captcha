# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtCore, QtGui

from untitled import Ui_MainWindow
import captcha

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.toolButtonBuscarCarpeta, QtCore.SIGNAL("clicked()"), self.folder_dialog)
        QtCore.QObject.connect(self.ui.toolButtonEntrenar,QtCore.SIGNAL("clicked()"), self.train)
        QtCore.QObject.connect(self.ui.toolButtonBuscarArchivo,QtCore.SIGNAL("clicked()"), self.file_dialog)
        QtCore.QObject.connect(self.ui.toolButtonCargar, QtCore.SIGNAL("clicked()"), self.captcha_in)
        QtCore.QObject.connect(self.ui.toolButtonDescifrar, QtCore.SIGNAL("clicked()"), self.process)
        QtCore.QObject.connect(self.ui.toolButtonModificar, QtCore.SIGNAL("clicked()"), self.modify)
        QtCore.QObject.connect(self.ui.pushButtonSalir, QtCore.SIGNAL("clicked()"), self.salir)

    def folder_dialog(self):
        fd = QtGui.QFileDialog(self)
        self.dir = fd.getExistingDirectory(caption= "Seleccionar carpeta", options=fd.ShowDirsOnly)
        self.ui.lineEditCarpeta.setText(self.dir)

    def train(self):
        folder = str(self.ui.lineEditCarpeta.text())
        dic = captcha.output_correcto(folder)
        files = os.walk(folder).next()[2]
        files = filter(lambda e: e.endswith(('.bmp', '.jpeg', '.jpg', '.png')), files)
        self.ui.progressBar.setRange(0, len(dic))
        count = 0
        for im in files:
            if dic.has_key(im):
                self.ui.labelProgress.setText(im)
                captcha.modify(folder + "/" + im, dic.get(im))
                count += 1
                self.ui.progressBar.setValue(count)

    def file_dialog(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getOpenFileName(caption= "Seleccionar archivo", filter="Images (*.png *.bmp *.jpg)")
        from os.path import isfile
        if isfile(self.filename):
            self.ui.lineEditArchivo.setText(self.filename)

    def captcha_in(self):
        scene = QtGui.QGraphicsScene()
        scene.addPixmap(QtGui.QPixmap(self.ui.lineEditArchivo.text()))
        self.ui.graphicsViewCaptcha.setScene(scene)

    def process(self):
        res = captcha.process(str(self.ui.lineEditArchivo.text()))
        self.ui.lineEdit.setText(res[0])
        self.ui.lineEdit_2.setText(res[1])
        self.ui.lineEdit_3.setText(res[2])
        self.ui.lineEdit_4.setText(res[3])
        self.ui.lineEdit_5.setText(res[4])

    def modify(self):
        l1 = str(self.ui.lineEdit.text())
        l2 = str(self.ui.lineEdit_2.text())
        l3 = str(self.ui.lineEdit_3.text())
        l4 = str(self.ui.lineEdit_4.text())
        l5 = str(self.ui.lineEdit_5.text())
        captcha.modify(str(self.ui.lineEditArchivo.text()), [l1,l2,l3,l4,l5])

    def salir(self):
        answer = QtGui.QMessageBox.question(self.parent(), u"¿Salir?", u"¿Está seguro que desea salir?",
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.Yes:
            self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
