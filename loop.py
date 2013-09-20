# Constants
DOT = '9'
NOLINE = '8'
LINE = '7'
CROSS = '6'
NUMBER = '5'
constants = dict(zip([DOT,NOLINE,CROSS], ['.',' ','x']))

def log(m):
    global DEBUG_MODE
    if DEBUG_MODE: print m

def isindex(i):
    try:
        #check if i is an iterable
        p = i[1]
    except (TypeError, IndexError):
        return False
    else:
        return True

class array(list):

    def __getitem__(self, key):
        if isindex(key):
            log("Iterator passed to numArray")
            return (list.__getitem__(self, key[0]))[key[1]]
        else:
            log("No iterator passed to numArray")
            return list.__getitem__(self, key)

    def __setitem__(self, key, item):
        row = self[key[0]]
        row[key[1]] = item
        list.__setitem__(self, key[0], row)

class lineArray(object):
    """Class for maintaining state of individual lines in the
    puzzle. Uses array of larger dimension to accomodate both
    horizontal and vertical lines in a single array.

    States:
    9    Represents dot("."), i.e. a cell where no lines are
         physically possible.
    8    Represents unfilled line (may be horizontal or vertical)
    7    Represents filled in lines (may be horizontal or vertical)
    6    Represents cross("x"), i.e a cell where no lines are
         logically possible
    Any other number represents numeral in the puzzle
    """
    order = 7
    def __init__(self):
        order, tempArray = lineArray.order, []
        for i in range(2*order + 1):
            if i % 2 == 0:  # horizontal lines row
                tempLine = []
                for n in range(2*order + 1):
                    tempLine.append((NOLINE if n%2 else DOT))
                tempArray.append(tempLine)
            else:           # vertical lines row
                tempLine = []
                for n in range(2*order + 1):
                    tempLine.append(NUMBER if n%2 else NOLINE)
                tempArray.append(tempLine)
        self.lines = array(tempArray)

    def __str__(self):
        s = ""
        for row in self.lines:
            line = " ".join([constants.get(i,i) for i in row])
            '''
            line = line.replace('-1','.')
            line = line.replace('0',' ')
            line = line.replace('2','x').replace('3',' ')
            '''
            if row[0] == -1:    # horizontal lines row
                line = line.replace('1', '_')
            else:              # vertical lines row
                line = line.replace('1', '|')
            s += line + '\n'
        return s

class loopBoard(object):

    order = 7

    def __init__(self, numArray):
        self.numArray = array(numArray)

puzzle1 = [(0,1),(0,3),(0,7),(0,13),
           (1,0),(1,4),(1,6),(1,8),(1,12),(1,14),
           (2,1),(2,5),(2,9),
           (3,2),(3,10),(3,12),(3,14),
           (4,1),(4,5),(4,7),(4,9),
           (5,0),(5,4),(5,12),(5,14),
           (6,1),(6,5),(6,7),(6,9),(6,11),
           (7,2),(7,14),
           (8,3),(8,5),(8,7),(8,11),(8,13),
           (9,8),(9,10),
           (10,1),(10,3),(10,5),(10,7),(10,11),(10,13),
           (11,0),(11,14),
           (12,3),(12,7),(12,9),
           (13,0),(13,2),(13,4),(13,6),(13,8),(13,10),(13,12),(13,14),
           (14,1),(14,5),(14,9),(14,13)]

if __name__ == "__main__":
    DEBUG_MODE = False
    l = lineArray()
    a = l.lines
    print '\n', l, '\n'
    for p in puzzle1: a[p] = LINE
    print '\n', l, '\n'



