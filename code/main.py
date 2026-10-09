import time

from imports import *
from ambiente import Environment
from camiao import TruckAgent
from lixo import BinAgent






#--------------------CLASSES-------------------





#REDIRECIONAR O OUTPUT PARA O LOG DO TKINTER
class TextRedirector:

    #INICIAR WIDGET
    def __init__(self, widget):
        self.widget = widget

    #IMPRIMIR NO TERMINAL
    def write(self, string):
        sys.__stdout__.write(string)  # Usa o stdout original para não perder o output no terminal
        self.widget.configure(state=tk.NORMAL)
        self.widget.insert(tk.END, string)
        self.widget.configure(state=tk.DISABLED)
        self.widget.see(tk.END)

    def flush(self):
        pass





#--------------------BINS/TRUCKS/ROADBLOCKS--------------------





#MAIN
async def main(environment):



    #OPCOES DE TRUCKS                       #
    num_trucks = 5                          #quantidade
    truck_capacity = 500                    #capacidade
    truck_load_return = None                #a que quantidade de carga voltar ao depot
    truck_gas = 30                          #combustivel total

    #OPCOES DE BINS                         #
    num_bins = 15                           #quantidade
    bin_capacity = 100                      #capacidade
    bin_waste_pickup = None                 #a que quantidade de lixo avisar para recolha


    #CRIAR CAMIOES
    truck_agents = []
    for i in range(num_trucks):
        truck_agents.append(TruckAgent(f"truck{i}@localhost", "truckpassword", environment, truck_capacity, truck_gas))
        environment.trucks.add(truck_agents[i])
    for agent in truck_agents:
        await agent.start()

    #CRIAR CAMIOES
    bin_agents = []
    for i in range(num_bins):
        bin_agents.append(BinAgent(f"bin{i}@localhost", "binpassword", environment, bin_capacity))
        environment.bins.add(bin_agents[i])
    for agent in bin_agents:
        await agent.start()





#--------------------INTERFACE--------------------





    #SETUP TKINTER
    def start_tkinter():

        #INICIAR ROUTE
        root = tk.Tk()
        root.title("Simulador de Recolha de Lixo")

        #LAYOUT PRINCIPAL COM 2 FRAMES
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        bottom_frame = tk.Frame(root, height=300)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        #CANVAS DE VISUALIZACAO
        canvas = tk.Canvas(top_frame, width=800, height=800, bg="lightgray")
        canvas.pack()

        #AJUSTAR TAMANHO IMAGENS E LIXEIRAS
        caminhao_img = Image.open("camiao.png").resize((80, 80), Image.Resampling.LANCZOS)
        caminhao_img_tk = ImageTk.PhotoImage(caminhao_img)
        lixo_img = Image.open("lixeira.png").resize((50, 50), Image.Resampling.LANCZOS)
        lixo_img_tk = ImageTk.PhotoImage(lixo_img)

        #WIDGET DE TEXTO PARA OS LOGS
        log_text = tk.Text(
            bottom_frame,
            height=15,  # Maior altura para mais linhas
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="black",
            fg="white",
            font=("Consolas", 8)  # Fonte maior para melhor leitura
        )
        log_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #REDIRECIONAR SAIDA DO TERMINAL PARA WODGET TEXTO
        sys.stdout = TextRedirector(log_text)

        #DESENHO DE GRID NO CANVAS
        def draw_grid():
            for i in range(0, 800, 80):
                canvas.create_line([(i, 0), (i, 800)], fill="gray")
                canvas.create_line([(0, i), (800, i)], fill="gray")

        #DESENHAR TEXTO COM CONTORNO (para melhorar a legibilidade)
        def outlined_text(x, y, text, outline_color="white", fill_color="black", font=("Helvetica", 10, "bold")):
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                canvas.create_text(x + dx, y + dy, text=text, fill=outline_color, font=font)
                canvas.create_text(x, y, text=text, fill=fill_color, font=font)

        #ATUALIZACAO CONTINUA DA INTERFACE
        def update_display(teste):
            canvas.delete("all")
            draw_grid()
            #DEPOT
            depot_x, depot_y = environment.central_depot
            canvas.create_rectangle(depot_x * 80, depot_y * 80, depot_x * 80 + 80, depot_y * 80 + 80, fill="blue")
            canvas.create_text(depot_x * 80 + 40, depot_y * 80 + 40, text="Depot", fill="white", font=("Helvetica", 12, "bold"))
            #CAMIOES
            for i, truck in enumerate(truck_agents):
                x, y = truck.location
                canvas.create_image(x * 80, y * 80, anchor=tk.NW, image=caminhao_img_tk)
                outlined_text(x * 80 + 40, y * 80 + 65,f"T{i}\nL{truck.current_load}/{truck.capacity}\nG{truck.gas}/{truck.gas_total}",outline_color="black", fill_color="white")
                if truck.is_stopped != 0:
                    canvas.create_text(x * 80 + 30, y * 80 + 20, text=f"Parado {truck.is_stopped}s", fill="red",font=("Helvetica", 15, "bold"))
            #LIXOS
            for i, b in enumerate(bin_agents):
                x, y = b.location
                canvas.create_image(x * 80 + 20, y * 80 + 20, anchor=tk.NW, image=lixo_img_tk)
                outlined_text(x * 80 + 40, y * 80 + 65, f"B{i} \n ({b.waste_percent}%)\n ",outline_color="black", fill_color="green" if b.waste_percent >= 70 else "white")
            #ROADBLOCKS
            for (rx, ry) in environment.roadblocks:
                canvas.create_rectangle(rx * 80 + 25, ry * 80 + 25, rx * 80 + 55, ry * 80 + 55, fill="black")
            #ROOT
            root.after(1, update_display, "teste")

        #INICIA ATUALIZACAO DA INTERFACE
        root.after(1, update_display, "teste")
        root.mainloop()


    #THREAD PARA RODAR TKINTER E EXECUCAO PRINCIPAL
    tk_thread = threading.Thread(target=start_tkinter)
    tk_thread.start()





