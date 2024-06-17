from ast import ExceptHandler
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from functools import partial

class ExcelLikeTable(GridLayout):
    def __init__(self,
                 callbackButtonColumn = None, callbackButtonRow = None, defaultCellInit = None,
                 callbackAddColumn = None, callbackAddRow = None,
                 callbackAddColumnAfter = None, callbackAddRowAfter = None,
                 callbackRemoveColumn = None, callbackRemoveRow = None,
                 **kwargs):
        super(ExcelLikeTable, self).__init__(**kwargs)

        #Устанавливаем размеры колонок и строк
        self.columnHeight = 100
        self.columnWidth = 330
        self.rowHeight = 100
        self.rowWidth = 130

        #Префикс перед названием
        self.columnPrefix = ""                              #Префикс колонки
        self.rowPrefix = ""                                 #Префкси строки
        
        #Основные служебные поля
        self.columnHeaders = list()                         #Надписи для колонок
        self.rowHeaders  = list()                           #Надписи для строк

        self.columnHeadersID = list()                       #ID каждой колонки
        self.rowHeadersID  = list()                         #ID каждой строки
        self.columnUID = 0                                  #Счётчик ID для колонок
        self.rowUID = 0                                     #Счётчик ID для строк
        
        #В данном GridLayout располагаются названия всех колонок
        self.headerRow = GridLayout(rows = 1, size_hint_x = None, size_hint_y = None, spacing = 3)
        self.headerRow.height = self.columnHeight
        self.headerRow.width = self.rowWidth
        self.headerRow.add_widget(self.CreateFirstCell("Состояние"))#Крайняя левая верхняя ячейка
        self.add_widget(self.headerRow, 1)

        #Привязываем обратные вызовы
        self.callbackButtonColumn = callbackButtonColumn        #Когда произошло нажатие на название колонки
        self.callbackButtonRow = callbackButtonRow              #Когда произошло нажатие на название строки
        self.defaultCellInit = defaultCellInit                  #Создание стандартной ячейки
        self.callbackAddColumn = callbackAddColumn              #Когда добавлена новая колонка
        self.callbackAddRow = callbackAddRow                    #Когда добавлена новая строка
        self.callbackAddColumnAfter = callbackAddColumnAfter    #Когда добавлена новая колонка
        self.callbackAddRowAfter = callbackAddRowAfter          #Когда добавлена новая строка
        self.callbackRemoveColumn = callbackRemoveColumn        #Когда удалена колонка
        self.callbackRemoveRow = callbackRemoveRow              #Когда удалена строка
        
    @property
    def ColumnPrefix(self):
        return self.columnPrefix
    
    @ColumnPrefix.setter
    def ColumnPrefix(self, value):
        self.columnPrefix = value

    @property
    def RowPrefix(self):
        return self.rowPrefix
    
    @RowPrefix.setter
    def RowPrefix(self, value):
        self.rowPrefix = value
        
    #Создание ячейки
    def CreateCell(height, width):
        layout = BoxLayout(orientation = "vertical", size_hint_x = None, size_hint_y = None, height = height, width = width)
        return layout
    
    def CreateTemplatedCell(text, height, width, bind = None):
        layout = ExcelLikeTable.CreateCell(height, width)
        label = Button(text = text, background_normal = "", font_size = 22)
        label.background_color = [0.4, 0.4, 0.4, 1]
        layout.add_widget(label)
        
    #Создание крайней левой верхней ячейки
    def CreateFirstCell(self, value):
        layout = ExcelLikeTable.CreateCell(self.columnHeight, self.rowWidth)
        label = Button(text = value, background_normal = "", font_size = 22)
        label.background_color = [0.4, 0.4, 0.4, 1]
        layout.add_widget(label)
        
        return layout

    #Создание надписи для колонки
    def CreateHeaderColumn(self, column, value):
        button = Button(text = self.columnPrefix + value, background_normal = "", font_size = 22)
        button.background_color = [0.4, 0.4, 0.4, 1]
        button.bind(on_press=partial(self.HandleButtonColumn, self.columnUID))

        #Привязка (U)ID и индекса
        self.columnHeadersID.append([self.columnUID, column])
        self.columnUID += 1
        
        layout = ExcelLikeTable.CreateCell(self.columnHeight, self.columnWidth)
        layout.add_widget(button)
        return layout

    #Создание надписи для строки
    def CreateHeaderRow(self, row, value):
        button = Button(text = self.rowPrefix + value, background_normal = "", font_size = 22)
        button.background_color = [0.4, 0.4, 0.4, 1]
        button.bind(on_press=partial(self.HandleButtonRow, self.rowUID))

        #Привязка (U)ID и индекса
        self.rowHeadersID.append([self.rowUID, row])
        self.rowUID += 1
        
        layout = ExcelLikeTable.CreateCell(self.rowHeight, self.rowWidth)
        layout.add_widget(button)
        return layout

    #Создание ячейки в таблице
    def CreateTableCell(self, column, row):
        layout = ExcelLikeTable.CreateCell(self.rowHeight, self.columnWidth)
        layout.add_widget(self.defaultCellInit(column, row))
        return layout

    '''
    Функции для работы с (U)ID
    '''
    def GetColumnByUID(self, uid):
        for record in self.columnHeadersID:
            if record[0] == uid:
                return record[1]
        return -1

    def GetRowByUID(self, uid):
        for record in self.rowHeadersID:
            if record[0] == uid:
                return record[1]
        return -1

    def GetUIDByColumn(self, column):
        for record in self.columnHeadersID:
            if record[1] == column:
                return record[0]
        return -1

    def GetUIDByRow(self, row):
        for record in self.rowHeadersID:
            if record[1] == row:
                return record[0]
        return -1
    
    #Перестройка индексов под работу в GridLayout
    def IndexInGridLayout(index, length):
        if index == -1:#Если index = -1, то добавить в конец
            index = length
            newIndex = -length
        else:
            newIndex = -index-1
        return [index, newIndex]
    
    def IndexCheck(index, length):
        return not (index < 0 or index >= length)

    def IndexConvertation(self, index, length):
        #Если индекс неверен
        if index != -1 and not ExcelLikeTable.IndexCheck(index, length):
            return None
        return ExcelLikeTable.IndexInGridLayout(index, length)

    #Добавить новую колонку
    def AddColumn(self, name, index = -1):
        
        #Преобразование индекса
        indexes = self.IndexConvertation(index, len(self.headerRow.children))
        if indexes == None:
            return False
        index = indexes[0]
        newIndex = indexes[1]
        
        #Вставляем новое название в список названий колонок
        self.columnHeaders.insert(index, name)
        
        #Добавляем новое название в первую строчку на newIndex место
        self.headerRow.add_widget(self.CreateHeaderColumn(index-1, name), newIndex)
        self.headerRow.width += self.columnWidth

        #Сообщаем о добавлении
        if self.callbackAddColumn != None:
            self.callbackAddColumn(index-1, name)

        #Добавляем недостающие ячейки таблицы
        i = 0
        for row in reversed(self.children):
            if row != self.headerRow:
                rule = self.CreateTableCell(self.columnUID-1, self.GetUIDByRow(i))
                row.add_widget(rule, newIndex)
                i += 1
                
        #Сообщаем о добавлении
        if self.callbackAddColumnAfter != None:
            self.callbackAddColumnAfter(index-1, name)
                
        return True

    #Добавить новую строку
    def AddRow(self, name, index = -1):
        
        #Преобразование индекса
        indexes = self.IndexConvertation(index, len(self.children))
        if indexes == None:
            return False
        index = indexes[0]
        newIndex = indexes[1]
        
        #Вставляем новое название в список названий строк
        self.rowHeaders.insert(index, name)
        
        #Создаём новый экземпляр строки
        layout = GridLayout(rows = 1, size_hint_x = None, size_hint_y = None,
                            spacing = 3)
        layout.height = self.rowHeight
        layout.width = self.rowWidth

        #Добавляем в первую строчку название строки
        layout.add_widget(self.CreateHeaderRow(index-1, name))
        #Добавляем строку на newIndex место
        self.add_widget(layout, newIndex)

        #Сообщаем о добавлении
        if self.callbackAddRow != None:
            self.callbackAddRow(index-1, name)

        #Добавляем в эту строчку все новые ячейки
        i = 0
        for columnHeader in self.columnHeaders:
            layout.add_widget(self.CreateTableCell(self.GetUIDByColumn(i), self.rowUID-1))
            i += 1
            
        #Сообщаем о добавлении
        if self.callbackAddRowAfter != None:
            self.callbackAddRowAfter(index-1, name)

        return True
    
    #Удаляем запись из пула ID и смещаем остальные записи
    def DeleteIndexRecord(pool, index):
        for record in pool:
            if record[1] == index:
                pool.remove(record)
                break
            
        #Уменьшаем все последующие колонки на единицу
        for record in pool:
            if record[1] > index:
                record[1] -= 1

    #Удалить колонку
    def RemoveColumn(self, index):
        if(not ExcelLikeTable.IndexCheck(index, len(self.children[0].children))):
            return False
        
        #Сообщаем об удалении
        if self.callbackRemoveColumn != None:
            self.callbackRemoveColumn(index)
        
        #Удаляем из каждой строки нужную нам колонку
        for row in self.children:
            row.remove_widget(row.children[len(row.children)-index-2])
        #Удаляем название колонки
        del self.columnHeaders[index]
        self.headerRow.width -= self.columnWidth

        ExcelLikeTable.DeleteIndexRecord(self.columnHeadersID, index)
        
        return True

    #Удалить строку
    def RemoveRow(self, index):
        if(not ExcelLikeTable.IndexCheck(index, len(self.children))):
            return False
        
        #Сообщаем об удалении
        if self.callbackRemoveRow != None:
            self.callbackRemoveRow(index)

        #Удаляем строчку по индексу
        self.remove_widget(self.children[len(self.children)-index-2])
        #Удаляем название строчки
        del self.rowHeaders[index]

        ExcelLikeTable.DeleteIndexRecord(self.rowHeadersID, index)
        
        return True

    #Удалить колонку по названию
    def RemoveColumnByName(self, name):
        try:
            index = self.columnHeaders.index(name)
        except:
            return False
        return self.RemoveColumn(index-1)

    #Удалить строку по названию
    def RemoveRowByName(self, name):
        try:
            index = self.rowHeaders.index(name)
        except:
            return False
        return self.RemoveRow(index-1)

    #Найти колонку по индексу (не UID)
    def GetColumn(self, index):
        if index < 0 or index >= len(self.children[0].children):
            return None
        return self.headerRow.children[len(self.headerRow.children)-index-2].children[0]

    #Найти строку по индексу (не UID)
    def GetRow(self, index):
        if index < 0 or index >= len(self.children):
            return None
        return self.children[len(self.children)-index-2].children[-1].children[0]

    #Получить индекс колонки по названию
    def GetColumnIndex(self, name):
        try:
            return self.columnHeaders.index(name)
        except:
            return -1

    #Получить индекс строки по названию
    def GetRowIndex(self, name):
        try:
            return self.rowHeaders.index(name)
        except:
            return -1
        
    #Получить название колонки по индексу
    def GetColumnName(self, index):
        return self.columnHeaders[index]
    
    #Получить название строки по индексу
    def GetRowName(self, index):
        return self.rowHeaders[index]

    #Изменить название колонки по индексу
    def SetColumnName(self, index, name):
        if index < 0 or index >= len(self.children[0].children):
            return False
        self.columnHeaders[index] = name
        self.GetColumn(index).text = self.columnPrefix + name
        return True

    #Изменить название строки по индексу 
    def SetRowName(self, index, name):
        if index < 0 or index >= len(self.children):
            return False
        self.rowHeaders[index] = name
        self.GetRow(index).text = self.rowPrefix + name
        return True

    def CountOfColumns(self):
        return len(self.columnHeaders)
    
    def CountOfRows(self):
        return len(self.rowHeaders)

    def Clear(self):
        self.clear_widgets()

        self.columnHeaders = list()
        self.rowHeaders  = list()

        self.columnHeadersID = list()
        self.rowHeadersID  = list()
        self.columnUID = 0
        self.rowUID = 0
        
        #В данном GridLayout располагаются названия всех колонок
        self.headerRow = GridLayout(rows = 1, size_hint_x = None, size_hint_y = None, spacing = 3)
        self.headerRow.height = self.columnHeight
        self.headerRow.width = self.rowWidth
        self.headerRow.add_widget(self.CreateFirstCell("Состояние"))
        self.add_widget(self.headerRow, 1)

    '''
    Handle'еры как функции обратного вызова от кнопок
    '''
    def HandleButtonColumn(self, columnUID, button):
        if self.callbackButtonColumn != None:
            self.callbackButtonColumn(button, columnUID)

    def HandleButtonRow(self, rowUID, button):
        if self.callbackButtonRow != None:
            self.callbackButtonRow(button, rowUID)

    def HandleButtonCell(self, columnUID, rowUID, button):
        if self.callbackButtonCell != None:
            self.callbackButtonCell(button, columnUID, rowUID)
            