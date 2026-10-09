from imports import *



#CAMIAO
class TruckAgent(Agent):





#--------------------FUNCOES--------------------





    #INICIA O TRUCK                                                                                                                                 #
    def __init__(self, jid, password, environment, capacity, gas):                                                                                  #
        super().__init__(jid, password)                                                                                                             #agente
        self.environment = environment                                                                                                              #ambiente
                                                                                                                                                    #
        self.location = environment.central_depot                                                                                                   #posicao inicial (central_depot)
        self.current_load = 0                                                                                                                       #load atual (no inicio 0)
        self.capacity = capacity                                                                                                                    #capacidade total
        self.gas = gas                                                                                                                              #gas atual (no inicio cheio)
        self.gas_total = gas                                                                                                                        #gas total
                                                                                                                                                    #
        self.target_bin = None                                                                                                                      #bin alvo
        self.target_bin_location = None                                                                                                             #localizacao bin alvo
        self.target_bin_waste_level = None                                                                                                          #waste level bin alvo
        self.target_bin_waste_percent = None                                                                                                        #waste percent bin alvo
                                                                                                                                                    #
        self.is_stopped = 0                                                                                                                         #saber se truck esta no transito
                                                                                                                                                    #
        #METRICAS                                                                                                                                   #
        self.bins_recolhidos = 0                                                                                                                    #numero de bins que recolheu
        self.lixo_recolhido = 0                                                                                                                     #quantidade total de lixo recolhido
        self.gas_consumido = 0                                                                                                                      #quantidade total de gas consumido (=distancia_total)
        self.vezes_depot_voluntario = 0                                                                                                             #quantidade de vezes que voltou ao depot voluntariamente
        self.vezes_depot_passagem = 0                                                                                                               #quantidade de vezes que passou no depot e aproveitou para descarregar/abastecer
        self.vezes_depot_total = 0                                                                                                                  #quantidade de vezes total que parou no depot




