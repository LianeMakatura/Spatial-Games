# Written by Liane Makatura
# Winter 2017, CS76: Evolutionary Game Dynamics
# Final Project

from PyQt5.QtWidgets import *
from canvas import *
from colony import *
from math import *
from weighting_functions import *
from colonyParams import *

DURATION = 5000

debug = False

# create the colony
settings = ColonyParams()
hive = Colony(20, 20, 20, settings)

hive.cell(10, 10).defect()
hive.cell(11, 11).defect()
hive.cell(12, 9).defect()
hive.cell(12, 10).defect()
hive.cell(12, 11).defect()

#reset the default functions
hive.settings.next_gen_type = "Perfect Best Response"
hive.settings.weight_func = uniform_w

# helper class for horizontal lines
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

# simple gui for math 76 project
class ColonyUI(QWidget):

    def __init__(self, parameters):
        super().__init__()
        self.params = parameters
        control_box = self.initControls()

        self.hive = hive
        self.canvas = set_canvas(draw, mouse_press=click)
        if debug:
            print("canvas assigned: " + str(self.canvas))

        evo_gui = QGridLayout(self)
        evo_gui.addWidget(self.canvas, 0,  0, 15, 10)
        evo_gui.addLayout(control_box, 0, 10, 12, 6)

        self.canvas.c_start_timer()
        self.setFixedSize(1050, 450)
        self.window().setLayout(evo_gui)
        self.setWindowTitle("Evolutionary Dynamics of Spatial Games")

        self.show()


    def initControls(self):
        control_box = QGridLayout()
        row = 0

        # radio buttons to select thresholding, perf best response, or irrational best response
        next_gen_select = QButtonGroup()
        thresh = QRadioButton("Threshold")
        thresh.toggled.connect(lambda: self.genFuncChanged(thresh))
        pbr = QRadioButton("Perfect Best Response")
        pbr.setChecked(True) # default to pbr
        pbr.toggled.connect(lambda: self.genFuncChanged(pbr))
        ibr = QRadioButton("Irrational Best Response")
        ibr.toggled.connect(lambda: self.genFuncChanged(ibr))

        next_gen_select.addButton(thresh)
        next_gen_select.addButton(pbr)
        next_gen_select.addButton(ibr)
        control_box.addWidget(thresh, row, 0, 1, 2)
        control_box.addWidget(pbr, row, 2, 1, 2)
        control_box.addWidget(ibr, row, 4, 1, 2)

        row += 1
        control_box.addWidget(QHLine(), row, 0, 1, 6)
        row += 1

        # threshold
        t_entry = QLineEdit(str(self.params.threshold), self)
        t_entry.textChanged[str].connect(self.tChanged)
        t_entry.setToolTip('Minimum number of defector neighbors needed '
                           'for central pixel to defect in next generation'
                           '\nRange: [0,8]')
        t_entry.setToolTipDuration(DURATION)
        control_box.addWidget(QLabel("Threshold ="), row, 0, 1, 2)
        control_box.addWidget(t_entry, row, 2, 1, 1)

        row += 1
        control_box.addWidget(QHLine(), row, 0, 1, 6)
        row+=1

        a_entry = QLineEdit(str(self.params.payoff[0]), self)
        a_entry.setToolTip('Payoff: cooperator vs. cooperator')
        a_entry.setToolTipDuration(DURATION)
        a_entry.textChanged[str].connect(self.aChanged)

        b_entry = QLineEdit(str(self.params.payoff[1]), self)
        b_entry.setToolTip('Payoff: cooperator vs. defector')
        b_entry.setToolTipDuration(DURATION)
        b_entry.textChanged[str].connect(self.bChanged)

        c_entry = QLineEdit(str(self.params.payoff[2]), self)
        c_entry.setToolTip('Payoff: defector vs. cooperator')
        c_entry.setToolTipDuration(DURATION)
        c_entry.textChanged[str].connect(self.cChanged)

        d_entry = QLineEdit(str(self.params.payoff[3]), self)
        d_entry.setToolTip('Payoff: defector vs. defector')
        d_entry.setToolTipDuration(DURATION)
        d_entry.textChanged[str].connect(self.dChanged)

        control_box.addWidget(QLabel("a ="), row, 1, 1, 1)
        control_box.addWidget(a_entry, row, 2, 1, 1)
        control_box.addWidget(QLabel("b ="), row, 3, 1, 1)
        control_box.addWidget(b_entry, row, 4, 1, 2)
        row+=1

        control_box.addWidget(QLabel("c ="), row, 1, 1, 1)
        control_box.addWidget(c_entry, row, 2, 1, 1)
        control_box.addWidget(QLabel("d ="), row, 3, 1, 1)
        control_box.addWidget(d_entry, row, 4, 1, 1)

        row += 1
        control_box.addWidget(QHLine(), row, 0, 1, 6)
        row+=1

        # stubbornness
        stub = QSlider(Qt.Horizontal, self)
        stub.setFocusPolicy(Qt.NoFocus)
        stub.setMaximum(100)
        stub.setValue(self.params.stubbornness * 100)
        stub.valueChanged[int].connect(self.stubChanged)
        stub.setToolTip('An individual\'s resistance to adopting a new strategy\n'
                        'Range: [0,1]\n'
                        '0 - always switch to the best strategy <--- DEFAULT, same as no stubbornness param\n'
                        '1 - never change your original strategy')
        stub.setToolTipDuration(DURATION)

        control_box.addWidget(QLabel("Stubbornness ="), row, 0, 1, 2)
        control_box.addWidget(stub, row, 2, 1, 1)
        row+=1

        # silence
        sil = QSlider(Qt.Horizontal, self)
        sil.setFocusPolicy(Qt.NoFocus)
        sil.setMaximum(100)
        sil.setValue(self.params.silence * 100)
        sil.valueChanged[int].connect(self.silChanged)
        sil.setToolTip('An individual\'s probability of remaining silent for a given round\n'
                        'Silent cells do not share their opinion, but do absorb/respond to their neighbors\'\n'
                        'Range: [0,1]\n'
                        '0 - never silent, always share opinion <--- DEFAULT, same as no silence param\n'
                        '1 - always silent, never share opinion')
        sil.setToolTipDuration(DURATION)

        control_box.addWidget(QLabel("Silence ="), row, 0, 1, 2)
        control_box.addWidget(sil, row, 2, 1, 1)

        row+=1

        weights = QComboBox()
        functions = ["Uniform", "Inverse Manhattan", "Inverse Euclidean"]
        weights.addItems(functions)
        weights.activated[str].connect(self.weightChanged)
        control_box.addWidget(QLabel("Weighting Function = "), row, 0, 1, 2)
        control_box.addWidget(weights, row, 2, 1, 1)

        row += 1
        control_box.addWidget(QHLine(), row, 0, 1, 6)
        row += 1

        beta = QSlider(Qt.Horizontal, self)
        beta.setFocusPolicy(Qt.NoFocus)
        beta.setMaximum(1000)
        beta.setValue(self.params.beta)
        beta.valueChanged[int].connect(self.betaChanged)
        beta.setToolTip('An individual\'s rationality, higher beta indicates better rationality\n'
                        'Range: [0,1000]\n'
                        '0 - highly irrational'
                        '1000 - very rational <--- DEFAULT, similar to good rationality\n')
        beta.setToolTipDuration(DURATION)

        control_box.addWidget(QLabel("Beta (Rationality) ="), row, 0, 1, 2)
        control_box.addWidget(beta, row, 2, 1, 1)

        row+=1
        control_box.addWidget(QHLine(), row, 0, 1, 6)
        row += 1

        #add combo box
        presets = QComboBox()
        ops = ["All Cooperators", "von Neumann", "3x3 Defectors", "5x5 Defectors"]
        presets.addItems(ops)
        presets.activated[str].connect(self.presetChosen)
        control_box.addWidget(QLabel("Preset Grid Formation: "), row, 0, 1, 2)
        control_box.addWidget(presets, row, 2, 1, 1)

        preset_go = QPushButton('Reset', self)
        preset_go.clicked.connect(reset_grid)
        control_box.addWidget(preset_go, row, 3, 1, 1)

        row += 1

        next_gen = QPushButton('Compute Next Generation', self)
        next_gen.setToolTip('Use the current parameters to compute\n the next generation of the colony')
        next_gen.clicked.connect(next_gen_click)

        control_box.addWidget(next_gen, row, 1, 1, 4)

        return control_box

    def aChanged(self, text):
        val = line_to_float(text)
        if val != float("-inf"):
            self.params.payoff[0] = val
            if debug:
                print(self.params.payoff)

    def bChanged(self, text):
        val = line_to_float(text)
        if val != float("-inf"):
            self.params.payoff[1] = val

    def cChanged(self, text):
        val = line_to_float(text)
        if val != float("-inf"):
            self.params.payoff[2] = val

    def dChanged(self, text):
        val = line_to_float(text)
        if val != float("-inf"):
            self.params.payoff[3] = val

    def tChanged(self, text):
        val = line_to_float(text)
        if val != float("-inf"):
            self.params.threshold = val # should make sure this is positive, <= # neighbors
            if debug:
                print(self.params.threshold)

    def stubChanged(self, value):
        self.params.stubbornness = value / 100.0
        if debug:
            print(self.params.stubbornness)

    def silChanged(self, value):
        self.params.silence = value / 100.0
        if debug:
            print(self.params.silence)

    def weightChanged(self, text):
        if text == "Inverse Manhattan":
            self.params.weight_func = inv_manhattan
        elif text == "Inverse Euclidean":
            self.params.weight_func = inv_euclidean
        else:
            self.params.weight_func = uniform_w
        if debug:
            print(self.params.weight_func)

    def betaChanged(self, value):
        self.params.beta = value
        if debug:
            print(self.params.beta)

    def presetChosen(self, text):
        self.params.preset = text
        if debug:
            print(self.params.preset)

    def genFuncChanged(self, b):       # b is selected button
        if (b.isChecked()):
            self.params.next_gen_type = b.text()
            if debug:
                print(self.params.next_gen_type)

