class ColonyParams():
    def __init__(self):
        self.COOP_COLOR = [0.0, 0.0, 0.8]
        self.DEFECT_COLOR = [0.8, 0.0, 0.0]
        self.threshold = 3
        self.payoff = [1.0, 0.0, 0.0, 7/3.0]
        self.stubbornness = 0.0
        self.silence = 0.0
        self.weight_func = None
        self.next_gen_type = None
        self.beta = 1000
        self.preset = "All Cooperators"

    def __str__(self):
        return "\nThreshold: " + str(self.threshold) +\
                "\nPayoff: " + str(self.payoff) +\
                "\nStubbornness: " + str(self.stubbornness) +\
                "\nSilence: " + str(self.silence) +\
                "\nWeight function: " + str(self.weight_func) +\
                "\nNext Gen Type: " + str(self.next_gen_type) +\
                "\nBeta: " + str(self.beta)