from kivy.uix.button import Button

from turingMachine import TuringMachine
from controllers.tableRule import TableRuleController
from controllers.tape import TapeController

'''
Подсветка разделяется на 5 типов:

Подсветка текущей позиции на ленте - зелёный цвет (лента)
Подсветка текущего правила - зелёный цвет (таблица)
Подсветка точки останова - красный цвет (таблица)
Подсветка начального правила - зелёный (ячейка с надписью)
Подсветка конечных правил - красный (ячейка с надписью)
'''

class Highlighting:
    def __init__(self, turingMachine:TuringMachine = None,
                 controllerRules:TableRuleController = None,
                 controllerTape:TapeController = None):
        
        self.turingMachine = turingMachine
        self.controllerRules = controllerRules
        self.controllerTape = controllerTape

        self.buttonHighlighted:Button = None
        self.highlightedColumn = 0
        self.highlightedRow = 0
        
        self.controllerRules.callbackAddBreakpointSymbol = self.OnAddBreakpointSymbol
        self.controllerRules.callbackRemoveBreakpointSymbol = self.OnRemoveBreakpointSymbol
        self.controllerRules.callbackAddBreakpointState = self.OnAddBreakpointState
        self.controllerRules.callbackRemoveBreakpointState = self.OnRemoveBreakpointState
        self.controllerRules.callbackAddBreakpointRule = self.OnAddBreakpointRule
        self.controllerRules.callbackRemoveBreakpointRule = self.OnRemoveBreakpointRule
        
    def Update(self):
        self.HighlightCurrentTapeSymbol(True)
        self.HighlightCurrentRule(True)
        
    def Disable(self):
        self.HighlightCurrentTapeSymbol(False)
        self.HighlightCurrentRule(False)        

    #Подсветка текущего символа
    def HighlightCurrentTapeSymbol(self, enable = True):
        if enable:
            self.controllerTape.tapeInputCells[self.controllerTape.WindowSize//2].background_color = [0, 1, 0, 1]
        else:
            self.controllerTape.tapeInputCells[self.controllerTape.WindowSize//2].background_color = [1, 1, 1, 1]
    
    #Подсветка правила
    def HighlightRule(self, column, row, color) -> Button:
        #Установить цвет
        button:Button = self.controllerRules.GetButtonRule(column, row)
        button.background_color = color
        return button

    #Подсветка текущего правила
    def HighlightCurrentRule(self, enable = True) -> bool:
        if self.buttonHighlighted != None:
            #Восстановить цвет
            if not self.controllerRules.IsRuleBreakpointIndexCurrently(self.highlightedColumn, self.highlightedRow):
                #Установить белый цвет
                self.buttonHighlighted.background_color = [1, 1, 1, 1]
            else:
                #Установить красный цвет
                self.buttonHighlighted.background_color = [1, 0, 0, 1]
            self.buttonHighlighted = None

        if enable:
            symbol = self.turingMachine.CurrentSymbol
            state = self.turingMachine.State
            
            column = self.controllerRules.table.GetColumnIndex(symbol)
            row = self.controllerRules.table.GetRowIndex(state)
            
            #Когда не были найдены колонка или строка для символа или состояния 
            if column == -1 or row == -1:
                return False

            self.highlightedColumn = column
            self.highlightedRow = row
            
            if not self.controllerRules.IsRuleBreakpointIndexCurrently(column, row):
                #Установить зелёный цвет
                self.buttonHighlighted = self.HighlightRule(column, row, [0, 1, 0, 1])
            else:
                #Установить жёлтый цвет
                self.buttonHighlighted = self.HighlightRule(column, row, [1, 1, 0, 1])
        return True
    
    def UpdateStatesHighlight(self):
        length = self.controllerRules.table.CountOfRows()
        for i in range(length):
            state = self.controllerRules.table.GetRowName(i)
            button:Button = self.controllerRules.table.GetRow(i)

            isStop = False
            isStart = False
            if state in self.turingMachine.StopStates:
                isStop = True
            if state == self.turingMachine.InitState:
                isStart = True

            if isStop and isStart:
                button.background_color = [0, 0, 1, 1]
            elif isStop:
                button.background_color = [1, 0, 0, 1]
            elif isStart:
                button.background_color = [0, 1, 0, 1]
            else:
                button.background_color = [0.4, 0.4, 0.4, 1]
    
    def OnAddBreakpointSymbol(self, column, symbol):
        for row in range(self.controllerRules.table.CountOfRows()):
            if self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted:
                self.HighlightRule(column, row, [1, 0, 0, 1])
    
    def OnRemoveBreakpointSymbol(self, column, symbol):
        for row in range(self.controllerRules.table.CountOfRows()):
            if (not self.controllerRules.IsRowBreakpoint(row)) and \
            (not self.controllerRules.IsRuleBreakpointIndex(column, row)) and \
            (self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted):
                self.HighlightRule(column, row, [1, 1, 1, 1])
    
    def OnAddBreakpointState(self, row, state):
        for column in range(self.controllerRules.table.CountOfColumns()):
            if self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted:
                self.HighlightRule(column, row, [1, 0, 0, 1])
    
    def OnRemoveBreakpointState(self, row, state):
        for column in range(self.controllerRules.table.CountOfColumns()):
            if (not self.controllerRules.IsColumnBreakpoint(column)) and \
            (not self.controllerRules.IsRuleBreakpointIndex(column, row)) and \
            (self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted):
                self.HighlightRule(column, row, [1, 1, 1, 1])
    
    def OnAddBreakpointRule(self, column, row, symbol, state):
        if self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted:
            self.HighlightRule(column, row, [1, 0, 0, 1])
    
    def OnRemoveBreakpointRule(self, column, row, symbol, state):
        if (not self.controllerRules.IsColumnBreakpoint(column)) and \
        (not self.controllerRules.IsRowBreakpoint(row)) and \
        (self.controllerRules.GetButtonRule(column, row) != self.buttonHighlighted) and \
        (not self.controllerRules.IsRuleBreakpointIndex(column, row)):
            self.HighlightRule(column, row, [1, 1, 1, 1])