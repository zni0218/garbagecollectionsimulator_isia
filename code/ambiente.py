from imports import *



#AMBIENTE
class Environment:





#--------------------FUNCOES--------------------





    #iINICIA O ENVIRONMENT
    def __init__(self, size=10):
        self.size = size                                    #tamannho da grelha
        self.central_depot = (size//2,size//2)              #depot de combustivel/descarga no centro

        self.roadblocks = set()                             #conjunto de roadblocks no momento
        self.bins = set()                                   #conjunto de bins no momento
        self.trucks = set()                                 #conjunto de trucks no momento



    #GERA POSICAO ALEATORIA
    def random_position(self):
        return random.randint(0, self.size - 1), random.randint(0, self.size - 1)



    #GERA ROADBLOCKS ALEATORIOS
    async def generate_temporary_roadblocks(self):
        self.roadblocks = set()
        #num_roadblocks = 4
        #occupied_positions = {b.location for b in self.bins} | {t.location for t in self.trucks} | {self.central_depot}
        #for i in range(num_roadblocks):
        #    position = self.random_position()
        #    while position in occupied_positions:
        #        position = self.random_position()
        #    self.roadblocks.add(position)
        await asyncio.sleep(5)
        #self.roadblocks.clear()