#--------------------CONTROL NET PROTOCOL--------------------





    #passo 2 do CNP                                                                                                                                 #CEATE BID e SEND BID
    #COMPORTAMENTO PARA RESPONDER AS PROPOSTAS DE RECOLHA VALIDAS                                                                                   #
    class CreateBid_SendBid(CyclicBehaviour):                                                                                                       #
        async def run(self):                                                                                                                        #
            msg_rfb = await self.receive()                                                                                                          #esperar por msg continuamente
            if msg_rfb and msg_rfb.metadata.get("performative") == "cfp":                                                                           #se receber msg e a performativa for call for proposal
                if not self.agent.target_bin:                                                                                                       #   se nao tiver bin alvo
                    bin_jid = str(msg_rfb.body.split(";")[0])                                                                                       #       obter jid do bin
                    bin_location = str(msg_rfb.body.split(";")[1])                                                                                  #       obter localizacao do bin
                    bin_waste_level = int(msg_rfb.body.split(";")[2])                                                                               #       obter waste level do bin
                    bin_waste_percent = int(msg_rfb.body.split(";")[3])                                                                             #       obter waste percent do bin
                    bin_distance = manhattan_distance(self.agent.location, eval(bin_location))                                                      #       calcular diatancia do bin
                    if self.agent.gas>bin_distance and self.agent.gas>self.agent.gas_total*0.4:                                                     #       se tem gas para ir ao bin (opcao mais naive, pode voltar para o depot a meio do caminho, mas ao menos nao fica preso)
                        if self.agent.current_load+bin_waste_level<=self.agent.capacity and self.agent.current_load<self.agent.capacity*0.7:        #           se houver espaco para a carga do bin (igualmente naive)
                            if not self.agent.target_bin:                                                                                           #               se continuar sem bin alvo
                                msg_bid = Message(to=str(bin_jid))                                                                                  #                   msg para o bin
                                msg_bid.set_metadata("performative", "propose")                                                          #                   metadata proposta
                                msg_bid.body = f"{self.agent.jid};{bin_distance}"                                                                   #                   corpo da msg é jid e distancia
                                await self.send(msg_bid)                                                                                            #                   enviar msg
                                #print(f"{self.agent.jid} respondeu ao pedido de recolha de {bin_jid}")                                             #                   print
            await asyncio.sleep(0.01)                                                                                                               #esperar 0.01 segundos



    #passo 4.1 do CNP                                                                                                                               #CONRIM AWARD CONTRACT
    #COMPORTAMENTO PARA RECEBER AWARD CONTRACT (se tudo estiver correto, aceita)                                                                    #
    class ConfirmAwardContract(CyclicBehaviour):                                                                                                    #
        async def run(self):                                                                                                                        #
            msg_award = await self.receive()                                                                                                        #esperar por msg continuamente
            if msg_award and msg_award.get_metadata("performative") == "accept-proposal":                                                           #se recebe msg e a performativa é aceitar proposta
                if not self.agent.target_bin:                                                                                                       #   se nao tiver bin alvo
                    bin_jid = str(msg_award.body.split(";")[0])                                                                                     #       receber jid do bin
                    bin_location = str(msg_award.body.split(";")[1])                                                                                #       receber localizacao do bin
                    bin_waste_level = int(msg_award.body.split(";")[2])                                                                             #       receber waste_level do bin
                    bin_waste_percent = int(msg_award.body.split(";")[3])                                                                           #       receber waste_percent do bin
                    bin_distance = manhattan_distance(self.agent.location, eval(bin_location))                                                      #       calcular a distancia do bin
                    if self.agent.gas>bin_distance and self.agent.gas>self.agent.gas_total*0.4:                                                     #       se tem gas para ir ao bin (denovo calcula opcao naive)
                        if self.agent.current_load+bin_waste_level<=self.agent.capacity and self.agent.current_load<self.agent.capacity*0.7:        #           se houver espaco para a carga do bin (denovo calcula opcao naive)
                            if not self.agent.target_bin:                                                                                           #               se continuar sem bin alvo
                                self.agent.target_bin = bin_jid                                                                                     #                   definir jid do bin alvo
                                self.agent.target_bin_location = bin_location                                                                       #                   definir localizacao do bin alvo
                                self.agent.target_bin_waste_level = bin_waste_level                                                                 #                   definir waste_level do bin alvo
                                self.agent.target_bin_waste_percent = bin_waste_percent                                                             #                   definir ewaste_percent do bin alvo
                                #print(f"{self.agent.jid} aceitou award de {self.agent.target_bin}!")                                               #                   print
                                msg_accept_award = Message(to=self.agent.target_bin)                                                                #                   msg para o bin alvo
                                msg_accept_award.set_metadata("performative", "confirm")                                                 #                  performativa é confirmar
                                msg_accept_award.body = f"{self.agent.jid};{self.agent.location};{self.agent.gas};{self.agent.current_load}"        #                   corpo da msg com jid, localizacao, gas e load
                                await self.send(msg_accept_award)                                                                                   #                   enviar a msg
            await asyncio.sleep(0.01)                                                                                                               #esperar 0.01 segundos



    #passo 4.3                                                                                                                                      #PERFORM WORK e SEND RESULTS
    #COMPORTAMENTO PARA REALIZAR O TRABALHO E ENVIAR O RESULTADO (movimentar para o objetivo e colher lixo)                                         #
    class PerformWork_SendResults(CyclicBehaviour):                                                                                                 #
        async def run(self):                                                                                                                        #
            if self.agent.target_bin:                                                                                                               #se tem bin alvo
                cx, cy = self.agent.location                                                                                                        #   coordenadas do truck
                tx, ty = int(self.agent.target_bin_location[1]), int(self.agent.target_bin_location[4])                                             #   coordenadas do bin alvo
                if (cx, cy) != (tx, ty):                                                                                                            #       se as coordenadas do truck e do bin alvo forem diferentes
                    if random.random() < 0.05:                                                                                                      #           se um numero aleatorio entre 0 e 1 for menor que 0.05
                        delay = random.randint(1, 5)                                                                                          #               definir delay aleatorio entre 1 e 5 segundos
                        self.agent.is_stopped=delay                                                                                                    #               atualizar paragem
                        print(f"{self.agent.jid} preso no transito por {delay} segundos. A realocar recolha de {self.agent.target_bin}")            #               print
                        msg_restart_bin = Message(to=self.agent.target_bin)                                                                         #               msg para o bin alvo
                        msg_restart_bin.set_metadata("performative", "inform")                                                           #               performativa é inform
                        msg_restart_bin.body = "RESTART_BIN"                                                                                        #               corpo é RESTART_BIN
                        await self.send(msg_restart_bin)                                                                                            #               enviar a msg
                        await asyncio.sleep(delay)                                                                                                  #               esperar o delay
                        self.agent.is_stopped=0                                                                                                     #               atualizar paragem
                        self.agent.target_bin = None                                                                                                #               tirar bin alvo
                        self.agent.target_bin_location = None                                                                                       #               tirar localizacao do bin alvo
                        self.agent.target_bin_waste_level = None                                                                                    #               tirar waste level do bin alvo
                        self.agent.target_bin_waste_percent = None                                                                                  #               tirar waste percent do bin alvo
                        return                                                                                                                      #               return
                    if cx < tx and cx + 1 < self.agent.environment.size and (cx + 1, cy) not in self.agent.environment.roadblocks:                  #           condicao
                        cx += 1                                                                                                                     #               movimento
                    elif cx > tx and cx - 1 < self.agent.environment.size and (cx - 1, cy) not in self.agent.environment.roadblocks:                #           condicao
                        cx -= 1                                                                                                                     #               movimento
                    elif cy < ty and cy + 1 < self.agent.environment.size and (cx, cy + 1) not in self.agent.environment.roadblocks:                #           condicao
                        cy += 1                                                                                                                     #               movimento
                    elif cy > ty and cy - 1 < self.agent.environment.size and (cx, cy - 1) not in self.agent.environment.roadblocks:                #           condicao
                        cy -= 1                                                                                                                     #               movimento
                    else:                                                                                                                           #           caso nao consiga movimentar
                        print(f"{self.agent.jid} encontrou roadblock!")                                                                             #               print
                        return                                                                                                                      #               return
                    self.agent.location = (cx, cy)                                                                                                  #           atualizar localizacao do truck
                    self.agent.gas -= 1                                                                                                             #           atualizar gas do truck
                    self.agent.gas_consumido+=1                                                                                                     #           adicionar 1 ao gas total consumido
                    await asyncio.sleep(0.5)                                                                                                        #           esperar 0.5 segundos
                else:                                                                                                                               #       se as coordenadas do bin alvo coincidirem com as do truck
                    msg_results = Message(to=str(self.agent.target_bin))                                                                            #           msg para bin alvo
                    msg_results.set_metadata("performative", "agree")                                                                    #           performativa é agree
                    msg_results.body = f"{self.agent.jid}"                                                                                          #           corpo da msg com o jid do truck
                    await self.send(msg_results)                                                                                                    #           enviar a msg
                    self.agent.current_load += self.agent.target_bin_waste_level                                                                    #           adicionar o waste recolhido
                    self.agent.lixo_recolhido+=self.agent.target_bin_waste_level                                                                    #           adicionar o lixo recolhido a quantidade total de lixo recolhido
                    self.agent.target_bin = None                                                                                                    #           tirar bin alvo
                    self.agent.target_bin_location = None                                                                                           #           tirar localizacao do bin alvo
                    self.agent.target_bin_waste_level = None                                                                                        #           tirar waste level do bin alvo
                    self.agent.target_bin_waste_percent = None                                                                                      #           tirar waste percent do bin alvo
                    self.agent.bins_recolhidos+=1                                                                                                   #           adicionar 1 ao numero total de bins recolhidos
            await asyncio.sleep(0.5)                                                                                                                #esperar 0.5 segundos





