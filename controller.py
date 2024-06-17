from gui.popup import PopupAddState
from gui.popup import PopupAddSymbol
from highlighting import Highlighting
from tape.tapeHead import TapeHead
from userGuide import *

from kivy.uix.button import Button

from turingMachine import TuringMachineException
from turingMachine import TuringMachine
from controllers.mainPanel import MainPanelController
from controllers.tableRule import TableRuleController
from controllers.tape import TapeController
import turingMachine
from turingMachine.ruleTable import RuleTable

class ControlledTuringMachine:
    def __init__(self,
                 turingMachine:TuringMachine = None,
                 controllerRules:TableRuleController = None,
                 controllerTape:TapeController = None,
                 controllerMainPanel:MainPanelController = None):
        self.isStarted:bool = False
        self.firstStep:bool = False

        self.turingMachine:TuringMachine = turingMachine
        self.controllerRules:TableRuleController = controllerRules
        self.controllerTape:TapeController = controllerTape
        self.controllerMainPanel:MainPanelController = controllerMainPanel

        self.controllerMainPanel.callbackRun = self.RunHandle
        self.controllerMainPanel.callbackStep = self.StepHandle
        self.controllerMainPanel.callbackReset = self.Reset
        self.controllerMainPanel.callbackClearTape = self.ClearTape

        self.controllerMainPanel.callbackAddSymbol = self.AddSymbol
        self.controllerMainPanel.callbackAddState = self.AddState
        self.controllerMainPanel.callbackClearTable = self.ClearTable
        
        self.controllerRules.callbackUpdateState = self.UpdateStatesHighlight
        
        #Намертво связываем графическое представление и внутреннее
        self.tape:TapeHead = TapeHead()
        self.turingMachine.tapeHead = self.tape
        self.controllerTape.tapeHead = self.tape
        self.controllerTape.EmptySymbol = "λ"
        self.controllerTape.Update()
        
        self.turingMachine.StopStates = self.controllerRules.stoppedStates
        
        self.highlighting = Highlighting(turingMachine, controllerRules, controllerTape)
        
    @property
    def IsStarted(self):
        return self.isStarted

    #Написать текст в информационное поле (обычно ошибка)
    def SetInfo(self, text):
        self.controllerMainPanel.SetInfo(text)
    
    #Проверка начального состояния
    def CheckInitState(self):
        if self.turingMachine.InitState == None:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.SetInfo("Начальное состояние не задано")
            return False

        try:
            self.controllerRules.table.rowHeaders.index(self.turingMachine.InitState)
        except:
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
            self.SetInfo("Такого состояния не существует (см. таблицу ниже)")
            return False
        
        return True
    
    #Заполнение таблицы правил для машины Тьюринга
    def RuleTableCopy(self):
        ruleTable:RuleTable = self.turingMachine.TableRules
        self.turingMachine.TableRules.Clear()
        for i in range(len(self.controllerRules.ruleTable)):
            ruleState = self.controllerRules.ruleTable[i]
            for j in range(len(ruleState)):
                ruleTable.Set(self.controllerRules.table.columnHeaders[j], self.controllerRules.table.rowHeaders[i], ruleState[j])

    #Запуск исполнителя
    def Start(self):
        if not self.CheckInitState():
            return False
        self.firstStep = True
        self.isStarted = True

        #Заполняем таблицу правил для машины Тьюринга
        self.RuleTableCopy()

        self.turingMachine.State = self.turingMachine.InitState

        self.controllerRules.Access = False
        self.controllerMainPanel.Access = False

        return True
    
    #Остановка исполнителя
    def Stop(self):
        self.isStarted = False
        self.firstStep = None
        
        self.turingMachine.Stop()
        
        self.highlighting.Disable()

        self.controllerRules.Access = True
        self.controllerMainPanel.Access = True
        
    def Run(self):
        if not self.IsStarted:
            if not self.Start():
                return False
        numberOfStep = 0
        while self.Step():
            symbol = self.turingMachine.CurrentSymbol
            state = self.turingMachine.State
                
            #Точка останова
            if self.controllerRules.IsSymbolBreakpoint(symbol) or \
                self.controllerRules.IsStateBreakpoint(state) or \
                self.controllerRules.IsRuleBreakpoint(symbol, state):
                    return True
            
            if numberOfStep >= 10000:
                self.SetInfo("Превышен лимит итераций в 10000")
                SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
                return False
            numberOfStep += 1
        return True

    #Шаг исполнителя
    def Step(self):
        #Запуск исполнителя
        if not self.IsStarted:
            if not self.Start():
                return False

        #Делаем первый шаг специально для отображения подсветки
        if self.firstStep:
            self.firstStep = False
            self.turingMachine.Head = 0

            self.controllerTape.Update()
            self.highlighting.Update()
        else:
            try:
                if self.turingMachine.Step():
                    self.controllerTape.Update()
                    self.highlighting.Update()
                else:
                    self.SetInfo("Достигнут конец")
                    self.Stop()
                    return False
            except TuringMachineException:
                if self.turingMachine.State == None:
                    stateName = "None"
                else:
                    stateName = str(self.turingMachine.State)
                self.SetInfo(
                    'Правила для данного случая не существует (символ "' + self.turingMachine.CurrentSymbol +
                    '"; состояние "' + stateName + '")')
                self.Stop()
                return False

        self.SetInfo("")
        return True

    #Когда нажата кнопка шага
    def StepHandle(self):
        self.Step()
        
    #Когда нажата кнопка запуска
    def RunHandle(self):
        self.Run()

    #Когда нажата кнопка сброса
    def Reset(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        self.SetInfo("")
        self.Stop()

    #Когда нажата кнопка очистки ленты
    def ClearTape(self):
        self.Reset()
        self.turingMachine.tapeHead.Clear()
        self.controllerTape.Update()

    #Когда был добавлен новый символ
    def AddSymbol(self):
        PopupAddSymbol(self.controllerRules).open()

    #Когда было добавлено новое состояние
    def AddState(self):
        PopupAddState(self.controllerRules).open()

    #Очистить таблицу правил
    def ClearTable(self):
        self.controllerRules.Clear()
        
    def UpdateStatesHighlight(self):
        self.turingMachine.InitState = self.controllerRules.initState
        #self.turingMachine.StopStates = self.controllerRules.stoppedStates.copy()
        self.highlighting.UpdateStatesHighlight()