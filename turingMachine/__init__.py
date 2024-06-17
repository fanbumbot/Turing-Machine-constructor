from ast import Index

from .rule import Rule
from .ruleTable import RuleTable
from .direction import Direction
from tape.tapeHead import TapeHead

class TuringMachineException(Exception):
    pass

class TuringMachine:
    def __init__(self, emptySymbol: str = "", state: str = "",
            callbackSymbolChanged = None,
            callbackStateChanged = None,
            callbackHeadPosChanged = None):
        
        self.tapeHead: TapeHead = TapeHead()        #Лента с головкой чтения
        self.TableRules = RuleTable()               #Таблица правил (таблица переходов)
        
        self.initState: str = state                 #Начальное состояние
        self.state: str = None                      #Текущеее состояние
        
        self.StopStates: list = list()              #Список со стоп-состояниями
        
        self.callbackSymbolChanged = callbackSymbolChanged
        self.callbackStateChanged = callbackStateChanged
        self.callbackHeadPosChanged = callbackHeadPosChanged
        
    @property
    def InitState(self):
        return self.initState
    
    @InitState.setter
    def InitState(self, state: str):
        self.initState = state
        
    @property
    def State(self) -> str:
        return self.state
    
    @State.setter
    def State(self, state: str):
        if self.callbackStateChanged != None:
            self.callbackStateChanged(self.State, state)
        self.state = state
    
    @property
    def EmptySymbol(self) -> str:
        return self.tapeHead.EmptySymbol 
    
    @EmptySymbol.setter
    def EmptySymbol(self, symbol: str):
        self.tapeHead.EmptySymbol = symbol

    @property
    def CurrentSymbol(self) -> str:
        return self.tapeHead.CurrentSymbol 
    
    @CurrentSymbol.setter
    def CurrentSymbol(self, symbol: str):
        if self.callbackSymbolChanged != None:
            self.callbackSymbolChanged(self.tapeHead.Head, self.tapeHead.CurrentSymbol, symbol)
        self.tapeHead.CurrentSymbol = symbol
        
    @property
    def Head(self) -> int:
        return self.tapeHead.Head 
    
    @Head.setter
    def Head(self, index: int):
        if self.callbackHeadPosChanged != None:
            self.callbackHeadPosChanged(self.tapeHead.Head, index)
        self.tapeHead.Head = index
        
    @property
    def IsStarted(self):
        return self.State != None
        
    def Step(self) -> bool:
        #Инициализация
        if self.State == None:
            self.State = self.InitState

        symbol: str = self.tapeHead.CurrentSymbol
        state: str = self.State
        
        rule: Rule = self.TableRules.Get(symbol, state)
        if rule == None:
            raise TuringMachineException("Recieved rule does not exist")

        self.CurrentSymbol = rule.NewSymbol
        self.State = rule.NewState

        #Направление перехода
        direction: Direction = rule.Direction
        match direction:
            case Direction.left:
                self.Head = self.Head-1
            case Direction.right:
                self.Head = self.Head+1
                
        #Если в стоп состояниях есть текущее, то вернуть False для остановки в непрерывном цикле
        try:
            self.StopStates.index(self.State)
            return False
        except:
            pass
                
        return True
    
    def Stop(self):
        self.State = None
    
    def RunThrough(self):
        while self.Step():
            pass
        
    def __getitem__(self, index: int):
        self.tapeHead[index]
    
    def __setitem__(self, index: int, symbol: str):
        self.tapeHead[index] = symbol



