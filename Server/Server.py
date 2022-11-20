import random
import sys
from time import *
from weakref import WeakKeyDictionary

import pygame
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

pygame.init()
minions = []
snacks = []
nicknames = ['John', 'Dreamer', 'Jacek', 'Mario', 'Esmeralda', 'Geralt']
map = (40, 40)
squaresize = 30
clock = pygame.time.Clock()


class Body:
    def __init__(self, pos, dirnx=0, dirny=0):
        self.pos = pos
        self.dirnx = dirnx
        self.dirny = dirny

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)


class Player:
    def __init__(self, x, y, nickname, r, g, b, id):
        self.x = x
        self.y = y
        self.direction = 0
        self.nextDirection = 0
        self.nickname = nickname
        self.id = id
        self.color = pygame.color
        self.r = r
        self.g = g
        self.b = b
        self.head = Body((x, y))
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.stopmoving = 0
        self.points = 0
        self.ready = 0

    def addBody(self):
        tail = self.body[-1]

        dx, dy = tail.dirnx, tail.dirny

        if dx == squaresize and dy == 0:
            self.body.append(Body((tail.pos[0] - squaresize, tail.pos[1])))
        elif dx == -squaresize and dy == 0:
            self.body.append(Body((tail.pos[0] + squaresize, tail.pos[1])))
        elif dx == 0 and dy == squaresize:
            self.body.append(Body((tail.pos[0], tail.pos[1] - squaresize)))
        elif dx == 0 and dy == -squaresize:
            self.body.append(Body((tail.pos[0], tail.pos[1] + squaresize)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy


class Map:
    def __init__(self, x, y):
        self.sizeX = x
        self.sizeY = y
        self.appleList = []


class ServerChannel(Channel):
    """
    This is the server representation of a single connected client.
    """

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        self.initialized = 0
        intid = int(self.id)
        self.color = [(intid + 1) % 3 * 84, (intid + 2) % 3 * 84,
                      (intid + 3) % 3 * 84]  # tuple([randint(0, 127) for r in range(3)])
        self.lines = []

    def PassOn(self, data):
        # pass on what we received to all connected clients
        data.update({"id": self.id})
        self._server.SendToAll(data)

    def Close(self):
        self._server.DelPlayer(self)

    def GetId(self):
        return self.id

    ##################################
    ### Network specific callbacks ###
    ##################################
    # def Network_ActionName(self,data):
    def Network_imready(self,data):
        idd=data["id"]
        for i in range(len(minions)):
            if minions[i].id==idd:
                minions[i].ready=1


    def Network_changedirection(self, data):
        dir2 = data["dir"]
        id2 = data["id"]
        # print(data)
        for i in range(len(minions)):
            if minions[i].id == id2:
                if (minions[i].stopmoving == False):
                    if dir2 == 1 and minions[i].body[0].dirnx != squaresize:
                        minions[i].dirnx = -squaresize
                        minions[i].dirny = 0
                        minions[i].turns[minions[i].head.pos[:]] = [minions[i].dirnx, minions[i].dirny]
                    if dir2 == 2 and minions[i].body[0].dirnx != -squaresize:
                        minions[i].dirnx = squaresize
                        minions[i].dirny = 0
                        minions[i].turns[minions[i].head.pos[:]] = [minions[i].dirnx, minions[i].dirny]
                    if dir2 == 3 and minions[i].body[0].dirny != squaresize:
                        minions[i].dirnx = 0
                        minions[i].dirny = -squaresize
                        minions[i].turns[minions[i].head.pos[:]] = [minions[i].dirnx, minions[i].dirny]
                    if dir2 == 4 and minions[i].body[0].dirny != -squaresize:
                        minions[i].dirnx = 0
                        minions[i].dirny = squaresize
                        minions[i].turns[minions[i].head.pos[:]] = [minions[i].dirnx, minions[i].dirny]



    def Network_ping(self, data):
        time = data["time"]
        self.Send({"action": "ping", "time": time})


class WhiteboardServer(Server):
    channelClass = ServerChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.frame = 0
        self.id = 0
        self.playerdictionary = {}
        snacks.append(Body((random.randrange(0, map[0]) * squaresize, random.randrange(0, map[1]) * squaresize)))
        self.players = WeakKeyDictionary()  # list of channels for network managing
        print('Server launched')

    def NextId(self):
        self.id += 1
        return self.id

    def Move(self):
        for j in range(len(minions)):
            if (minions[j].stopmoving == False):
                for i, c in enumerate(minions[j].body):
                    p = c.pos[:]
                    if p in minions[j].turns:  # kolejne ruchy ciala weza
                        turn = minions[j].turns[p]
                        c.move(turn[0], turn[1])
                        if i == len(minions[j].body) - 1:
                            minions[j].turns.pop(p)
                    else:  # kolizje krawedzi map
                        if c.dirnx == -squaresize and c.pos[0] <= 0:
                            c.pos = (map[0] * squaresize-squaresize, c.pos[1])
                        elif c.dirny == squaresize and c.pos[1] >= map[1] * squaresize - squaresize:
                            c.pos = (c.pos[0], 0)

                        elif c.dirny == -squaresize and c.pos[1] <= 0:
                            c.pos = (c.pos[0], map[0] * squaresize-squaresize)

                        elif c.dirnx == squaresize and c.pos[0] >= map[0] * squaresize - squaresize:
                            c.pos = (0, c.pos[1])




                        else:
                            c.move(c.dirnx, c.dirny)

    def collisionChceck(self):
        for i in range(len(minions)):
            for j in range(len(minions)):
                if (minions[i].id == minions[j].id):  # kolizja z samym soba
                    for k in range(1,len(minions[j].body)):
                        if (minions[i].body[0].pos == minions[j].body[k].pos):
                            # print("kolizja z samym soba")
                            minions[i].stopmoving = True
                            minions[i].dirnx = 0
                            minions[i].dirny = 0
                            self.SendToAll({"action": "selfcollision", "id": minions[i].id})
                else:  # kolizje z innymi graczami
                    # print("minions[i].id" + str(minions[i].id) + " " + str(minions[j].id))
                    for k in range(len(minions[j].body)):
                        if (minions[i].body[0].pos == minions[j].body[0].pos):
                            minions[i].stopmoving = True
                            minions[i].dirnx = 0
                            minions[i].dirny = 0

                            minions[j].stopmoving = True
                            minions[j].dirnx = 0
                            minions[j].dirny = 0

                            self.SendToAll({"action": "headcollision", "id": minions[i].id})
                        elif (minions[i].body[0].pos == minions[j].body[k].pos and k>=1):
                            minions[i].stopmoving = True
                            minions[i].dirnx = 0
                            minions[i].dirny = 0
                            self.SendToAll({"action": "othercollision", "id": minions[i].id})
                            # print("kolizja:glowa gracza "+ str(i)+" uderzyla "+" cialo nr "+str(k)+" gracza nr"+str(j))

    def update(self):
        for i in range(len(minions)):
            for j in range(len(minions[i].body)):
                x = minions[i].body[j].pos[0]
                y = minions[i].body[j].pos[1]
                idd = minions[i].id
                ready = minions[i].ready
                self.SendToAll({"action": "update", "x": x, "y": y, "j": j, "id": idd,"ready":ready})

    def updateapple(self):
        for i in range(len(snacks)):
            x = snacks[i].pos[0]
            y = snacks[i].pos[1]
            self.SendToAll({"action": "updateapple", "x": x, "y": y})

    def Connected(self, channel, addr):  # on client connection
        self.AddPlayer(channel)

    def AddPlayer(self, channel):  # setting base data and sending it to client
        print("New Player" + str(channel.addr))
        self.players[channel] = True
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        x = random.randrange(1, map[0]) * squaresize
        y = random.randrange(1, map[1]) * squaresize
        id = channel.GetId()
        nick = nicknames.pop(random.randrange(0, len(nicknames)))
        if (channel.initialized == 0):
            channel.Send({"action": "initid", "id": id})
            channel.initialized = 1
        p = Player(x, y, nick, r, g, b, id)
        minions.append(p)
        channel.Send(
            {"action": "initial", "x": x, "y": y, "nick": nick, "r": r, "g": g, "b": b,
             "id": id})  # send base data to connecting client

        for i in range(len(minions)):
            self.SendToAll(
                {"action": "initial", "x": minions[i].x, "y": minions[i].y, "nick": minions[i].nickname,
                 "r": minions[i].r, "g": minions[i].g, "b": minions[i].b,
                 "id": minions[i].id})  # send base data of connected client to other clients

    def DelPlayer(self, channel):  # on client disconnect
        print("Deleting Player" + str(channel.addr))
        delid = channel.GetId()
        mark = []
        for i in range(len(minions)):
            if (minions[i].id == delid):
                mark.append(i)

        for m in mark:
            del minions[m]

        del self.players[channel]
        self.SendToAll({"action": "playerdc", "playerid": delid})

    def SendToAll(self, data):
        [p.Send(data) for p in self.players]

    def Launch(self):
        while True:
            clock.tick(120)
            if (self.frame % 10 == 0):
                self.Move()
                self.collisionChceck()
                self.update()
                self.updateapple()

                for i in range(len(minions)):  # zjadanie jablek
                    for j in range(len(snacks)):
                        if (len(minions[i].body) > 0):
                            if minions[i].body[0].pos == snacks[j].pos:
                                minions[i].addBody()
                                minions[i].points += 1
                                self.SendToAll({"action": "addpoints", "id": minions[i].id})
                                snacks.pop(j)
                                snacks.append(Body((random.randrange(0, map[0]) * squaresize,
                                                    random.randrange(0, map[1]) * squaresize)))

            self.Pump()
            self.frame += 1


# get command line argument of server, port
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        s = WhiteboardServer(localaddr=(host, int(port)))
        s.Launch()
