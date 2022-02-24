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
        self.myGUI.println("HEJ " +str(pkt.sourceid))

        #Uppdatera cost på något sätt hmmmmmmmmmmmmm.....
        tempcosts = self.costs

        for cost in tempcosts:
        #   dx(y) = minv{c(x,v) + dv(y)}
            cost = min(cost[self.myID],cost) + (max(self.costs) - cost)

        for cost in tempcosts:
            if cost != self.costs:
                for i in range(self.sim.NUM_NODES):
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)



    # --------------------------------------------------
    def sendUpdate(self, pkt):
        
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))
        self.myGUI.println(str(self.costs))

    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):

        self.myGUI.println(str(newcost))

        
        
        
        pass
