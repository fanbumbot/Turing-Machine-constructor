from controller import ControlledTuringMachine
from turingMachine.ruleTable import RuleTable

class SavingTuringMachine:
    def __init__(self, machine: ControlledTuringMachine):
        self.machine:ControlledTuringMachine = machine
        
    def WriteRulesString(self, ruleTable:RuleTable) -> str:
        i = 0
        string = ""
        for row in ruleTable:
            string += f"rules({i}) = "
            for rule in row:
                string += "[" + rule.newSymbol + ", " + rule.newState + ", " + str(rule.Direction.value) + "] | "
            string = string[:-3] + "\n"
            i += 1
        return string

    def WriteString(self, tape, tapeOffset, initState, stopStates, symbols, states, ruleTable:RuleTable) -> str:
        string = \
            "#Лента\ntape = " + \
            str(tape) + \
            "\ntapeOffset = " + \
            str(tapeOffset) + \
            "\n#Начальное состояние\ninitState = " + \
            str(initState) + \
            "\n#Конечные состояния\nstopStates = " + \
            str(stopStates) + \
            "\n#Алфавит\nsymbols = " + \
            str(symbols) + \
            "\n#Состояния\nstates = " + \
            str(states) + \
            "\n#Правила\n" + \
            self.WriteRulesString(ruleTable)
        return string

    def Save(self, fileName: str):
        string = self.WriteString(self.machine.turingMachine.tapeHead.tapeList,
                                  self.machine.turingMachine.tapeHead.Offset,
                                  self.machine.turingMachine.InitState,
                                  self.machine.turingMachine.StopStates,
                                  self.machine.controllerRules.table.columnHeaders,
                                  self.machine.controllerRules.table.rowHeaders,
                                  self.machine.controllerRules.ruleTable)
        with open(fileName, "w", encoding="utf-8") as file:
            file.write(string)