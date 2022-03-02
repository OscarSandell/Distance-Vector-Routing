#!/usr/bin/env python
from asyncio.windows_events import INFINITE
from msilib.schema import IniFile
import GuiTextArea, RouterPacket, F
from copy import deepcopy
from RouterSimulator import Event
from RouterPacket import RouterPacket
import time
class RouterNode():
    
    myID = None
    myGUI = None
    sim = None
    costs = None

    nbrcosts2d = None
    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)
        self.printDistanceTable()

        [0,2,3]
        [2,0,i]
        [3,i,0]


        #Initiate the 2D neighbour list
        self.nbrcosts2d = [[INFINITE for x in range(self.sim.NUM_NODES)] for y in range(self.sim.NUM_NODES)]
        for x in range(self.sim.NUM_NODES):
            for y in range(self.sim.NUM_NODES):
                if x == self.myID:
                    self.nbrcosts2d[x][y] = self.costs[y]
                elif y == x:
                    self.nbrcosts2d[x][y] = 0
                else:
                    self.nbrcosts2d[x][y] = INFINITE
        self.printNeighbourList()
    # --------------------------------------------------

    def printNeighbourList(self):
        for i in range(self.sim.NUM_NODES):
            self.myGUI.println(str(self.nbrcosts2d[i]))

    def recvUpdate(self, pkt):
        self.myGUI.println(self.time() + " Packet recieved -- Src: " +str(pkt.sourceid) + "; mincost: " + str(pkt.mincost))
        
        #Uppdatera cost på något sätt hmmmmmmmmmmmmm.....

        changed = False
        '''for i in range(len(pkt.mincost)):
        #   dx(y) = minv{c(x,v) + dv(y)}
            if i != self.myID and i != pkt.sourceid:
                if pkt.mincost[i] < self.costs[i]:
                    changed = True
                    self.costs[i] = pkt.mincost[i]
        '''

        for i in range(0,len(pkt.mincost)):
            if pkt.mincost[i] + pkt.mincost[self.myID] < self.costs[i]:
                self.costs[i] = pkt.mincost[i] + pkt.mincost[self.myID]
                changed = True


        if changed:
            self.myGUI.println(self.time() + " Costs updated! : " + str(self.costs))
            for i in range(len(self.costs)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)
                    self.myGUI.println(self.time() + " Send update to : " + str(i))


    # --------------------------------------------------
    def sendUpdate(self, pkt):
        
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println(self.time()) # <--- printa table
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))
        self.myGUI.println("Costs: " + str(self.costs))
        
        
        

        pass

    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):

        self.myGUI.println(str(newcost) + " : " + str(dest))
        self.costs[dest] = newcost
        self.nbrcosts2d[self.myID][dest] = newcost
        self.printNeighbourList()
        for i in range(len(self.costs)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)
                    self.myGUI.println(self.time() + " Send update to : " + str(i))
        
        
        
        pass

    def time(self):
        tid = time.process_time()
        #self.myGUI.println(str(tid))
        return str(tid)
