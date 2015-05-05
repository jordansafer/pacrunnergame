import random
import math
import string
from Tkinter import *
from animationClass import EventBasedAnimationClass
import os

# empty class to be used for data management in other classes
class Struct(object): pass

# First I need to randomly generate a list of streets: I'll use a dictionary
#  with node info for each intersection, if the node is already saved on a
# reset the dictionary will not add information for the point
class PacmanMap(object):

    # create a new game map for playing pacman
    def __init__(self, point, size, scale, game):
        self.scalingFactor = scale
        self.grid = dict()
        self.streetNumber = 0
        self.size = size
        self.makeNavigationDictionary()
        self.makeGrid(point, game)

    # initializes a dictionary to keep directions linked to shifts
    def makeNavigationDictionary(self):
        directionLabels = ["N","S","W","E","NW","SE","NE","SW"]
        rowColDirections = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1),
                                            (1, 1), (-1, 1), (1, -1)]
        xyDirections = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1),
                                            (1, 1), (1, -1), (-1, 1)]
        reverseDirection = ["S","N","E","W","SE","NW","SW","NE"]
        self.navigationDictionary = dict()
        for i in xrange(len(directionLabels)):
            label = directionLabels[i]
            (rowCol, coordinate) = (rowColDirections[i], xyDirections[i])
            flip = reverseDirection[i]
            self.navigationDictionary[label] = (rowCol, coordinate, flip)

    # creates a grid of intersections, stored in a dictionary
    def makeGrid(self, point, game):
        startPoint = (point[0] - self.size / 2, point[1] - self.size / 2)
        for i in xrange(self.size): #intersection points going down (rows)
            for j in xrange(self.size):
                currentPoint = (startPoint[0] + i, startPoint[1] + j)
                if currentPoint not in self.grid:
                    connections = self.getConnections(currentPoint, game)
                    self.grid[currentPoint] = connections

    # fills a dictionary with the "street names" going in each direction
    # from an intersection, two intersections are connected if they share
    # a street (the street passing through both has the same "name")
    def getConnections(self, newPoint, game):
        connectionList = dict()
        directions = self.navigationDictionary
        for direction in directions:
            shift = directions[direction][0] # row col shift in 0, xy in 1
            oldPoint = (newPoint[0] + shift[0], newPoint[1] + shift[1])
            if oldPoint in self.grid and self.willExist(shift, newPoint, game):
                oldConnections = self.grid[oldPoint]
                reverseDirection = directions[direction][2] # reverse key
                connectionList[direction] = oldConnections[reverseDirection]
            else:
                connectionList[direction] = str(self.streetNumber)
                self.streetNumber += 1
        return connectionList

    # decides whether a street will exist based on a premade tile or
    # a random choice
    def willExist(self, direction, point, game):
        if game.howMapIsMade == "tiled":
            return self.userSelectedExistence(direction, point, game)
        if abs(direction[0] + direction[1]) == 1:
            return bool(random.randint(0,4)) # True 4/5 times
        else:
            return not bool(random.randint(0,4)) # True 1/5 times

    # determines whether the key in for a user made tile indicates that
    # a connection exists between 2 intersections
    def userSelectedExistence(self, direction, point, game):
        baseKey = game.keyTile
        nav = game.reverseNavigationDictionary
        newRow = point[0] % len(baseKey)
        newCol = point[1] % len(baseKey[0])
        label = nav[direction]
        return baseKey[newRow][newCol][label]

    # draws the designated lines to the grid
    def draw(self, canvas, center, game):
        self.getLines(center, game)
        self.lineWidth = 2
        for values in self.linesToDraw:
            canvas.create_line(values.p1, values.p2, width = self.lineWidth,
                            fill = values.color)

    # determines which lines need to be drawn (based on proximity to pacman)
    def getLines(self, center, game):
        self.nonVisitedLines = []
        self.visitedLines = []
        cPoint = (center[1]/self.scalingFactor, center[0]/self.scalingFactor)
        startPoint = (cPoint[0] - self.size / 2, cPoint[1] - self.size / 2)
        drawDirections = ["N", "W", "NW", "NE"]
        for i in xrange(self.size):
            for j in xrange(self.size):
                key = (i + startPoint[0], j + startPoint[1])
                for direction in drawDirections:
                    self.manageLines(direction, key, center, game)
        self.linesToDraw = self.nonVisitedLines + self.visitedLines

    # determines coordinates of lines and whether they have been visited
    def manageLines(self, direction, key, center, game):
        directions = self.navigationDictionary
        shift = directions[direction][1] # this time, an xy shift
        if self.hasConnection(key, direction):
            (row, col) = (key[0], key[1])
            x0 = self.findVisualCoordinate(col, center[0], game.width)
            y0 = self.findVisualCoordinate(row, center[1], game.height)
            x1 = x0 + self.scalingFactor * shift[0]
            y1 = y0 + self.scalingFactor * shift[1]
            line = "%d.%d_%d.%d" % (row, col, row + shift[1], col + shift[0])
            if self.visitedContains(line, game):
                self.addLineValues((x0, y0), (x1, y1), "orange",
                                                    self.visitedLines)
            else:
                self.addLineValues((x0, y0), (x1, y1), "white",
                                                self.nonVisitedLines)

    # creates a struct with information about each line stored
    def addLineValues(self, p1, p2, color, list):
        values = Struct()
        values.p1 = p1
        values.p2 = p2
        values.color = color
        list.append(values)

    # checks whether a line in the set of visited lines
    def visitedContains(self, line, game):
        middle = self.findMiddle(line)
        reverseLine = line[middle + 1:] + "_" + line[:middle]
        return line in game.pacman.visitedLines or \
                reverseLine in game.pacman.visitedLines

    # finds the middle of a label for a line in the set of visited lines
    def findMiddle(self, line):
        dashSpot = line.find("_")
        return dashSpot

    # returns true if two intersections have a connection in the grid
    def hasConnection(self, key, direction):
        directions = self.navigationDictionary
        gridDirection = directions[direction][0]
        reverseDirection = directions[direction][2]
        keyStreetForDirection = self.grid[key][direction]
        nextPoint = (key[0] + gridDirection[0], key[1] + gridDirection[1])
        if nextPoint not in self.grid: return False
        nextStreetInDirection = self.grid[nextPoint][reverseDirection]
        return keyStreetForDirection == nextStreetInDirection

    # finds the visual coordinates for a point in the grid based on pacman
    def findVisualCoordinate(self, index, pixelCenter, screenSize):
        pixelDistanceToIndex = self.scalingFactor * index
        pixelDistanceToCenter = pixelDistanceToIndex - pixelCenter
        # finally adjust pixel location so center is shifted from top left
        finalLocation = pixelDistanceToCenter + screenSize / 2.0
        return finalLocation

    # flips row and col and x and y, if you are switching types of coordinates
    def convertViewToModel(self, direction):
        return (direction[1], direction[0])

