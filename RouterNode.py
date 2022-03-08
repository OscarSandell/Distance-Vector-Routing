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

    #nbrcost2d is the distancevector of the neighbours
    nbrcosts2d = None
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
        #Initiate the 2D neighbour list
        self.nbrcosts2d = [[self.sim.INFINITY for x in range(self.sim.NUM_NODES)] for y in range(self.sim.NUM_NODES)]
        self.minCost = [0]*self.sim.NUM_NODES
        self.route = [0]*self.sim.NUM_NODES  
        
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)
        
        
        #Intitializing all nodes in the vector matrix to infinity except for the nodes that point to themselves
        #whos cost is obviously 0.
        for i in range(self.sim.NUM_NODES):
            for j in range(self.sim.NUM_NODES):
                if i != j:
                    self.nbrcosts2d[i][j] = self.sim.INFINITY 
                else:
                    self.nbrcosts2d[i][j] = 0
            #Initializing routes to i, as long as the cost to i isnt infinity
            if self.costs[i] < self.sim.INFINITY:
                self.route[i] = i
            else:
                self.route[i] = self.sim.INFINITY
        #Initiate the minCost variable, it is currently our direct cost to our neighbours
        self.minCost = deepcopy(self.costs)

        
        self.broadcast()
        self.printDistanceTable()
    # --------------------------------------------------
    
    def recvUpdate(self, pkt):
        self.myGUI.println(" Packet recieved -- Src: " +str(pkt.sourceid) + "; mincost: " + str(pkt.mincost))
        changed = False

        self.myGUI.println(f"Old vector for {pkt.sourceid}: \n{self.nbrcosts2d[pkt.sourceid]}")
        #Update the vector table with the newly recieved packet. 
        for i in range(self.sim.NUM_NODES):
            if self.nbrcosts2d[pkt.sourceid] != pkt.mincost:
                changed = True
                self.nbrcosts2d[pkt.sourceid] = deepcopy(pkt.mincost)
        self.myGUI.println(f"New vector for {pkt.sourceid}: \n{self.nbrcosts2d[pkt.sourceid]}")
         
        if changed:

            for i in range(self.sim.NUM_NODES):
                #if we are using the incoming packets sourceid as a route. We need to update our mincost acordingly
                if self.route[i] == pkt.sourceid and self.route[i] != self.sim.INFINITY:
                    self.minCost[i] = self.costs[pkt.sourceid] + self.nbrcosts2d[pkt.sourceid][i]

                #If our direct path is shorter then the routed path, then swap to the direct path. 
                if self.minCost[i] > self.costs[i]:
                    self.minCost[i] = self.costs[i]
                    self.route[i] = i

                for j in range(self.sim.NUM_NODES):
                    if j != self.myID:
                        #if there is a node with a shorter cost to i, then check if the cost to
                        # j + (j to i) is bigger then our cost to i.
                        if self.minCost[i] > self.costs[j] + self.nbrcosts2d[j][i]:
                            self.minCost[i] = self.costs[j] + self.nbrcosts2d[j][i]
                            self.route[i] = j
                            self.nbrcosts2d[self.myID] = self.minCost
            
            self.printDistanceTable()

        
            self.myGUI.println("Costs updated! : " + str(self.minCost))
            self.broadcast()

        
    # --------------------------------------------------
    def sendUpdate(self, pkt):
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    def printDistanceTable(self):
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
        
    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):
        
        self.myGUI.println("---Updating link cost---")
        #Chaning costs of our direct link
        self.myGUI.println("from: " + str(self.costs))
        
        #If the mincost route uses dest, then update mincost to newcost
        print(self.route)
        for i in range(self.sim.NUM_NODES):
            if self.route[i] == dest:
                #since mincost contains self.costs[dest] we need to subract it before
                #adding the newcost, otherwise the mincost will be too high.
                #alternative method would be to look up the intermediate nodes cost to
                #destination and add the new cost to that and then assign minCost as that.
                self.minCost[i] +=  (newcost - self.costs[dest])
        
        self.nbrcosts2d[self.myID] = self.minCost
        self.costs[dest] = newcost
        self.myGUI.println("to: " + str(self.costs))

        #Search for another path that is cheaper if there is any. 
        for i in range(self.sim.NUM_NODES):
            for j in range(self.sim.NUM_NODES):
                if self.costs[j] < self.sim.INFINITY:
                    if self.costs[dest] > self.costs[j] + self.nbrcosts2d[j][i] and i != self.myID:
                        self.minCost[i] = self.costs[j] + self.nbrcosts2d[j][i]
                        self.route[i] = j
        self.broadcast()

    
    def broadcast(self):
        tempCost = [0]*self.sim.NUM_NODES
        tempCost = deepcopy(self.minCost)

        for i in range(self.sim.NUM_NODES):
            if self.costs[i] != 0 and self.costs[i] != self.sim.INFINITY:
                if self.sim.POISONREVERSE:
                    #if i is a route in our routing table, then set the mincost of that route to infinity and send that insted. 
                    #This is to break any loops occuring that counts to infinity. 
                    for j in range(self.sim.NUM_NODES):
                        if self.route[j] == i and i != j:
                            tempCost[j] = self.sim.INFINITY
                        else:
                            tempCost[j] = self.minCost[j]

                self.sendUpdate(RouterPacket(self.myID,i,tempCost))
                self.myGUI.println("Send update to : " + str(i))
    