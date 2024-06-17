import enum
#import json
import subprocess

from kivy.app import App
from kivy.uix.widget import Widget

from kivy.graphics import Color, Rectangle

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
#Config.set('kivy', 'exit_on_escape', '0')

from userGuide import *

from functools import partial

class Direction(enum.Enum):
    left = -1
    halt = 0
    right = 1

class Rule:
    newState = ""#Новое состояние
    newSymbol = ""#Новый символ
    direction = Direction.halt#Направление сдвига

    def __init__(self, newState, newSymbol, direction = Direction.halt):
        self.newState = newState
        self.newSymbol = newSymbol
        self.direction = direction

    def copy(self):
        return Rule(self.newState, self.newSymbol, self.direction)

class RuleTable:
    table = {}

    def __init__(self):
        pass

    def Set(self, symbol, state, rule):
        if not (state in self.table):
            self.table.update({state: {}})
        self.table[state].update({symbol: rule})

    def Get(self, symbol, state):
        try:
            return self.table[state][symbol]
        except:
            return None

    def Remove(self, symbol, state):
        try:
            del self.table[state][symbol]
        except:
            return False
        return True

    def RemoveState(self, state):
        try:
            del self.table[state]
        except:
            return False
        return True

    def RemoveSymbol(self, symbol):
        for state in self.table:
            try:
                del self.table[state][symbol]
            except:
                return False
        return True

    def Clear(self):
        self.table = {}


