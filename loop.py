import os, urllib, subprocess, pickle

def isindex(i):
    try:
        #check if i is an iterable
        p = i[1]
    except (TypeError, IndexError):
        return False
    else:
        return True

def isValidIndex(key, maxIndex):
    kx, ky = key
    return (0<=kx<=maxIndex and 0<=ky<=maxIndex)

class array(list):

    def __getitem__(self, key):
        if isindex(key):
            return (list.__getitem__(self, key[0]))[key[1]]
        else:
            return list.__getitem__(self, key)

    def __setitem__(self, key, item):
        row = self[key[0]]
        row[key[1]] = item
        list.__setitem__(self, key[0], row)

    def _neighbors(self, key, maxIndex, diagonal=True):
        """
        Legacy 'neighbors' function, retained for historic reasons,
        as well as some interesting twisted code logic used in
        lines 3 and 4 within this function.
        """
        if isindex(key):
            y, x = key
            yOffsets = [-1,0,1][int(y<=0):(int(y<maxIndex)+2)]
            xOffsets = [-1,0,1][int(x<=0):(int(x<maxIndex)+2)]
            nOffsets = [(i,j) for i in yOffsets for j in xOffsets]
            nOffsets.remove((0,0))
            if not diagonal:
                for c in [(i,j) for i in (-1,1) for j in (-1,1)]:
                    try:
                        nOffsets.remove(c)
                    except ValueError:
                        pass
            return ((y+yOff, x+xOff) for yOff,xOff in nOffsets)
        else:
            raise ValueError("Parameter 'key' must be tuple")

    def neighbors(self, key, maxIndex, diagonal=True):
        """
        Returns indices of cells neighboring cell with given key as
        index as a generator.
        'maxIndex' is the maximum valid/possible index of the array
        'diagonal' specifies if the diagonally neighboring cells are to be
                   counted
        """
        if isindex(key):
            y, x = key
            nOffsets = [(i,j) for i in (-1,0,1) for j in (-1,0,1)]
            nOffsets.remove((0,0))
            if not diagonal:
                for c in ((i,j) for i in (-1,1) for j in (-1,1)):
                    nOffsets.remove(c)
            nPos = [(y+yOff, x+xOff) for yOff,xOff in nOffsets if isValidIndex((y+yOff, x+xOff), maxIndex)]
            for c in nPos:
                cy, cx = c[0], c[1]
                if cy<0 or cx<0 or cy>maxIndex or cx>maxIndex:
                    nPos.remove(c)
                '''
                # more legacy twisted logic
                elif diagonal and (cy+cx)%2==0:
                    # if none of cy or cx are 0 then it is one of the diagonal
                    # cells, and hence their sum can only be -1 or 1 which are
                    # not even.
                    nOffsets.remove(c)
                '''
            return (c for c in nPos)
        else:
            raise ValueError("Parameter 'key' must be 2-tuple")


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
    browser = 'chrome'  # default

    # Constants
    DOT = '9'
    NOLINE = '8'
    LINE = '7'
    CROSS = '6'
    NUMBER = '5'
    constants = dict(zip([DOT,NOLINE,CROSS], ['.',' ','x']))

    # ASCII box-drawing lines
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
        self.lineArray = array(tempArray)
        # path where this file is stored, used in 'view' function
        self.path = __file__

    def display(self, outArray = False):
        if outArray:  # output required in array format
            a = []
        else:         # output required in string format
            s = ""
        seperator = "" if outArray else " "
        for row in self.lineArray:
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
                    self.lineArray[2*y + 1, 2*x + 1] = str(cell)
                else:
                    self.lineArray[2*y + 1, 2*x + 1] = ' '

    def inputNum(self):
        """
        Valid input format (line by line)

        ..33323
        3120..3
        122..22
        ....2..
        ..1.322
        2.2...2
        ..32322

        """
        tempArray = []
        s = ""
        for i in range(7):
            s = raw_input("Row #{}".format(i))
            a = [(int(n) if n!='.' else (-1)) for n in s]
            tempArray.append(a)
        self.inject(tempArray)

    def view(self):
        b = Board.browser
        if self.numArray:
            param = str(self.numArray).replace(' ','')
        else:
            param = ""
        htmlFile = self.path.replace('\\','/').replace('.py', '.html')
        htmlFile = urllib.quote(htmlFile, safe=":/")
        print "HTML", htmlFile
        query = "?" + urllib.urlencode([('param', param)])
        commandStr = "start {} file:///".format(b) + htmlFile + query
        print commandStr
        subprocess.call(commandStr, shell=True)


