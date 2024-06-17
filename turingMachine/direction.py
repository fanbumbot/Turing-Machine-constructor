import enum

class Direction(enum.Enum):
    left = -1
    halt = 0
    right = 1
    
def GetNameDirection(direction: Direction) -> str:
    match(direction):
        case Direction.left:
            return "Влево"
        case Direction.right:
            return "Вправо"
        case Direction.halt:
            return "На месте"