class ExcelLikeTable(GridLayout):
    columnHeight = 100
    columnWidth = 330
    rowHeight = 100
    rowWidth = 130

    columnHeaders = list()
    rowHeaders  = list()

    columnHeadersID = list()
    rowHeadersID  = list()
    columnUID = 0
    rowUID = 0

    headerRow = None

    callbackButtonColumn = None
    callbackButtonRow = None
    defaultCellInit = None

    callbackAddColumn = None
    callbackAddRow = None
    callbackRemoveColumn = None
    callbackRemoveRow = None

    columnPrefix = ""
    rowPrefix = ""

    def __init__(self,
                 callbackButtonColumn = None, callbackButtonRow = None, defaultCellInit = None,
                 callbackAddColumn = None, callbackAddRow = None,
                 callbackRemoveColumn = None, callbackRemoveRow = None,
                 **kwargs):
        super(ExcelLikeTable, self).__init__(**kwargs)

        self.callbackButtonColumn = callbackButtonColumn
        self.callbackButtonRow = callbackButtonRow
        self.defaultCellInit = defaultCellInit
        self.callbackAddColumn = callbackAddColumn
        self.callbackAddRow = callbackAddRow
        self.callbackRemoveColumn = callbackRemoveColumn
        self.callbackRemoveRow = callbackRemoveRow

        self.headerRow = GridLayout(rows = 1, size_hint_x = None, size_hint_y = None, spacing = 3)

        self.headerRow.height = self.columnHeight
        self.headerRow.width = self.rowWidth

        self.headerRow.add_widget(self.CreateFirstCell("Состояние"))
        self.add_widget(self.headerRow, 1)
        
    def CreateCell(height, width):
        layout = BoxLayout(orientation = "vertical", size_hint_x = None, size_hint_y = None, height = height, width = width)
        return layout

    def CreateFirstCell(self, value):
        layout = ExcelLikeTable.CreateCell(self.columnHeight, self.rowWidth)
        label = Button(text = value, background_normal = "", font_size = 22)
        label.background_color = [0.4, 0.4, 0.4, 1]
        layout.add_widget(label)
        
        return layout

    def CreateHeaderColumn(self, column, value):
        button = Button(text = self.columnPrefix + value, background_normal = "", font_size = 22)
        button.background_color = [0.4, 0.4, 0.4, 1]
        button.bind(on_press=partial(self.HandleButtonColumn, self.columnUID))

        self.columnHeadersID.append([self.columnUID, column])
        self.columnUID += 1
        
        layout = ExcelLikeTable.CreateCell(self.columnHeight, self.columnWidth)
        layout.add_widget(button)
        return layout

    def CreateHeaderRow(self, row, value):
        button = Button(text = self.rowPrefix + value, background_normal = "", font_size = 22)
        button.background_color = [0.4, 0.4, 0.4, 1]
        button.bind(on_press=partial(self.HandleButtonRow, self.rowUID))

        self.rowHeadersID.append([self.rowUID, row])
        self.rowUID += 1
        
        layout = ExcelLikeTable.CreateCell(self.rowHeight, self.rowWidth)
        layout.add_widget(button)
        return layout

    def CreateTableCell(self, column, row):
        layout = ExcelLikeTable.CreateCell(self.rowHeight, self.columnWidth)
        layout.add_widget(self.defaultCellInit(column, row))
        return layout

    def GetColumnByUID(self, uid):
        for record in self.columnHeadersID:
            if record[0] == uid:
                return record[1]
        return -1

    def GetRowByUID(self, uid):
        for record in self.rowHeadersID:
            if record[0] == uid:
                return record[1]
        return -1

    def GetUIDByColumn(self, column):
        for record in self.columnHeadersID:
            if record[1] == column:
                return record[0]
        return -1

    def GetUIDByRow(self, row):
        for record in self.rowHeadersID:
            if record[1] == row:
                return record[0]
        return -1

    def AddColumn(self, name, index = -1):
        if (index < 0 and index != -1) or index >= len(self.headerRow.children):
            return False
        if index == -1:
            index = len(self.headerRow.children)
            newIndex = -len(self.headerRow.children)
        else:
            newIndex = -index-1
        
        self.columnHeaders.insert(index, name)
        
        self.headerRow.add_widget(self.CreateHeaderColumn(index-1, name), newIndex)
        self.headerRow.width += self.columnWidth

        if self.callbackAddColumn != None:
            self.callbackAddColumn(index-1, name)

        i = 0
        for row in reversed(self.children):
            if row != self.headerRow:
                rule = self.CreateTableCell(self.columnUID-1, self.GetUIDByRow(i))
                row.add_widget(rule, newIndex)
                i += 1
                
        return True

    def AddRow(self, name, index = -1):
        if (index < 0 and index != -1) or index >= len(self.children):
            return False
        if index == -1:
            index = len(self.children)
            newIndex = -len(self.children)
        else:
            newIndex = -index-1
        
        self.rowHeaders.insert(index, name)
        
        layout = GridLayout(rows = 1, size_hint_x = None, size_hint_y = None,
                            spacing = 3)
        layout.height = self.rowHeight
        layout.width = self.rowWidth

        layout.add_widget(self.CreateHeaderRow(index-1, name))

        if self.callbackAddRow != None:
            self.callbackAddRow(index-1, name)

        i = 0
        for columnHeader in self.columnHeaders:
            layout.add_widget(self.CreateTableCell(self.GetUIDByColumn(i), self.rowUID-1))
            i += 1
            
        self.add_widget(layout, newIndex)

        return True

    def RemoveColumn(self, index):
        if index < 0 or index >= len(self.children[0].children):
            return False
        for row in self.children:
            row.remove_widget(row.children[len(row.children)-index-2])
        del self.columnHeaders[index]
        self.headerRow.width -= self.columnWidth

        for record in self.columnHeadersID:
            if record[1] == index:
                self.columnHeadersID.remove(record)
                break
        for record in self.columnHeadersID:
            if record[1] > index:
                record[1] -= 1

        if self.callbackRemoveColumn != None:
            self.callbackRemoveColumn(index)
        
        return True

    def RemoveRow(self, index):
        if index < 0 or index >= len(self.children):
            return False
        self.remove_widget(self.children[len(self.children)-index-2])
        del self.rowHeaders[index]

        for record in self.rowHeadersID:
            if record[1] == index:
                self.rowHeadersID.remove(record)
                break
        for record in self.rowHeadersID:
            if record[1] > index:
                record[1] -= 1

        if self.callbackRemoveRow != None:
            self.callbackRemoveRow(index)
        
        return True

    def RemoveColumnByName(self, name):
        try:
            index = self.columnHeaders.index(name)
        except:
            return False
        return self.RemoveColumn(index-1)

    def RemoveRowByName(self, name):
        try:
            index = self.rowHeaders.index(name)
        except:
            return False
        return self.RemoveRow(index-1)

    def GetColumn(self, index):
        if index < 0 or index >= len(self.children[0].children):
            return None
        return self.headerRow.children[len(self.headerRow.children)-index-2].children[0]

    def GetRow(self, index):
        if index < 0 or index >= len(self.children[0].children):
            return None
        return self.children[len(self.children)-index-2].children[-1].children[0]

    def GetColumnIndex(self, name):
        try:
            return self.columnHeaders.index(name)
        except:
            return -1

    def GetRowIndex(self, name):
        try:
            return self.rowHeaders.index(name)
        except:
            return -1

    def EditColumn(self, index, name):
        if index < 0 or index >= len(self.children[0].children):
            return False
        self.columnHeaders[index] = name
        self.GetColumn(index).text = self.columnPrefix + name
        return True

    def EditRow(self, index, name):
        if index < 0 or index >= len(self.children):
            return False
        self.rowHeaders[index] = name
        self.GetRow(index).text = self.rowPrefix + name
        return True

    def EditColumnByName(self, oldName, newName):
        try:
            index = self.columnHeaders.index(oldName)
        except:
            return False
        return self.EditColumn(index-1, newName)

    def EditRowByName(self, oldName, newName):
        try:
            index = self.rowHeaders.index(oldName)
        except:
            return False
        return self.EditRow(index-1, newName)

    def HandleButtonColumn(self, columnUID, button):
        if self.callbackButtonColumn != None:
            self.callbackButtonColumn(button, columnUID)

    def HandleButtonRow(self, rowUID, button):
        if self.callbackButtonRow != None:
            self.callbackButtonRow(button, rowUID)

    def HandleButtonCell(self, columnUID, rowUID, button):
        if self.callbackButtonCell != None:
            self.callbackButtonCell(button, columnUID, rowUID)
            
