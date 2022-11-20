from sys import exit
from os import environ
import pygame
from pygame.locals import *

SCREENSIZE = (640, 480)

environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)

pygame.font.init()
fnt = pygame.font.SysFont("Arial", 14)
txtpos = (100, 90)

class Body:
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Player:
    def __init__(self,x,y,color,id):
        self.x = x
        self.y = y
        self.direction = 0
        self.nextDirection = 0
        self.id = id
        self.color=color
        self.lenght = 0;
        self.body = []
        self.body.append(Body(50,50))
        self.speed=1

class Map:
    def __init__(self, x, y):
        self.sizeX = x
        self.sizeY = y
        self.appleList = []

    def drawMap(self):
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                pygame.draw.rect(screen, Color(100, 100, 100), Rect(x * 10, y * 10, 10, 10), 1)
        for i in range(len(self.appleList)):
            pygame.draw.rect(screen, Color(255, 0, 0), Rect(self.appleList[i].x * 10, self.appleList[i].y * 10, 10, 10),0)


class Whiteboard:
    def __init__(self):

        self.down = False


