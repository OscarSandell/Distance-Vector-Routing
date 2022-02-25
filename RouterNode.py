#!/usr/bin/env python
import GuiTextArea, RouterPacket, F
from copy import deepcopy
from RouterSimulator import Event
from RouterPacket import RouterPacket
class RouterNode():
    myID = None
    myGUI = None
    sim = None
    costs = None

    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)
        self.printDistanceTable()

    # --------------------------------------------------
    def recvUpdate(self, pkt):
        self.myGUI.println("Packet recieved -- Src: " +str(pkt.sourceid) + "; mincost: " + str(pkt.mincost))
        
        #Uppdatera cost på något sätt hmmmmmmmmmmmmm.....

        changed = False
        '''for i in range(len(pkt.mincost)):
        #   dx(y) = minv{c(x,v) + dv(y)}
            if i != self.myID and i != pkt.sourceid:
                if pkt.mincost[i] < self.costs[i]:
                    changed = True
                    self.costs[i] = pkt.mincost[i]
        '''
        if self.myID == 0:
            if pkt.sourceid == 1:
                if self.costs[2] > pkt.mincost[2] + self.costs[1]:
                    self.costs[2] = pkt.mincost[2] + self.costs[1]
                    changed = True
            elif pkt.sourceid == 2:
                if self.costs[1] > pkt.mincost[1] + self.costs[2]:
                    self.costs[1] = pkt.mincost[1] + self.costs[2]
                    changed = True
        elif self.myID == 1:
            if pkt.sourceid == 2:
                if self.costs[0] > pkt.mincost[0] + self.costs[2]:
                    self.costs[0] = pkt.mincost[0] + self.costs[2]
                    changed = True
            elif pkt.sourceid == 0:
                if self.costs[2] > pkt.mincost[2] + self.costs[0]:
                    self.costs[2] = pkt.mincost[2] + self.costs[0]
                    changed = True
        elif self.myID == 2:
            if pkt.sourceid == 1:
                if self.costs[0] > pkt.mincost[0] + self.costs[1]:
                    self.costs[0] = pkt.mincost[0] + self.costs[1]
                    changed = True
            elif pkt.sourceid == 0:
                if self.costs[1] > pkt.mincost[1] + self.costs[0]:
                    self.costs[1] = pkt.mincost[1] + self.costs[0]
                    changed = True
        if changed:
            self.myGUI.println("Costs updated! : " + str(self.costs))
            for i in range(len(self.costs)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)
        

        '''for cost in tempcosts:
            if cost != self.costs:
                for i in range(self.sim.NUM_NODES):
           '''         



    # --------------------------------------------------
    def sendUpdate(self, pkt):
        
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))
        self.myGUI.println("Costs: " + str(self.costs))

    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):

        self.myGUI.println(str(newcost) + " : " + str(dest))
        pkt = RouterPacket(self.myID,dest,self.costs)
        self.sendUpdate(pkt)
        
        
        
        pass
