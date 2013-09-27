import os

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

class Board(object):
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

    # Constants
    DOT = '9'
    NOLINE = '8'
    LINE = '7'
    CROSS = '6'
    NUMBER = '5'
    constants = dict(zip([DOT,NOLINE,CROSS], ['.',' ','x']))

    # ASCII art lines
    VERTICAL     = chr(186)
    HORIZONTAL   = chr(205)
    connectors = {"LEFT_BOTTOM" : chr(187),
                  "LEFT_TOP"    : chr(188),
                  "RIGHT_TOP"   : chr(200),
                  "RIGHT_BOTTOM": chr(201)}

    def __init__(self):
        order, tempArray = Board.order, []
        for i in range(2*order + 1):
            if i % 2 == 0:  # horizontal lines row
                tempLine = []
                for n in range(2*order + 1):
                    tempLine.append((Board.NOLINE if n%2 else Board.DOT))
                tempArray.append(tempLine)
            else:           # vertical lines row
                tempLine = []
                for n in range(2*order + 1):
                    tempLine.append(Board.NUMBER if n%2 else Board.NOLINE)
                tempArray.append(tempLine)
        self.lines = array(tempArray)

    def display(self, outArray = False):
        if outArray:  # output required in array format
            a = []
        else:         # output required in string format
            s = ""
        seperator = "" if outArray else " "
        for row in self.lines:
            line = seperator.join([Board.constants.get(i,i) for i in row])
            if row[0] == Board.DOT:    # horizontal lines row
                #line = line.replace(LINE, '_')
                line = line.replace(Board.LINE, Board.HORIZONTAL)
            else:              # vertical lines row
                #line = line.replace(LINE, '|')
                line = line.replace(Board.LINE, Board.VERTICAL)
            if outArray: # output required in array format
                a.append(list(line))
            else:        # output required in string format
                s += line + '\n'
        return array(a) if outArray else s

    def __str__(self):
        return self.display(False)

    def isValid(self, y, x):
        ymax = xmax = 2*Board.order
        return all((y>=0, x>=0, y<=ymax, x<=xmax))

    def pos(self, y, x, optimal = False):
        """
        Diagram for reference in comments

         x (a) x (b) x
        (c) . [ ]   (d)
         x (e) x (f) x

        Square brackets show current cell
        Round brackets show cells to check

        'optimal' mode returns only the cell to the left in
        the same row to avoid redundancy while processing all
        the cells in left to right and top to bottom fashion.
        """
        p = [(y-1,x-1), (y-1,x+1),  # (a), (b)
             (y  ,x-2), (y,  x+2),  # (c), (d)
             (y+1,x-1), (y+1,x+1)]  # (e), (f)
        if optimal: p.remove((y, x+2))
        return [(a,b) for a,b in p if self.isValid(a, b)]

    def pretty(self):
        lines = self.display(outArray = True)  # array format output
        j = Board.connectors
        for y, row in enumerate(lines):
            if row[0] == Board.constants[Board.DOT]: # horizontal lines row
                for x, cell in enumerate(row):
                    if cell == Board.HORIZONTAL:
                        p = self.pos(y, x, True)
                        connected = 0
                        for c in p:
                            if lines[c] == Board.HORIZONTAL:
                                lines[c[0], (c[1]+x)/2] = Board.HORIZONTAL
                                connected += 1
                            elif lines[c] == Board.VERTICAL:
                                place = ["RIGHT_","LEFT_"][int(c[1] > x)]
                                place += ["TOP","BOTTOM"][int(c[0] > y)]
                                lines[y, c[1]] = j[place]
                                connected += 1
                            if connected == 2:
                                break
            else: # vertical lines row
                for x, cell in enumerate(row):
                    if cell == Board.VERTICAL:
                        if y > 2 and lines[y-2, x] == Board.VERTICAL:
                            lines[y-1, x] = Board.VERTICAL
        s = "\n".join([" ".join(line) for line in lines])
        h = Board.HORIZONTAL
        s = s.replace(' ' + h + ' ', h*3) # " _ " => '___'
        print s

    def inject(self, numArray):
        self.numArray = numArray
        for y, row in enumerate(numArray):
            for x, cell in enumerate(row):
                if cell != -1:
                    self.lines[2*y + 1, 2*x + 1] = str(cell)
                else:
                    self.lines[2*y + 1, 2*x + 1] = ' '

    def edit(self):
        os.startfile(r"H:\My DOcs\Portable Python\Scripts\GUI\Loop\loop.html")
        a = eval(raw_input("Array: \n"))
        if a: self.numArray = a

puzzles = [array([[ 3, 2, 3, 3, 2, 1, 3],
                  [ 3,-1, 2,-1,-1,-1, 2],
                  [ 3,-1, 3, 2, 2, 2, 2],
                  [-1,-1,-1,-1,-1, 2, 2],
                  [ 1, 2,-1,-1, 2,-1, 2],
                  [-1, 2,-1,-1, 0, 2, 2],
                  [-1, 3,-1, 3, 3, 3,-1]]),
           array([[-1,-1, 3, 3, 3, 2, 3],
                  [ 3, 1, 2, 0,-1,-1, 3],
                  [ 1, 2, 2,-1,-1, 2, 2],
                  [-1,-1,-1,-1, 2,-1,-1],
                  [-1,-1, 1,-1, 3, 2, 2],
                  [ 2,-1, 2,-1,-1,-1, 2],
                  [-1,-1, 3, 2, 3, 2, 2]]),
           array([[ 3,-1,-1, 3, 1, 2,-1],
                  [-1,-1,-1, 1,-1,-1,-1],
                  [ 2,-1,-1, 2, 2, 1,-1],
                  [-1, 3, 0, 2, 2,-1,-1],
                  [ 2,-1, 2,-1,-1,-1,-1],
                  [ 3,-1,-1,-1, 2,-1,-1],
                  [-1, 2, 1, 2,-1,-1,-1]]),
           array([[ 2,-1,-1, 1, 2, 2, 2],
                  [-1, 2,-1, 2,-1,-1,-1],
                  [-1, 2, 3, 0,-1,-1,-1],
                  [-1, 2,-1,-1,-1,-1,-1],
                  [ 1, 3,-1,-1, 2,-1, 2],
                  [ 2, 2, 1, 3,-1,-1, 2],
                  [-1, 2,-1,-1, 2, 3,-1]])]

solution1 = [(0,1),(0,3),(0,7),(0,13),
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
           (12,3),(12,7),(12,11),
           (13,0),(13,2),(13,4),(13,6),(13,8),(13,10),(13,12),(13,14),
           (14,1),(14,5),(14,9),(14,13)]
if __name__ == "__main__":
    DEBUG_MODE = False
    b = Board()
    #for p in puzzle1: b.lines[p] = Board.LINE
    b.inject(puzzles[1])
    #print l
    b.pretty()