# the class for the game itself, includes main game function, in and out of
# game navigation, like a splash screen, and replay and level editor functions
class PacGame(EventBasedAnimationClass):

    # three methods from the lecture notes, for equality of floats and
    # managing external files used by the game
    @staticmethod
    def almostEquals(a, b, epsilon = .001):
        return abs(a - b) < epsilon

    # reads a file
    @staticmethod
    def readFile(filename, mode="rt"):
        # rt = "read text"
        with open(filename, mode) as fin:
            return fin.read()

    # writes a file
    @staticmethod
    def writeFile(filename, contents, mode="wt"):
        # wt = "write text"
        with open(filename, mode) as fout:
            fout.write(contents)

    # creates a new instance of a pacgame
    def __init__(self):
        (width, height) = (500, 500)
        super(PacGame, self).__init__(width, height)
        self.createKeyMap()
        self.createHighScoresList()

    ############### Model ##

    # creates a dictionary mapping keys to directions
    def createKeyMap(self):
        self.keyMap = dict()
        keys = ["q","w","e","a","d","z","s","c","Up","Down","Right","Left"]
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1),
                        (0, 1), (1, 1), (0, -1), (0, 1), (1, 0), (-1, 0)]
        directionLabels = ["NW", "N", "NE", "W", "E", "SW", "S", "SE", "N",
                                                                "S", "E", "W"]
        for i in xrange(len(keys)):
            self.keyMap[keys[i]] = Struct()
            self.keyMap[keys[i]].direction = directions[i]
            self.keyMap[keys[i]].label = directionLabels[i]

    # prepare a high score list on file
    def createHighScoresList(self):
        self.highScores = []
        self.names = []
        filename = "highscores.txt"
        path = "HighScores" + os.sep + filename
        if os.path.exists("HighScores"):
            contents = PacGame.readFile(path)
            self.prepHighScores(contents)
        else:
            os.makedirs("HighScores")
            self.highScores = [0] * 10
            self.names = [""] * 10

    # reading highscores from the file
    def prepHighScores(self, contents):
        (names, scores) = contents.splitlines()
        self.names = names.split(" ")
        # the scores will be converted to integers
        self.highScores = [int(score) for score in scores.split(" ")]

    # intializing the animation, sets score to 0
    def initAnimation(self):
        self.howMapIsMade = "generated"
        self.timerDelay = 50
        self.inUpper = False
        self.setDefaults()
        self.addNewTypesOfEvents()
        self.setSplashScreen()
        self.prepReplay()
        self.prepareGame()
        self.prepEditor()
        self.prepareScoreScreen()
        self.prepSettings()
        self.score = 0

    # sets default values that are adjusted in different modes
    def setDefaults(self):
        self.lastTen = 0
        self.numberOfGhosts = 1
        self.ghostSpeedList = [15, 20, 30]
        self.shift = 10

    # binds new events to canvas for mouse motion and mouse release
    def addNewTypesOfEvents(self):
        self.root.bind("<B1-ButtonRelease>",
                    lambda event: self.onMouseReleasedWrapper(event))
        self.root.bind("<B1-Motion>",
                    lambda event: self.onMouseMovedWrapper(event))

    # calls onMouseReleased function and redraws canvas
    def onMouseReleasedWrapper(self, event):
        self.onMouseReleased(event)
        self.redrawAll()

    # calls onMouseMoved function and redraws canvas
    def onMouseMovedWrapper(self, event):
        self.onMouseMoved(event)
        self.redrawAll()

    # makes the start screen
    def setSplashScreen(self):
        self.settings = False
        self.mode = "splash"
        self.makeButtons()
        margin = self.height / 10
        size = self.height / 10
        (x, y) = (margin, self.height - margin - size)
        smallMargin = margin / 2
        self.challengeTextLocation = (margin + size + smallMargin, y)
        self.challengeOption = CheckBox((x, y), size)
        self.makeHelpMenu()

    # set up the help menu
    def makeHelpMenu(self):
        (x, y) = (.1 * self.width, .1 * self.height)
        (dx, dy) = (.05 * self.width, .05 * self.height)
        (p1, p2) = self.getPoints((x, y), dx, dy)
        self.helpButton = BetterButton(p1, p2, fill="#EEBBF0", text="?",
                                    font = "arial 40 bold")
        self.helpBack = self.makeBackButton()
        self.helpOk = self.makeContinueButton()
        self.helpTextX = self.width / 2
        self.helpTextY = .45 * self.height

    # set up buttons for the splash screen
    def makeButtons(self):
        heightBuffer = .35
        (midX, buttonWidth) = (self.width / 2, self.width / 4)
        yInit = self.height * heightBuffer
        yFinal = self.height * (1 - heightBuffer)
        (numOfButtons, ptList) = (4, [])
        step = (yFinal - yInit) / numOfButtons
        for i in xrange(numOfButtons):
            (y0, y1) = (yInit + i * step, yInit + (i + 1) * step)
            (p1, p2) = ((midX - buttonWidth, y0), (midX + buttonWidth, y1))
            ptList += [p1, p2]
        self.startButton = BetterButton(ptList[0],ptList[1],text = "START!",
                                            fill = "green", font= "Times 36")
        self.editorButton = BetterButton(ptList[2], ptList[3],
            text = "Level Editor", fill = "blue", font= "Times 36")
        self.highScoreButton = BetterButton(ptList[4], ptList[5],
            text = "High Scores", fill = "yellow", font = "Times 36")
        self.settingsButton = BetterButton(ptList[6], ptList[7],
            text = "Settings", fill = "red", font = "Times 36")

    # sets up replay button and prepares list for replays
    def prepReplay(self):
        self.rewind = False
        self.replayIndex = None
        self.actionList = []
        self.nextActions = []
        self.visitedList = []  # keeps an ordered list of visited lines
        self.lastVisitedPointsList = []
        (widthScale, heightScale) = (.5, .75)
        midPoint = (widthScale * self.width, heightScale * self.height)
        (widthDivisor, heightDivisor) = (6, 22)
        (rx, ry) = (self.width / widthDivisor, self.height / heightDivisor)
        (p1, p2) = ((midPoint[0] - rx, midPoint[1] - ry),
                    (midPoint[0] + rx, midPoint[1] + ry))
        self.replayButton =  BetterButton(p1, p2, text = "WATCH REPLAY?",
                                            font = "Impact 20", fill = "blue")

    # prepares the game component of the animation
    def prepareGame(self):
        self.makeMap()
        self.makePacman()
        self.newActiveGrid()
        self.prepareGhosts()

    # creates the game map
    def makeMap(self):
        startPoint = (0,0)
        (size, scale) = (7, 120) # scale is distance between intersections
        self.gameMap = PacmanMap(startPoint, size, scale, self)

    # intializes the center of the board and the pacman object
    def makePacman(self):
        self.currentPoint = Struct()
        self.currentPoint.pixels = (0, 0)
        self.currentPoint.grid = (0, 0)
        self.pacman = Pacman(self.shift, self.currentPoint.grid)
        self.intersectionDelay = False
        self.previousLocation = (0, 0)
        self.pacman.inReverse = False

    # prepares the level editor
    def prepEditor(self):
        self.validFieldKeys = ["0","1","2","3","4","5","6","7","8","9",
                                                            "BackSpace"]
        # these are valid keys for the row col entry fields in the editor
        self.selection = True
        self.prepSelectionScreen()
        self.prepEditorScreen()

    # creates ghosts on the border of the active grid
    def prepareGhosts(self):
        numberOfGhosts = self.numberOfGhosts
        self.ghostList = []
        for i in xrange(numberOfGhosts):
            ghost = self.spawnedGhost()
            self.ghostList.append(ghost)

    # spawns a new ghost on the edge of the active grid
    def spawnedGhost(self):
        (minRow, minCol) = self.activeGrid[0]
        (maxRow, maxCol) = self.activeGrid[len(self.activeGrid) - 1]
        borderIntersections = []
        for intersection in self.activeGrid:
            if intersection[0] == minRow or intersection[0] == maxRow or\
                intersection[1] == minCol or intersection[1] == maxCol:
                borderIntersections.append(intersection)
        spawnPoint = random.choice(borderIntersections)
        fastGhostDivisor = random.choice(self.ghostSpeedList)
        speed = self.gameMap.scalingFactor / fastGhostDivisor
        return Ghost(speed, spawnPoint)

    # prepares variables for getting user input on tile size
    # stores all variables in substruct self.tileEditorInfo
    def prepSelectionScreen(self):
        zheight = self.height
        info = self.tileEditorInfo = Struct()
        info.tileStringY = .1 * zheight
        info.rowscolsY = .5 * zheight
        info.noteStringY = .6 * zheight
        step = 1.0 / 6
        info.rowsColsX = [step * i * self.width for i in xrange(1, 5)]
        dW = self.width / 15
        dH = zheight / 30
        (p1, p2) = self.getPoints((info.rowsColsX[1], info.rowscolsY), dW, dH)
        (p3, p4) = self.getPoints((info.rowsColsX[3], info.rowscolsY), dW, dH)
        info.continueButton = self.makeContinueButton()
        info.backButton = self.makeBackButton()
        info.rowButton = BetterButton(p1, p2, fill = "white")
        info.colButton = BetterButton(p3, p4, fill = "white")

    # finds corner points for a button based on its center and size
    def getPoints(self, center, deltaWidth, deltaHeight):
        x0 = center[0] - deltaWidth
        y0 = center[1] - deltaHeight
        x1 = center[0] + deltaWidth
        y1 = center[1] + deltaHeight
        return ((x0, y0), (x1, y1))

    # returns a default continue button in the bottom corner
    def makeContinueButton(self):
        (midX, midY) = (.9 * self.width, .9 * self.height)
        (dx, dy) = (self.width / 13, self.height / 30)
        (p1, p2) = self.getPoints((midX, midY), dx, dy)
        return BetterButton(p1, p2, text="Okay", fill="#89cff0")#baby blue

    # returns a default back button next to the default continue button
    def makeBackButton(self):
        (midX, midY) = (.72 * self.width, .9 * self.height)
        (dx, dy) = (self.width / 13, self.height / 30)
        (p1, p2) = self.getPoints((midX, midY), dx, dy)
        return BetterButton(p1, p2, text="Back", fill="orange")

    # prepares the tile editor screen with help text and buttons
    def prepEditorScreen(self):
        edit = self.tileEditingScreen = Struct()
        edit.connecting = False
        edit.editingGridBottom = .75 * self.height
        edit.stringY = .8 * self.height
        edit.stringX = self.width / 2
        edit.backButton = self.makeBackButton()
        edit.continueButton = self.makeContinueButton()
        self.buildViewToLabelNavigationDictionary()
        (x , y)= (self.width * .44, self.height * .9)
        (dx, dy) = (self.width / 10, self.height / 30)
        (p1, p2) = self.getPoints((x, y), dx, dy)
        edit.randomButton = BetterButton(p1, p2, text = "Random Map",
                                            fill="purple")
        (x1, y1) = (self.width * .59, self.height * .9)
        (p3, p4) = self.getPoints((x1, y1), self.width / 30, self.height / 31)
        edit.blackRect = (p3, p4)
        self.newTileSavingApparatus()
        self.newUploadApparatus()

    # prepares tile saving buttons and miniscreen
    def newTileSavingApparatus(self):
        edit = self.tileEditingScreen
        (x1, y1) = (self.width * .25, self.height * .9)
        (dx1, dy1) = (self.width / 15, self.height / 30)
        (p3, p4) = self.getPoints((x1, y1), dx1, dy1)
        edit.saveTileButton = BetterButton(p3, p4, text="Save",fill="#F191BA")
        edit.savingField = False
        rectP1 = (self.width / 4, self.height /4)
        rectP2 = (3 * self.width / 4, 3 * self.height /4)
        edit.backRect = (rectP1, rectP2)
        edit.saveStringPt = (self.width / 2, .35 * self.height)
        (fieldX, fieldY) = (self.width / 2, self.height / 2)
        (dx2, dy2) = (self.width / 9, self.height / 30)
        (fieldP1, fieldP2) = self.getPoints((fieldX, fieldY), dx2, dy2)
        edit.saveField = BetterButton(fieldP1, fieldP2, fill="white")
        (okX, okY) = (self.width / 2, .65 * self.height)
        (okP1, okP2) = self.getPoints((okX, okY), dx1, dy1)
        edit.okSaveButton = BetterButton(okP1, okP2, text="Okay",fill="green")

    # prepares tile upload buttons and upload miniscreen
    def newUploadApparatus(self):
        edit = self.tileEditingScreen
        (x1, y1) = (self.width * .1, self.height * .9)
        (dx1, dy1) = (self.width / 15, self.height / 30)
        (p3, p4) = self.getPoints((x1, y1), dx1, dy1)
        edit.uploadTileButton = BetterButton(p3, p4, text="Upload",
                                    fill="#64BD4F")
        edit.loadingField = False

    # a reverse of the navigation dictionary held by a map object, can be
    # used to convert a shift to a direction
    def buildViewToLabelNavigationDictionary(self):
        coords = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),
                                                            (1, 0), (1, 1)]
        directions = ["NW", "N", "NE", "W", "E", "SW", "S", "SE"]
        newNav = dict()
        for i in xrange(len(coords)):
            newNav[coords[i]] = directions[i]
        self.reverseNavigationDictionary = newNav

    # prepares high scores screen
    def prepareScoreScreen(self):
        highc = self.highScoresThings = Struct()
        highc.backButton = self.makeBackButton()
        highc.nameMenu = False

    # prepares settings screen (secret screen from main menu)
    def prepSettings(self):
        set = self.settingsThings = Struct()
        set.backButton = self.makeBackButton()
        set.continueButton = self.makeContinueButton()
        set.ghostStringY = .5 * self.height
        ghostFieldY = .6 * self.height
        ghostFieldX = self.width / 2
        (dx, dy) = (self.width / 15, self.height / 30)
        (p1, p2) = self.getPoints((ghostFieldX, ghostFieldY), dx, dy)
        set.ghostField = BetterButton(p1, p2, fill="white")

    ##############Controller (mouseClick)
    # top level onMousedPressed checks what mode the game is in and delegates
    def onMousePressed(self, event):
        if self.mode == "splash":
            self.manageSplashClicks(event)
        elif self.mode == "help":
            self.manageHelpClicks(event)
        elif self.mode == "gameOver":
            self.manageEndClicks(event)
        elif self.mode == "editor":
            if self.selection: self.manageSelectionClicks(event)
            else: self.manageEditorClicks(event)
        elif self.mode == "scores":
            self.manageScoreClicks(event)
        elif self.mode == "settings":
            self.manageSetClicks(event)

    # manages clicks on the splash screen, adjusts modes
    def manageSplashClicks(self, event):
        if self.challengeOption.isClicked(event.x, event.y):
            self.manageChallenge()
        elif self.startButton.isClicked(event.x, event.y):
            self.prepareGhosts()
            self.mode = "game"
        elif self.editorButton.isClicked(event.x, event.y):
            self.mode = "editor"
        elif self.highScoreButton.isClicked(event.x, event.y):
            self.mode = "scores"
        elif self.helpButton.isClicked(event.x, event.y):
            self.mode = "help"
        elif self.settings and self.settingsButton.isClicked(event.x, event.y):
            self.mode = "settings"

    # manages clicks on the help screen
    def manageHelpClicks(self, event):
        if self.helpBack.isClicked(event.x, event.y):
            self.mode = "splash"
        elif self.helpOk.isClicked(event.x, event.y):
            self.mode = "splash"

    # manages clicks on the end screen, eg replay mode
    def manageEndClicks(self, event):
        if self.highScoresThings.nameMenu:
            self.manageScoreNameClicks(event)
        elif self.replayButton.isClicked(event.x, event.y):
            self.mode = "replay"
            self.replayIndex = 0
            self.pacman.visitedLines.clear()
            self.timerDelay = 20

    # manages clicks when the high score name field is open
    def manageScoreNameClicks(self, event):
        highc = self.highScoresThings
        edit = self.tileEditingScreen
        if edit.saveField.isClicked(event.x, event.y):
            edit.saveField.clicked = True
        else: edit.saveField.clicked =  False
        if edit.okSaveButton.isClicked(event.x, event.y):
            self.updateHighScores()
            highc.nameMenu = False

    #updates High Scores List after a game
    def updateHighScores(self):
        i = 0
        while (i < len(self.highScores)):
            if self.score > self.highScores[i]:
                break
            i+=1
        name = self.getNameOfScorer()
        self.highScores.insert(i, self.score)
        self.highScores.pop()
        self.names.insert(i, name)
        self.names.pop()
        self.updateHighScoreFile()

    # requests the user's name for their highscore
    def getNameOfScorer(self):
        edit = self.tileEditingScreen
        name = edit.saveField.text
        edit.saveField.text = ""
        return name

    #updates the highscore file
    def updateHighScoreFile(self):
        contents = self.makeHighScoreString()
        path = "HighScores" + os.sep + "highscores.txt"
        if os.path.exists(path): os.remove(path)
        PacGame.writeFile(path, contents)

    # makes a string to be saved in the highscores file
    def makeHighScoreString(self):
        fileString = ""
        for name in self.names[:-1]: # don't want a space at the end
            fileString += name + " "
        fileString += self.names[-1] + "\n"
        for score in self.highScores[:-1]: # still no space at end intended
            fileString += str(score) + " "
        fileString += str(self.highScores[-1])
        return fileString

    # manages clicks in the first screen of the editor, like clicking
    # into the number fields
    def manageSelectionClicks(self, event):
        info = self.tileEditorInfo
        buttons = [info.rowButton, info.colButton]
        for button in buttons:
            if button.isClicked(event.x, event.y):
                button.clicked = True
            else: button.clicked = False
        if info.backButton.isClicked(event.x, event.y): self.mode = "splash"
        elif info.continueButton.isClicked(event.x, event.y):
            self.selection = False
            self.prepTileEditing()

    # prepares editable tile for editing in second screen of editor
    def prepTileEditing(self):
        self.updateTileEditingSize()
        self.setEditingGrid()
        self.setBaseTileList()

    # sets tile size for the editor
    def updateTileEditingSize(self):
        info = self.tileEditorInfo
        edit = self.tileEditingScreen
        (edit.rows, edit.cols) = (2, 2) # sets to default each time
        if not info.rowButton.text == "":
            newRows = int(info.rowButton.text)
            if newRows > 0 and newRows < 8: edit.rows = newRows
        if not info.colButton.text == "":
            newCols = int(info.colButton.text)
            if newCols > 0 and newCols < 8: edit.cols = newCols

    # prepares the visual grid for editing a tile
    def setEditingGrid(self):
        edit = self.tileEditingScreen
        edit.grid = []
        margin = self.height / 10
        x0 = y0 = margin
        verticalStep = (edit.editingGridBottom - 2 * margin) / edit.rows
        horizantalStep = (self.width - 2 * margin) / edit.cols
        step = min(verticalStep, horizantalStep)
        for row in xrange(edit.rows + 1):
            edit.grid.append([])
            for col in xrange(edit.cols + 1):
                (x, y) = (x0 + step * col, y0 + step * row)
                edit.grid[row].append((x, y))

    # initializes a list of connections for a user made tile, all set to false
    def setBaseTileList(self):
        edit = self.tileEditingScreen
        tileList = []
        for row in xrange(edit.rows):
            tileList.append([])
            for col in xrange(edit.cols):
                pointInfo = dict()
                for direction in self.gameMap.navigationDictionary:
                    pointInfo[direction] = False # each point starts without
                                                 # connections to other points
                tileList[row].append(pointInfo)
        edit.baseTile = tileList

    # manages clicks within the editing screen for buttons or editor
    def manageEditorClicks(self, event):
        edit = self.tileEditingScreen
        if edit.savingField: self.manageSavingFieldClicks(event)
        elif edit.loadingField: self.manageLoadingFieldClicks(event)
        elif edit.backButton.isClicked(event.x, event.y): self.selection = True
        elif edit.randomButton.isClicked(event.x, event.y):
            self.howMapIsMade = "generated"
            self.makeMap()
            self.mode = "splash"
            self.selection = True
        elif edit.continueButton.isClicked(event.x, event.y):
            self.updateMap()
            self.selection = True
            self.mode = "splash"
        elif edit.saveTileButton.isClicked(event.x, event.y):
            edit.savingField = True
        elif edit.uploadTileButton.isClicked(event.x, event.y):
            edit.loadingField = True
            self.findUploadOptions()
            self.prepareUploadButtons()
        else:
            self.checkIfMakingPointConnection(event)

    # manages clicks when the saving field is open
    def manageSavingFieldClicks(self, event):
        edit = self.tileEditingScreen
        if edit.saveField.isClicked(event.x, event.y):
            edit.saveField.clicked = True
        else: edit.saveField.clicked =  False
        if edit.saveTileButton.isClicked(event.x, event.y):
            edit.savingField = False
        elif edit.okSaveButton.isClicked(event.x, event.y):
            if edit.saveField.text != "":
                self.saveThisTile()
                edit.savingField = False

    # manages clicks when the upload miniscreen is open
    def manageLoadingFieldClicks(self, event):
        edit = self.tileEditingScreen
        if edit.uploadTileButton.isClicked(event.x, event.y):
            edit.loadingField = False
        for button in edit.uploadButtons:
            if button.isClicked(event.x, event.y):
                fileString = self.getFileString(button)
                self.convertFileToTile(fileString)
                edit.loadingField = False
                break

    # returns a string stored in a file
    def getFileString(self, button):
        path = "savedTiles" + os.sep + button.text + ".txt"
        return PacGame.readFile(path)

    # saves the tile to the location of its selected name
    def saveThisTile(self):
        edit = self.tileEditingScreen
        fileString = self.convertTileToFile()
        fileName = edit.saveField.text + ".txt"
        edit.saveField.text = ""
        path = "savedTiles" + os.sep + fileName
        if not os.path.exists("savedTiles"): os.makedirs("savedTiles")
        if os.path.exists(path): os.remove(path)
        PacGame.writeFile(path, fileString)

    # changes map generation mode to tiled from a user map
    def updateMap(self):
        self.keyTile = self.tileEditingScreen.baseTile
        self.howMapIsMade = "tiled"
        self.makeMap()

    # creates a string based on the data in a tile
    def convertTileToFile(self):
        edit = self.tileEditingScreen
        fileString = ""
        tile = edit.baseTile
        for row in xrange(len(tile)):
            fileString += "--"
            for col in xrange(len(tile[0])):
                fileString += "/"
                for direction in tile[row][col]:
                    fileString += "."
                    fileString += direction
                    fileString += str(int(tile[row][col][direction]))
        return fileString

    # converts a stored string to a tile
    def convertFileToTile(self, fileString):
        edit = self.tileEditingScreen
        edit.baseTile = []
        rowList = fileString.split("--")[1:]
        edit.rows = len(rowList)
        for i in xrange(len(rowList)):
            edit.baseTile.append([])
            colList = rowList[i].split("/")[1:]
            for col in colList:
                directionList = col.split(".")[1:]
                directionDictionary = dict()
                for direction in directionList:
                    key = direction[:-1]
                    value = bool(int(direction[-1]))
                    directionDictionary[key] = value
                edit.baseTile[i].append(directionDictionary)

    # creates a list of uploadable files
    def findUploadOptions(self):
        edit = self.tileEditingScreen
        options = []
        if os.path.exists("savedTiles"):
            path = "savedTiles"
            for filename in os.listdir(path):
                if filename[-4:] == ".txt":
                    options.append(filename[:-4])
        edit.uploadOptions = options

    # creates buttons for each uploadable file
    def prepareUploadButtons(self):
        edit = self.tileEditingScreen
        edit.uploadButtons = []
        x = self.width / 2
        topY = .4 * self.height
        dx = self.width / 10
        bottomY = .6 * self.height
        step = (bottomY - topY) / (len(edit.uploadOptions) + 1)
        for i in xrange(1, len(edit.uploadOptions) + 1):
            y = topY + i * step
            (p1, p2) = self.getPoints((x, y), dx, step / 3)
            edit.uploadButtons.append(BetterButton(p1, p2,
                    text=edit.uploadOptions[i - 1], fill="pink"))

    # adjusts settings if click is made to connect points in tile
    def checkIfMakingPointConnection(self, event):
        edit = self.tileEditingScreen
        for row in xrange(len(edit.grid)):
            for col in xrange(len(edit.grid[row])):
                point = edit.grid[row][col]
                if self.clickIsNear(point, event):
                    edit.connecting = True
                    edit.firstPoint = (row, col)
                    edit.tempScreenPoint = edit.grid[row][col]
                    return
        edit.connecting = False

    # returns true if click is near a point in the grid
    def clickIsNear(self, point, event):
        dx = abs(point[0] - event.x)
        dy = abs(point[1] - event.y)
        validClickingDistance = 15
        return math.sqrt(dx ** 2 + dy ** 2) < validClickingDistance

    # turns on challenge settings if the user selects it
    def manageChallenge(self):
        if self.challengeOption.clicked:
            self.ghostSpeedList = 49 * [10] + [5]
            self.shift = 30
        else: self.setDefaults()

    # works back button for high scores
    def manageScoreClicks(self, event):
        highc = self.highScoresThings
        if highc.backButton.isClicked(event.x, event.y):
            self.mode = "splash"

    # controls clicks and field click in settings screen
    def manageSetClicks(self, event):
        set = self.settingsThings
        if set.backButton.isClicked(event.x, event.y):
            self.mode = "splash"
            set.ghostField.text = ""
        elif set.continueButton.isClicked(event.x, event.y):
            self.mode = "splash"
            self.challengeOption.clicked = False
            self.setDefaults()
            if not set.ghostField.text == "":
                self.numberOfGhosts = int(set.ghostField.text)
                self.prepareGhosts()
                set.ghostField.text = ""
        elif set.ghostField.isClicked(event.x, event.y):
            set.ghostField.clicked = True

    ############### Controller (key navigation)
    # top level onKeyPressedFunction delegates actions based on mode
    def onKeyPressed(self, event):
        self.checkUpperCase(event)
        if self.mode == "splash":
            if event.keysym == "x": self.settings = not self.settings
        elif self.mode == "gameOver" and \
                            self.tileEditingScreen.saveField.clicked:
            self.fileNameInput(event)
        elif self.mode == "replay":
            self.manageReplayButtons(event)
        elif self.mode == "editor":
            if self.selection: self.manageSelectionNumbers(event)
            elif self.tileEditingScreen.savingField: self.fileNameInput(event)
        elif self.mode == "settings":
            self.manageSettingsNumbers(event)
        if not (self.mode == "splash" or self.tileEditingScreen.savingField
                or self.highScoresThings.nameMenu):
            if event.keysym == "r": self.resetAnimation()
            if not self.mode == "game": return
            if event.keysym in self.keyMap:
                if not self.isLegalMove(event): return
                self.nextMove = event.keysym
                self.updateDirection(event.keysym)

    # informs the user if they have just typed an uppercase letter
    def checkUpperCase(self, event):
        if event.keysym in string.ascii_uppercase and\
                not self.tileEditingScreen.savingField: self.inUpper = True
        else: self.inUpper = False

    # allows the user to adjust the speed of the replay
    def manageReplayButtons(self, event):
        if self.timerDelay > 1000:
            self.rewind = not self.rewind
            self.timerDelay /= 2
        speedKey = "Up" if not self.rewind else "Down"
        slowKey = "Down" if not self.rewind else "Up"
        if event.keysym == speedKey: self.timerDelay = self.timerDelay / 2 + 1
        elif event.keysym == slowKey: self.timerDelay *= 2

    # manages fields in first screen of tile editor
    def manageSelectionNumbers(self, event):
        if event.keysym in self.validFieldKeys:
            info = self.tileEditorInfo
            if info.rowButton.clicked:
                self.modifyField(info.rowButton, event)
            elif info.colButton.clicked:
                self.modifyField(info.colButton, event)

    # adjusts a number field based on a key press
    def modifyField(self, field, event):
        if event.keysym == "BackSpace" and len(field.text) > 0:
            field.text = field.text[:-1]
        elif event.keysym != "BackSpace":
            newText = field.text + event.keysym
            largestEnterableValue = 999
            if int(newText) > largestEnterableValue: return
            else: field.text = newText

    # manages key presses in the settings screen
    def manageSettingsNumbers(self, event):
        set = self.settingsThings
        if set.ghostField.clicked: self.modifyField(set.ghostField, event)

    # adjusts field for typing a file name
    def fileNameInput(self, event):
        field = self.tileEditingScreen.saveField
        if not field.clicked: return
        if event.keysym == "BackSpace" and len(field.text) > 0:
            field.text = field.text[:-1]
        elif event.keysym in string.digits or\
                        event.keysym in string.ascii_letters:
            if len(field.text) < 20: field.text += event.keysym
        elif self.highScoresThings.nameMenu and event.keysym == " ":
            if len(field.text) < 20: field.text += event.keysym

    # returns to the splash screen when 'r' is pressed
    def resetAnimation(self):
        self.timerDelay = 50
        self.prepReplay()
        self.mode = "splash"
        self.score = 0
        self.prepareGame()
        self.lastTen = 0

    # changes pacmans next moving direction when a directing key is pressed
    def updateDirection(self, letter):
        self.pacman.direction.label = self.keyMap[letter].label
        self.pacman.direction.grid = self.keyMap[letter].direction
        self.pacman.gliding = True
        self.intersectionDelay = False

    # verifies a change in direction is a legal while pacman is moving
    # also checks if pacman is at an intersection
    def isLegalMove(self, event):
        directionLabel = self.keyMap[event.keysym].label
        pFlow = self.pacman.direction.label
        if self.pacman.gliding:
            if directionLabel == self.gameMap.navigationDictionary[pFlow][2]:
                self.pacman.inReverse = not self.pacman.inReverse
                return True
            elif (self.willBeALegalMove(event.keysym)):
                self.nextMove = event.keysym
            return False
        lastIntersection = self.currentPoint.grid
        return self.gameMap.hasConnection(lastIntersection, directionLabel)

    # if pacman is at an intersection, returns true if a turn is legal
    def willBeALegalMove(self, letter):
        key = self.keyMap[letter].label
        if self.pacman.inReverse:
            return self.gameMap.hasConnection(self.previousLocation, key)
        shift = self.pacman.direction.grid # x, y format
        newLocation = (self.previousLocation[0] + shift[1],
                                self.previousLocation[1] + shift[0])
        return self.gameMap.hasConnection(newLocation, key)

    ############# Continuous movement (timer fired)
    # toplevel onTimerFired function checks whether mode is ingame or replay
    def onTimerFired(self):
        self.score = len(self.pacman.visitedLines)
        if self.mode == "replay":
            self.updateReplayPositions()
        elif self.mode == "game":
            self.checkGameOver()
            self.movePacman()
            self.moveGhosts()
            self.resetActionLists()

    # moves characters in the replay
    def updateReplayPositions(self):
        if self.replayIndex == len(self.actionList):
            self.mode = "gameOver"
        else:
            actions = self.actionList[self.replayIndex]
            self.fixReplayView(actions)
            self.makeReplayGhosts(actions)
            self.makeReplayForVisitedLines()
            if self.rewind:
                if self.replayIndex == 0: self.rewind = False
                else: self.replayIndex -= 1
            else: self.replayIndex += 1

    # 'revisits' lines in the replay
    def makeReplayForVisitedLines(self):
        self.previousLocation = self.lastVisitedPointsList[self.replayIndex]
        if self.visitedList[self.replayIndex] == None: return
        self.pacman.visitedLines.clear()
        loopEnd = self.replayIndex + (1 if not self.rewind else 0)
        for i in xrange(1, loopEnd):
            self.pacman.visitedLines.add(self.visitedList[i])

    # adjusts game position based on progression in replay
    def fixReplayView(self, actions):
        self.currentPoint.pixels = actions[0][0]
        self.pacman.direction.grid = actions[0][1]

    # adjusts ghosts in replay
    def makeReplayGhosts(self, actions):
        self.ghostList = []
        for i in xrange(len(actions) - 1):
            self.ghostList.append(Ghost(None, actions[i + 1][0]))
            self.ghostList[i].color = actions[i + 1][1]

    # checks if game is over
    def checkGameOver(self):
        pacPoint = self.currentPoint.pixels
        r1 = self.pacman.r
        for ghost in self.ghostList:
            (row, col) = ghost.currentLocation
            scale = self.gameMap.scalingFactor
            ghostPoint = (col * scale, row * scale)
            r2 = ghost.r
            if PacGame.almostEquals(ghostPoint[0], pacPoint[0], r1 + r2) and \
                PacGame.almostEquals(ghostPoint[1], pacPoint[1], r1 + r2):
                self.mode = "gameOver"
                self.saveReplayInformationAboutPacmansWhereabouts()
                self.storeGhostInformation()
                self.visitedList.append(None)
                self.resetActionLists()
                barrier = self.highScores[-1] # the lowest high score
                if self.score > barrier: self.highScoresThings.nameMenu = True

    # continues updating actionlist (for replay) during the game
    def resetActionLists(self):
        self.actionList.append(tuple(self.nextActions))
        self.nextActions = []

    # moves pacman based on gliding condition and stores visited line in set
    def movePacman(self):
        self.saveReplayInformationAboutPacmansWhereabouts()
        line = None
        if self.pacman.gliding:
            self.gridMotion()
            if self.reachedIntersection():
                prevLocation = self.previousLocation
                newLocation = self.pacman.currentLocation
                line = "%d.%d_%d.%d" % (prevLocation[0], prevLocation[1],
                                        newLocation[0], newLocation[1])
                if not self.gameMap.visitedContains(line, self):
                    self.pacman.visitedLines.add(line)
                self.previousLocation = newLocation
                self.newActiveGrid()
                self.pacman.gliding = False
                self.pacman.inReverse = False
                if self.pathContinues():
                    self.intersectionDelay = True
        elif self.intersectionDelay:
            self.updateDirection(self.nextMove)
            self.gridMotion()
        self.visitedList.append(line)

    # stores pacmans locatioin for replay
    def saveReplayInformationAboutPacmansWhereabouts(self):
        self.nextActions.append((self.currentPoint.pixels,
                                            self.pacman.direction.grid))
        self.lastVisitedPointsList.append(self.previousLocation)

    # moves grid opposite the direction pacman is 'moving'
    def gridMotion(self):
        movement = self.pacman.direction.grid
        newX = self.currentPoint.pixels[0] + movement[0] * self.shift
        newY = self.currentPoint.pixels[1] + movement[1] * self.shift
        divisor = self.gameMap.scalingFactor
        row = newY / divisor
        col = newX / divisor
        self.currentPoint.pixels = (newX, newY)
        self.currentPoint.grid = (row, col) # new location
        self.pacman.currentLocation = self.currentPoint.grid
        self.gameMap.makeGrid(self.currentPoint.grid, self)

    # adds to the grid based on pacman's new location
    def newActiveGrid(self):
        gridCenter = self.pacman.currentLocation
        size = self.gameMap.size
        (minRow, minCol) = (gridCenter[0] - size/2, gridCenter[1] - size/2)
        self.activeGrid = []
        for i in xrange(size):
            for j in xrange(size):
                (row, col) = (minRow + i, minCol + j)
                self.activeGrid.append((row, col))

    # returns true if pacman can continue gliding (no T intersection)
    def pathContinues(self):
        direction = self.pacman.direction.label
        location = self.pacman.currentLocation
        return self.gameMap.hasConnection(location, direction)

    # moves ghosts on timer fired
    def moveGhosts(self):
        self.storeGhostInformation()
        for i in xrange(len(self.ghostList)):
            ghost = self.ghostList[i]
            if ghost.gliding:
                ghost.glide(self)
            elif not ghost.currentLocation in self.activeGrid:
                self.ghostList[i] = self.spawnedGhost()
            else:
                ghost.findDirection(self)
                ghost.gliding = True
                ghost.glide(self)
        if self.score / 10 > self.lastTen:
            self.lastTen += 1
            self.ghostList += [self.spawnedGhost()]

    # stores ghost locations for replay
    def storeGhostInformation(self):
        for ghost in self.ghostList:
            self.nextActions.append((ghost.currentLocation, ghost.color))

    # returns true if an intersection is reached
    def reachedIntersection(self):
        (x, y) = self.currentPoint.pixels
        (row, col) = self.currentPoint.grid
        floatDivisor = float(self.gameMap.scalingFactor)
        (newRow, newCol) = (y / floatDivisor, x / floatDivisor)
        return PacGame.almostEquals(row, newRow) and \
               PacGame.almostEquals(col, newCol)

    ############## Controller (mouse release) ####
    # adds connections if mouse motion ends at a different legal point
    def onMouseReleased(self, event):
        edit = self.tileEditingScreen
        if not edit.connecting: return
        for row in xrange(len(edit.grid)):
            for col in xrange(len(edit.grid[row])):
                point = edit.grid[row][col]
                if self.clickIsNear(point, event):
                    edit.secondPoint = (row, col)
                    self.formConnection()
        edit.connecting = False

    # creates a connection between two newly connected points in the tile data
    def formConnection(self):
        edit = self.tileEditingScreen
        (a, b) = (edit.firstPoint, edit.secondPoint)
        (shiftA, shiftB) = ((b[0]-a[0], b[1]-a[1]), (a[0]-b[0], a[1]-b[1]))
        revDict = self.reverseNavigationDictionary
        if shiftA in revDict:
            (labelA, labelB) = (revDict[shiftA], revDict[shiftB])
            (newA, newB) = (self.simplify(a), self.simplify(b))
            edit.baseTile[newA[0]][newA[1]][labelA] = True
            edit.baseTile[newB[0]][newB[1]][labelB] = True

    # stores data in first data point (in a two by two grid, the third point
    # is the same as the first point)
    def simplify(self, point):
        edit = self.tileEditingScreen
        row = point[0] % edit.rows
        col = point[1] % edit.cols
        return (row, col)

    ############## Controller (mouse motion [left drag]) ##
    # extends line based on where mouse is dragged
    def onMouseMoved(self, event):
        edit = self.tileEditingScreen
        if not edit.connecting: return
        edit.tempScreenPoint = (event.x, event.y)

    ########### View
    # top level drawing function draws screens based on mode
    def redrawAll(self):
        self.canvas.delete(ALL)
        if self.mode == "splash": self.drawSplashScreen()
        elif self.mode == "help": self.drawHelpScreen()
        elif self.mode == "editor": self.drawEditor()
        elif self.mode == "scores": self.drawScores()
        elif self.mode == "settings": self.drawSettings()
        elif self.mode == "gameOver": self.drawEndScreen()
        elif self.mode == "game" or self.mode == "replay":
            self.drawMap()
            self.pacman.draw(self)
            for ghost in self.ghostList:
                ghost.draw(self)
            self.canvas.create_text(.9 * self.width, .9 * self.height,
                text = self.score, fill = "Blue", font = "arial 40 bold")
            self.canvas.create_text(.1 * self.width, .9 * self.height,
                text = "Ghosts: %d" % len(self.ghostList), fill="purple",
                                    font = "arial 40 bold", anchor = W)
        if self.inUpper: self.canvas.create_text(self.width / 2, 50,
            text = "WARNING: CHECK CAPS LOCK", fill="red", font="arial 30")

    # draws the splash screen
    def drawSplashScreen(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                                        fill = "gray")
        heightScale = 4
        self.canvas.create_text(self.width / 2, self.height / heightScale,
                        text = "PacRunner", font = "Georgia 70 bold")
        self.startButton.draw(self.canvas)
        self.editorButton.draw(self.canvas)
        self.highScoreButton.draw(self.canvas)
        if self.settings: self.settingsButton.draw(self.canvas)
        self.challengeOption.draw(self.canvas)
        self.canvas.create_text(self.challengeTextLocation, anchor = NW,
                        text = "Challenge", font = "Times 40 bold")
        self.helpButton.draw(self.canvas)

    # draws the help screen with instructions
    def drawHelpScreen(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                    fill = "#F5F5DC")
        self.helpBack.draw(self.canvas)
        self.helpOk.draw(self.canvas)
        helpText = """Ready to race?\nHow far can you get with Pacman?\n
Move Pacman for as far and as long as you can while avoiding a never\
ending flow of ghosts.\n\nThen, make your own level by building your\
own tile to generate the Pacman map.\n\nSo how do you play?\n\n\
w: up  s: down  a: left  d: right (q, e, z, c for diagonals)\n\n\
Want to see a replay? No problem.\n\n\
Use the up and down arrows to speed and slow your replay after \
you finish a game.
                   """
        self.canvas.create_text(self.helpTextX, self.helpTextY,
            text = helpText, width = self.width, font = "arial 20")

    # top level function for drawing editor
    def drawEditor(self):
        if self.selection: self.drawSelectionScreen()
        else: self.drawEditorScreen()

    # draws the first screen of the editor
    def drawSelectionScreen(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height,
            fill="blue")
        info = self.tileEditorInfo
        self.canvas.create_text(self.width / 2, info.tileStringY,
            text = "Select Tile Size", font = "Arial 40")
        self.canvas.create_text(info.rowsColsX[0],info.rowscolsY,
            text = "Row", font = "arial 20")
        self.canvas.create_text(info.rowsColsX[2],info.rowscolsY,
            text = "Col", font = "arial 20")
        info.rowButton.draw(self.canvas)
        info.colButton.draw(self.canvas)
        self.canvas.create_text(self.width / 2, info.noteStringY,
            text = "Max Tile Size is 7 by 7", font = "arial 30")
        info.continueButton.draw(self.canvas)
        info.backButton.draw(self.canvas)

    # draws the tile editing screen of the editor
    def drawEditorScreen(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height,
            fill="gray")
        edit = self.tileEditingScreen
        if edit.connecting:
            (row, col) = edit.firstPoint
            pt2 = edit.grid[row][col]
            self.canvas.create_line(edit.tempScreenPoint, pt2, width = 3)
        self.drawEditableTile()
        self.canvas.create_text(edit.stringX, edit.stringY,
            text = "Click and Drag to Connect Points", font= "Arial 30")
        edit.backButton.draw(self.canvas)
        edit.continueButton.draw(self.canvas)
        edit.randomButton.draw(self.canvas)
        self.canvas.create_rectangle(edit.blackRect[0], edit.blackRect[1],
                                        fill = "black")
        edit.saveTileButton.draw(self.canvas)
        edit.uploadTileButton.draw(self.canvas)
        if edit.savingField: self.drawSaveMenu()
        elif edit.loadingField: self.drawLoadMenu()

    # draws the save menu in the tile editor
    def drawSaveMenu(self):
        edit = self.tileEditingScreen
        self.canvas.create_rectangle(edit.backRect[0], edit.backRect[1],
                fill="#D3D3D3", width = 2)
        self.canvas.create_text(edit.saveStringPt, font = "Arial 25",
                    text = "Choose a save name")
        edit.saveField.draw(self.canvas)
        edit.okSaveButton.draw(self.canvas)

    # draws the upload menu in the editor
    def drawLoadMenu(self):
        edit = self.tileEditingScreen
        self.canvas.create_rectangle(edit.backRect[0], edit.backRect[1],
                fill="#D3D3D3", width = 2)
        self.canvas.create_text(edit.saveStringPt, font = "Arial 25",
                    text = "Choose a File")
        edit.okSaveButton.draw(self.canvas)
        for button in edit.uploadButtons:
            button.draw(self.canvas)

    # draws the editable tile in the tile editing screen
    def drawEditableTile(self):
        edit = self.tileEditingScreen
        r = 5
        for row in xrange(len(edit.grid)):
            for col in xrange(len(edit.grid[row])):
                (x, y) = edit.grid[row][col]
                for direction in ["SW","S","SE","E"]:
                    goesOffLeft = col == 0 and direction == "SW"
                    goesOffRight = col == len(edit.grid[row]) - 1 and\
                                   (direction == "E" or direction == "SE")
                    goesOffBottom = row==len(edit.grid) - 1 and direction!="E"
                    if not (goesOffLeft or goesOffRight or goesOffBottom):
                        newRow = row % len(edit.baseTile)
                        newCol = col % len(edit.baseTile[newRow])
                        if edit.baseTile[newRow][newCol][direction]:
                            nav = self.gameMap.navigationDictionary
                            shift = nav[direction][0]
                            newCoord = (row + shift[0], col + shift[1])
                            (x1, y1) = edit.grid[newCoord[0]][newCoord[1]]
                            self.canvas.create_line(x, y, x1, y1, width = 3)
                self.canvas.create_oval(x - r, y - r, x + r, y + r,
                    fill = "white", width = 2)

    # draw the highscore screen
    def drawScores(self):
        highc = self.highScoresThings
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                                        fill = "gray")
        highc.backButton.draw(self.canvas)
        self.canvas.create_text(self.width / 2, .2 * self.height,
            text="High Scores", font="Arial 60 bold")
        (x0, x1) = (self.width * .3, self.width * .7)
        (y0, y1) = (self.height * .33, self.height * .88)
        step = (y1 - y0) / len(self.highScores)
        for i in xrange(len(self.highScores)):
            y = y0 + step * i
            nameText = str(i + 1) + ". " + self.names[i]
            self.canvas.create_text(x0, y, text= nameText,
                                    anchor = W, font="Arial 20")
            self.canvas.create_text(x1, y, text= str(self.highScores[i]),
                                    anchor = E, font = "Arial 20")

    # draws the settings screen
    def drawSettings(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height,
            fill ="#FFFF7A") # light yellow
        set = self.settingsThings
        set.backButton.draw(self.canvas)
        set.continueButton.draw(self.canvas)
        set.ghostField.draw(self.canvas)
        self.canvas.create_text(self.width / 2, set.ghostStringY,
            text = "Set the number of ghosts", font = "Arial 30")

    # draws the end screen
    def drawEndScreen(self):
        scoreMultiplier = 1
        linesList = self.pacman.visitedLines
        tiles = len(linesList) - (1 if None in linesList else 0)
        self.score = scoreMultiplier * tiles
        self.canvas.create_rectangle(0, 0, self.width, self.height,fill="red")
        self.canvas.create_text(self.width / 2, self.height / 2,
                        text = "GAME OVER", font = "Arial 40 bold")
        text = "SCORE: %d" % self.score
        self.canvas.create_text(self.width / 2, self.height / 4,
                        text = text, font = "Arial 20 bold")
        self.canvas.create_text(self.width / 2, .9 * self.height,
            text = "Press 'r' to return to main menu", font="arial 20 bold")
        self.replayButton.draw(self.canvas)
        if self.highScoresThings.nameMenu: self.drawNameMenu()

    # draws a menu to get the high scorer's name
    def drawNameMenu(self):
        edit = self.tileEditingScreen
        self.canvas.create_rectangle(edit.backRect[0], edit.backRect[1],
                fill="#D3D3D3", width = 2)
        self.canvas.create_text(edit.saveStringPt, font = "Arial 25",
                    text = "New High Score!")
        edit.saveField.draw(self.canvas)
        edit.okSaveButton.draw(self.canvas)

    # draws the game map if in game and an orange line from the
    # previous visited point to pacman
    def drawMap(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="Black")
        self.gameMap.draw(self.canvas, self.currentPoint.pixels, self)
        spot = self.currentPoint.pixels
        previousGridPoint = self.previousLocation
        x = self.gameMap.findVisualCoordinate(previousGridPoint[1],
            spot[0], self.width)
        y = self.gameMap.findVisualCoordinate(previousGridPoint[0],
            spot[1], self.height)
        currentPoint = (self.width / 2, self.height / 2)
        pastPoint = (x, y)
        self.canvas.create_line(currentPoint, pastPoint,
                            width = self.gameMap.lineWidth, fill = "orange")

