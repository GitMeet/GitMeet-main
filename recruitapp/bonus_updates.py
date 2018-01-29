import collections

class Bonuses:
    def __init__(self, *args):
        self.__dict__ = dict(zip(['user', 'bonusdb'], args))
        if not [a for a, b, c in self.bonusdb.get_user_latest_awardfor('bonus') if a == self.user]:
            self.full_bonuses = []
        else:
            self.bonus_data = [[b, c] for a, b, c in self.bonusdb.get_user_latest_awardfor('bonus') if a == self.user][0]
            print "self.bonus_data", self.bonus_data
            self.latest = [i for i in self.bonus_data[0] if i[-1]]
            print "self.latest", self.latest
            self.full_bonuses = [[a, c[0]] for [a, b], c in zip(self.latest, self.bonus_data[-1][-len(self.latest):])] if self.latest else []
            print "self.full_bonuses", self.full_bonuses
            self.bonusdb.update('bonus', [('latest', map(lambda (x, y):[x, False], self.bonus_data[0]))], [('user', self.user)])
    @property
    def length(self):
        return len(self.full_bonuses)

    def __len__(self):
        return len(self.full_bonuses)

    def __bool__(self):
        return len(self.full_bonuses) > 0

    def __iter__(self):
        if not self.full_bonuses:
            raise StopIteration('no new bonuses')
        bonus = collections.namedtuple('bonus', ['amount', 'project'])
        for b, project in self.full_bonuses:
            yield bonus(b, project)
