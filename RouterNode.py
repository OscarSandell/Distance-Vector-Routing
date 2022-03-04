#!/usr/bin/env python
from calendar import c
import collections
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
            else:
                self.route.append(self.sim.INFINITY)
        #Send our minCost to our neighbours.
        for i in range(len(self.neighbours)):
            if (i != self.myID):
                self.sendUpdate(RouterPacket(self.myID,i,self.minCost))
        
        self.printDistanceTable()
    # --------------------------------------------------
    
        

    def recvUpdate(self, pkt):
        self.myGUI.println(self.time() + " Packet recieved -- Src: " +str(pkt.sourceid) + "; mincost: " + str(pkt.mincost))
        changed = False
        #Uppdatera cost på något sätt hmmmmmmmmmmmmm.....
        '''
        list = [elm1[item1,item2],
                elm2[item1,item2],
                elm3[item1,item2]]
        
        list[0][0]
        '''
        self.myGUI.println("Old table:")
        self.printDistanceTable()
        for i in range(self.sim.NUM_NODES):
            if self.nbrcosts2d[pkt.sourceid] != pkt.mincost:
                changed = True
                self.nbrcosts2d[pkt.sourceid] = deepcopy(pkt.mincost)
        self.myGUI.println("New Table:")
        self.printDistanceTable()
        
        if changed:
            '''
            for row in range(self.sim.NUM_NODES):
                if row != self.myID:
                    for column in range(self.sim.NUM_NODES):
                        #if column != row:
                            print(self.route)
                            print(row)
                            newCost = self.minCost[column] + self.nbrcosts2d[self.route[column]][column]
                            if self.route[column] == self.sim.INFINITY:
                                self.myGUI.println("Thisis the \"row\" value: " + str(row))
                                self.myGUI.println("Thisis the \"column\" value: " + str(column))
                                self.myGUI.println("This is the \"newcost\": " + str(newCost))
                            if (self.minCost[column] > newCost):
                                self.route[column] = row
                                self.minCost[column] = newCost
                                self.nbrcosts2d[self.myID] = self.minCost
            '''
            for column in range(self.sim.NUM_NODES):
                if self.route[column] == pkt.sourceid:
                    self.minCost[column] = self.costs[pkt.sourceid] + self.nbrcosts2d[pkt.sourceid][column]
                for row in range(self.sim.NUM_NODES):
                    if row != self.myID:
                    #find a node that has a shorter cost to colum
                        if self.minCost[column] > self.nbrcosts2d[row][column]:
                            #if there is a node with a shorter cost to column, then check if the cost to
                            #that row + the cost from that row to the colum is bigger then our cost to the
                            #column.
                            if self.minCost[column] > self.costs[row] + self.nbrcosts2d[row][column]:
                                self.minCost[column] = self.costs[row] + self.nbrcosts2d[row][column]
                                self.route[column] = row
                                self.nbrcosts2d[self.myID] = self.minCost
            
            self.printDistanceTable()

        
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
        
        #Print neigbourlist
        self.printNeighbourList()
        self.myGUI.println("Distance vector: " + str(self.minCost))
        self.myGUI.println("Routes: "+ str(self.route))
        
    #Print the route
    def printRoute(self):
        self.myGUI.println("---Route---")
        self.myGUI.println(str(self.route))

    #Print the neighbour list
    def printNeighbourList(self):
        self.myGUI.println("---NeighbourList---")
        for i in range(self.sim.NUM_NODES):
            #if i != self.myID:
            self.myGUI.println("nbr  " + str(i) + str(self.nbrcosts2d[i]))
        self.myGUI.println(str(self.neighbours))
        
    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):
        
        self.myGUI.println("---Updating link cost---")
        #Chaning costs of our direct link
        self.myGUI.println("from: " + str(self.costs))
        
        
        
        #If the mincost route uses dest, then update mincost to newcost
        print(self.route)
        for i in range(self.sim.NUM_NODES):
            if self.route[i] == dest:
                self.minCost[i] += (-1 * self.costs[dest]) + newcost
        
        self.nbrcosts2d[self.myID] = self.minCost
        self.costs[dest] = newcost
        self.myGUI.println("to: " + str(self.costs))

        for i in range(self.sim.NUM_NODES):
            if self.route[i] == dest:
                for j in range(self.sim.NUM_NODES):
                    if self.costs[j] < self.sim.INFINITY:
                        if self.minCost[i] > self.costs[j] + self.nbrcosts2d[j][i]:
                            self.minCost[i] = self.costs[j] + self.nbrcosts2d[j][i]
                            self.route[i] = j
        '''
        #Find if the cost is less then the minCost
        for column in range(self.sim.NUM_NODES):
            if self.minCost[i] > self.costs[i]:
                self.minCost[i] = self.costs[i]
                self.nbrcosts2d[self.myID] = self.minCost
                self.route[i] = i
        
        for i in range(self.sim.NUM_NODES):
            for j in range(self.sim.NUM_NODES):
                if i != self.myID:
                    tempCost = self.nbrcosts2d[self.myID][i] + self.nbrcosts2d[i][j]
                    if self.minCost[j] > tempCost:
                        self.minCost[j] = tempCost
                        self.route[j] = i
        self.printDistanceTable()
        '''


        self.broadcast()

    
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