# basic sprite class for any moving character in game
class sprite(object):

    # sets sprite speed, and location
    def __init__(self, speed, location):
        self.speed = speed
        self.currentLocation = location

    # empty draw function
    def draw(self, game): pass

    # empty movement function
    def glide(self, game): pass

# Pacman class extends sprite class
class Pacman(sprite):

    # pacaman initializes with a direction and a set of visited lines
    def __init__(self, speed, location):
        super(Pacman, self).__init__(speed, location)
        self.direction = Struct()
        self.direction.label = "E"
        self.direction.grid = (1, 0)
        self.gliding = False
        self.visitedLines = set()
        self.r = 15
        self.bite = False
        self.biteDelay = 5

    # pacman draws itself
    def draw(self, game):
        self.biteDelay -= 1
        if self.biteDelay == 0:
            self.bite = not self.bite
            self.biteDelay = 5
        canvas = game.canvas
        (width, height) = (game.width, game.height)
        (cx, cy) = (width / 2, height / 2)
        start = self.checkStart()
        r = self.r
        arcLength = 356 if self.bite else 270
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start = start,
            extent = arcLength, width = 2, fill = "yellow")

    # find the starting angle of pacmans mouth based on direction
    def checkStart(self):
        direction = self.direction.grid
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        return angle + (2 if self.bite else 45)