def line_to_float(text):
    frac = str(text).split("/")
    if len(frac) == 1:
        try:
            return float(frac[0])
        except ValueError:
            print("try again")
            return float("-inf")

    elif len(frac) == 2:
        try:
            return float(float(frac[0]) / float(frac[1]))
        except ValueError:
            print("try again")
            return float("-inf")

    return float("-inf")



## Graphics / UI interactions
def next_gen_click():
    if hive.settings.next_gen_type == "Threshold":
        hive.next_generation_threshold()
        if debug:
            print("Updated via Simple Thresholding")
    elif hive.settings.next_gen_type == "Perfect Best Response":
        hive.next_generation_best_response(hive.settings.weight_func)
        if debug:
            print("Updated via Perfect Best Response")
    elif hive.settings.next_gen_type == "Irrational Best Response":
        hive.irrational_best_response(hive.settings.weight_func)
        if debug:
            print("Updated via Irrational Best Response")
    else:
        print("Unrecognized update function. Please select another from the drop down.")
    print(hive.settings)


def click(mx, my):
    col = int(floor(mx / hive.cell_size))
    row = int(floor(my / hive.cell_size))

    if (0 <= col < hive.columns) and (0 <= row < hive.rows):
        hive.cell(row, col).flip()


def reset_grid():
    r = 12
    c = 10
    ["All Cooperators", "von Neumann", "3x3 Defectors", "5x5 Defectors"]
    if hive.settings.preset == "All Cooperators":
        hive.preset_all_blue()
    elif hive.settings.preset == "von Neumann":
        hive.preset_vonNeumann(r, c)
    elif hive.settings.preset == "3x3 Defectors":
        hive.preset_3x3(r, c)
    elif hive.settings.preset == "5x5 Defectors":
        hive.preset_5x5(r, c)
    else:
        pass


def draw():
    hive.draw()

if __name__ == '__main__':
    ex = ColonyUI(settings)
    sys.exit(app.exec_())