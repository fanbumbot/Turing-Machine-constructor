from ast import Assert
import unittest

from tape.tape import Tape
from tape.tapeIndexed import TapeIndexed
from tape.tapeHead import TapeHead

class test_tape(unittest.TestCase):
    def test_constructor(self):
        tape = Tape("")

        self.assertEqual(tape.tapeList, [""])
        
    def test_emptySymbol(self):
        tape = Tape()
        
        tape.emptySymbol = "1"
        tape.tapeList = ['1', '2', '1', '1', '5']

        tape.EmptySymbol = "0"

        self.assertEqual(tape.tapeList, ['0', '2', '0', '0', '5'])
        
    def test_length(self):
        tape = Tape()
        
        tape.tapeList = ['1', '2', '1', '1', '5']

        self.assertEqual(tape.Length, 5)
        
class test_tapeIndexed(unittest.TestCase):
    def test_constructor(self):
        tape = TapeIndexed("")
        self.assertEqual(tape.tapeList, [""])
        
    def test_tryPut1(self):
        tape = TapeIndexed("")
        tape[0] = "A"
        
        tape.TryPut(-3)

        self.assertEqual(tape.tapeList, ["", "", "", "A"])
        
    def test_tryPut2(self):
        tape = TapeIndexed("")
        tape[0] = "A"
        
        tape.TryPut(3)

        self.assertEqual(tape.tapeList, ["A", "", "", ""])
        
    def test_tryPut3(self):
        tape = TapeIndexed("")
        tape[0] = "A"
        
        tape.TryPut(3)
        tape.TryPut(5)

        self.assertEqual(tape.tapeList, ["A", "", "", "", "", ""])
        
    def test_tryPut4(self):
        tape = TapeIndexed("")
        tape[0] = "A"
        
        tape.TryPut(-3)
        tape.TryPut(-5)

        self.assertEqual(tape.tapeList, ["", "", "", "", "", "A"])
        
    def test_tryPut5(self):
        tape = TapeIndexed("")
        tape[0] = "A"
        
        tape.TryPut(3)
        tape.TryPut(5)
        
        tape.TryPut(-3)
        tape.TryPut(-5)

        self.assertEqual(tape.tapeList, ["", "", "", "", "", "A", "", "", "", "", ""])
        
    def test_get1(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1

        self.assertEqual(tape[0], "0")
        self.assertEqual(tape[-1], "-1")
        self.assertEqual(tape[1], "1")
     
    def test_get2(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1
        
        self.assertEqual(tape[-2], "")
        self.assertEqual(tape.tapeList, ["", "-1", "0", "1"])
        self.assertEqual(tape.offset, 2)

    def test_get3(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1
        
        with self.assertRaises(TypeError):
            tape['A']
            
    def test_set1(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1

        tape[0] = "2"

        self.assertEqual(tape.tapeList, ["-1", "2", "1"])
        
    def test_set2(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1

        tape[-2] = "2"

        self.assertEqual(tape.tapeList, ["2", "-1", "0", "1"])
        self.assertEqual(tape.offset, 2)
        
    def test_set3(self):
        tape = TapeIndexed("")
        tape.tapeList = ["-1", "0", "1"]
        tape.offset = 1

        tape[-2] = 2

        with self.assertRaises(TypeError):
            tape['A'] = "A"
            
class test_tapeHead(unittest.TestCase):
    def test_constructor(self):
        tape = TapeHead("")
        self.assertEqual(tape.tapeList, [""])
        
    def test_headSet(self):
        tape = TapeHead("")
        tape[0] = "0"

        tape.Head = -3
        
        self.assertEqual(tape.tapeList, ["", "", "", "0"])
        self.assertEqual(tape.Head, -3)
        
    def test_currentSymbolSet(self):
        tape = TapeHead("")

        tape.CurrentSymbol = "A"
        tape.Head += 2
        tape.CurrentSymbol = "B"
        
        self.assertEqual(tape.tapeList, ["A", "", "B"])
        
    def test_currentSymbolGet(self):
        tape = TapeHead("")

        tape.CurrentSymbol = "A"
        tape.Head += 2
        tape.CurrentSymbol = "B"
        
        self.assertEqual(tape.CurrentSymbol, "B")
        tape.Head += 1
        self.assertEqual(tape.CurrentSymbol, "")
        self.assertEqual(tape.tapeList, ["A", "", "B", ""])
        
if __name__ == '__main__':
    unittest.main()