# Ghost class extends sprite class
class Ghost(sprite):

    # ghost initializes with a speed location and direction
    def __init__(self, speed, location):
        super(Ghost, self).__init__(speed, location)
        self.direction = Struct()
        self.direction.label = "E"
        self.direction.grid = (0, 0)
        self.gliding = False
        self.color = self.getColor()
        self.r = 15

    # decides on a color from a premade list of ghost colors
    def getColor(self):
        colors = ["#00d8ff", "#00ff18", "#ff00e1", "#ff0000", "#ff69b4",
                                "white", "#0000ff", "#228B22"]
        return random.choice(colors)

    # ghost finds best direction to reach pacman
    def findDirection(self, game):
        location = self.currentLocation
        movesAhead = 3
        shortestDistanceSoFar = 2 * game.gameMap.size # this is larger than
                    # the distance that ghosts will respawn closer from
        label = "E"
        for direction in game.gameMap.navigationDictionary:
            way = game.gameMap.navigationDictionary[direction]
            if game.gameMap.hasConnection(location, direction):
                newPoint = (location[0] + way[0][0],
                                    location[1] + way[0][1])
                distance = self.shortestDistance(newPoint, game, movesAhead)
                if distance < shortestDistanceSoFar:
                    label = direction
                    shortestDistanceSoFar = distance
        self.direction.label = label
        self.direction.grid = game.gameMap.navigationDictionary[label][0]

    # recursive function for ghost to find shortest distance to pacman
    # penalty is used to prioritize fewer moves
    def shortestDistance(self, location, game, movesAhead):
        if movesAhead == 0:
            return self.findDistance(location, game)
        else:
            penalty = .01 # taking more moves to reach pacman is worse
            shortestDistanceSoFar = self.findDistance(location, game)
            for direction in game.gameMap.navigationDictionary:
                if game.gameMap.hasConnection(location, direction):
                    way = game.gameMap.navigationDictionary[direction]
                    newPoint = (location[0] + way[0][0],
                                        location[1] + way[0][1])
                    distance = self.shortestDistance(newPoint, game,
                                    movesAhead - 1) + movesAhead * penalty
                    if distance < shortestDistanceSoFar:
                        shortestDistanceSoFar = distance
            return shortestDistanceSoFar

    # finds the distance from a point to pacman
    def findDistance(self, location, game):
        (x, y) = (location[0], location[1])
        (pacX, pacY) = game.pacman.currentLocation
        distanceSquared = (pacX - x) ** 2 + (pacY - y) ** 2
        distance = math.sqrt(distanceSquared)
        return distance

    # changes ghost location when it is gliding
    def glide(self, game):
        gridChange = float(self.speed) / game.gameMap.scalingFactor
        newRow = self.currentLocation[0] + gridChange * self.direction.grid[0]
        newCol = self.currentLocation[1] + gridChange * self.direction.grid[1]
        if game.almostEquals(newRow, round(newRow)) and \
                game.almostEquals(newCol, round(newCol)):
            self.currentLocation = (int(round(newRow)), int(round(newCol)))
            self.gliding = False
        else:
            self.currentLocation = (newRow, newCol)

    # ghost draws itself
    def draw(self, game):
        canvas = game.canvas
        (width, height) = (game.width, game.height)
        (row, col) = self.currentLocation
        pixelCenter = game.currentPoint.pixels
        x = game.gameMap.findVisualCoordinate(col, pixelCenter[0], width)
        y = game.gameMap.findVisualCoordinate(row, pixelCenter[1], height)
        r = self.r
        canvas.create_oval(x - r, y - r, x + r, y + r, fill = self.color,
                                        width = 0)
        canvas.create_rectangle(x - r, y, x + r, y + r, fill = self.color,
                                        width = 0)
        self.drawTentacles(canvas, x, y)
        self.drawEyes(canvas, x, y)

    # draws the Tentacles
    def drawTentacles(self, canvas, x, y):
        x0 = x - self.r
        y0 = y + self.r
        step = 3 * self.r / 4
        dHeight = self.r / 3
        dWidth = self.r / 3.6
        numberOfTentacles = 3
        for i in xrange(numberOfTentacles):
            (y1, y2) = (y0 - dHeight, y0 + dHeight)
            x1 = x0 + i * step
            x2 = x1 + 2 * dWidth
            canvas.create_oval(x1, y1, x2, y2, fill = self.color, width = 0)

    # draws the eyes
    def drawEyes(self, canvas, x, y):
        dx = self.r / 2.5
        y0 = y - self.r / 4
        dWidth = self.r / 5
        dHeight = self.r / 3
        pupil = self.r / 7
        cornea = "white" if not self.color == "white" else "gray"
        canvas.create_oval(x - dx - dWidth, y0 - dHeight, x - dx + dWidth,
                    y0 + dHeight, fill = cornea, width = 0)
        canvas.create_oval(x - dx - pupil, y0 - pupil, x - dx + pupil,
                    y0 + pupil, fill = "blue", width = 0)
        canvas.create_oval(x + dx - dWidth, y0 - dHeight, x + dx + dWidth,
                    y0 + dHeight, fill = cornea, width = 0)
        canvas.create_oval(x + dx - pupil, y0 - pupil, x + dx + pupil,
                    y0 + pupil, fill = "blue", width = 0)

