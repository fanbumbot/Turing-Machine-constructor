import fileinput
from .save import *
from .load import *

class SavingLoadingTuringMachine:
    def __init__(self, machine: ControlledTuringMachine):
        self.machine:ControlledTuringMachine = machine
        self.saving:SavingTuringMachine = SavingTuringMachine(machine)
        self.loading:LoadingTuringMachine = LoadingTuringMachine(machine)
        
    def Save(self, fileName:str):
        self.saving.Save(fileName)
        
    def Load(self, fileName:str):
        self.loading.Load(fileName)