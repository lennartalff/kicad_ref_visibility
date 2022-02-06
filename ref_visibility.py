import pcbnew
import re
import datetime
from PyQt5 import QtWidgets, uic, QtCore
import sys
import os
import logging


class Dialog(QtWidgets.QDialog):
    apply = QtCore.pyqtSignal(object, object)

    def __init__(self, parent):
        super(Dialog, self).__init__(parent)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(dir_path, "ref_visibility.ui")
        uic.loadUi(ui_file, self)
        self.ref_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.hide_button.clicked.connect(self.on_hide)
        self.unhide_button.clicked.connect(self.on_unhide)
        apply_button = self.buttonBox.button(self.buttonBox.Apply)
        apply_button.clicked.connect(self.on_ok)
        self.show()

    def add_refs(self, refs, states):
        for ref, state in zip(refs, states):
            item = QtWidgets.QListWidgetItem(ref)
            item.setFlags(QtCore.Qt.ItemIsEnabled
                          | QtCore.Qt.ItemIsSelectable
                          | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(
                QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
            self.ref_list.addItem(item)

    def on_hide(self):
        items = self.ref_list.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Unchecked)

    def on_unhide(self):
        items = self.ref_list.selectedItems()
        for item in items:
            item.setCheckState(QtCore.Qt.Checked)

    def on_ok(self, button):
        logging.info("Apply clicked")
        refs = []
        states = []
        for i in range(self.ref_list.count()):
            item = self.ref_list.item(i)
            refs.append(item.text())
            states.append(bool(item.checkState()))
        self.apply.emit(refs, states)


class HideAllRef(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Ref Visibility"
        self.category = "Modify PCB"
        self.description = "Sets the visibility of modules' refs."

    def on_apply(self, refs, states):
        logging.info("applying visibility.")
        for ref, state in zip(refs, states):
            for footprint in self.pcb.Footprints():
                if ref == footprint.GetReference():
                    logging.info("Set {}={}".format(ref, state))
                    footprint.Reference().SetVisible(state)
                    break
        pcbnew.Refresh()

    def Run(self):
        logging.basicConfig(filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logfile.log"),
                            level=logging.INFO)
        
        logging.info("started")
        app = QtWidgets.QApplication(sys.argv)
        diag = Dialog(None)
        diag.apply.connect(self.on_apply)
        refs = []
        states = []
        self.pcb = pcbnew.GetBoard()
        for footprint in self.pcb.Footprints():
            refs.append(footprint.GetReference())
            states.append(footprint.Reference().IsVisible())
        diag.add_refs(refs, states)
        app.exec_()
        logging.info("finished")


if __name__ == "__main__":

    p = HideAllRef()
    pcb = pcbnew.LoadBoard("/home/lennartalff/ph_esp32.kicad_pcb")
    p.pcb = pcb
    p.Run()