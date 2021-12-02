from random import randint
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from pathfinding.core.grid import Grid as GridP
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import numpy

class Bot(Agent):
    def __init__(self, model, pos, mapB):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.occupied = False
        self.mapB = mapB
        self.route = []

    def step(self):
        aList = self.model.grid.get_cell_list_contents(self.pos)
        crates = self.model.crateCounter(aList)

        if(crates == 1 and self.route == []):
            for agent in aList:
                if(type(agent) == Crate and agent.active):
                    if(self.occupied == False):
                        self.occupied = True
                        agent.active = False
                        self.createRoute()

        elif(self.route != []):
            num_box = self.model.crateCounter(self.model.grid.get_cell_list_contents(self.route[0]))
            self.model.grid.move_agent(self, self.route[0])
            self.route.pop(0)
            if(self.route == [] and num_box < 5):
                self.occupied = False
                crate = Crate(self.model, self.pos)
                self.model.grid.place_agent(crate, crate.pos)

        elif(self.route == [] and self.occupied):
            self.createRoute()
        else:
            next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
            next_move = self.random.choice(next_moves)
            self.model.grid.move_agent(self, next_move)

    def createRoute(self):
        mapRoute = numpy.ones((len(self.mapB), len(self.mapB[0])), dtype=int)
        grid = GridP(matrix = mapRoute)
        start = grid.node(self.pos[0], self.pos[1])
        around = self.model.grid.get_neighborhood(self.pos, moore=False, radius=20)

        for j in around:
            check = self.model.crateCounter(self.model.grid.get_cell_list_contents(j))
            if (check > 0 and check < 5):
                end = grid.node(j[0], j[1])
                finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
                self.route, _ = finder.find_path(start, end, grid)
                self.route.pop(0)
                break

class Crate(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.active = True

class Warehouse(Model):
    def __init__(self, C = 20, R = 20, botN = 5, crateN = 40, maxSteps = 1000):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(C, R, torus=False)
        self.maxSteps = maxSteps
        self.botN = botN
        self.crateN = crateN
        self.pList = []
        self.mapR = numpy.zeros((C,R))
        
        while(botN > 0):
            row = randint(0, R-1)
            column = randint(0, C-1)
            if(self.mapR[column][row] == 0):
                self.mapR[column][row] = 1
                botN -= 1

        while(crateN > 0):
            row = randint(0, R-1)
            column = randint(0, C-1)
            if(self.mapR[column][row] == 0):
                self.mapR[column][row] = 2
                crateN -= 1
        

        for _,x,y in self.grid.coord_iter():
            if self.mapR[y][x] == 1:
                bot = Bot(self, (x, y), self.mapR)
                self.grid.place_agent(bot, bot.pos)
                self.schedule.add(bot)
            elif self.mapR[y][x] == 2:
                crate = Crate(self, (x, y))
                self.grid.place_agent(crate, crate.pos)
                self.schedule.add(crate)

    @staticmethod
    def crateCounter(list):
        num = 0
        for agent in list:
            if type(agent) == Crate and agent.active:
                num += 1
        return num

    def step(self):
        self.pList = []
        piledCrates = 0
        c = 1
        for _,x,y in self.grid.coord_iter():
            if(self.mapR[y][x] == 2):
                pile = self.crateCounter(self.grid.get_cell_list_contents((x, y)))
                self.pList.append({"x": x, "y": y, "crateN": pile})
                if(pile == 1):
                    break
                elif(c < self.crateN):
                    piledCrates += pile
                    c += 1
                elif(self.crateN == piledCrates):
                    self.running = False

        if(self.schedule.steps >= self.maxSteps):
            self.running = False
        else:
            self.schedule.step()
