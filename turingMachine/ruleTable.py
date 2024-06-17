from .rule import Rule

class RuleTable(object):
    def __init__(self):
        self.table = {}

    def Set(self, symbol: str, state: str, rule: Rule) -> None:
        if not (state in self.table):
            self.table.update({state: {}})
        self.table[state].update({symbol: rule})

    def Get(self, symbol: str, state: str) -> Rule:
        try:
            return self.table[state][symbol]
        except:
            return None

    def Remove(self, symbol: str, state: str) -> bool:
        try:
            del self.table[state][symbol]
        except:
            return False
        return True

    def RemoveState(self, state: str) -> bool:
        try:
            del self.table[state]
        except:
            return False
        return True

    def RemoveSymbol(self, symbol: str) -> bool:
        for state in self.table:
            try:
                del self.table[state][symbol]
            except:
                return False
        return True

    def Clear(self) -> None:
        self.table = {}
