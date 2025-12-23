import threading
import socket
import pickle
import sys
from comun import Processo, salvar_saida
import matplotlib.pyplot as plt
import numpy as np

HOST = 'localhost'
PORT_ESCALONADOR_TAREFAS = 4002  
PORT_ESCALONADOR_TICKS = 4003     
PORT_CLOCK_CONTROL = 4000

fila_pronta = []
sequencia = []
tempo_atual = 0


def fcfs(fila):
    fila.sort(key=lambda x: x.tempo_ingresso)
    tempo = 0
    for p in fila:
        if tempo < p.tempo_ingresso:
            tempo = p.tempo_ingresso
        p.inicio_execucao = tempo
        tempo += p.duracao_prevista
        p.fim_execucao = tempo
        sequencia.append(p.id)

def rr(fila, quantum=2):
    tempo = 0
    fila.sort(key=lambda p: p.tempo_ingresso)
    fila_aux = []
    fila_aux.append(fila[0])
    fila = fila[1:]
    restante = {p.id: p.duracao_prevista for p in fila_aux + fila}
    while fila_aux or fila:
        if not fila_aux:
            fila_aux.append(fila.pop(0))
        atual = fila_aux.pop(0)
        if atual.inicio_execucao is None:
            atual.inicio_execucao = tempo
        execucao = min(quantum, restante[atual.id])
        tempo += execucao
        restante[atual.id] -= execucao
        sequencia.append(atual.id)
        for p in fila[:]:
            if p.tempo_ingresso <= tempo:
                fila_aux.append(p)
                fila.remove(p)
        if restante[atual.id] > 0:
            fila_aux.append(atual)
        else:
            atual.fim_execucao = tempo

def sjf(fila_pronta, tempo, sequencia):
    fila_aux = fila_pronta.copy()
    fila_aux.sort(key=lambda x: (x.tempo_ingresso, x.duracao_prevista))
    tempo = fila_aux[0].tempo_ingresso

    while fila_aux:
        fila_disp = [p for p in fila_aux if p.tempo_ingresso <= tempo]
        if not fila_disp:
            tempo += 1
            continue
        fila_disp.sort(key=lambda x: x.duracao_prevista)
        atual = fila_disp[0]
        atual.inicio_execucao = tempo
        for _ in range(atual.duracao_prevista):
            sequencia.append(atual.id)
            tempo += 1
        atual.fim_execucao = tempo
        fila_aux.remove(atual)


def srtf(fila_pronta, tempo_atual, sequencia):
    fila_execucao = []
    processos_finalizados = []

    
    for processo in fila_pronta:
        processo.tempo_restante = processo.duracao_prevista

    
    fila_pronta.sort(key=lambda p: p.tempo_ingresso)

    while fila_pronta or fila_execucao:
       
        while fila_pronta and fila_pronta[0].tempo_ingresso <= tempo_atual:
            processo = fila_pronta.pop(0)
            fila_execucao.append(processo)

        if fila_execucao:
            
            fila_execucao.sort(key=lambda p: p.tempo_restante)
            processo_em_execucao = fila_execucao[0]

            
            if processo_em_execucao.inicio_execucao is None:
                processo_em_execucao.inicio_execucao = tempo_atual

            processo_em_execucao.tempo_restante -= 1
            sequencia.append(processo_em_execucao.id)

            if processo_em_execucao.tempo_restante == 0:
                processo_em_execucao.fim_execucao = tempo_atual + 1
                fila_execucao.pop(0)
                processos_finalizados.append(processo_em_execucao)
        else:
            sequencia.append("idle")

        tempo_atual += 1

    fila_pronta[:] = processos_finalizados


def prioc(fila_pronta, tempo, sequencia):
    fila_aux = fila_pronta.copy()
    fila_aux.sort(key=lambda x: (x.tempo_ingresso, x.prioridade))
    tempo = fila_aux[0].tempo_ingresso

    while fila_aux:
        fila_disp = [p for p in fila_aux if p.tempo_ingresso <= tempo]
        if not fila_disp:
            tempo += 1
            continue
        fila_disp.sort(key=lambda x: x.prioridade)
        atual = fila_disp[0]
        atual.inicio_execucao = tempo
        for _ in range(atual.duracao_prevista):
            sequencia.append(atual.id)
            tempo += 1
        atual.fim_execucao = tempo
        fila_aux.remove(atual)


def priop(fila_pronta, tempo, sequencia):
    fila_aux = fila_pronta.copy()
    fila_aux.sort(key=lambda x: x.tempo_ingresso)
    tempo = fila_aux[0].tempo_ingresso
    em_execucao = None
    restante = {p.id: p.duracao_prevista for p in fila_aux}
    fila_final = []

    while fila_aux or em_execucao:
        disponiveis = [p for p in fila_aux if p.tempo_ingresso <= tempo]
        if disponiveis:
            disponiveis.sort(key=lambda x: x.prioridade)
            if not em_execucao or disponiveis[0].prioridade < em_execucao.prioridade:
                if em_execucao and restante[em_execucao.id] > 0:
                    fila_aux.append(em_execucao)
                em_execucao = disponiveis[0]
                if em_execucao.inicio_execucao is None:
                    em_execucao.inicio_execucao = tempo
                fila_aux.remove(em_execucao)

        if em_execucao:
            restante[em_execucao.id] -= 1
            sequencia.append(em_execucao.id)
            tempo += 1
            if restante[em_execucao.id] == 0:
                em_execucao.fim_execucao = tempo
                fila_final.append(em_execucao)
                em_execucao = None
        else:
            tempo += 1

    fila_pronta[:] = fila_final


