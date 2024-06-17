from .tape import Tape

class TapeIndexed(Tape):
    def __init__(self, emptySymbol:str = "") -> None:
        super().__init__(emptySymbol)
        self.offset:int = 0
        
    @property
    def Offset(self) -> int:
        return self.offset
    
    @Offset.setter
    def Offset(self, offset: int):
        self.offset:int = offset

    def GetRealIndex(self, index:int):
        return index+self.offset
    
    #index - индекс
    #realIndex - действительный индекс
    def TryPut(self, index:int):
        realIndex:int = self.GetRealIndex(index)
        if realIndex < 0:
            self.offset = -index
            #Добавляем недостающие элементы в начало
            self.tapeList = ([self.emptySymbol] * (-realIndex)) + self.tapeList
            return 0
        elif realIndex >= self.Length:
            #Добавляем недостающие элементы в конец
            self.tapeList = self.tapeList + ([self.emptySymbol] * (realIndex-self.Length+1))
            
        return realIndex
        
    def __getitem__(self, index: int):
        if not isinstance(index, int):
            raise TypeError("Индекс - целое число")
        realIndex = self.TryPut(index)
        return self.tapeList[realIndex]
    
    def __setitem__(self, index: int, symbol: str):
        if not isinstance(index, int):
            raise TypeError("Индекс - целое число")
        
        realIndex = self.TryPut(index)
        self.tapeList[realIndex] = symbol