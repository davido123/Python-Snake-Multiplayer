import sys
from time import *
from PodSixNet.Connection import connection, ConnectionListener
from Whiteboard import *
from pygame import *

squaresize = 30
mapsizex = 40
mapsizey = 40

scrx = squaresize * mapsizex
scry = squaresize * mapsizey + squaresize

SCREENSIZE = (scrx, scry)

environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)

pygame.font.init()

font_style = pygame.font.SysFont("Arial", 20)
font_style2 = pygame.font.SysFont("Arial", 100)
font_style3 = pygame.font.SysFont("Arial", 40)
font_style4 = pygame.font.SysFont("Arial", 15)
font_style.set_bold(1)
font_style4.set_bold(1)
# txtpos = (100, 90)
clock = pygame.time.Clock()
# textures = pygame.image.load('Textures.png').convert_alpha()
startsceen = pygame.image.load('StartScreen.png')
resstartscreen = pygame.transform.scale(startsceen, (scrx, scry))


# resizedtx= pygame.transform.scale(textures,(int(textures.get_width()/24),int(textures.get_height()/24)))
# tex=[]
# for y in range (0,2):
# for x in range (0,7):
# tex.append(resizedtx.subsurface(pygame.Rect(x*squaresize, y*squaresize, squaresize, squaresize)))


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Body:
    def __init__(self, pos, dirnx=0, dirny=0):
        self.pos = pos
        self.dirnx = dirnx
        self.dirny = dirny


class Player:
    def __init__(self, x, y, nick, color, id):
        self.x = x
        self.y = y
        self.nickname = nick
        self.id = id
        self.color = color
        self.body = []
        self.dirnx = 0
        self.dirny = 0
        self.speed = 1
        self.points = 0
        self.ready = 0

    def __eq__(self, other):
        return self.id == other.id


class Map:
    def __init__(self, x, y):
        self.sizeX = x
        self.sizeY = y
        self.appleList = []

