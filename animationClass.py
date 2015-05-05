from Tkinter import *

# basic MVC animation setup with Tkinter
class EventBasedAnimationClass(object):

    def __init__(self, width=300, height=300):
        (self.width, self.height) = (width, height)
        self.timerDelay = 250 # milliseconds, this delay between timer events

    def run(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, height=self.height, width=self.width)
        self.canvas.pack()

        #now start the animation sequence, create the model
        # (note nonstandard actions will be bound to the root here)
        self.initAnimation()

        # add actions
        self.root.bind("<Button-1>", lambda event: self.onMousePressedWrapper(event))
        self.root.bind("<Key>", lambda event: self.onKeyPressedWrapper(event))
        self.onTimerFiredWrapper()

        # run the program
        self.root.mainloop()

    def onMousePressedWrapper(self, event):
        self.onMousePressed(event)
        self.redrawAll()

    def onKeyPressedWrapper(self, event):
        self.onKeyPressed(event)
        self.redrawAll()

    def onTimerFiredWrapper(self):

        self.onTimerFired()
        self.redrawAll()
        self.canvas.after(self.timerDelay, self.onTimerFiredWrapper)

    def onMousePressed(self, event): pass
    def onKeyPressed(self, event): pass
    def onTimerFired(self): pass
    def initAnimation(self): pass
    def redrawAll(self): pass