class Solver(object):

    # Constants
    DOT = '9'
    NOLINE = '8'
    LINE = '7'
    CROSS = '6'
    NUMBER = '5'
    constants = dict(zip([DOT,NOLINE,CROSS], ['.',' ','x']))

    def __init__(self, numArray):
        """
        'numArray' must be an array of just the numbers.
        """
        self.numArray = array(numArray)
        self.puzzle = Board()
        self.puzzle.inject(self.numArray)
        self.maxIndex = 14

    def iterCells(self):
        """
        Returns generator to iterate over all cell indices
        """
        return ((2*i+1, 2*j+1) for i in range(7) for j in range(7))

    def iterDots(self):
        """
        Returns generator to iterate over all dots (points where
        lines meet).
        """
        return ((2*i, 2*j) for i in range(8) for j in range(8))

    def basicElim(self):
        """
        Works on 2 basic rules
        1) If a numbered cell is surrounded by the same number of lines,
           the remaining positions surrounding it must all be 'crosses'
        2) If a numbered cell has just the same number of positions
           left and with the others being 'crosses', the remaining positions
           surrounding it must all be 'lines'.
        """
        a = self.puzzle.lineArray
        for c in self.iterCells():
            if a[c]!=' ':
                if a[c] == '0':
                    pass
                num = int(a[c])
                crosses, lines, blanks = [], [], []
                for n in a.neighbors(c, self.maxIndex, False):
                    if a[n] == Solver.CROSS:
                        crosses.append(n)
                    elif a[n] == Solver.LINE:
                        lines.append(n)
                    elif a[n] == Solver.NOLINE:
                        blanks.append(n)
                if len(lines) == num:
                    print "Found completed lines: {}".format(blanks)
                    for toCross in blanks:
                        a[toCross] = Solver.CROSS
                elif len(crosses) == (4 - num):
                    print "Found completed crosses {}".format(blanks)
                    for toLine in blanks:
                        a[toLine] = Solver.LINE

    def dotElim(self):
        """
        Works on 1 basic rule
        1) The number of lines around a dot (4 directions) must be 0 or 2

        Implications
        1) If there are already 2 lines (maximum allowed) surrounding a dot the
           remaining positions must all be crosses
        2) If all the surrounding positions of a 'dot' (possible lines) except
           one are filled with crosses then the remaining position must also
           be filled with a cross.
        3) If only one line is filled in and all except one of the remaining are
           crosses the remaining position must be a line.
        """
        a = self.puzzle.lineArray
        for dot in self.iterDots():
            crosses, lines, blanks = [], [], []
            for l in a.neighbors(dot, self.maxIndex, False):
                if a[l] == Solver.LINE:
                    lines.append(l)
                elif a[l] == Solver.CROSS:
                    crosses.append(l)
                else:
                    blanks.append(l)
            if len(lines) == 2:
                print "Found 2 line pair at {}".format(l)
                for toCross in blanks:
                    a[toCross] = Solver.CROSS
            t = len(lines) + len(crosses) + len(blanks)  # total possible lines
            if len(blanks)==1:
                if len(crosses) == t-1:  # number of crosses is 1 less than 't'
                    a[blanks[0]] = Solver.CROSS
                    print "Found cross compulsion at {}".format(l)
                if len(lines) == 1:      # one blank, one line, remaining cross
                    a[blanks[0]] = Solver.LINE
                    print "Found line compulsion at {}".format(l)



puzzles = []

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


