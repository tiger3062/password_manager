import re
import string
import sys

import qtmodern.styles
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QHeaderView
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from password_generator import PasswordGenerator
from password_strength import PasswordStats
import pykeepass
from pykeepass import PyKeePass

from stacked_test import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        self.model = QtGui.QStandardItemModel()
        self.main_win.setWindowIcon(QtGui.QIcon("D:\School\password_manager\keepass-icon-11.png"))
        self.main_win.setWindowTitle("Password Manager")


        #Buttons config
        self.ui.openBtn.clicked.connect(self.filedia)
        self.ui.createBtn.clicked.connect(self.tocreatedb)

        self.ui.genBtn.clicked.connect(self.generate)
        self.ui.horizontalSlider_2.valueChanged.connect(self.genpass_2)
        self.ui.entrypassInput_2.textChanged.connect(lambda: self.passwordstrenth(self.ui.entrypassInput_2, self.ui.passstatLab_2))
        self.ui.genbackBtn.clicked.connect(self.back)
        self.ui.copy.clicked.connect(self.copypass)

        self.ui.unlockBtn.clicked.connect(self.unlockdb)
        self.ui.createpageBtn.clicked.connect(self.createdb)
        self.ui.createpbackBtn.clicked.connect(self.back)
        self.ui.unpagebackBtn.clicked.connect(self.back)
        self.ui.deleteBtn.clicked.connect(self.deleteentry)
        self.ui.lockdbBtn.clicked.connect(self.lockdb)
        self.ui.addBtn.clicked.connect(self.addentry)
        self.ui.horizontalSlider.valueChanged.connect(self.genpass)
        self.ui.entrypassInput.textChanged.connect(lambda: self.passwordstrenth(self.ui.entrypassInput, self.ui.passstatLab))
        self.ui.okBtn.clicked.connect(self.saveentry)
        self.ui.canceBtn.clicked.connect(self.cancel)


        #Database table config
        header = self.ui.tableWidget.horizontalHeader()
        header.ResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def cancel(self):
        self.ui.entrytitleInput.clear()
        self.ui.entryuserInput.clear()
        self.ui.entrypassInput.clear()
        self.ui.horizontalSlider.setValue(0)
        self.ui.spinBox.setValue(0)
        self.ui.stackedWidget.setCurrentWidget(self.ui.dbdata)

    def show(self):
        self.main_win.show()

    def lockdb(self):
        l.save()
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)

    def back(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        self.ui.entrypassInput_2.clear()


    def tocreatedb(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.create)

    def generate(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.generate)

    def addentry(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.genpassPage)

    def copypass(self):
        if self.ui.entrypassInput_2.text() != '':
            clipboard = QtGui.QGuiApplication.clipboard()
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText(self.ui.entrypassInput_2.text(), mode=clipboard.Clipboard)

    def filedia(self):
        global flocal
        fname = QFileDialog.getOpenFileNames(self, "Open file", ".", "Keepass 2 Database (*kdbx)")
        flocal = str(re.sub(r"[\[\]\']", '', str(fname[0])))
        if flocal != '':
            print(flocal)
            self.ui.flocalLab.setText(flocal)
            self.ui.stackedWidget.setCurrentWidget(self.ui.unlock)
        return flocal

    def dbtable(self, x):
        n = int(len(x.entries))
        self.ui.tableWidget.setRowCount(n)
        print(x.groups)
        for g in range(0, n):
            entry = str(x.entries[g]).split(' ')
            self.ui.tableWidget.setItem(g, 0,
                                        QtWidgets.QTableWidgetItem(str(re.sub(r"[\"\)\(]", '', str(entry[1])))))
            self.ui.tableWidget.setItem(g, 1,
                                        QtWidgets.QTableWidgetItem(str(re.sub(r"[\"\)\(]", '', str(entry[2])))))
            t = str(re.sub(r"[\"\)\(]", '', str(entry[1])))
            y = x.find_entries(title=t, first=True)
            o = y.password
            self.ui.tableWidget.setItem(g, 2, QtWidgets.QTableWidgetItem(o))
        self.ui.stackedWidget.setCurrentWidget(self.ui.dbdata)

    def deleteentry(self):
        currentRow = self.ui.tableWidget.currentRow()
        selected = self.ui.tableWidget.selectionModel().currentIndex().isValid()
        if selected:
            selectedEntry = self.ui.tableWidget.item(currentRow, 0).text()
            print(currentRow)
            print(selectedEntry)
            y = l.find_entries(title=selectedEntry, first=True)
            print(y)
            l.delete_entry(y)
            l.save()
            self.ui.tableWidget.removeRow(currentRow)


    def unlockdb(self):
        global l, edb
        dbpw = str(self.ui.lineEdit.text())
        try:
            edb = PyKeePass(f"{flocal}", password=dbpw) #edb = existed database
        except Exception:
            self.ui.infounpLab.setText("Wrong password.")
        else:
            l = edb
            self.dbtable(edb)
            self.ui.lineEdit.clear()


    def createdb(self): #c stands for create
        global l, cdb
        cdbname = str(self.ui.inputnameField.text())
        cdbpw = str(self.ui.inputpwField.text())
        confirmpw = str(self.ui.confirmpwField.text())
        if cdbname != '':
            if cdbpw != '':
                if confirmpw != '':
                    if cdbpw == confirmpw and cdbname != "" and cdbpw != '':
                        #cdb = created database
                        dum = './'
                        fname = ''.join([dum, f"{cdbname}.kdbx"])
                        cdb = pykeepass.create_database(fname, password=f'{confirmpw}', keyfile=None, transformed_key=None)
                        print(fname)
                        l = cdb
                        self.dbtable(cdb)
                        self.ui.inputnameField.clear()
                        self.ui.inputpwField.clear()
                        self.ui.confirmpwField.clear()
                    else:
                        self.ui.infocreatepLab.setText("Wrong password.")
                else:
                    self.ui.infocreatepLab.setText("Please fill all the fields.")
            else:
                self.ui.infocreatepLab.setText("Please fill all the fields.")
        else:
            self.ui.infocreatepLab.setText("Please fill all the fields.")

    def excludeuchars(self, x, y):
        if y.isChecked():
            x.minuchars = 0
        else:
            x.minuchars = 0
            x.excludeuchars = string.ascii_uppercase

    def excludelchars(self, x, y):
        if y.isChecked():
            x.minlchars = 0
        else:
            x.minlchars = 0
            x.excludelchars = string.ascii_lowercase

    def excludenumchars(self, x, y):
        if y.isChecked():
            x.minnumbers = 0
        else:
            x.minnumbers = 0
            x.excludenumbers = string.digits

    def excludeschars(self, x, y):
        if y.isChecked():
            x.minschars = 0
        else:
            x.minschars = 0
            x.excludeschars = [
            "!",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "(",
            ")",
            ",",
            ".",
            "-",
            "_",
            "+",
            "=",
            "<",
            ">",
            "?",
        ]

    def genpass(self):
        global pwo
        self.ui.warningLab.setText("")
        if self.ui.uppercaseBox.isChecked() or self.ui.lowercaseBox.isChecked() or self.ui.numberBox.isChecked() \
                or self.ui.specialBox.isChecked():
            p = self.ui.horizontalSlider.value()
            pwo = PasswordGenerator()
            pwo.minlen = p
            pwo.maxlen = p
            self.excludeuchars(pwo, self.ui.uppercaseBox)
            self.excludelchars(pwo, self.ui.lowercaseBox)
            self.excludeschars(pwo, self.ui.specialBox)
            self.excludenumchars(pwo, self.ui.numberBox)
            password = pwo.generate()
            self.ui.entrypassInput.setText(password)
        else:
            self.ui.warningLab.setText("Please choose at least one option.")

    def genpass_2(self):
        self.ui.warningLab.setText("")
        if self.ui.uppercaseBox_2.isChecked() or self.ui.lowercaseBox_2.isChecked() or self.ui.numberBox_2.isChecked() \
                or self.ui.specialBox_2.isChecked():
            p = self.ui.horizontalSlider_2.value()
            pwo_2 = PasswordGenerator()
            pwo_2.minlen = p
            pwo_2.maxlen = p
            self.excludeuchars(pwo_2, self.ui.uppercaseBox_2)
            self.excludelchars(pwo_2, self.ui.lowercaseBox_2)
            self.excludeschars(pwo_2, self.ui.specialBox_2)
            self.excludenumchars(pwo_2, self.ui.numberBox_2)
            password = pwo_2.generate()
            self.ui.entrypassInput_2.setText(password)
        else:
            self.ui.warningLab_2.setText("Please choose at least one option.")


    def passwordstrenth(self, x, y):
        pas = x.text()
        if pas != '':
            stat = int(PasswordStats(pas).strength() * 100)
            print(stat)
            if 61 <= stat <= 85:
                y.setText("Password quality: Good")
            elif 25 <= stat <= 49:
                y.setText("Password quality: Weak")
            elif 0 <= stat <= 24:
                y.setText("Password quality: Poor")
            else:
                y.setText("Password quality: Excellent")

    def saveentry(self):
        etitle = self.ui.entrytitleInput.text()
        euser = self.ui.entryuserInput.text()
        epass = self.ui.entrypassInput.text()
        if etitle != '' or euser != '' or epass != '':
            print(etitle)
            print(euser)
            print(epass)
            print(l.entries)
            l.add_entry(l.root_group, etitle, euser, epass)
            print(l.entries)
            l.save()
            self.dbtable(l)
            self.ui.entryuserInput.clear()
            self.ui.entrytitleInput.clear()
            self.ui.entrypassInput.clear()

        else:
            self.ui.notiLab.setText("Please fill all the information.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    qtmodern.styles.dark(app)

    main_win.show()
    sys.exit(app.exec_())
