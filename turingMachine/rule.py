from .direction import Direction

class Rule:
    def __init__(self, newState: str = "", newSymbol: str = "", direction: Direction = Direction.halt):
        self.newState = newState  #Новое состояние
        self.newSymbol = newSymbol  #Новый символ
        self.direction = direction  #Направление сдвига
        
    @property
    def NewState(self) -> str:
        return self.newState
    
    @NewState.setter
    def NewState(self, state: str):
        self.newState = state
        
    @property
    def NewSymbol(self) -> str:
        return self.newSymbol
    
    @NewSymbol.setter
    def NewSymbol(self, symbol: str):
        self.newSymbol = symbol
        
    @property
    def Direction(self) -> str:
        return self.direction
    
    @Direction.setter
    def Direction(self, direction: 'Direction'):
        self.direction = direction
        
    def Copy(self):
        return Rule(self.newState, self.newSymbol, self.direction)



