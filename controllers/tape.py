from tape.tapeHead import TapeHead
from gui.popup import *

from kivy.uix.textinput import TextInput

from functools import partial

class TapeController:
    def __init__(self, tape = None):
        self.windowSize = 7
        
        self.tape = tape
        self.tapeHead = TapeHead()
        
        self.Head = 0

        self.tapeInputCells = list()
        
        #�������� ����� �� ������� ������
        self.tape.ids["TapeLeft"].children[1].on_press = self.OnLeft
        self.tape.ids["TapeRight"].children[1].on_press = self.OnRight

        #��������� ������ ��� ����� ��������
        index = 0
        for tapeCell in reversed(tape.children[1].children):
            textInput = tapeCell.children[1]
            self.tapeInputCells.append(textInput)
            textInput.bind(text=partial(self.OnText, index))
            textInput.bind(focus=partial(self.OnCellFocused))
            index += 1
            
        self.Update()

    @property
    def EmptySymbol(self) -> str:
        return self.tapeHead.EmptySymbol 
    
    @EmptySymbol.setter
    def EmptySymbol(self, symbol: str):
        self.tapeHead.EmptySymbol = symbol

        for tapeCell in reversed(self.tape.children[1].children):
            textInput = tapeCell.children[1]
            textInput.hint_text = self.EmptySymbol
            
        self.Update()
            
    @property
    def Head(self) -> str:
        return self.tapeHead.Head
    
    @Head.setter
    def Head(self, index: int):
        self.tapeHead.Head = index
        self.Update()
        
    @property
    def WindowSize(self) -> str:
        return self.windowSize

    #����� �� ������ ������ ��� ��������� ���������� � ������
    def OnCellFocused(self, instance, value):
        if value:
            SetHelpState(IDH_TOPIC_RABOTA_S_LENTOJ)
        else:
            SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)

    #����� � ������ ���-�� �������. ����������� �� ���� ������ �������
    def OnText(self, index, instance, text):
        if len(text) > 1:
            instance.text = instance.text[0]
            return
        if len(text) != 0 and (text[0] == '\n' or text[0] == '\r' or text[0] == '\t' or text[0] == '\b' or text[0] == ' '):
            instance.text = ""
            return

        tapeIndex = self.CellIndexToHeadIndex(index)
        if instance.text == "":
            self.tapeHead[tapeIndex] = self.EmptySymbol
        else:
            self.tapeHead[tapeIndex] = instance.text

    #����� ���� ������ ������ ������ �����
    def OnLeft(self):
        self.Head = self.Head-1
    
    #����� ���� ������ ������ ������ ������
    def OnRight(self):
        self.Head = self.Head+1
        
    #������ ������ ����������� ������
    def GetCenterCellIndex(self):
        return self.windowSize//2
    
    #������ ������ ����������� ������
    def CellIndexToHeadIndex(self, index):
        return self.tapeHead.Head-self.GetCenterCellIndex()+index
        
    #�������� ����������� �����
    def Update(self):
        index = self.CellIndexToHeadIndex(0)#�������� ������ ������� �������� �������
        for i in range(self.windowSize):
            #���������� �������
            self.tape.children[1].children[self.windowSize-1-i].children[0].text = str(index)
            #���������� ��������
            if self.tapeHead[index] == self.EmptySymbol:
                self.tape.children[1].children[self.windowSize-1-i].children[1].text = ""
            else:
                self.tape.children[1].children[self.windowSize-1-i].children[1].text = self.tapeHead[index]
            index += 1