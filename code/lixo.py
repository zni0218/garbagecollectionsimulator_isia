import time

from imports import *



#LIXO
class BinAgent(Agent):





#--------------------FUNCOES--------------------





    #INICIA O BIN                                                                                                                                                       #
    def __init__(self, jid, password, environment, capacity):                                                                                                           #
        super().__init__(jid, password)                                                                                                                                 #agente
        self.environment = environment                                                                                                                                  #ambiente
                                                                                                                                                                        #
        self.location = self.gen_valid_pos()                                                                                                                            #colocar em posicao random
        self.waste_level = random.randint(0, int(0.6*capacity))                                                                                                      #nivel inicial de lixo
        self.capacity = capacity                                                                                                                                        #capacidade total de lixo
        self.waste_percent = int((self.waste_level/self.capacity)*100)                                                                                                  #percentagem de lixo atual
                                                                                                                                                                        #
        self.nearest_truck = None                                                                                                                                       #truck mais proximo
        self.nearest_truck_distance = 10000                                                                                                                             #distancia do truck mais proximo
                                                                                                                                                                        #
        self.inNegotiation = False                                                                                                                                      #flag para saber se esta em negociacao de contrato
                                                                                                                                                                        #
        self.target_truck = None                                                                                                                                        #truck alvo
        self.target_truck_location = None                                                                                                                               #localizacao truck alvo
        self.target_truck_distance = None                                                                                                                               #distancia truck alvo
        self.target_truck_gas = None                                                                                                                                    #gas truck alvo
        self.target_truck_load = None                                                                                                                                   #load truck alvo
                                                                                                                                                                        #
        #METRICAS                                                                                                                                                       #
        self.numero_recolhas = 0                                                                                                                                        #numero de vezes que lixo foi recolhido
        self.numero_recolhas_emergencia = 0                                                                                                                             #numero de vezes que um pedido de recolha de emergencia foi emitido
        self.numero_realocacoes_transito_ou_depot = 0                                                                                                                   #numero de vezes que a recolha teve de ser realocada devido a transito ou paragem em depot
        self.numero_realocacoes_erro = 0                                                                                                                                #numero de vezes que a recolha teve de ser realocada devido a nao haver resposta a award contract
        #
        self.tempo_total_recolha = 0                                                                                                                                    #tempo total gasto em recolhas
        self.tempo_total_comunicacao = 0                                                                                                                                #tempo gasto em comunicacao (desde askforbid ate handshake)
        #
        self.tempo_inicial_comunicacao = 0                                                                                                                              #TEMP, tempo inicial da comunicacao
        self.temp_inicial_recolha = 0                                                                                                                                   #TEMP, tempo inicial da recolha