class Client(ConnectionListener, Whiteboard):
    def __init__(self, host, port):
        super().__init__()
        self.Connect((host, port))
        self.id = 0
        self.playerdictionary = {}
        self.minions = []
        self.canapplyminion = 1
        self.player = Player(0, 0, "", Color(0, 0, 0), 0)
        self.map = Map(mapsizex, mapsizey)
        self.statusLabel = "connecting"
        self.clock = pygame.time.get_ticks()
        self.seconds = 0
        self.frame = 0
        self.pingms = 0
        self.apples = []
        self.drawinfo = 0
        self.allready = 0
        self.ready=0
        self.connected = 0
        self.nickname = ""
        self.collided=0
        self.win=0


    def message(self, msg, x, y, color=None, font=font_style):

        if color is not None:
            mesg = font.render(msg, True, color)
        else:
            mesg = font.render(msg, True, Color(0, 0, 0))
        screen.blit(mesg, [x, y])

    def ProcessClick(self, m):
        if(self.ready==0):
            self.ready = 1
            connection.Send({"action":"imready","id":self.id})

    def Events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 27):
                exit()
            if event.type == KEYDOWN:
                self.KeyPress(event)
            if event.type == MOUSEBUTTONDOWN:
                self.ProcessClick(event)

    def DrawNoServer(self):
        screen.fill([255, 255, 255])
        str = "Nie znaleziono serwera"
        str2 = "uruchom serwer i zrestartuj gre"
        strw, strh = font_style3.size(str)
        str2w, str2h = font_style3.size(str2)
        self.message(str, scrx / 2 - strw / 2, scry / 2 - strh / 2 - squaresize, Color(0, 0, 0), font_style3)
        self.message(str2, scrx / 2 - str2w / 2, scry / 2 - str2h / 2 - squaresize + 50, Color(0, 0, 0), font_style3)
        pygame.display.flip()

    def Draw(self, minions):
        screen.fill([255, 255, 255])
        self.drawPlayers()
        self.drawHead()
        self.drawEyes()

        if (self.allready == 0):
            str1 = "Oczekiwanie na innych graczy"
            str1w, str1h = font_style.size(str1)
            self.message(str1, scrx / 2 - str1w / 2, scry / 2 - str1h / 2 - squaresize, Color(0, 0, 0), font_style)

        if (self.collided==1):
            str1 = "Przegrales"
            str1w, str1h = font_style.size(str1)
            self.message(str1, scrx / 2 - str1w / 2, scry / 2 - str1h / 2 - squaresize, Color(255, 0, 0), font_style)

        if (self.win==1):
            str1 = "Wygrales"
            str1w, str1h = font_style.size(str1)
            self.message(str1, scrx / 2 - str1w / 2, scry / 2 - str1h / 2 - squaresize, Color(0, 255, 0), font_style)

        if (self.drawinfo):
            self.message("Game info:", 410, 10,None,font_style4)

            self.message("Connection Status:", 410, 30,None,font_style4)
            self.message(self.statusLabel, 510, 30,None,font_style4)

            self.message("Players count", 410, 50,None,font_style4)
            self.message(str(len(self.minions)), 510, 50,None,font_style4)

            self.message("MY ID:" + str(self.id), 410, 70,None,font_style4)

            self.message("loop speed:" + str(pygame.time.get_ticks()), 410, 100,None,font_style4)
            self.message("fps:" + str(clock.get_fps()), 410, 120,None,font_style4)
            self.message("ping:" + str(self.pingms), 410, 150,None,font_style4)
            self.message("nacisnij TAB aby usunąć informacje", 410, 170,None,font_style4)

        self.drawApples()
        stringoffset = 0
        for i in range(len(self.minions)):
            if i == 0:
                pygame.draw.rect(screen, (200, 200, 200), Rect(0, 0, squaresize * mapsizex, squaresize))
                self.message("Punkty:", 2, squaresize / 4, None, font_style4)
            strnick = str(self.minions[i].nickname)
            strpts = " Punkty:" + str(self.minions[i].points)
            strlen = strnick + strpts
            w, h = font_style4.size(strlen)

            self.message(strnick + strpts, 50 + stringoffset, squaresize / 4, self.minions[i].color, font_style4)
            stringoffset += w + 10

        # self.message("MESSAGE",X,Y,Color(optional))

        pygame.display.flip()
        self.frame += 1

    def drawPlayers(self):
        for i in range(len(self.minions)):
            for j in range(1, len(self.minions[i].body)):
                # self.message(self.minions[i].nickname,self.minions[i].body[j].x-20,self.minions[i].body[j].y-20)
                pygame.draw.rect(screen, self.minions[i].color,
                                 Rect(self.minions[i].body[j].pos[0], self.minions[i].body[j].pos[1]+squaresize, squaresize,
                                      squaresize), 0)
                # screen.blit(tex[2],(self.minions[i].body[j].pos[0], self.minions[i].body[j].pos[1]))

    def drawHead(self):
        for i in range(len(self.minions)):
            pygame.draw.rect(screen, self.minions[i].color,
                             Rect(self.minions[i].body[0].pos[0], self.minions[i].body[0].pos[1]+squaresize, squaresize,
                                  squaresize), 0)

    def drawEyes(self):
        for i in range(len(self.minions)):
            for j in range(len(self.minions[i].body)):
                pygame.draw.circle(screen, (0, 0, 0), (
                    int(self.minions[i].body[0].pos[0] + squaresize / 2 - squaresize / 6),
                    int(self.minions[i].body[0].pos[1] + squaresize / 2 - squaresize / 8)+squaresize), 3)
                pygame.draw.circle(screen, (0, 0, 0), (
                    int(self.minions[i].body[0].pos[0] + squaresize / 2 + squaresize / 6),
                    int(self.minions[i].body[0].pos[1] + squaresize / 2 - squaresize / 8)+squaresize), 3)

    def drawApples(self):
        for i in range(len(self.apples)):
            pygame.draw.rect(screen, Color(255, 0, 0),
                             Rect(self.apples[i].pos[0], self.apples[i].pos[1]+squaresize, squaresize, squaresize), 0)

    def drawMenu(self):
        screen.fill([255, 255, 255])
        # screen.blit(tex[2],(self.minions[i].body[j].pos[0], self.minions[i].body[j].pos[1]))
        screen.blit(resstartscreen, (0, 0))

        pygame.display.flip()

    def ping(self):
        if (self.frame % 60 == 0):
            connection.Send({"action": "ping", "time": str(pygame.time.get_ticks())})

    def Loop(self):###########################glowna petla gry
        clock.tick(600)
        self.ping()

        seconds = (pygame.time.get_ticks() - self.clock)
        self.Pump()
        connection.Pump()
        self.Events()
        readycounter = 0
        for i in range(len(self.minions)):

            if(self.minions[i].ready):
                readycounter+=1
            if readycounter == len(self.minions) and readycounter>=2:
                self.allready=1

        if (self.ready == False):
            self.drawMenu()
        elif (self.connected == False):
            self.DrawNoServer()
        else:
            self.Draw(self.minions)

        if "connecting" in self.statusLabel:
            self.statusLabel = "connecting" + "".join(["." for s in range(int(self.frame / 30) % 4)])

    #######################
    ### Event callbacks ###
    #######################
    # def PenDraw(self, e):
    #    connection.Send({"action": "draw", "point": e.pos})
    def KeyPress(self, e):
        if self.allready == 1:

            otherid=0
            for i in range(len(self.minions)):
                if self.id != self.minions:
                    otherid=self.minions[i].id

            if e.key == K_LEFT:
                connection.Send({"action": "changedirection", "dir": 1, "id": self.id})
            if e.key == K_RIGHT:
                connection.Send({"action": "changedirection", "dir": 2, "id": self.id})
            if e.key == K_UP:
                connection.Send({"action": "changedirection", "dir": 3, "id": self.id})
            if e.key == K_DOWN:
                connection.Send({"action": "changedirection", "dir": 4, "id": self.id})
            if e.key == K_a:
                connection.Send({"action": "changedirection", "dir": 1, "id": otherid})
            if e.key == K_d:
                connection.Send({"action": "changedirection", "dir": 2, "id": otherid})
            if e.key == K_w:
                connection.Send({"action": "changedirection", "dir": 3, "id": otherid})
            if e.key == K_s:
                connection.Send({"action": "changedirection", "dir": 4, "id": otherid})

        if e.key == K_TAB:
            if (self.drawinfo == 0):
                self.drawinfo = 1
            else:
                self.drawinfo = 0

    ###############################
    ### Network event callbacks ###
    ###############################
    def Network_selfcollision(self,data):
        idd=data["id"]
        if self.id==idd:
            self.collided=1
        else:
            self.win=1

    def Network_headcollision(self,data):
        self.collided=1

    def Network_othercollision(self,data):
        idd = data["id"]
        if self.id == idd:
            self.collided = 1
        elif(self.collided==0):
            self.win = 1

   # def Network_headcollision(self,data):
   #     idd=data["id"]
    #    for i in range(len(self.minions)):
     #       if self.minions[i].id==idd:
      #          self.collided=1

    def Network_initid(self, data):
        self.id = data['id']

    def Network_ping(self, data):
        time = data["time"]
        self.pingms = pygame.time.get_ticks() - int(time)

    def Network_update(self, data):
        x = data["x"]
        y = data["y"]
        j = data["j"]
        id = data["id"]
        ready= data["ready"]
        for i in range(len(self.minions)):
            if id == self.minions[i].id:
                try:
                    self.minions[i].body[j].pos = (x, y)
                    self.minions[i].ready=ready
                except:
                    self.minions[i].body.append(Body((x, y)))

    def Network_addpoints(self, data):
        idd = data["id"]
        for i in range(len(self.minions)):
            if (self.minions[i].id == idd):
                self.minions[i].points += 1

    def Network_updateapple(self, data):
        x = data["x"]
        y = data["y"]
        self.apples.clear()
        self.apples.append(Body([x, y]))

    def Network_initial(self, data):  # get base data of players and you from server
        self.connected = 1
        x = data['x']
        y = data['y']
        id = data['id']
        r = data['r']
        g = data['g']
        b = data['b']
        nick = data['nick']
        player = Player(x, y, nick, Color(r, g, b), id)
        player.body.append(Body((x, y)))
        # print("my id:" + str(self.id) + " incoming id:" + str(id))
        if (player not in self.minions):  # ensure you dont duplicate yourself on other client connecting
            self.minions.append(player)

    def Network_playerdc(self, data):  # on other player disconnect
        # self.playersLabel = str(len(data['players'])) + " players"
        mark = []
        delid = data["playerid"]
        for i in range(len(self.minions)):
            if (self.minions[i].id == delid):
                mark.append(i)

        for m in mark:
            del self.minions[m]

    def Network(self, data):
        # print('network:', data)
        pass

    def Network_connected(self, data):
        self.statusLabel = "connected"

    def Network_error(self, data):
        print(data)
        import traceback
        traceback.print_exc()
        self.statusLabel = data['error'][1]
        connection.Close()

    def Network_disconnected(self, data):
        self.statusLabel += " - disconnected"


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        c = Client(host, int(port))
        while 1:
            c.Loop()
            # sleep(0.001)
