from kivy.uix.behaviors import button
from gui.excelLikeTable import ExcelLikeTable
from gui.popup import *

from gui.popup import PopupAddState
from gui.popup import PopupAddSymbol
from gui.popup import PopupChangeRule
from gui.popup import PopupChangeState
from gui.popup import PopupChangeSymbol

from turingMachine.rule import Rule

from kivy.uix.button import Button

from functools import partial

class TableRuleController:
    def __init__(self, table:ExcelLikeTable = None,
                 callbackAddBreakpointSymbol = None,
                 callbackRemoveBreakpointSymbol = None,
                 callbackAddBreakpointState = None,
                 callbackRemoveBreakpointState = None,
                 callbackAddBreakpointRule = None,
                 callbackRemoveBreakpointRule = None,
                 callbackUpdateState = None):

        self.access:bool = True

        self.table:ExcelLikeTable = table       #Таблица
        self.emptySymbol:str = "λ"              #Пустой символ
        
        self.ruleTable = list()                 #Состояние - символ - правило
        self.buttonTable = list()               #Состояние - символ - кнопка
        
        self.stoppedStates = list()             #Конечные состояния
        self.breakpointStates = list()          #Точки останова для состояний
        self.breakpointSymbols = list()         #Точки останова для символов
        self.breakpointRules = list()           #Точки останова для конкретных правил
        self.initState = None                   #Начальное состояние

        #Привязка функций обратного вызова
        table.callbackButtonColumn = self.OnPressedColumn
        table.callbackButtonRow = self.OnPressedRow
        table.defaultCellInit = self.DefaultCell
        table.callbackAddColumn = self.OnAddSymbol
        table.callbackAddRow = self.OnAddState
        table.callbackAddColumnAfter = self.OnAddSymbolAfter
        table.callbackAddRowAfter = self.OnAddStateAfter
        table.callbackRemoveColumn = self.OnRemoveSymbol
        table.callbackRemoveRow = self.OnRemoveState
        
        self.callbackAddBreakpointSymbol = callbackAddBreakpointSymbol
        self.callbackRemoveBreakpointSymbol = callbackRemoveBreakpointSymbol
        self.callbackAddBreakpointState = callbackAddBreakpointState
        self.callbackRemoveBreakpointState = callbackRemoveBreakpointState
        self.callbackAddBreakpointRule = callbackAddBreakpointRule
        self.callbackRemoveBreakpointRule = callbackRemoveBreakpointRule
        
        self.callbackUpdateState = callbackUpdateState

        #Устанавливаем префикс
        table.ColumnPrefix = "Символ\n"
        table.RowPrefix = "Состояние\n"

        #Добавляем колонку с пустым символом
        table.AddColumn(self.emptySymbol)

    @property
    def Access(self) -> bool:
        return self.access 
    
    @Access.setter
    def Access(self, access:bool):
        self.access = access

    #Создание ячейки в таблице
    def DefaultCell(self, columnUID, rowUID):
        column = self.table.GetColumnByUID(columnUID)
        row = self.table.GetRowByUID(rowUID)
        
        button = Button(text = str(column) + " " + str(row), color = [0, 0, 0, 1], background_normal = "", font_size = 22)
        button.background_color = [1, 1, 1, 1]
        button.bind(on_press=partial(self.HandleButtonCell, columnUID, rowUID))

        self.buttonTable[row][column] = button
        self.UpdateRuleButton(columnUID, rowUID)
        return button

    #Создание правила
    def DefaultRule(self, column, row):
        return Rule(self.table.GetRowName(row), self.table.GetColumnName(column), Direction.halt)

    #Получить кнопку правила по колонке и строке
    def GetButtonRule(self, column, row):
        return self.buttonTable[row][column]

    #Получить правило по колонке и строке
    def GetRule(self, column, row):
        return self.ruleTable[row][column]

    #Когда был добавлен новый символ
    def OnAddSymbol(self, column, symbol):
        countRows = self.table.CountOfRows()
        for row in range(countRows):
            state = self.table.GetRowName(row)
            self.ruleTable[row].insert(column, self.DefaultRule(column, row))

            self.buttonTable[row].insert(column, None)
                
    #Когда был добавлен новый символ
    def OnAddSymbolAfter(self, column, symbol):
        countRows = self.table.CountOfRows()
        for row in range(countRows):
            state = self.table.GetRowName(row)
            if self.IsStateBreakpoint(state):
                self.SetBreakpointRow(row)

    #Когда было добавлено новое состояние
    def OnAddState(self, row, state):
        self.ruleTable.insert(row, list())
        self.buttonTable.insert(row, list())
        
        countColumns = self.table.CountOfColumns()
        for column in range(countColumns):
            symbol = self.table.GetColumnName(column)
            self.ruleTable[row].append(self.DefaultRule(column, row))
            
            self.buttonTable[row].append(None)
            
            if self.IsSymbolBreakpoint(symbol):
                self.SetBreakpointColumn(column)
                
    def OnAddStateAfter(self, row, state):
        countColumns = self.table.CountOfColumns()
        for column in range(countColumns):
            symbol = self.table.GetColumnName(column)
            if self.IsSymbolBreakpoint(symbol):
                self.SetBreakpointColumn(column)

    #Когда был удалён символ
    def OnRemoveSymbol(self, column):
        for i in range(len(self.ruleTable)):
            del self.ruleTable[i][column]
            del self.buttonTable[i][column]
        symbol = self.table.GetColumnName(column)
        if self.IsSymbolBreakpoint(symbol):
            self.SetBreakpointColumn(column, False)
        
        tempList = list()
        for rule in self.breakpointRules:
            if rule[0] != symbol:
                tempList.append(rule)
        self.breakpointRules = tempList

    #Когда было удалено состояние
    def OnRemoveState(self, row):
        del self.ruleTable[row]
        del self.buttonTable[row]
        state = self.table.GetRowName(row)
        if self.IsStateBreakpoint(state):
            self.SetBreakpointRow(row, False)
            
        tempList = list()
        for rule in self.breakpointRules:
            if rule[1] != state:
                tempList.append(rule)
        self.breakpointRules = tempList
        
        if state in self.stoppedStates:
            self.stoppedStates.remove(state)

        if state == self.initState:
            self.initState = None

    #Обновить кнопку (внешний вид)
    def UpdateRuleButton(self, columnUID, rowUID, isUID:bool = True):
        if isUID:
            column = self.table.GetColumnByUID(columnUID)
            row = self.table.GetRowByUID(rowUID)
        else:
            column = columnUID
            row = rowUID
        
        rule = self.ruleTable[row][column]

        direction = GetNameDirection(rule.direction)
        self.buttonTable[row][column].text = "Новый символ: " + rule.newSymbol + "\nНовое состояние: " + rule.newState + "\nНаправление: " + direction

    #Перехват с нажатия на кнопку ячейки
    def HandleButtonCell(self, column, row, button):
        self.OnPressedCell(button, column, row)

    #Когда было нажатие на кнопку названия символа
    def OnPressedColumn(self, button, index):
        if not self.Access:
            return
        column = self.table.GetColumnByUID(index)
        symbol = self.table.GetColumnName(column)

        try:
            self.breakpointSymbols.index(symbol)
            isBreakpoint = True
        except:
            isBreakpoint = False

        if symbol != self.emptySymbol:
            PopupChangeSymbol(self, index, symbol, isBreakpoint).open()
        else:   
            self.SetBreakpointColumn(column, not isBreakpoint)

    #Когда было нажатие на кнопку названия состояния
    def OnPressedRow(self, button, index):
        if not self.Access:
            return
        row = self.table.GetRowByUID(index)
        state = self.table.GetRowName(row)
        
        if self.initState != None and self.initState == state:
            isInit = True
        else:
            isInit = False

        try:
            self.stoppedStates.index(state)
            isStopped = True
        except:
            isStopped = False

        try:
            self.breakpointStates.index(state)
            isBreakpoint = True
        except:
            isBreakpoint = False

        PopupChangeState(self, index, state, isBreakpoint, isInit, isStopped).open()

    #Когда было нажатие на кнопку правила
    def OnPressedCell(self, button, columnUID, rowUID):
        if not self.Access:
            return
        column = self.table.GetColumnByUID(columnUID)
        row = self.table.GetRowByUID(rowUID)
        
        symbol = self.table.GetColumnName(column)
        state = self.table.GetRowName(row)

        if [symbol, state] in self.breakpointRules:
            isBreakpoint = True
        else:
            isBreakpoint = False
        
        PopupChangeRule(self, columnUID, rowUID, symbol, state, isBreakpoint).open()

    #Проверка существует ли символ
    def IsSymbolExist(self, symbol):
        return self.table.GetColumnIndex(symbol) != -1

    #Проверка существует ли состояние
    def IsStateExist(self, state):
        return self.table.GetRowIndex(state) != -1

    #Изменить символ
    def ChangeSymbol(self, column, symbol, isBreakpoint):
        self.table.SetColumnName(column, symbol)
        
        try:
            self.breakpointSymbols.index(symbol)
            isBreakpointExist = True
        except:
            isBreakpointExist = False

        if isBreakpoint:
            if not isBreakpointExist:
                self.SetBreakpointColumn(column, True)
        else:
            if isBreakpointExist:
                self.SetBreakpointColumn(column, False)

    #Изменить состояние
    def ChangeState(self, row, state, isBreakpoint, isInit, isStopped):
        self.table.SetRowName(row, state)
        
        try:
            self.breakpointStates.index(state)
            isBreakpointExist = True
        except:
            isBreakpointExist = False

        if isBreakpoint:
            if not isBreakpointExist:
                self.SetBreakpointRow(row, True)
        else:
            if isBreakpointExist:
                self.SetBreakpointRow(row, False)
        
        try:
            self.stoppedStates.index(state)
            isExist = True
        except:
            isExist = False

        if isStopped:
            if not isExist:
                self.stoppedStates.append(state)
                self.callbackUpdateState()
        else:
            if isExist:
                self.stoppedStates.remove(state)
                self.callbackUpdateState()
        
        if not isInit:
            if self.initState == state:
                self.initState = None
                self.callbackUpdateState()
        else:
            if self.initState == None or not self.initState == state:
                self.initState = state
                self.callbackUpdateState()

    #Изменить правило
    def ChangeRule(self, column: int, row: int, rule: Rule, isBreakpoint: bool):
        symbol = self.table.GetColumnName(column)
        state = self.table.GetRowName(row)
        
        if [symbol, state] in self.breakpointRules:
            isBreakpointExist = True
        else:
            isBreakpointExist = False

        if isBreakpoint:
            if not isBreakpointExist:
                self.breakpointRules.append([symbol, state])
                if self.callbackAddBreakpointRule != None:
                    self.callbackAddBreakpointRule(column, row, symbol, state)
        else:
            if isBreakpointExist:
                self.breakpointRules.remove([symbol, state])
                if self.callbackRemoveBreakpointRule != None:
                    self.callbackRemoveBreakpointRule(column, row, symbol, state)

        columnUID = self.table.GetUIDByColumn(column)
        rowUID = self.table.GetUIDByRow(row)
        
        self.ruleTable[row][column] = rule
        self.UpdateRuleButton(columnUID, rowUID)

    #Удалить символ
    def DeleteSymbol(self, column, symbol):
        self.table.RemoveColumn(column)

    #Удалить состояние
    def DeleteState(self, row, state):
        self.table.RemoveRow(row)
        
    #Очистить таблицу
    def Clear(self):
        self.table.Clear()
        self.buttonTable = list()
        self.ruleTable = list()
        
        self.breakpointStates = list()
        self.breakpointRules = list()
        self.breakpointSymbols = list()
        self.initState = None
        
        self.table.AddColumn(self.emptySymbol)

    def IsRowBreakpoint(self, row):
        state = self.table.GetRowName(row)
        return self.IsStateBreakpoint(state)

    def IsColumnBreakpoint(self, column):
        symbol = self.table.GetColumnName(column)
        return self.IsSymbolBreakpoint(symbol)
    
    def IsRuleBreakpointIndex(self, column, row):
        return self.IsRuleBreakpoint(self.table.GetColumnName(column), self.table.GetRowName(row))
    
    def IsRuleBreakpointIndexCurrently(self, column, row):
        return self.IsRuleBreakpointCurrently(self.table.GetColumnName(column), self.table.GetRowName(row))
        
    def IsSymbolBreakpoint(self, symbol):
        return symbol in self.breakpointSymbols
    
    def IsStateBreakpoint(self, state):
        return state in self.breakpointStates
    
    def IsRuleBreakpoint(self, symbol, state):
        return [symbol, state] in self.breakpointRules
    
    def IsRuleBreakpointCurrently(self, symbol, state):
        return self.IsRuleBreakpoint(symbol, state) or self.IsSymbolBreakpoint(symbol) or self.IsStateBreakpoint(state)
    
    def SetBreakpointColumn(self, column, enable:bool = True):
        symbol = self.table.GetColumnName(column)
        if enable:
            if self.callbackAddBreakpointSymbol != None:
                self.callbackAddBreakpointSymbol(column, symbol)
            if not self.IsSymbolBreakpoint(symbol):
                self.breakpointSymbols.append(symbol)
        else:
            if self.IsSymbolBreakpoint(symbol):
                if self.callbackRemoveBreakpointSymbol != None:
                    self.callbackRemoveBreakpointSymbol(column, symbol)
                self.breakpointSymbols.remove(symbol)
                
    def SetBreakpointRow(self, row, enable:bool = True):
        state = self.table.GetRowName(row)
        if enable:
            if self.callbackAddBreakpointState != None:
                self.callbackAddBreakpointState(row, state)
            if not self.IsStateBreakpoint(state):
                self.breakpointStates.append(state)
        else:
            if self.IsStateBreakpoint(state):
                if self.callbackRemoveBreakpointState != None:
                    self.callbackRemoveBreakpointState(row, state)
                self.breakpointStates.remove(state)
                
        