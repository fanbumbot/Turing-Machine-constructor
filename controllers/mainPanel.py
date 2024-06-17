from gui.popup import *

from functools import partial

class MainPanelController:
    def __init__(self, controlPanel = None,
                 callbackRun = None, callbackStep = None,
                 callbackReset = None, callbackClearTape = None,
                 callbackAddSymbol = None, callbackAddState = None,
                 callbackClearTable = None):
        self.controlPanel = controlPanel
        self.info = controlPanel.ids["Info"]

        self.access = True

        controlPanel.ids["Run"].bind(on_press=partial(self.Run))
        controlPanel.ids["Step"].bind(on_press=partial(self.Step))
        controlPanel.ids["Reset"].bind(on_press=partial(self.Reset))
        controlPanel.ids["ClearTape"].bind(on_press=partial(self.ClearTape))

        controlPanel.ids["AddSymbol"].bind(on_press=partial(self.AddSymbol))
        controlPanel.ids["AddState"].bind(on_press=partial(self.AddState))
        controlPanel.ids["ClearTable"].bind(on_press=partial(self.ClearTable))

        self.callbackRun = callbackRun
        self.callbackStep = callbackStep
        self.callbackReset = callbackReset
        self.callbackClearTape = callbackClearTape

        self.callbackAddSymbol = callbackAddSymbol
        self.callbackAddState = callbackAddState
        self.callbackClearTable = callbackClearTable
        
    @property
    def Access(self) -> bool:
        return self.access 
    
    @Access.setter
    def Access(self, access: bool):
        self.access = access

    def SetInfo(self, text):
        self.info.text = text

    def Run(self, instance):
        if self.callbackRun != None:
            self.callbackRun()

    def Step(self, instance):
        if self.callbackStep != None:
            self.callbackStep()
    
    def Reset(self, instance):
        if self.callbackReset != None:
            self.callbackReset()

    def ClearTape(self, instance):
        if self.callbackClearTape != None:
            self.callbackClearTape()

    def AddSymbol(self, instance):
        if self.callbackAddSymbol != None and self.Access:
            self.callbackAddSymbol()

    def AddState(self, instance):
        if self.callbackAddState != None and self.Access:
            self.callbackAddState()

    def ClearTable(self, instance):
        if self.callbackClearTable != None and self.Access:
            self.callbackClearTable()