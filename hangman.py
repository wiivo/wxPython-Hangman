#!/usr/bin/env python3
from random import choice
import string
import wx
import os


class MyForm(wx.Frame):
    def __init__(self):
        # initialize frame
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Hangman")
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.CreateStatusBar()

        # initialize fail counter and hanged man image
        self.failCounter = 0
        self.bitmap = wx.Bitmap(
            os.path.join(os.path.dirname(__file__), "hangman", "0.jpg")
        )
        self.image = wx.StaticBitmap(self.panel, 0, self.bitmap)

        # initialize word
        self.answer = getWord()
        # creates initial bitmask we use to determine which letters are visible using bit operators
        # example bitmask -> APPLE = 10001 = 10000 | 00001
        self.bitmask = 1 << (len(self.answer) - 1) | 1

        # mark non-letters also with 1
        for i in range(1, len(self.answer) - 1):
                if self.answer[i] not in string.ascii_letters:
                    self.bitmask = self.bitmask | 1 << i

        self.word = wx.StaticText(
            self.panel, wx.ID_ANY, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        self.displayWord()

        # initialize letter buttons
        self.buttons = []
        for i in range(26):
            self.buttons.append(
                wx.ToggleButton(
                    self.panel, wx.ID_ANY, string.ascii_uppercase[i], size=(40, -1)
                )
            )
            self.buttons[i].Bind(wx.EVT_TOGGLEBUTTON, self.onLetterPress)

        # initialize New Game button
        resetButton = wx.Button(self.panel, wx.ID_ANY, "New Game", size=(180, -1))
        resetButton.Bind(wx.EVT_BUTTON, self.reset)

        # sizer for the letter buttons
        buttonSizer = wx.FlexGridSizer(0, 7, 5, 10)
        for i in range(26):
            # add an empty staticText to the sizer so the last row is centered
            # there might be a better way to do this
            if i == 21:
                buttonSizer.Add(wx.StaticText(self.panel), 0, wx.ALL, 0)
            buttonSizer.Add(self.buttons[i], 0, wx.ALL, 0)

        # put everything in one BoxSizer
        topSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer.Add(self.image, 0, wx.ALL | wx.EXPAND, 3)
        topSizer.Add(self.word, 0, wx.ALL | wx.EXPAND, 6)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 6)
        topSizer.Add(buttonSizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 6)
        topSizer.Add(resetButton, 0, wx.ALL | wx.ALIGN_CENTER, 12)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

    def displayWord(self):
        # shows visible letters using the bitmask by modifying the label on self.word
        newDisplay = ""
        # goes through bitmask
        # if 1 -> appends coresponding letter to newDisplay
        # if 0 -> appends '_' to newDisplay
        for i in range(len(self.answer)):
            if (self.bitmask >> i) & 1:
                newDisplay = newDisplay + self.answer[i] + " "
            else:
                newDisplay = newDisplay + "_ "
        self.word.SetLabel(newDisplay)

    def onLetterPress(self, event):
        # only does actions if the button hasn't been pressed
        if event.GetEventObject().GetValue() == True:
            letter = event.GetEventObject().GetLabel()

            # finds if there are any matches and updates the bitmask and the display
            # if there are no matches, failCounter goes up and the image updates
            hasLetter = False
            for i in range(1, len(self.answer) - 1):
                if self.answer[i] == letter:
                    hasLetter = True
                    self.bitmask = self.bitmask | 1 << i

            if hasLetter:
                self.SetStatusText("Good Guess!")

                # if you have guessed all the letters the game ends
                if (1 << len(self.answer)) - 1 == self.bitmask:
                    self.gameOver(True)
                else:
                    self.displayWord()
            else:
                self.failCounter = self.failCounter + 1
                self.bitmap.LoadFile(
                    os.path.join(
                        os.path.dirname(__file__),
                        "hangman",
                        repr(self.failCounter) + ".jpg",
                    )
                )
                self.image.SetBitmap(self.bitmap)
                self.SetStatusText(
                    "Wrong! You have " + repr(6 - self.failCounter) + " tries left."
                )

                # if you failed too many times the game also ends
                if self.failCounter > 5:
                    self.gameOver(False)

        # makes it so the button can't be unpressed
        event.GetEventObject().SetValue(True)

    def gameOver(self, hasWon: bool):
        # the game ends by making all the buttons unclickable and showing the answer
        for i in self.buttons:
            i.SetValue(True)
        for i in range(1, len(self.answer) - 1):
            self.bitmask = self.bitmask | 1 << i
        if hasWon:
            self.word.SetForegroundColour((0,128,0))
            self.SetStatusText("Game Over. You Win!")
        else:
            self.word.SetForegroundColour((128,0,0))
            self.SetStatusText("Game Over. You Lose!")
        self.displayWord()
            
    
    def reset(self, event):
        # puts game back to initial state
        self.failCounter = 0

        self.bitmap.LoadFile(
            os.path.join(os.path.dirname(__file__), "hangman", "0.jpg")
        )
        self.image.SetBitmap(self.bitmap)

        self.answer = getWord()
        self.bitmask = 1 << (len(self.answer) - 1) | 1
        for i in range(1, len(self.answer) - 1):
                if self.answer[i] not in string.ascii_letters:
                    self.bitmask = self.bitmask | 1 << i
        self.word.SetForegroundColour((0,0,0))
        self.displayWord()

        for i in self.buttons:
            i.SetValue(False)

        self.SetStatusText("")


def getWord():
    # picks a random word from words.txt
    word = ""
    while(len(word) < 2):
        file = open(os.path.join(os.path.dirname(__file__), "words.txt"), "r")
        word = choice(file.read().split("\n"))
        file.close()
    # print("Hint: The word is" + word)
    return word.upper()


app = wx.App()
frame = MyForm().Show()
app.MainLoop()