def main():
    b = Board()
    #for p in solution1: b.lines[p] = Board.LINE
    b.inject(puzzles[0])
    #print l
    b.pretty()
    return b

def config():
    try:
        f = open(__file__.replace('.py','.config'), "r")
    except IOError:
        choice = input("""
        Which browser would you like to be associated with this file ?
        1. Google Chrome
        2. Mozilla Firefox
        3. Opera
        4. Internet Explorer

        Enter 1, 2, 3, or 4:
        """)
        browsers = ["chrome", "firefox", "opera", "iexplore"]
        Board.browser = browsers[choice-1]
        with open(__file__.replace('.py','.config'), "w") as f:
            f.write(str([Board.browser]))
    else:
        Board.browser = eval(f.readline())[0]
        f.close()
    with open(__file__.replace('loop.py','puzzles.pkl'),'r') as f:
        global puzzles
        puzzles = pickle.load(f)

def addToPuzzles():
    b.inputNum()
    puzzles.append(b.numArray)
    with open(__file__.replace('loop.py','puzzles.pkl'),'w') as f:
        pickle.dump(puzzles, f)

if __name__ == "__main__":
    #print os.path.realpath(__file__)
    config()
    b = main()
    n = b.numArray
    #addToPuzzles()
    s = Solver(puzzles[8])
    s.basicElim()
    s.puzzle.pretty()
    s.basicElim()
    s.puzzle.pretty()
    s.basicElim()
    s.puzzle.pretty()
    s.dotElim()
    s.puzzle.pretty()



'''
# This array has been 'pickled' and dumped into the file 'puzzles.pkl'
# which is loaded by the config function into the variable 'puzzles'
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
                  [-1, 2,-1,-1, 2, 3,-1]]),
           array([[-1,-1,-1,-1, 2, 2, 2],
                  [ 2,-1,-1, 2,-1,-1,-1],
                  [ 2, 2,-1, 2, 1, 1,-1],
                  [ 1, 2,-1, 3, 2,-1, 2],
                  [-1, 3,-1, 3, 0,-1, 2],
                  [-1, 2, 2, 3, 2,-1,-1],
                  [ 2, 1,-1, 2,-1,-1, 3]]),
           array([[-1, 2,-1, 3, 3, 3,-1],  # good one
                  [-1, 3, 2, 2,-1, 0, 3],
                  [-1,-1,-1, 1,-1,-1, 3],
                  [-1,-1,-1,-1,-1,-1, 2],
                  [-1, 2, 1,-1,-1,-1, 3],
                  [-1,-1, 1,-1,-1,-1, 2],
                  [-1,-1, 2, 3, 1,-1,-1]]),
           array([[-1, 1,-1,-1,-1,-1, 3],
                  [-1,-1,-1,-1,-1,-1, 2],
                  [ 3,-1, 3,-1,-1,-1, 3],
                  [ 3,-1, 2, 1, 3, 0, 3],
                  [ 2,-1,-1,-1,-1,-1, 3],
                  [ 3, 3, 3, 3, 2,-1, 2],
                  [-1,-1,-1,-1,-1, 3, 3]]),
           array([[-1, 2, 3, 1,-1,-1,-1],
                  [-1,-1,-1,-1, 3,-1, 2],
                  [ 2, 2, 2, 0, 3, 2, 2],
                  [-1, 2,-1, 2, 3, 2, 2],
                  [ 3, 1,-1,-1, 2, 2,-1],
                  [ 3, 2,-1,-1, 3,-1,-1],
                  [-1,-1,-1,-1, 3,-1, 3]])
           array([[ 3, 3, 2, 3, 1,-1, 3],  # with the flow
                  [ 2,-1, 2,-1, 2, 2,-1],
                  [ 3,-1,-1,-1,-1, 2, 2],
                  [ 3,-1, 1,-1, 2,-1, 1],
                  [ 2, 3,-1,-1, 2,-1,-1],
                  [ 2, 2, 0,-1,-1,-1, 1],
                  [-1, 3, 3, 3, 3,-1,-1]])]
'''