def priod(fila_pronta, tempo, sequencia):
    fila_aux = fila_pronta.copy()
    fila_aux.sort(key=lambda x: x.tempo_ingresso)
    tempo = fila_aux[0].tempo_ingresso
    em_execucao = None
    restante = {p.id: p.duracao_prevista for p in fila_aux}
    fila_final = []

    while fila_aux or em_execucao:
        for p in fila_aux:
            p.prioridade -= 1  

        disponiveis = [p for p in fila_aux if p.tempo_ingresso <= tempo]
        if disponiveis:
            disponiveis.sort(key=lambda x: x.prioridade)
            if not em_execucao or disponiveis[0].prioridade < em_execucao.prioridade:
                if em_execucao and restante[em_execucao.id] > 0:
                    fila_aux.append(em_execucao)
                em_execucao = disponiveis[0]
                if em_execucao.inicio_execucao is None:
                    em_execucao.inicio_execucao = tempo
                fila_aux.remove(em_execucao)

        if em_execucao:
            restante[em_execucao.id] -= 1
            sequencia.append(em_execucao.id)
            tempo += 1
            if restante[em_execucao.id] == 0:
                em_execucao.fim_execucao = tempo
                fila_final.append(em_execucao)
                em_execucao = None
        else:
            tempo += 1

    fila_pronta[:] = fila_final

def plotar_gantt():
    fig, ax = plt.subplots(figsize=(10, 6))

    with open('saida.txt', 'r') as f:
        linhas = f.readlines()

    sequencia_execucao = linhas[0].strip().split(';')

    ids_unicos = sorted(set(sequencia_execucao), key=lambda x: int(x[1:])) 
    processo_indices = {pid: i for i, pid in enumerate(ids_unicos)}

    cmap = plt.get_cmap('tab20', len(ids_unicos))
    cores = {pid: cmap(i) for i, pid in enumerate(ids_unicos)}

    tempo_atual = 0
    for pid in sequencia_execucao:
        y = processo_indices[pid]
        ax.barh(y, 1, left=tempo_atual, height=0.5, color=cores[pid])
        ax.text(tempo_atual + 0.5, y, pid, va='center', ha='center', color='white', fontsize=8)
        tempo_atual += 1   

    
    ax.set_yticks(range(len(ids_unicos)))
    ax.set_yticklabels(ids_unicos)
    ax.set_xlabel('Tempo')
    ax.set_title('Diagrama de Gantt')
    ax.set_xlim(0, tempo_atual)
    plt.tight_layout()
    plt.show()

def tarefas():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT_ESCALONADOR_TAREFAS))
    s.listen()
    while True:
        conn, _ = s.accept()
        with conn:
            dados = b""
            while True:
                parte = conn.recv(4096)
                if not parte:
                    break
                dados += parte
            objeto = pickle.loads(dados)
            if objeto == "FIM":
                break
            fila_pronta.append(objeto)

def ticks():
    global tempo_atual
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT_ESCALONADOR_TICKS))
    s.listen()
    while True:
        conn, _ = s.accept()
        with conn:
            dados = b""
            while True:
                parte = conn.recv(4096)
                if not parte:
                    break
                dados += parte
            tempo_atual = pickle.loads(dados)

def enviar_sinal_fim():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT_CLOCK_CONTROL))
            s.sendall(pickle.dumps("FIM"))
            print("[Escalonador] Sinal de encerramento enviado ao Clock.")
            sys.exit(1)
        except ConnectionRefusedError:
            print("[Escalonador] Não foi possível se conectar ao Clock para encerramento.")
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Uso: python escalonador.py <algoritmo>")
        sys.exit(1)
    
    algoritmo = sys.argv[1].lower()
    algs = {
        'fcfs': fcfs,
        'rr': rr,
        'sjf': sjf,
        'srtf': srtf,
        'prioc': prioc,
        'priop': priop,
        'priod': priod
    }

    if algoritmo not in algs:
        print("Algoritmo inválido. Opções: fcfs, rr, sjf, srtf, prioc, priop, priod")
        sys.exit(1)

    print(f"[Escalonador] Aguardando tarefas e ticks usando algoritmo {algoritmo.upper()}...")

    t1 = threading.Thread(target=tarefas)
    t2 = threading.Thread(target=ticks)
    t1.start()
    t2.start()
    t1.join()
    

    print(f"[Escalonador] Escalonando {len(fila_pronta)} tarefas...")    
    if algoritmo in ["sjf", "srtf", "prioc", "priop", "priod"]:
        algs[algoritmo](fila_pronta, tempo_atual, sequencia)
    else:
        algs[algoritmo](fila_pronta)
    


    salvar_saida(fila_pronta, sequencia)
    print(f"[Escalonador] Escalonamento concluído. Resultados em saida.txt.")

    plotar_gantt()

    enviar_sinal_fim() #nao esta funcionando
    
if __name__ == "__main__":
    main()
