from .tapeIndexed import TapeIndexed

class TapeHead(TapeIndexed):
    def __init__(self, emptySymbol:str = "") -> None:
        super().__init__(emptySymbol)
        self.head = 0
        
    @property
    def Head(self) -> int:
        return self.head
    
    @Head.setter
    def Head(self, index: int):
        self.TryPut(index)
        self.head:int = index
        
    @property
    def CurrentSymbol(self) -> str:
        self.TryPut(self.Head)
        return self[self.Head]
    
    @CurrentSymbol.setter
    def CurrentSymbol(self, symbol: str):
        self.TryPut(self.Head)
        self[self.Head] = symbol
