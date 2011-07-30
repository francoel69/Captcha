# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtCore, QtGui
from os.path import isfile
from untitled import Ui_MainWindow
import captcha

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.nn = captcha.Net()
        QtCore.QObject.connect(self.ui.toolButtonBuscarCarpeta, QtCore.SIGNAL("clicked()"), self.folder_dialog)
        QtCore.QObject.connect(self.ui.toolButtonEntrenar,QtCore.SIGNAL("clicked()"), self.train)
        QtCore.QObject.connect(self.ui.toolButtonBuscarArchivo,QtCore.SIGNAL("clicked()"), self.file_dialog)
        QtCore.QObject.connect(self.ui.toolButtonCargar, QtCore.SIGNAL("clicked()"), self.show_captcha)
        QtCore.QObject.connect(self.ui.toolButtonDescifrar, QtCore.SIGNAL("clicked()"), self.process)
        QtCore.QObject.connect(self.ui.toolButtonModificar, QtCore.SIGNAL("clicked()"), self.modify)
        QtCore.QObject.connect(self.ui.pushButtonSalir, QtCore.SIGNAL("clicked()"), self.salir)

    def folder_dialog(self):
        fd = QtGui.QFileDialog(self)
        self.dir = fd.getExistingDirectory(caption= "Seleccionar carpeta", options=fd.ShowDirsOnly)
        self.ui.lineEditCarpeta.setText(self.dir)

    def train(self):
        folder = str(self.ui.lineEditCarpeta.text())
        #dic = captcha.targetDic(folder)
        files = os.walk(folder).next()[2]
        files = filter(lambda e: e.endswith(('.bmp', '.jpeg', '.jpg', '.png')), files)
        #self.ui.progressBar.setRange(0, len(dic))
        #count = 0
        #for im in files:
            #if dic.has_key(im):
                #self.ui.labelProgress.setText(im)
                #xi = captcha.getInputs(im)
                #for i in range(5):
        hash = folder + "/hash.txt"
        if(isfile(hash)):
            self.nn.train(files, folder)
        else:
            print "No existe el archivo \"hash.txt\""
                #count += 1
                #self.ui.progressBar.setValue(count)

    def file_dialog(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getOpenFileName(caption= "Seleccionar archivo", filter="Images (*.png *.bmp *.jpg)")
        if isfile(self.filename):
            self.ui.lineEditArchivo.setText(self.filename)

    def show_captcha(self):
        scene = QtGui.QGraphicsScene()
        scene.addPixmap(QtGui.QPixmap(self.ui.lineEditArchivo.text()))
        self.ui.graphicsViewCaptcha.setScene(scene)

    def process(self):
        xi = captcha.getInputs(str(self.ui.lineEditArchivo.text()))
        self.ui.lineEdit.setText(self.nn.update(xi[0]))
        self.ui.lineEdit_2.setText(self.nn.update(xi[1]))
        self.ui.lineEdit_3.setText(self.nn.update(xi[2]))
        self.ui.lineEdit_4.setText(self.nn.update(xi[3]))
        self.ui.lineEdit_5.setText(self.nn.update(xi[4]))

    def modify(self):
        l1 = str(self.ui.lineEdit.text())
        l2 = str(self.ui.lineEdit_2.text())
        l3 = str(self.ui.lineEdit_3.text())
        l4 = str(self.ui.lineEdit_4.text())
        l5 = str(self.ui.lineEdit_5.text())
        xi = captcha.getInputs(str(self.ui.lineEditArchivo.text()))
        targets = map(captcha.getTarget, [l1, l2, l3, l4, l5])
        for i in range(5):
            self.nn.update(xi[i])
            self.nn.backPropagate(targets[i])

    def salir(self):
        captcha.updateFile(self.nn.wi, "../pesos.txt")
        captcha.updateFile(self.nn.wo, "../pesos2.txt")
        answer = QtGui.QMessageBox.question(self.parent(), u"¿Salir?", u"¿Está seguro que desea salir?",
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.Yes:
            self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
