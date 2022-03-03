#!/usr/bin/env python
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

    #nbrcost2d is the distancevector of the neighbours
    nbrcosts2d = None
    #neighbour is every nodes neigbhourlist where each element is the index of the neighbour in the simulators nodelist
    neighbours = None
    #mincost is the minimum cost to each node from the current node
    minCost = None
    #Routing path
    route = None
    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)
        self.printDistanceTable()

        #Initiate the 2D neighbour list
        self.nbrcosts2d = [[self.sim.INFINITY for x in range(self.sim.NUM_NODES)] for y in range(self.sim.NUM_NODES)]

        for x in range(self.sim.NUM_NODES):
            for y in range(self.sim.NUM_NODES):
                if x == self.myID:
                    self.nbrcosts2d[x][y] = self.costs[y]
                elif y == x:
                    self.nbrcosts2d[x][y] = 0
                else:
                    self.nbrcosts2d[x][y] = self.sim.INFINITY
                    
        #Print neigbourlist
        self.printNeighbourList()
        
        #Initiate the minCost variable, it is currently our direct cost to our neighbours
        self.minCost = deepcopy(self.costs)
        
        #Initiate the list of who's our neighbours
        self.neighbours = []
        for i in range(self.sim.NUM_NODES):
            if costs[i] != self.sim.INFINITY:
                self.neighbours.append(i)
        
        #Inititate route
        self.route = []
        for i in range(self.sim.NUM_NODES):
            if costs[i] != self.sim.INFINITY:
                self.route.append(i)

        #Send our minCost to our neighbours.
        for i in range(len(self.neighbours)):
            if (i != self.myID):
                self.sendUpdate(RouterPacket(self.myID,i,self.minCost))
        
        
    # --------------------------------------------------
    #Print the route
    def printRoute(self):
        self.myGUI.println("---Route---")
        self.myGUI.println(str(self.route))

    #Print the neighbour list
    def printNeighbourList(self):
        self.myGUI.println("---NeighbourList---")
        for i in range(self.sim.NUM_NODES):
            self.myGUI.println(str(self.nbrcosts2d[i]))
        
        

    def recvUpdate(self, pkt):
        self.myGUI.println(self.time() + " Packet recieved -- Src: " +str(pkt.sourceid) + "; mincost: " + str(pkt.mincost))
        changed = False
        #Uppdatera cost på något sätt hmmmmmmmmmmmmm.....

        
        for i in range(self.sim.NUM_NODES):
            if self.nbrcosts2d[pkt.sourceid] != pkt.mincost:
                
                self.nbrcosts2d[pkt.sourceid] = deepcopy(pkt.mincost)

        for i in range(self.sim.NUM_NODES):
            if i != self.myID:
                for j in range(len(self.neighbours)):
                    if j != i:
                        newCost = self.nbrcosts2d[self.myID][j] + self.nbrcosts2d[j][i]
                        '''
                        if (self.nbrcosts2d[self.myID][i] + self.nbrcosts2d[i][i]) > (self.nbrcosts2d[self.myID][j] + self.nbrcosts2d[j][i]):
                            self.nbrcosts2d[self.myID][i] = self.nbrcosts2d[self.myID][j] + self.nbrcosts2d[j][i]
                            #self.costs = self.nbrcosts2d[self.myID]
                        '''
                        if (self.minCost[j] > newCost):
                            changed = True
                            self.route[j] = i
                            self.minCost[j] = newCost
                            self.nbrcosts2d[self.myID] = self.minCost
        self.printNeighbourList()
        self.printRoute()

        '''
        for i in range(0,len(pkt.mincost)):
            if pkt.mincost[i] + pkt.mincost[self.myID] < self.costs[i]:
                self.costs[i] = pkt.mincost[i] + pkt.mincost[self.myID]
                changed = True
        '''
        '''
        if changed:
            self.myGUI.println(self.time() + " Costs updated! : " + str(self.costs))
            for i in range(len(self.costs)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)
                    self.myGUI.println(self.time() + " Send update to : " + str(i))
        '''
        if changed:
            self.myGUI.println(self.time() + " Costs updated! : " + str(self.minCost))
            self.broadcast()

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
        self.myGUI.println("---Updating link cost---")
        #Chaning costs of our direct link
        self.myGUI.println("from: " + str(self.costs))
        self.costs[dest] = newcost
        self.myGUI.println("to: " + str(self.costs))

        #Checking to see if the new direct link is shorter then our previous minCost
        if self.minCost[dest] > self.costs[dest]:
            self.minCost[dest] = self.costs[dest]
            self.nbrcosts2d[self.myID] = self.minCost

        self.printNeighbourList()
        '''
        self.myGUI.println("to: " + str(self.costs))

        self.printNeighbourList()
        for i in range(len(self.costs)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.costs)
                    self.sendUpdate(pkt)
                    self.myGUI.println(self.time() + " Send update to : " + str(i))
        '''
        

        self.broadcast()
        
        
        
        pass
    
    def broadcast(self):
        for i in range(len(self.neighbours)):
                if i != self.myID:
                    pkt = RouterPacket(self.myID,i,self.minCost)
                    self.sendUpdate(pkt)
                    self.myGUI.println(self.time() + " Send update to : " + str(i))
    def time(self):
        tid = time.process_time()
        #self.myGUI.println(str(tid))
        return str(tid)