#--------------------CONTROL NET PROTOCOL--------------------





    #passo 1 do CNP                                                                                                                                                     #REQUEST FOR BIDS e SEND RFB
    #COMPORTAMENTO PARA PEDIR RECOLHA QUANDO O LIXO ULTRAPASSA 70%                                                                                                      #
    class RequestForBids_SendRFB(CyclicBehaviour):                                                                                                                      #
        async def run(self):                                                                                                                                            #
            if self.agent.waste_percent<70:                                                                                                                             #se lixo<70%
                self.agent.nearest_truck = None                                                                                                                         #   reinicia o truck mais proximo
                self.agent.nearest_truck_distance = 10000                                                                                                               #   reinicia a distanciua do truck mais proximo
                if self.agent.target_truck or self.agent.inNegotiation:                                                                                                 #       se tem truck alvo ou está em negociação
                    msg_restart_truck = Message(to=self.agent.target_truck)                                                                                             #           mensagem para truck alvo
                    msg_restart_truck.set_metadata("performative", "inform")                                                                                 #           performativa é informar
                    msg_restart_truck.body = "RESTART_TRUCK"                                                                                                            #           corpo da msg é RESTART_TRUCK (limpar alvo do truck)
                    await self.send(msg_restart_truck)                                                                                                                  #           enviar msg
                    self.agent.inNegotiation = False                                                                                                                    #           limpar negociacao
                    self.agent.target_truck = None                                                                                                                      #           limpar truck alvo
                    self.agent.target_truck_location = None                                                                                                             #           limpar localizacao do truck alvo
                    self.agent.target_truck_distance = None                                                                                                             #           limpar distancia do truck alvo
                    self.agent.target_truck_gas = None                                                                                                                  #           limpar gas do truck alvo
                    self.agent.target_truck_load = None                                                                                                                 #           limpar load do truck alvo
            else:                                                                                                                                                       #se lixo>=70%
                if not self.agent.inNegotiation and not self.agent.target_truck:                                                                                        #   se nao esta em negociacao e nao tem truck atribuido
                    for t in self.agent.environment.trucks:                                                                                                             #       para todos os trucks no ambiente
                        self.agent.tempo_inicial_comunicacao = time.time()
                        msg_rfb = Message(to=str(t.jid))                                                                                                                #          destinatario da msg (truck)
                        msg_rfb.set_metadata("performative", "cfp")                                                                                          #           performativa é call for proposal
                        msg_rfb.body = f"{self.agent.jid};{self.agent.location};{self.agent.waste_level};{self.agent.waste_percent}"                                    #           corpo da msg com jid, localizacao, waste level, waste percent
                        await self.send(msg_rfb)                                                                                                                        #           enviar a msg
                    print(f"{self.agent.jid} mandou pedido de recolha a todos os trucks disponíveis!")                                                                  #       print
            await asyncio.sleep(2)                                                                                                                                      #esperar 2 segundos para repetir



    #passo 3 do CNP                                                                                                                                                     #SELECT BID e AWARD CONTRACT
    #COMPORTAMENTO PARA SELECIONAR A BID                                                                                                                                #
    class SelectBid_AwardContract(CyclicBehaviour):                                                                                                                     #
        async def run(self):                                                                                                                                            #
            msg_bid = await self.receive()                                                                                                                              #esperar por msg constantemente
            if msg_bid and msg_bid.get_metadata("performative") == "propose":                                                                                           #se receber msg e a performativa for proposta
                if not self.agent.inNegotiation and not self.agent.target_truck:                                                                                        #   se nao tiver em negociacao e se nao tiver truck alvo
                    if self.agent.waste_percent>=70:                                                                                                                    #       se o waste >=70%
                        propostas = []                                                                                                                                  #           inicia conjunto de propostas
                        truck_jid = str(msg_bid.body.split(";")[0])                                                                                                     #           receber jid do truck
                        truck_distance = int(msg_bid.body.split(";")[1])                                                                                                #           receber distancia do truck
                        propostas.append((truck_jid, truck_distance))                                                                                                   #           adicionar proposta ao conjunto de propostas
                        start_time = asyncio.get_event_loop().time()                                                                                                    #           tempo de inicio
                        timeout=1                                                                                                                                       #           contador de 1 segundi
                        while asyncio.get_event_loop().time()-start_time<timeout:                                                                                       #           comecar contador
                            msg_bid = await self.receive(timeout=0.1)                                                                                                   #               esperar por msg
                            if msg_bid and msg_bid.get_metadata("performative") == "propose":                                                                           #               se receber msg e a performativa for proposta
                                truck_jid = str(msg_bid.body.split(";")[0])                                                                                             #                   receber jid do truck
                                truck_distance = int(msg_bid.body.split(";")[1])                                                                                        #                   receber distancia do truck
                                propostas.append((truck_jid, truck_distance))                                                                                           #                   adicionar proposta ao conjunto de propostas
                        if propostas:                                                                                                                                   #           se no fim do contador houver propostas
                            self.agent.inNegotiation = True                                                                                                             #               iniciar negociacao
                            nearest_truck, nearest_distance = min(propostas, key=lambda x: x[1])                                                                        #               selecionar truck mais proximo
                            if nearest_truck != self.agent.nearest_truck:                                                                                               #               se o truck atualmente mais proximo for diferente do anterior (i.e., diferente de none)
                                self.agent.nearest_truck_distance=nearest_distance                                                                                      #                   nova distancia minima do truck mais proximo
                                self.agent.nearest_truck=nearest_truck                                                                                                  #                   novo truck mais proximo
                                if self.agent.nearest_truck:                                                                                                            #                   se houver truck mais proximo
                                    #for truck, distance in propostas:                                                                                                   #                       para cada truck nas propostas
                                        #if truck!=self.agent.nearest_truck:                                                                                             #                           se o truck nao for o mais proximo
                                            #print(f"{self.agent.jid} rejeitou proposta de {truck}")                                                                     #                               print
                                    msg_award = Message(to=self.agent.nearest_truck)                                                                                    #                       msg para truck mais proximo
                                    msg_award.set_metadata("performative","accept-proposal")                                                                 #                       performativa é aceitar a proposta
                                    msg_award.body = f"{self.agent.jid};{self.agent.location};{self.agent.waste_level};{self.agent.waste_percent}"                      #                       corpo da msg com jid, localizacao, waste_level e waste_percent
                                    await self.send(msg_award)                                                                                                          #                       mandar a msg
                                    #print(f"{self.agent.jid} aceitou a proposta de {self.agent.nearest_truck}")                                                         #                       print
                        else:                                                                                                                                           #           se nao houver propostas no fim do contador
                            self.agent.inNegotiation = False                                                                                                            #               acabar negociacao
            await asyncio.sleep(0.01)                                                                                                                                   #esperar 0.01 segundos para repetir                                                                                                    #esperar 1 segundo



    #passo 4.2                                                                                                                                                          #CONFIRMAR ACEITACAO DE AWARD
    #COMPORTAMENTO PARA ATIVAR O CONTRATO                                                                                                                               #
    class Handshake(CyclicBehaviour):                                                                                                                                   #
        async def run(self):                                                                                                                                            #
            if self.agent.inNegotiation and not self.agent.target_truck:                                                                                                #se estiver em negociacao e nao tiver truck alvo
                if self.agent.waste_percent >= 70:                                                                                                                      #   se lixo>=70%
                    msg_accept = await self.receive(timeout=2)                                                                                                          #       esperar por msg por 5 segundos
                    if msg_accept and msg_accept.get_metadata("performative") == "confirm":                                                                             #       se receber msg e a performativa for confirmar
                        if self.agent.inNegotiation and not self.agent.target_truck:                                                                                    #           se continuar em negociacao e sem truck alvo
                            if self.agent.waste_percent >= 70:                                                                                                          #               se continuar com o waste_level>70                                                                                                #se nao tem truck alvo
                                self.agent.target_truck = str(msg_accept.body.split(";")[0])                                                                            #                   definir truck alvo
                                self.agent.target_truck_location = str(msg_accept.body.split(";")[1])                                                                   #                   definir localizacao do truck alvo
                                self.agent.target_truck_gas = int(msg_accept.body.split(";")[2])                                                                        #                   definir gas do truck alvo
                                self.agent.target_truck_load = int(msg_accept.body.split(";")[3])                                                                       #                   definir load do truck alvo
                                self.agent.target_truck_distance = manhattan_distance(self.agent.location, eval(self.agent.target_truck_location))                      #                   definir distancia do truck alvo
                                self.agent.inNegotiation = False                                                                                                        #                   terminar negociacao
                                print(f"{self.agent.jid} com recolha confirmada! À espera de {self.agent.target_truck}")                                                #                   print
                                self.agent.tempo_total_comunicacao += (time.time()-self.agent.tempo_inicial_comunicacao)
                                self.agent.tempo_inicia_recolha = time.time()
                    if not msg_accept:                                                                                                                                  #       se nao receber msg
                        print(f"{self.agent.jid} sem confirmacao! A realocar recolha!")                                                                                 #           print
                        self.agent.target_truck = None                                                                                                                  #           limpar truck alvo
                        self.agent.target_truck_location = None                                                                                                         #           limpar localizacao de truck alvo
                        self.agent.target_truck_gas = None                                                                                                              #           limpar gas de truck alvo
                        self.agent.target_truck_load = None                                                                                                             #           limpar load de truck alvo
                        self.agent.target_truck_distance = None                                                                                                         #           limpar distancia de truck alvo
                        self.agent.inNegotiation = False                                                                                                                #           terminar negociacao
                        self.agent.numero_realocacoes_erro+=1                                                                                                           #           adicionar 1 ao numero de realocacoes por falha em award contract
            await asyncio.sleep(0.01)                                                                                                                                   #esperar 0.01 segundos



    #passo 5                                                                                                                                                            #RECEBER RESULTADOS DE RECOLHA
    #COMPORTAMENTO PARA RECEBER O RESULTADO DA RECOLHA                                                                                                                  #
    class ReceiveResults(CyclicBehaviour):                                                                                                                              #
        async def run(self):                                                                                                                                            #
            msg_results = await self.receive()                                                                                                                          #esperar por msg constantemente
            if msg_results and msg_results.get_metadata("performative") == "agree":                                                                                     #se receber msg e tiver performativa agree
                if not self.agent.inNegotiation and self.agent.target_truck:                                                                                            #   se nao estiver em negociacao e houver truck alvo
                    if self.agent.waste_percent >= 70:                                                                                                                  #       se o waste>70%
                        self.agent.tempo_total_recolha += (time.time()-self.agent.tempo_inicia_recolha)
                        self.agent.waste_level = 0                                                                                                                      #           limpar waste level
                        self.agent.waste_percent = 0                                                                                                                    #           limpar waste percent
                        print(f"Lixo de {self.agent.jid} recolhido por {self.agent.target_truck}")                                                                      #           print
                        self.agent.target_truck = None                                                                                                                  #           limpar truck alvo
                        self.agent.target_truck_location = None                                                                                                         #           limpar localizacao truck alvo
                        self.agent.target_truck_distance = None                                                                                                         #           limpar distancia truck alvo
                        self.agent.target_truck_gas = None                                                                                                              #           limpar gas truck alvo
                        self.agent.target_truck_load = None                                                                                                             #           limpar load truck alvo
                        self.agent.inNegotiation = False                                                                                                                #           terminar negociacoes
                        self.agent.numero_recolhas+=1                                                                                                                   #           adicionar 1 recolha ao numero total de recolhas do bin
            await asyncio.sleep(0.01)                                                                                                                                   #esperar 0.01 segundos





