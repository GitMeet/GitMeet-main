class Rep:
    converter = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    def __init__(self, rep, datetimes):
        print "datetimes", datetimes
        self.rep = rep
        print "is there a rep increase?", self.rep
        #self.dates = ["{} {}".format(self.converter[a], b) for a, b, c in datetimes] if datetimes else []
        self.dates = [[a, b] for a, b, c in datetimes]
        self.rep_increase = sorted([c for a, b, c in datetimes]) if datetimes else []
        print "self.dates", self.dates
        print "self.rep_increase", self.rep_increase
    def __bool__(self):
        return self.rep > 0

    @property
    def length(self):
        return len(self.dates)

    def __repr__(self):
        return "{}(total:{}, increase:{})".format(self.__class__.__name__, self.rep, self.rep_increase)