# Button class for a button at a location with text and or color,
# 2.0 rendition now auto initializes values and allows for font changes
class BetterButton(object):

    # initializing a button for a designated screen location, with a color
    def __init__(self, point1, point2, text="", fill=None, font="arial 15"):
        self.clicked = False
        self.corner1 = point1
        self.corner2 = point2
        self.text = text
        self.font = font
        self.color = fill
        self.width = 0

    # the button draws itself on the canvas
    def draw(self, canvas):
        (p1, p2) = (self.corner1, self.corner2)
        text = self.text
        fill = self.color
        canvas.create_rectangle(p1, p2, fill = fill, width = self.width)
        midX = (p1[0] + p2[0]) / 2
        midY = (p1[1] + p2[1]) / 2
        canvas.create_text(midX, midY, text = text, font = self.font)

    # button returns if mouseclick is within its bounds
    def isClicked(self, x, y):
        (p1, p2) = (self.corner1, self.corner2)
        xCheck = p1[0] < x and x < p2[0]
        yCheck = p1[1] < y and y < p2[1]
        return xCheck and yCheck

# Checkbox class creates a new square button that can be 'checked'
class CheckBox(BetterButton):

    # initializes based on a corner and a side length
    def __init__(self, p1, side):
        p2 = (p1[0] + side, p1[1] + side)
        super(CheckBox, self).__init__(p1, p2, text ="", fill = "white")
        self.width = 3

    # knows when checked on click
    def isClicked(self, x, y):
        if super(CheckBox, self).isClicked(x, y):
            self.clicked = not self.clicked
            return True
        return False

    # draws itself checked or not checked, depending...
    def draw(self, canvas):
        super(CheckBox, self).draw(canvas)
        if self.clicked:
            canvas.create_line(self.corner1, self.corner2, width = self.width)
            (p1, p2) = (self.corner1, self.corner2)
            p3 = (p1[0], p2[1])
            p4 = (p2[0], p1[1])
            canvas.create_line(p3, p4, width = self.width)


PacGame().run()