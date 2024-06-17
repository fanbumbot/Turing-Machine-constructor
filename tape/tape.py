class Tape:
    def __init__(self, emptySymbol:str = "") -> None:
        self.emptySymbol:str = emptySymbol
        
        self.tapeList:list = [self.emptySymbol]

    @property
    def Length(self) -> int:
        return len(self.tapeList)

    @property
    def EmptySymbol(self) -> str:
        return self.emptySymbol
    
    @EmptySymbol.setter
    def EmptySymbol(self, symbol: str):
        #Заменяем все найденные пустые символы на новые на ленте
        for i in range(len(self.tapeList)):
            if self.tapeList[i] == self.emptySymbol:
                self.tapeList[i] = symbol
        self.emptySymbol = symbol
        
    def Clear(self):
        self.tapeList:list = [self.emptySymbol]