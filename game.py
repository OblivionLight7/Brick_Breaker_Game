import tkinter as tk
import random
import math
import copy
from tkinter.constants import NE, SE
#from util.color import Color

# Main class: inherit from tk.Canvas class
class Game(tk.Canvas):
    textDisplayed = False
    linesNb = 20
    seconds = 0

    # Bar properties
    barHeight = 20
    barSpeed = 10

    # Ball property
    ballSpeed = 7

    # Bricks properties
    bricks = []
    bricksWidth = 50
    bricksHeight = 20
    bricksNbByLine = 16
    bricksColors = {
        "r": "#e74c3c",
        "g": "#2ecc71",
        "b": "#3498db",
        "t": "#1abc9c",
        "p": "#9b59b6",
        "y": "#f1c40f",
        "o": "#e67e22",
    }

    # Screen properties
    screenHeight = 500
    screenWidth = bricksWidth * bricksNbByLine

    lives = 3
    score = 0

    # This method initializes some attributes: the ball, the bar...
    def __init__(self, root):
        tk.Canvas.__init__(self, root, bg="#ffffff", bd=0, highlightthickness=0, relief="ridge", width=self.screenWidth, height=self.screenHeight)
        self.pack()
        #self.timeContainer = self.create_text(self.screenWidth/2, self.screenHeight*4/5, text="00:00:00", fill="#cccccc", font=("Arial", 30), justify="center")
        self.shield = self.create_rectangle(0, 0, 0, 0, width=0)              
        self.bar = self.create_rectangle(0, 0, 0, 0, fill="#7f8c8d", width=0)
        self.ball = self.create_oval(0, 0, 0, 0, width=0)
        self.ballNext = self.create_oval(0, 0, 0, 0, width=0, state="hidden") 
        self.level(1)
        self.nextFrame()

    # This method, called each time a level is loaded or reloaded,
    # resets all the elements properties (size, position...).
    def reset(self):
        self.barWidth = 100
        self.ballRadius = 7
        self.coords(self.shield, (0, self.screenHeight-5, self.screenWidth, self.screenHeight))
        self.itemconfig(self.shield, fill=self.bricksColors["b"], state="hidden")
        self.coords(self.bar, ((self.screenWidth - self.barWidth)/2, self.screenHeight - self.barHeight, (self.screenWidth + self.barWidth)/2, self.screenHeight))
        self.coords(self.ball, (self.screenWidth/2 - self.ballRadius, self.screenHeight - self.barHeight - 2*self.ballRadius, self.screenWidth/2 + self.ballRadius, self.screenHeight - self.barHeight))
        self.itemconfig(self.ball, fill="#2c3e50")
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))
        self.effects = {
            "ballFire": [0, 0],
            "barTall":  [0, 0],
            "ballTall": [0, 0],
            "shield":   [0,-1],
        }
        self.effectsPrev = copy.deepcopy(self.effects)
        self.ballThrown = False
        self.keyPressed = [False, False]
        self.losed = False
        self.won = False
        self.ballAngle = math.radians(90)
        for brick in self.bricks:
            self.delete(brick)
            del brick

    def putpixel(self, x, y) -> None:
	    self.create_rectangle(x, y, x, y)

    def sigmoid(self, val):
        if val > 0: 
            return 1
        if val < 0: 
            return -1
        return 0
    



    def creates_oval(self, cx,  cy,  r): 
        x = 0
        y = r
        S = 3 - 2 * r

        while x <= y:
            self.putpixel(cx + x, cx + y)
            self.putpixel(cx + x, cx - y)
            self.putpixel(cx - x, cx + y)
            self.putpixel(cx - x, cx - y)

            self.putpixel(cx + y, cx + x)
            self.putpixel(cx + y, cx - x)
            self.putpixel(cx - y, cx + x)
            self.putpixel(cx - y, cx - x)

            x = x + 1
            
            if S <= 0:
                S += 4 * x + 6
            else:
                y = y - 1
                S += 4 * (x - y) + 10



    # This method displays the Nth level by reading the corresponding file (N.txt).
    def level(self, level):
        self.reset()
        self.levelNum = level
        self.bricks = []

        try:
            file = open(str(level) + ".txt")
            content = list(file.read().replace("\n", ""))[:(self.bricksNbByLine * self.linesNb)]
            file.close()
            for i, el in enumerate(content):
                col = i % self.bricksNbByLine
                line = i // self.bricksNbByLine
                if el != ".":
                    self.bricks.append(self.create_rectangle(col*self.bricksWidth, line*self.bricksHeight, (col+1)*self.bricksWidth, (line+1)*self.bricksHeight, fill=self.bricksColors[el], width=2, outline="#ffffff"))
        except IOError:     
            self.displayText("Congratulations! You completed game\nYour Final Score is\n" + "%02d" % self.score, hide = False)
            return
        self.displayText("LEVEL\n"+str(self.levelNum))
        

    def nextFrame(self):
        Label_middle = tk.Label(root, text = "Score:\n" + "%02d" % self.score)
        Label_middle.place(relx = 0.1, rely = 0.1, anchor = SE) 
        Label_middle = tk.Label(root, text = "Lives left:\n" + "%02d" % self.lives)
        Label_middle.place(relx = 0.98, rely = 0.1, anchor=SE) 
        
        if self.ballThrown and not(self.textDisplayed):
            self.moveBall()

                   
        self.updateEffects()

        if self.keyPressed[0]:
            self.moveBar(-game.barSpeed)
        elif self.keyPressed[1]:
            self.moveBar(game.barSpeed)

        if not(self.textDisplayed):
           
            if self.won:
                self.score += 50
                self.displayText("WON!", callback = lambda: self.level(self.levelNum + 1))
            elif self.losed:
                if self.lives != 0:
                    self.lives = self.lives - 1
                    self.displayText("LOST! Next Chance!!", callback = lambda: self.level(self.levelNum))
                    
                else:
                   self.displayText("You lost!\nYour Final Score is\n" + "%02d" % self.score, hide = False)

        self.after(int(1000/60), self.nextFrame)

    # This method, called when left or right arrows are pressed
    def moveBar(self, x):
        barCoords = self.coords(self.bar)
        if barCoords[0] < 10 and x < 0:
            x = -barCoords[0]
        elif barCoords[2] > self.screenWidth - 10 and x > 0:
            x = self.screenWidth - barCoords[2]
        
        self.move(self.bar, x, 0)
        if not(self.ballThrown):
            self.move(self.ball, x, 0)

    # This method, called at each frame, moves the ball.
    def moveBall(self):
        self.move(self.ballNext, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        ballNextCoords = self.coords(self.ballNext)
        
        i = 0
        while i < len(self.bricks):
            collision = self.collision(self.ball, self.bricks[i])
            collisionNext = self.collision(self.ballNext, self.bricks[i])
            if not collisionNext:
                brickColor = self.itemcget(self.bricks[i], "fill")
                
                # "barTall" effect (green bricks)
                if brickColor == self.bricksColors["g"]:
                    self.effects["barTall"][0] = 1
                    self.effects["barTall"][1] = 240
                # "shield" effect (blue bricks)
                elif brickColor == self.bricksColors["b"]:
                    self.effects["shield"][0] = 1
                # "ballFire" effect (purple bricks)
                elif brickColor == self.bricksColors["p"]:
                    self.effects["ballFire"][0] += 1
                    self.effects["ballFire"][1] = 240
                # "ballTall" effect (turquoise bricks)
                elif brickColor == self.bricksColors["t"]:
                    self.effects["ballTall"][0] = 1
                    self.effects["ballTall"][1] = 240

                if not(self.effects["ballFire"][0]):
                    if collision == 1 or collision == 3:
                        self.ballAngle = math.radians(180) - self.ballAngle
                    if collision == 2 or collision == 4:
                        self.ballAngle = -self.ballAngle
                
                # If the brick is red, it becomes orange.
                if brickColor == self.bricksColors["r"]:
                    self.score += 10
                    self.itemconfig(self.bricks[i], fill=self.bricksColors["o"])
                # If the brick is orange, it becomes yellow.
                elif brickColor == self.bricksColors["o"]:
                    self.score += 10
                    self.itemconfig(self.bricks[i], fill=self.bricksColors["y"])
                # If the brick is yellow (or an other color except red/orange), it is destroyed.
                else:
                    self.score += 10
                    self.delete(self.bricks[i])
                    del self.bricks[i]
            i += 1

        self.won = len(self.bricks) == 0

        if ballNextCoords[0] < 0 or ballNextCoords[2] > self.screenWidth:
            self.ballAngle = math.radians(180) - self.ballAngle
        elif ballNextCoords[1] < 0:
            self.ballAngle = -self.ballAngle
        elif not(self.collision(self.ballNext, self.bar)):
            ballCenter = self.coords(self.ball)[0] + self.ballRadius
            barCenter = self.coords(self.bar)[0] + self.barWidth/2
            angleX = ballCenter - barCenter
            angleOrigin = (-self.ballAngle) % (3.14159*2)
            angleComputed = math.radians(-70/(self.barWidth/2)*angleX + 90)
            self.ballAngle = (1 - (abs(angleX)/(self.barWidth/2))**0.25)*angleOrigin + ((abs(angleX)/(self.barWidth/2))**0.25)*angleComputed
        elif not(self.collision(self.ballNext, self.shield)):
            if self.effects["shield"][0]:
                self.ballAngle = -self.ballAngle
                self.effects["shield"][0] = 0
            else :
                self.losed = True

        self.move(self.ball, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))

    # This method, called at each frame, manages the remaining time
    # for each of effects and displays them (bar and ball size...).
    def updateEffects(self):
        for key in self.effects.keys():
            if self.effects[key][1] > 0:
                self.effects[key][1] -= 1
            if self.effects[key][1] == 0:
                self.effects[key][0] = 0
        
        if self.effects["ballFire"][0]:
            self.itemconfig(self.ball, fill=self.bricksColors["p"])
        else:
            self.itemconfig(self.ball, fill="#2c3e50")

        if self.effects["barTall"][0] != self.effectsPrev["barTall"][0]:
            diff = self.effects["barTall"][0] - self.effectsPrev["barTall"][0]
            self.barWidth += diff*60
            coords = self.coords(self.bar)
            self.coords(self.bar, tk._flatten((coords[0]-diff*30, coords[1], coords[2]+diff*30, coords[3])))
        
        if self.effects["ballTall"][0] != self.effectsPrev["ballTall"][0]:
            diff = self.effects["ballTall"][0] - self.effectsPrev["ballTall"][0]
            self.ballRadius += diff*10
            coords = self.coords(self.ball)
            self.coords(self.ball, tk._flatten((coords[0]-diff*10, coords[1]-diff*10, coords[2]+diff*10, coords[3]+diff*10)))
        
        if self.effects["shield"][0]:
            self.itemconfig(self.shield, fill=self.bricksColors["b"], state="normal")
        else:
            self.itemconfig(self.shield, state="hidden")

        self.effectsPrev = copy.deepcopy(self.effects)

    # This method displays some text.
    def displayText(self, text, hide = True, callback = None):
        self.textDisplayed = True
        self.textContainer = self.create_rectangle(0, 0, self.screenWidth, self.screenHeight, fill="#ffffff", width=0, stipple="gray50")
        self.text = self.create_text(self.screenWidth/2, self.screenHeight/2, text=text, font=("Arial", 25), justify="center")
        if hide:
            self.after(3000, self.hideText)
        if callback != None:
            self.after(3000, callback)

    # This method deletes the text display.
    def hideText(self):
        self.textDisplayed = False
        self.delete(self.textContainer)
        self.delete(self.text)

    # This method computes the relative position of 2 objects that is collisions.
    def collision(self, el1, el2):
        collisionCounter = 0

        objectCoords = self.coords(el1)
        obstacleCoords = self.coords(el2)
        
        if objectCoords[2] < obstacleCoords[0] + 5:
            collisionCounter = 1
        if objectCoords[3] < obstacleCoords[1] + 5:
            collisionCounter = 2
        if objectCoords[0] > obstacleCoords[2] - 5:
            collisionCounter = 3
        if objectCoords[1] > obstacleCoords[3] - 5:
            collisionCounter = 4
                
        return collisionCounter


# This function is called on key down.
def eventsPress(event):
    global game, hasEvent

    if event.keysym == "Left":
        game.keyPressed[0] = 1
    elif event.keysym == "Right":
        game.keyPressed[1] = 1
    elif event.keysym == "space" and not(game.textDisplayed):
        game.ballThrown = True

# This function is called on key up.
def eventsRelease(event):
    global game, hasEvent
    
    if event.keysym == "Left":
        game.keyPressed[0] = 0
    elif event.keysym == "Right":
        game.keyPressed[1] = 0


# Initialization of the window
root = tk.Tk()
root.title("Brick Breaker")
root.resizable(0,0)
root.bind("<Key>", eventsPress)
root.bind("<KeyRelease>", eventsRelease)

# Starting up of the game
game = Game(root)
root.mainloop()