class TuringRulesGUI:
    table = None

    emptySymbol = "λ"

    tablesRows = 0
    tablesColumns = 0
    ruleTable = list()#Состояние - символ - правило
    buttonTable = list()#Состояние - символ - кнопка
    
    def __init__(self, table = None):
        self.table = table
        table.callbackButtonColumn = self.OnPressedColumn
        table.callbackButtonRow = self.OnPressedRow
        table.defaultCellInit = self.DefaultCell
        table.callbackAddColumn = self.OnAddSymbol
        table.callbackAddRow = self.OnAddState
        table.callbackRemoveColumn = self.OnRemoveSymbol
        table.callbackRemoveRow = self.OnRemoveState

        table.columnPrefix = "Символ\n"
        table.rowPrefix = "Состояние\n"

        table.AddColumn(self.emptySymbol)

    def DefaultCell(self, columnUID, rowUID):
        column = self.table.GetColumnByUID(columnUID)
        row = self.table.GetRowByUID(rowUID)
        
        button = Button(text = str(column) + " " + str(row), color = [0, 0, 0, 1], background_normal = "", font_size = 22)
        button.background_color = [1, 1, 1, 1]
        button.bind(on_press=partial(self.HandleButtonCell, columnUID, rowUID))
        
        self.buttonTable[row][column] = button
        self.UpdateRuleButton(columnUID, rowUID)
        return button

    def DefaultRule(self, column, row):
        return Rule(self.table.rowHeaders[row], self.table.columnHeaders[column], Direction.halt)

    def GetButtonRule(self, column, row):
        return self.buttonTable[row][column]

    def GetRule(self, column, row):
        return self.ruleTable[row][column]#

    def OnAddSymbol(self, column, symbol):
        self.tablesColumns += 1
        for row in range(self.tablesRows):
            self.ruleTable[row].insert(column, self.DefaultRule(column, row))

            self.buttonTable[row].insert(column, None)

    def OnAddState(self, row, state):
        self.tablesRows += 1
        
        self.ruleTable.insert(row, list())
        self.buttonTable.insert(row, list())
        for column in range(self.tablesColumns):
            self.ruleTable[row].append(self.DefaultRule(column, row))
            
            self.buttonTable[row].append(None)

    def OnRemoveSymbol(self, column):
        self.tablesColumns -= 1
        for i in range(len(self.ruleTable)):
            del self.ruleTable[i][column]
            del self.buttonTable[i][column]

    def OnRemoveState(self, row):
        self.tablesRows -= 1
        del self.ruleTable[row]
        del self.buttonTable[row]

    def GetNameDirection(direction):
        if direction == direction.left:
            return "Влево"
        elif direction == direction.right:
            return "Вправо"
        else:
            return "На месте"

    def UpdateRuleButton(self, columnUID, rowUID):
        column = self.table.GetColumnByUID(columnUID)
        row = self.table.GetRowByUID(rowUID)
        
        rule = self.ruleTable[row][column]

        direction = TuringRulesGUI.GetNameDirection(rule.direction)
        
        self.buttonTable[row][column].text = "Новый символ: " + rule.newSymbol + "\nНовое состояние: " + rule.newState + "\nНаправление: " + direction

    def HandleButtonCell(self, column, row, button):
        self.OnPressedCell(button, column, row)

    def OnPressedColumn(self, button, index):
        column = self.table.GetColumnByUID(index)
        symbol = self.table.columnHeaders[column]

        if symbol != self.emptySymbol:
            popup = PopupChangeSymbol(self, button, index, symbol)
            popup.open()

    def OnPressedRow(self, button, index):
        row = self.table.GetRowByUID(index)
        state = self.table.rowHeaders[row]
        
        popup = PopupChangeState(self, button, index, state)
        popup.open()

    def OnPressedCell(self, button, columnUID, rowUID):
        column = self.table.GetColumnByUID(columnUID)
        row = self.table.GetRowByUID(rowUID)
        
        symbol = self.table.columnHeaders[column]
        state = self.table.rowHeaders[row]
        
        popup = PopupChangeRule(self, button, columnUID, rowUID, symbol, state)
        popup.open()

    def IsSymbolExist(self, symbol):
        return self.table.GetColumnIndex(symbol) != -1

    def IsStateExist(self, state):
        return self.table.GetRowIndex(state) != -1

    def ChangeSymbol(self, button, column, symbol):
        self.table.EditColumn(column, symbol)

    def ChangeState(self, button, row, state):
        self.table.EditRow(row, state)

    def ChangeRule(self, button, column, row, rule):
        columnUID = self.table.GetUIDByColumn(column)
        rowUID = self.table.GetUIDByRow(row)
        
        self.ruleTable[row][column] = rule
        self.UpdateRuleButton(columnUID, rowUID)

    def DeleteSymbol(self, button, column, symbol):
        self.table.RemoveColumn(column)

    def DeleteState(self, button, row, state):
        self.table.RemoveRow(row)

