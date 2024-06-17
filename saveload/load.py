from email.policy import default
from controller import ControlledTuringMachine
from turingMachine import *

class LoadingTuringMachine:
    def __init__(self, machine: ControlledTuringMachine):
        self.machine:ControlledTuringMachine = machine
        
    def ReadString(self, string: str):
        rows = string.split("\n")
        rules = list()
        for row in rows:
            row = row.strip()
            if len(row) != 0 and row[0] != "#":
                mark = row.find("=")
                if mark == -1:
                    return None

                key = row[:mark].strip()
                value = row[mark+1:].strip()
                
                match(key):
                    case "tape":
                        tape = [x[1:-1] for x in value.strip("[]").split(", ")]
                    case "tapeOffset":
                        headOffset = int(value)
                    case "initState":
                        initState = value
                    case "stopStates":
                        stopStates = [x[1:-1] for x in value.strip("[]").split(", ")]
                    case "symbols":
                        symbols = [x[1:-1] for x in value.strip("[]").split(", ")]
                    case "states":
                        states = [x[1:-1] for x in value.strip("[]").split(", ")]
                    case _:
                        markStart = key.find("(")
                        markEnd = key.find(")")
                        if markStart != -1 and markEnd != -1 and key[:markStart] == "rules":
                            rules.append([Rule(y[1], y[0], Direction(int(y[2]))) for y in (x.split(", ") for x in value.strip("[]").split("] | ["))])
                        else:
                            return None
            
        return [tape, headOffset, initState, stopStates, symbols, states, rules]
            
    def LoadedDataApply(self, tape, tapeOffset, initState, stopStates, symbols, states, rules):
        
        #Обновление отображения
        self.machine.highlighting.Disable()

        self.machine.turingMachine.tapeHead.tapeList = tape
        self.machine.turingMachine.tapeHead.Offset = tapeOffset
        self.machine.turingMachine.InitState = initState
        self.machine.turingMachine.Head = 0
        self.machine.turingMachine.StopStates = stopStates
        
        self.machine.controllerTape.Update()
        
        self.machine.controllerRules.Clear()
        for symbol in symbols:
            if symbol != self.machine.controllerTape.EmptySymbol:
                self.machine.controllerRules.table.AddColumn(symbol)
        for state in states:
            self.machine.controllerRules.table.AddRow(state)

        rowIter = 0
        for row in rules:
            columnIter = 0
            for rule in row:
                self.machine.controllerRules.ChangeRule(columnIter, rowIter, rule, False)
                columnIter += 1
            rowIter += 1

        self.machine.controllerRules.breakpointRules = list()
        self.machine.controllerRules.breakpointStates = list()
        self.machine.controllerRules.breakpointSymbols = list()
        
        #Обновление отображения
        self.machine.highlighting.UpdateStatesHighlight()

    def Load(self, fileName: str):
        try:
            with open(fileName, "r", encoding="utf-8") as file:
                string = file.read()
        except:
            return False
        data = self.ReadString(string)
        if data == None:
            return False
        self.LoadedDataApply(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        return True