#--------------------COMPORTAMENTOS VARIADOS--------------------





    #FUNCAO PARA GERAR POSICAO VALIDA                                                                                                                                   #
    def gen_valid_pos(self):                                                                                                                                            #
        position = self.environment.random_position()                                                                                                                   #gerar posicao aleatoria
        while position == self.environment.central_depot or position in self.environment.roadblocks or any(b.location==position for b in self.environment.bins):        #enquanto posicao for invalida
            position=self.environment.random_position()                                                                                                                 #   gerar nova posicao
        return position                                                                                                                                                 #retornar posicao valida



    #COMPORTAMENTO PARA REFRESH DA PERCENT                                                                                                                              #
    class RefreshPercent(PeriodicBehaviour):                                                                                                                            #
        async def run(self):                                                                                                                                            #
            self.agent.waste_percent = int((self.agent.waste_level / self.agent.capacity) * 100)                                                                        #calcular percentagem



    #COMPORTAMENTO PARA ATUALIZAR WASTE LEVEL                                                                                                                           #
    class UpdateWasteLevel(PeriodicBehaviour):                                                                                                                          #
        async def run(self):                                                                                                                                            #
            if self.agent.waste_level<=self.agent.capacity:                                                                                                             #se o lixo nao estiver cheio
                temp = self.agent.waste_level+random.randint(1,5)                                                                                                 #   gerar quantia aleatoria (mais 1-5) nova de lixo
                self.agent.waste_level=min(temp,self.agent.capacity)                                                                                                    #   se a nova quantia for valida, adicionar
                self.agent.waste_percent=int((self.agent.waste_level/self.agent.capacity)*100)                                                                          #   atualizar percentagem



    #COMPORTAMENTO PARA LIMPAR OBJETIVOS                                                                                                                                #
    class RestartBin(CyclicBehaviour):                                                                                                                                  #
        async def run(self):                                                                                                                                            #
            msg_restart_bin = await self.receive()                                                                                                                      #esperar por msg constantemente
            if msg_restart_bin and msg_restart_bin.get_metadata("performative") == "inform":                                                                            #se receber msg e a performativa for inform
                if "RESTART_BIN" in msg_restart_bin.body:                                                                                                               #   se o corpo for RESTART_BIN
                    self.agent.target_truck = None                                                                                                                      #       limpar truck alvo
                    self.agent.target_truck_location = None                                                                                                             #       limpar localizacao truck alvo
                    self.agent.target_truck_distance = None                                                                                                             #       limpar distancia truck alvo
                    self.agent.target_truck_gas = None                                                                                                                  #       limpar gas truck alvo
                    self.agent.target_truck_load = None                                                                                                                 #       limpar load truck alvo
                    self.agent.inNegotiation = False                                                                                                                    #       terminar negociacao
                    self.agent.nearest_truck = None                                                                                                                     #       limpar truck mais proximo
                    self.agent.nearest_truck_distance = 10000                                                                                                           #       limpar distancia do truck mais proximo
                    self.agent.numero_realocacoes_transito_ou_depot+=1                                                                                                  #       adicionar 1 ao numero de realocacoes por transito ou paragens em depot
            await asyncio.sleep(0.01)                                                                                                                                   #esperar 0.01 segundos



    #COMPORTAMENTO PARA PEDIR RECOLHA NOVAMENTE SE NAO É RECOLHIDO HA MUITO TEMPO                                                                                       #
    class EmergencyPickup(CyclicBehaviour):                                                                                                                             #
        async def run(self):                                                                                                                                            #
            if self.agent.waste_level >= 70:                                                                                                                            #se o waste>=70%
                await asyncio.sleep(30)                                                                                                                                 #   esperar 30 segunds
                if self.agent.waste_level>=70:                                                                                                                          #   se continuar waste>=70%
                    self.agent.target_truck = None                                                                                                                      #       limpar truck alvo
                    self.agent.target_truck_location = None                                                                                                             #       limpar localizacao truck alvo
                    self.agent.target_truck_distance = None                                                                                                             #       limpar distancia truck alvo
                    self.agent.target_truck_gas = None                                                                                                                  #       limpar gas truck alvo
                    self.agent.target_truck_load = None                                                                                                                 #       limpar load truck alvo
                    self.agent.inNegotiation = False                                                                                                                    #       terminar negociacao
                    self.agent.nearest_truck = None                                                                                                                     #       reinicia o truck mais proximo
                    self.agent.nearest_truck_distance = 10000                                                                                                           #       reinicia a distanciua do truck mais proximo
                    for t in self.agent.environment.trucks:                                                                                                             #       para todos os trucks no ambiente
                        msg_rfb = Message(to=str(t.jid))                                                                                                                #           destinatario da msg (truck)
                        msg_rfb.set_metadata("performative", "cfp")                                                                                          #           call for proposal
                        msg_rfb.body = f"{self.agent.jid};{self.agent.location};{self.agent.waste_level};{self.agent.waste_percent}"                                    #           corpo da msg com jid, localizacao, waste level, waste percent
                        await self.send(msg_rfb)                                                                                                                        #           enviar a msg
                    print(f"{self.agent.jid} à espera de recolha há muito tempo (30s)! A pedir recolha de emergência")                                                  #       print
                    self.agent.numero_recolhas_emergencia+=1                                                                                                            #       adicionar 1 ao numero total de recolhas de emergencia
            await asyncio.sleep(0.01)                                                                                                                                   #esperar 0.01 segundos




    #--------------------SETUP DE COMPORTAMENTOS--------------------





    #COMPORTAMENTOS                                                                                                                                                     #
    async def setup(self):                                                                                                                                              #
        self.add_behaviour(self.RefreshPercent(period=0.1))                                                                                                             #atualizar percent a cada 0.01 segundos
        self.add_behaviour(self.UpdateWasteLevel(period=random.randint(3,6)))                                                                                     #atualizar waste level a cada tempo random entre 3-6 segundos
        self.add_behaviour(self.EmergencyPickup())                                                                                                                      #verificar se precisa de recolha de emergencia
        self.add_behaviour(self.RestartBin())                                                                                                                           #escutar para reiniciar o bin
        self.add_behaviour(self.RequestForBids_SendRFB())                                                                                                               #escutar para pedir recolha
        self.add_behaviour(self.SelectBid_AwardContract())                                                                                                              #selecionar bid
        self.add_behaviour(self.Handshake())                                                                                                                            #finalizar contrato
        self.add_behaviour(self.ReceiveResults())                                                                                                                       #escutar para receber resultados do contrato