class PopupChangeSymbol(Popup):
    GUI = None
    button = None
    column = 0
    symbol = None
    def __init__(self, GUI, button, columnUID, symbol, *args):
        self.GUI = GUI
        self.button = button
        self.column = self.GUI.table.GetColumnByUID(columnUID)
        self.symbol = symbol
        
        super(PopupChangeSymbol, self).__init__(*args)
        
        self.ids["input"].text = symbol

        SetHelpState(IDH_TOPIC_IZMENENIE_I_UDALENIE_SIMVOLA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnApply(self):
        symbol = self.ids["input"].text.strip()
        if len(symbol) == 0:
            symbol = self.GUI.emptySymbol
        elif symbol != self.symbol and self.GUI.IsSymbolExist(symbol):
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Такой символ уже существует"
        else:
            self.GUI.ChangeSymbol(self.button, self.column, symbol)
            self.dismiss()
            
    def OnDelete(self):
        self.GUI.DeleteSymbol(self.button, self.column, self.symbol)
        self.dismiss()

class PopupChangeState(Popup):
    GUI = None
    button = None
    row = 0
    state = None
    def __init__(self, GUI, button, rowUID, state, *args):
        self.GUI = GUI
        self.button = button
        self.row = self.GUI.table.GetRowByUID(rowUID)
        self.state = state
        
        super(PopupChangeState, self).__init__(*args)
        
        self.ids["input"].text = state

        SetHelpState(IDH_TOPIC_IZMENENIE_I_UDALENIE_SOSTOYANIYA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnApply(self):
        state = self.ids["input"].text
        if len(state) == 0:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Пустая строка"
        elif state != self.state and self.GUI.IsStateExist(state):
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Такое состояние уже существует"
        else:
            self.GUI.ChangeState(self.button, self.row, state)
            self.dismiss()
            
    def OnDelete(self):
        self.GUI.DeleteState(self.button, self.row, self.state)
        self.dismiss()

class PopupChangeRule(Popup):
    GUI = None
    button = None
    column = 0
    row = 0

    rule = None
    
    def __init__(self, GUI, button, columnUID, rowUID, symbol, state, *args):
        self.GUI = GUI
        self.button = button
        self.column = self.GUI.table.GetColumnByUID(columnUID)
        self.row = self.GUI.table.GetRowByUID(rowUID)
        
        super(PopupChangeRule, self).__init__(*args)

        self.rule = self.GUI.GetRule(self.column, self.row).copy()

        self.ids["inputSymbol"].text = self.rule.newSymbol
        self.ids["inputState"].text = self.rule.newState

        self.ids["direction"].text = TuringRulesGUI.GetNameDirection(self.rule.direction)

        SetHelpState(IDH_TOPIC_IZMENENIE_PRAVILA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    def NextDirection(self):
        direction = self.rule.direction
        
        if direction == Direction.right:
            direction = Direction.left
        elif direction == Direction.left:
            direction = Direction.halt
        else:
            direction = Direction.right
            
        self.rule.direction = direction
        self.ids["direction"].text = TuringRulesGUI.GetNameDirection(self.rule.direction)
        
    def OnApply(self):
        symbol = self.ids["inputSymbol"].text
        state = self.ids["inputState"].text

        self.ids["error"].text = ""
        error = False

        if symbol == "":
            symbol = self.GUI.emptySymbol
        
        if not self.GUI.IsSymbolExist(symbol):
            self.ids["error"].text += "Введённый символ не существует"
            error = True
        if not self.GUI.IsStateExist(state):
            if error == True:
                self.ids["error"].text += "\n"
            self.ids["error"].text += "Введённое состояние не сщуествует"
            error = True
            
        if error:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        else:
            self.rule.newSymbol = symbol
            self.rule.newState = state
            
            self.GUI.ChangeRule(self.button, self.column, self.row, self.rule)
            self.dismiss()

class TuringTapeGUI:
    emptySymbol = ""
    
    tape = None
    currentOffset = 0
    tapeWindowSize = 7

    tapeList = list()
    tapeListStart = 0

    tapeInputCells = list()
    
    def __init__(self, tape = None):
        self.tape = tape

        tape.ids["TapeLeft"].children[1].on_press = self.OnLeft
        tape.ids["TapeRight"].children[1].on_press = self.OnRight

        self.SetOffset(0)

        index = 0
        for tapeCell in reversed(tape.children[1].children):
            textInput = tapeCell.children[1]
            self.tapeInputCells.append(textInput)
            textInput.bind(text=partial(self.OnText, index))
            textInput.bind(focus=partial(self.OnCellFocused))
            index += 1

    def OnCellFocused(self, instance, value):
        if value:
            SetHelpState(IDH_TOPIC_RABOTA_S_LENTOJ)
        else:
            SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    def SetEmptySymbol(self, symbol):
        self.emptySymbol = symbol

        for tapeCell in reversed(self.tape.children[1].children):
            textInput = tapeCell.children[1]
            textInput.hint_text = self.emptySymbol

    def GetCenterWindowIndex(self):
        return self.tapeWindowSize//2

    def OnText(self, index, instance, substring, from_undo=False):
        if len(instance.text) > 1:
            substring = ""
        TextInput.insert_text(instance, substring, from_undo)

    def OnText(self, index, instance, text):
        if len(text) > 1:
            instance.text = instance.text[0]
            
        center = self.GetCenterWindowIndex()
        tapeIndex = self.currentOffset-center+index
        tapeListIndex = tapeIndex-self.tapeListStart
        self.tapeList[tapeListIndex] = instance.text

    def OnLeft(self):
        self.SetOffset(self.currentOffset-1)
    
    def OnRight(self):
        self.SetOffset(self.currentOffset+1)

    def SetOffset(self, offset):
        center = self.GetCenterWindowIndex()

        #Переназначение начала ленты
        if self.tapeListStart > offset-center:
            self.tapeListStart = offset-center
            self.tapeList.insert(0, "")
        
        self.currentOffset = offset
        for i in range(self.tapeWindowSize):
            
            #Обновление индексов
            index = (offset-center)+i
            self.tape.children[1].children[self.tapeWindowSize-1-i].children[0].text = str(index)
            
            #Обновление символов (ленты)
            tapeListIndex = index-self.tapeListStart
            
            try:
                self.tapeList[tapeListIndex]
            except:
                self.tapeList.insert(tapeListIndex, "")
                
            self.tape.children[1].children[self.tapeWindowSize-1-i].children[1].text = self.tapeList[tapeListIndex]

class TuringControlGUI:
    controlPanel = None

    info = None

    callbackStep = None
    callbackReset = None
    callbackClearTape = None
    callbackInputState = None

    callbackAddSymbol = None
    callbackAddState = None
    callbackClearTable = None

    def __init__(self, controlPanel = None,
                 callbackStep = None, callbackReset = None,
                 callbackClearTape = None, callbackInputState = None,
                 callbackAddSymbol = None, callbackAddState = None,
                 callbackClearTable = None):
        self.controlPanel = controlPanel
        self.info = controlPanel.ids["Info"]

        controlPanel.ids["Step"].bind(on_press=partial(self.Step))
        controlPanel.ids["Reset"].bind(on_press=partial(self.Reset))
        controlPanel.ids["ClearTape"].bind(on_press=partial(self.ClearTape))
        controlPanel.ids["InputState"].bind(text=partial(self.InputState))
        controlPanel.ids["InputState"].bind(focus=partial(self.OnInputStateFocused))

        controlPanel.ids["AddSymbol"].bind(on_press=partial(self.AddSymbol))
        controlPanel.ids["AddState"].bind(on_press=partial(self.AddState))
        controlPanel.ids["ClearTable"].bind(on_press=partial(self.ClearTable))

        self.callbackStep = callbackStep
        self.callbackReset = callbackReset
        self.callbackClearTape = callbackClearTape
        self.callbackInputState = callbackInputState

        self.callbackAddSymbol = callbackAddSymbol
        self.callbackAddState = callbackAddState
        self.callbackClearTable = callbackClearTable

    def OnInputStateFocused(self, instance, value):
        if value:
            SetHelpState(IDH_TOPIC_IZMENENIE_NACHALNOGO_SOSTOYANIYA)
        else:
            SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    def SetInfo(self, text):
        self.info.text = text

    def Step(self, instance):
        self.callbackStep()
    
    def Reset(self, instance):
        self.callbackReset()

    def ClearTape(self, instance):
        self.callbackClearTape()

    def InputState(self, instance, text):
        self.callbackInputState(text)

    def AddSymbol(self, instance):
        self.callbackAddSymbol()

    def AddState(self, instance):
        self.callbackAddState()

    def ClearTable(self, instance):
        self.callbackClearTable()

class TuringMachine:
    emptySymbol = ""
   
    state = ""#Состояние
    headPos = 0#Позиция головки чтения-записи

    memoryTape = [emptySymbol]#Теущая память ленты

    tableRules = RuleTable()#Таблица правил (таблица переходов)

    def SetHead(self, pos):
        if pos < 0 or pos >= len(self.memoryTape):
            return False
        headPos = pos
        return True

    def StepLeft(self):
        #Если последний символ на ленте - пустой
        if self.headPos == (len(self.memoryTape)-1) and self.memoryTape[self.headPos] == self.emptySymbol:
            del self.memoryTape[self.headPos]#То удаляем его
                    
        self.headPos -= 1
        if self.headPos < 0:#Если слева нет места
            self.memoryTape.insert(0, self.emptySymbol)#Тогда выделяем
            self.headPos = 0#И обнуляем положение головки
            
    def StepRight(self):
        symbol = self.memoryTape[0]
        #Если первый символ на ленте - пустой
        if self.headPos == 0 and symbol == self.emptySymbol:
            del self.memoryTape[self.headPos]#То удаляем его

        self.headPos += 1        
        if self.headPos > len(self.memoryTape):#Если справа нет места
            self.memoryTape.append(self.emptySymbol)#Тогда выделяем

    def Step(self):
        symbol = self.memoryTape[self.headPos]

        rule = self.tableRules.Get(symbol, self.state)#Чтение правила

        if rule == None:#Если правила не существует
            return False

        #Установка новых значений согласно правилу
        symbol = self.memoryTape[self.headPos] = rule.newSymbol

        direction = rule.direction
        #Переход на новую позицию
        match direction:
            case Direction.left:
                self.StepLeft()
            case Direction.right:
                self.StepRight()

        #Установка нового состояния
        self.state = rule.newState
        return True
    
    def Run(self):
        while self.Step():
            pass

    def GetRuleTable(self):
        return self.tableRules

class ControlledTuringMachine:
    turingMachine = None
    rulesGUI = None
    tapeGUI = None
    controlGUI = None

    isStarted = False
    initState = None

    lastColumn = 0
    lastRow = 0
    firstStep = False

    def __init__(self,
                 turingMachine = None, rulesGUI = None, tapeGUI = None, controlGUI = None):
        self.turingMachine = turingMachine
        self.rulesGUI = rulesGUI
        self.tapeGUI = tapeGUI
        self.controlGUI = controlGUI

        self.controlGUI.callbackStep = self.StepHandle
        self.controlGUI.callbackReset = self.Reset
        self.controlGUI.callbackClearTape = self.ClearTape
        self.controlGUI.callbackInputState = self.InputState

        self.controlGUI.callbackAddSymbol = self.AddSymbol
        self.controlGUI.callbackAddState = self.AddState
        self.controlGUI.callbackClearTable = self.ClearTable

        self.isStarted = False

        self.turingMachine.emptySymbol = "λ"
        self.tapeGUI.SetEmptySymbol("λ")

        self.initState = None

    def SetInfo(self, text):
        self.controlGUI.SetInfo(text)

    def RestoreLastHighlight(self):
        try:
            self.rulesGUI.buttonTable[self.lastRow][self.lastColumn].background_color = [1, 1, 1, 1]
        except:
            return False
        return True

    def HighlightCurrentRules(self):
        self.RestoreLastHighlight()
        
        symbol = self.turingMachine.memoryTape[self.turingMachine.headPos]
        state = self.turingMachine.state
        
        rule = self.turingMachine.tableRules.Get(symbol, self.turingMachine.state)

        table = self.rulesGUI.table

        column = table.GetColumnIndex(symbol)
        row = table.GetColumnIndex(state)-1

        try:
            self.rulesGUI.buttonTable[row][column].background_color = [1, 0, 0, 1]
        except:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.SetInfo("Вы удалили важную часть таблицы. Выполнение было прервано")
            self.Stop()
            
        self.lastColumn = column
        self.lastRow = row

    def Start(self):
        if self.initState == None:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.SetInfo("Начальное состояние не задано")
            return False

        try:
            self.rulesGUI.table.rowHeaders.index(self.initState)
        except:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.SetInfo("Такого состояние не существует (см. таблицу ниже)")
            return False

        initPos = 0
        self.lastColumn = 0
        self.lastRow = 0
        self.firstStep = True
        
        self.turingMachine.state = self.initState
        
        self.isStarted = True
        self.tapeGUI.SetOffset(initPos)

        #Устанавливаем каретку
        self.turingMachine.headPos = initPos-self.tapeGUI.tapeListStart

        self.turingMachine.memoryTape = self.tapeGUI.tapeList.copy()

        #Заполняем таблицу правил для машины Тьюринга
        ruleTable = self.turingMachine.GetRuleTable()
        for i in range(len(self.rulesGUI.ruleTable)):
            ruleState = self.rulesGUI.ruleTable[i]
            for j in range(len(ruleState)):
                ruleTable.Set(self.rulesGUI.table.columnHeaders[j], self.rulesGUI.table.rowHeaders[i], ruleState[j])

        return True
    def Stop(self):
        self.isStarted = False
        self.RestoreLastHighlight()

    def Step(self):
        if not self.isStarted:
            if not self.Start():
                return False

        if self.firstStep:
            self.HighlightCurrentRules()
            self.firstStep = False
        elif self.turingMachine.Step():
            self.HighlightCurrentRules()
            headPos = self.turingMachine.headPos
            self.tapeGUI.SetOffset(headPos+self.tapeGUI.tapeListStart)
        else:
            self.Stop()
            self.SetInfo("Достигнут конец")
            return False

        self.SetInfo("")
        return True

    def StepHandle(self):
        self.Step()

    def Reset(self):
        self.tapeGUI.SetOffset(0)
        self.SetInfo("")
        self.Stop()

    def ClearTape(self):
        self.turingMachine.memoryTape = list()
        self.tapeGUI.tapeList = list()
        self.tapeGUI.tapeListStart = 0
        self.Reset()

    def InputState(self, text):
        if len(text) == 0:
            self.initState = None
        else:
            self.initState = text

    def AddSymbol(self):
        PopupAddSymbol(self.rulesGUI).open()

    def AddState(self):
        PopupAddState(self.rulesGUI).open()

    def ClearTable(self):
        pass

class PopupAddSymbol(Popup):
    GUI = None
    def __init__(self, GUI, *args):
        self.GUI = GUI
        super(PopupAddSymbol, self).__init__(*args)

        SetHelpState(IDH_TOPIC_DOBAVLENIE_SIMVOLA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnAdd(self):
        symbol = self.ids["input"].text.strip()
        if len(symbol) == 0:
            self.ids["error"].text = "Пустая строка"
        elif self.GUI.IsSymbolExist(symbol):
            self.ids["error"].text = "Такой символ уже существует"
        else:
            self.GUI.table.AddColumn(symbol)
            self.dismiss()

class PopupAddState(Popup):
    GUI = None
    def __init__(self, GUI, *args):
        self.GUI = GUI
        super(PopupAddState, self).__init__(*args)

        SetHelpState(IDH_TOPIC_DOBAVLENIE_SOSTOYANIYA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnAdd(self):
        state = self.ids["input"].text.strip()
        if len(state) == 0:
            self.ids["error"].text = "Пустая строка"
        elif self.GUI.IsStateExist(state):
            self.ids["error"].text = "Такое состояние уже существует"
        else:
            self.GUI.table.AddRow(state)
            self.dismiss()


class MyLabel(Label):
    background_color = [0, 0, 0, 0]
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])
            Rectangle(pos=self.pos, size=self.size) 
            
class MainScreen(BoxLayout):
    machine = None
    proc = None
    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.machine = ControlledTuringMachine(TuringMachine(),
                                TuringRulesGUI(self.ids["GeneralField"].ids["TuringRules"]),
                                TuringTapeGUI(self.ids["GeneralField"].ids["TuringTape"]),
                                TuringControlGUI(self.ids["GeneralField"].ids["TuringControlPanel"]))

        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    def Save(self):
        return
        tape = self.machine.tapeGUI
        rules = self.machine.rulesGUI
        
        initState = self.machine.initState

        dictionary = {
          "initState": initState,
          "tapeList": tape.tapeList,
          "tapeListStart": tape.tapeListStart,
          "columnHeaders": rules.table.columnHeaders,
          "rowHeaders": rules.table.rowHeaders
        }

        for rowI in range(len(rules.ruleTable)):
            row = rules.ruleTable[rowI]
            for columnI in range(len(row)):
                rule = row[columnI]
                s = "rule_" + str(rowI) + "_" + str(columnI) 
                dictionary[s] = [rule.newState, rule.newSymbol, rule.direction.value]

        with open("test.json", "w") as file:
            json.dump(dictionary, file)

    def Load(self):
        return
        dictionary = None
        with open("test.json", "r") as file:
            dictionary = json.load(file)

        #print(dictionary)

        tape = self.machine.tapeGUI
        rules = self.machine.rulesGUI
        
        self.machine.initState = dictionary["initState"]
        tape.tapeList = dictionary["tapeList"]
        tape.tapeListStart = dictionary["tapeListStart"]

        #rules.table.columnHeaders = dictionary["columnHeaders"]
        #rules.table.rowHeaders = dictionary["rowHeaders"]

        for symbol in rules.table.columnHeaders:
            rules.table.AddColumn(symbol)

        for state in rules.table.rowHeaders:
            rules.table.AddColumn(symbol)

        for word in dictionary:
            if word[:5] == "rule_":
                mark = word.find("_", 5)
                row = int(word[5:mark])
                column = int(word[mark+1:])
    def Help(self):
        if self.proc != None:
            self.proc.kill()
            
        self.proc = subprocess.Popen("hh.exe -mapid" + str(IDH_TOPIC_VVEDENIE) + " help.chm")
        
class UIApp(App):
    proc = None
    #Отключение настроек на f1, замена на справку
    def open_settings(self, *largs):
        if self.proc != None:
            self.proc.kill()
            
        self.proc = subprocess.Popen("hh.exe -mapid" + str(GetHelpState()) + " help.chm")
    def build(self):
        screen = MainScreen()
        return screen

if __name__ == '__main__':
    UIApp().run()






