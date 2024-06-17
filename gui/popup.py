from calendar import c
from pickle import OBJ
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

from turingMachine import Rule
from turingMachine.direction import *
from userGuide import *

class PopupAddSymbol(Popup):
    def __init__(self, controller, *args):
        self.controller = controller
        super(PopupAddSymbol, self).__init__(*args)

        SetHelpState(IDH_TOPIC_DOBAVLENIE_SIMVOLA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnAdd(self):
        symbol = self.ids["input"].text.strip()
        if len(symbol) == 0:
            self.ids["error"].text = "Пустая строка"
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        elif self.controller.IsSymbolExist(symbol):
            self.ids["error"].text = "Такой символ уже существует"
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        else:
            self.controller.table.AddColumn(symbol)
            self.dismiss()

class PopupAddState(Popup):
    def __init__(self, controller, *args):
        self.controller = controller
        super(PopupAddState, self).__init__(*args)

        SetHelpState(IDH_TOPIC_DOBAVLENIE_SOSTOYANIYA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnAdd(self):
        state = self.ids["input"].text.strip()
        if len(state) == 0:
            self.ids["error"].text = "Пустая строка"
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        elif self.controller.IsStateExist(state):
            self.ids["error"].text = "Такое состояние уже существует"
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        else:
            self.controller.table.AddRow(state)
            self.dismiss()
            
class PopupChangeSymbol(Popup):
    isBreakpoint = ObjectProperty(False)
    def __init__(self, controller, columnUID: int, symbol: str, isBreakpoint:bool, *args):
        self.controller = controller
        self.column: int = self.controller.table.GetColumnByUID(columnUID)
        self.symbol: int = symbol
        
        super(PopupChangeSymbol, self).__init__(*args)
        
        self.ids["input"].text = symbol
        self.isBreakpoint = isBreakpoint

        SetHelpState(IDH_TOPIC_IZMENENIE_I_UDALENIE_SIMVOLA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnApply(self):
        symbol = self.ids["input"].text.strip()
        if len(symbol) == 0:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Пустая строка"

        elif symbol != self.symbol and self.controller.IsSymbolExist(symbol):
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Такой символ уже существует"
        else:
            self.controller.ChangeSymbol(self.column, symbol, self.ids["Breakpoint"].active)
            self.dismiss()
            
    def OnDelete(self):
        self.controller.DeleteSymbol(self.column, self.symbol)
        self.dismiss()

class PopupChangeState(Popup):
    isBreakpoint = ObjectProperty(False)
    isStopped = ObjectProperty(False)
    isInit = ObjectProperty(False)
    def __init__(self, controller, rowUID: int, state: int, isBreakpoint: bool, isInit:bool, isStopped:bool, *args):
        self.controller = controller
        self.row: int = self.controller.table.GetRowByUID(rowUID)
        self.state: int = state
        
        super(PopupChangeState, self).__init__(*args)
        
        self.ids["input"].text = state
        self.isInit = isInit
        self.isStopped = isStopped
        self.isBreakpoint = isBreakpoint

        SetHelpState(IDH_TOPIC_IZMENENIE_I_UDALENIE_SOSTOYANIYA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def OnApply(self):
        state = self.ids["input"].text
        if len(state) == 0:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Пустая строка"
        elif state != self.state and self.controller.IsStateExist(state):
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.ids["error"].text = "Такое состояние уже существует"
        else:
            self.controller.ChangeState(self.row, state,
                                        self.ids["Breakpoint"].active,
                                        self.ids["InitState"].active,
                                        self.ids["StopState"].active)
            self.dismiss()
            
    def OnDelete(self):
        self.controller.DeleteState(self.row, self.state)
        self.dismiss()

class PopupChangeRule(Popup):
    isBreakpoint = ObjectProperty(False)
    def __init__(self, controller,
                 columnUID: int, rowUID: int, symbol: int, state: int, isBreakpoint: bool, *args):
        self.controller = controller
        self.column: int = self.controller.table.GetColumnByUID(columnUID)
        self.row: int = self.controller.table.GetRowByUID(rowUID)
        
        super(PopupChangeRule, self).__init__(*args)

        self.rule:Rule = self.controller.GetRule(self.column, self.row).Copy()

        self.ids["inputSymbol"].text = self.rule.newSymbol
        self.ids["inputState"].text = self.rule.newState

        self.ids["direction"].text = GetNameDirection(self.rule.direction)
        
        self.isBreakpoint = isBreakpoint

        SetHelpState(IDH_TOPIC_IZMENENIE_PRAVILA)

    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    def NextDirection(self):
        direction:Direction = self.rule.direction
        
        match(direction):
            case Direction.right:
                direction = Direction.left
            case Direction.left:
                direction = Direction.halt
            case Direction.halt:
                direction = Direction.right
            
        self.rule.direction = direction

        self.ids["direction"].text = GetNameDirection(self.rule.direction)
        
    def OnApply(self):
        symbol = self.ids["inputSymbol"].text
        state = self.ids["inputState"].text

        self.ids["error"].text = ""
        error = False

        if symbol == "":
            symbol = self.controller.emptySymbol
        
        if not self.controller.IsSymbolExist(symbol):
            self.ids["error"].text += "Введённый символ не существует"
            error = True
        if not self.controller.IsStateExist(state):
            if error == True:
                self.ids["error"].text += "\n"
            self.ids["error"].text += "Введённое состояние не сщуествует"
            error = True
            
        if error:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        else:
            self.rule.newSymbol = symbol
            self.rule.newState = state
            
            self.controller.ChangeRule(self.column, self.row, self.rule, self.ids["Breakpoint"].active)
            
            self.dismiss()