#--------------------COMPORTAMENTOS VARIADOS--------------------





    #COMPORTAMENTO PARA LIMPAR OBJETIVOS                                                                                                            #
    class RestartTruck(CyclicBehaviour):                                                                                                            #
        async def run(self):                                                                                                                        #
            msg_restart_truck = await self.receive()                                                                                                #esperar por msg continuamente
            if msg_restart_truck and msg_restart_truck.get_metadata("performative") == "inform":                                                    #se recebe msg e a performativa é inform
                if "RESTART_TRUCK" in msg_restart_truck.body:                                                                                       #   se o corpo é RESTART_TRUCK
                    self.agent.target_bin = None                                                                                                    #       tirar bin alvo
                    self.agent.target_bin_location = None                                                                                           #       tirar localizacao do bin alvo
                    self.agent.target_bin_waste_level = None                                                                                        #       tirar waste level do bin alvo
                    self.agent.target_bin_waste_percent = None                                                                                      #       tirar waste percent do bin alvo
            await asyncio.sleep(0.01)                                                                                                               #esperar 0.01 segundos



    #quando leva delay, ele volta a correr e move sem ter a posicao atualizada, foi tirado o delay para evitar isso                                 #
    #COMPORTAMENTO PARA NECESSIDADE DE IR AO DEPOT                                                                                                  #
    class IfNeedDepot(CyclicBehaviour):                                                                                                             #
        async def run(self):                                                                                                                        #
            if self.agent.gas<=0.4*self.agent.gas_total or self.agent.current_load>=0.7*self.agent.capacity:                                        #se tem pouco gas ou muita carga
                if self.agent.target_bin:                                                                                                           #   se tem bin alvo
                    msg_restart_bin = Message(to=self.agent.target_bin)                                                                             #       msg para o bin alvo
                    msg_restart_bin.set_metadata("performative", "inform")                                                               #       performativa é inform
                    msg_restart_bin.body = "RESTART_BIN"                                                                                            #       corpo é RESTART_BIN
                    await self.send(msg_restart_bin)                                                                                                #       mandar msg
                    print(f"{self.agent.jid} teve de ir ao depot! A realocar a recolha de {self.agent.target_bin}")                                 #       print
                    self.agent.target_bin = None                                                                                                    #       tirar bin alvo
                    self.agent.target_bin_location = None                                                                                           #       tirar localizacao do bin alvo
                    self.agent.target_bin_waste_level = None                                                                                        #       tirar  waste level do bin alvo
                    self.agent.target_bin_waste_percent = None                                                                                      #       tirar waste percent do bin alvo
                #print(f"{self.agent.jid} com pouco combustivel ou excesso de carga, a dirigir-se ao depot!")                                       #   print
                cx, cy = self.agent.location                                                                                                        #   coordenadas do truck
                tx, ty = self.agent.environment.central_depot                                                                                       #   coordenadas do depot
                await asyncio.sleep(0.49)                                                                                                           #   esperar 0.49 segundos
                if (cx, cy) != (tx, ty):                                                                                                            #   se as coordenadas do truck nao forem as do depot
                    if cx < tx and cx+1<self.agent.environment.size and (cx + 1, cy) not in self.agent.environment.roadblocks:                      #       condicao
                        cx += 1                                                                                                                     #           movimento
                    elif cx > tx and cx-1<self.agent.environment.size and (cx - 1, cy) not in self.agent.environment.roadblocks:                    #       condicao
                        cx -= 1                                                                                                                     #           movimento
                    elif cy < ty and cy+1<self.agent.environment.size and (cx, cy + 1) not in self.agent.environment.roadblocks:                    #       condicao
                        cy += 1                                                                                                                     #           movimento
                    elif cy > ty and cy-1<self.agent.environment.size and (cx, cy - 1) not in self.agent.environment.roadblocks:                    #       condicao
                        cy -= 1                                                                                                                     #           movimento
                    else:                                                                                                                           #       caso nao consiga mexer
                        print(f"{self.agent.jid} encontrou roadblock!")                                                                             #           print
                        return                                                                                                                      #           retornar
                    self.agent.location = (cx, cy)                                                                                                  #       atualizar coordenadas do truck
                    self.agent.gas -= 1                                                                                                             #       atualizar gas do truck
                    self.agent.gas_consumido+=1                                                                                                     #       adicionar 1 ao gas total consumido
                    await asyncio.sleep(0.5)                                                                                                        #       esperar 0.5 segundos
            await asyncio.sleep(0.01)                                                                                                               #esperar 0.5 segundos



    #COMPORTAMENTO PARA CASO ESTEJA NO DEPOT E POSSA DESCARREGAR LIXO/REABASTECER                                                                                                                                           #
    class IfInDepot(CyclicBehaviour):                                                                                                                                                                                       #
        async def run(self):                                                                                                                                                                                                #
            if self.agent.location==self.agent.environment.central_depot:                                                                                                                                                   #se o truck estiver no depot
                if self.agent.gas<self.agent.gas_total*0.5 or self.agent.current_load>self.agent.capacity*0.5:                                                                                                              #   se tiver gas a menos ou lixo a mais
                    if self.agent.target_bin:                                                                                                                                                                               #       se tiver bin alvo
                        print(f"{self.agent.jid} passou no depot e aproveitou para descarregar lixo e abastecer combustivel durante 3 segundos! A realocar a sua recolha de {self.agent.target_bin} se necessário!")        #           print
                        msg_restart_bin = Message(to=self.agent.target_bin)                                                                                                                                                 #           msg para o bin alvo
                        msg_restart_bin.set_metadata("performative", "inform")                                                                                                                                   #           performativa é inform
                        msg_restart_bin.body = "RESTART_BIN"                                                                                                                                                                #           corpo é RESTART_BIN
                        await self.send(msg_restart_bin)                                                                                                                                                                    #           mandar msg
                        await asyncio.sleep(3)                                                                                                                                                                              #           esperar 3 segundos
                        self.agent.target_bin = None                                                                                                                                                                        #           tirar bin alvo
                        self.agent.target_bin_location = None                                                                                                                                                               #           tirar localizacao do bin alvo
                        self.agent.target_bin_waste_level = None                                                                                                                                                            #           tirar waste level do bin alvo
                        self.agent.target_bin_waste_percent = None                                                                                                                                                          #           tirar waste percent do bin alvo
                        self.agent.vezes_depot_passagem+=1                                                                                                                                                                  #           adiciona 1 as vezes total que o camiao passa no depot e aproveita para abastecer/descarregae
                    else:                                                                                                                                                                                                   #       se nao tiver bin alvo
                        print(f"{self.agent.jid} chegou depot, as descarregar lixo e abastecer combustivel durante 3 segundos!")                                                                                            #           print
                        self.agent.vezes_depot_voluntario+=1                                                                                                                                                                #           adicona 1 as vezes total que o camiao vai ao depot propositadamente
                        await asyncio.sleep(3)                                                                                                                                                                              #           esperar 3 sgundos
                    self.agent.vezes_depot_total+=1                                                                                                                                                                         #       adiciona 1 as vezes total que parou no depot
                    self.agent.current_load = 0                                                                                                                                                                             #       tirar lixo
                    self.agent.gas = self.agent.gas_total                                                                                                                                                                   #       encher gas
            await asyncio.sleep(0.1)                                                                                                                                                                                        #esperar 0.1 segundos






#--------------------SETUP DE COMPORTAMENTOS--------------------





    #COMPORTAMENTOS                                             #
    async def setup(self):                                      #
        self.add_behaviour(self.RestartTruck())                 #escutar para reiniciar truck
        self.add_behaviour(self.IfInDepot())                    #ver se estiver no depot
        self.add_behaviour(self.IfNeedDepot())                  #ver se precisa de ir ao depot
        self.add_behaviour(self.CreateBid_SendBid())            #escturar propostas criar bid e mandar
        self.add_behaviour(self.ConfirmAwardContract())         #confirmar award
        self.add_behaviour(self.PerformWork_SendResults())      #enviar resultados