#--------------------INICIAR/PARAR--------------------





    #CRONOMETRIZACAO
    tempo_inicio = time.time()
    tempo_simulacao = 600

    #COMECAR (e roadblocks)
    try:
        while time.time()-tempo_inicio<tempo_simulacao:
            await environment.generate_temporary_roadblocks()
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("Stopping agents...")



    #PARAR BINS
    for agent in bin_agents:
        await agent.stop()



    #PARAR TRUCKS
    for agent in truck_agents:
        await agent.stop()





#--------------------EXTRACAO VALORES METRICAS-------------------





    #DEFINICAO METRICAS (truck)                          #
    bins_recolhidos_truck = []                  #lista com numero de bins recolhidos por cada TRUCK
    lixo_recolhido_truck = []                   #lista com quantidade total de lixo recolhido por cada TRUCK
    lixo_recolhido_medio_truck = []             #lista com quantidade media de lixo recolhida por recolha
    gas_consumido_total_truck = []              #lista com consumo total de gas por cada TRUCK (=distancia_percorrida_total_truck)
    gas_consumido_medio_truck = []              #lista com consump medio de gas por recolha (=distancia_percorrida_media_truck)
    vezes_depot_voluntario_truck = []           #lista com vezes total que o truck voltou ao depot voluntariamente
    vezes_depot_passagem_truck = []             #lista com vezes total que o truck aproveitou quando passou no depot para reabastecer e deixar lixo
    vezes_depot_total_truck = []                #lista com vezes total que o truck parou no depot (voluntariamente e de passagem)
    #nao vale a pena fazer tempo medio de recolha do truck para o bin, pois sera +/- a distancia do truck ao bin.
    #vale a pena fazer o tempo medio de recolha de cada bin, pois a recolha pode ser cancelada, realocada, atrasada,...s

    #DEFINICAO METRICAS (bin)                            #
    num_recolhas_bin = []                       #lista com numero de recolhas de cada BIN
    num_recolhas_emergencia_bin = []            #lista com numero de recolhas de emergencias de cada BIN
    num_realocacoes_transito_ou_depot_bin = []  #lista com numero de realocacoes devido a transito ou paragem/regresso ao depot de cada BIN
    num_realocacoes_erro_bin = []               #lista com numero de realocacoes devido a falha de comunicacao de cada BIN
    distancia_media_bin_bins = []               #lista com distancia media de cada BIN aos restantes bins
    distancia_bin_depot = []                    #lista com distancia de cada BIN ao depot
    tempo_total_recolha_bin = []                #lista com tempo total de recolha de cada BIN
    tempo_medio_recolha_bin = []                #lista com tempo medio de recolha de cada BIN
    tempo_total_comunicacao_bin = []            #lista com tempo total gasto em comunicacoes (desde request for bids ate handshake)
    tempo_medio_comunicacao_bin = []            #lista com tempo medio de cada comunicacao


    #OBTENCAO METRICAS (truck)
    for i, agent in enumerate(truck_agents):
        bins_recolhidos_truck.append(agent.bins_recolhidos)
        lixo_recolhido_truck.append(agent.lixo_recolhido)
        lixo_recolhido_medio_truck.append(round(lixo_recolhido_truck[i]/bins_recolhidos_truck[i], 2) if bins_recolhidos_truck[i] != 0 else 0.0)
        gas_consumido_total_truck.append(agent.gas_consumido)
        gas_consumido_medio_truck.append(round(gas_consumido_total_truck[i]/bins_recolhidos_truck[i], 2) if bins_recolhidos_truck[i] != 0 else 0.0)
        vezes_depot_voluntario_truck.append(agent.vezes_depot_voluntario)
        vezes_depot_passagem_truck.append(agent.vezes_depot_passagem)
        vezes_depot_total_truck.append(agent.vezes_depot_total)

    #OBTENCAO METRICAS (bin)
    for i, agent in enumerate(bin_agents):
        num_recolhas_bin.append(agent.numero_recolhas)
        num_recolhas_emergencia_bin.append(agent.numero_recolhas_emergencia)
        num_realocacoes_transito_ou_depot_bin.append(agent.numero_realocacoes_transito_ou_depot)
        num_realocacoes_erro_bin.append(agent.numero_realocacoes_erro)
        distancia_bin_depot.append(manhattan_distance(agent.location, environment.central_depot))
        tempo_total_recolha_bin.append(round(agent.tempo_total_recolha, 2) if agent.tempo_total_recolha != 0 else 0.0)
        tempo_medio_recolha_bin.append(round(tempo_total_recolha_bin[i]/num_recolhas_bin[i], 2) if num_recolhas_bin[i] != 0 else 0.0)
        tempo_total_comunicacao_bin.append(round(agent.tempo_total_comunicacao, 2) if agent.tempo_total_comunicacao != 0 else 0.0)
        tempo_medio_comunicacao_bin.append(round(tempo_total_comunicacao_bin[i]/num_recolhas_bin[i], 2) if num_recolhas_bin[i] != 0 else 0.0)

        distancia_total = 0
        for j, agent2 in enumerate(bin_agents):
            if agent!=agent2:
                distancia_total+=manhattan_distance(agent.location, agent2.location)
        distancia_media_bin_bins.append(round(distancia_total/(num_bins-1), 2) if num_bins-1 != 0 else 0.0)


    #PRINT METRICAS (todas)
    print()
    print("--------------------MÉTRICAS--------------------")
    print()
    print("MÉTRICAS TRUCK:")
    print(f"quantidade de bins recolhidos por truck = {bins_recolhidos_truck}")
    print(f"quantidade total de lixo recolhido por truck = {lixo_recolhido_truck}")
    print(f"quantidade media de lixo recolhida em cada recolha por truck = {lixo_recolhido_medio_truck}")
    print(f"quantidade total de gas consumido por truck = {gas_consumido_total_truck}")
    print(f"quantidade media de gas consumido em cada recolha por truck = {gas_consumido_medio_truck}")
    print(f"quantidade de idas ao depot (voluntarias) por truck = {vezes_depot_voluntario_truck}")
    print(f"quantidade idas ao depot (por passagem) por truck = {vezes_depot_passagem_truck}")
    print(f"quantidade idas ao depot (total) por truck = {vezes_depot_total_truck}")
    print()
    print("MÉTRICAS BIN:")
    print(f"quantidade de recolhas normais por bin = {num_recolhas_bin}")
    print(f"quantidade de recolhas de emergencia por bin = {num_recolhas_emergencia_bin}")
    print(f"quantidade de realocacoes (derivadas de paragens no transito ou no depot) por bin = {num_realocacoes_transito_ou_depot_bin}")
    print(f"quantidade de realocacoes (derivadas de erros de comunicacao) por bin = {num_realocacoes_erro_bin}")
    print(f"distancia do bin ao depot = {distancia_bin_depot}")
    print(f"distancia media do bin aos restantes bins = {distancia_media_bin_bins}")
    print(f"tempo total gasto em recolhas por bin = {tempo_total_recolha_bin}")
    print(f"tempo medio gasto por recolha por bin = {tempo_medio_recolha_bin}")
    print(f"tempo total gasto em comunicacoes por bin = {tempo_total_comunicacao_bin}")
    print(f"tempo medio gasto por comunicacao por bin = {tempo_medio_comunicacao_bin}")





#--------------------INICIAR--------------------





#INICIAR
if __name__ == "__main__":
    asyncio.run(main(Environment()))
