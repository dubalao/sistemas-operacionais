import socket
import threading
import pickle
import sys
from comun import Processo, enviar_dado

HOST = 'localhost'
PORT_CLOCK = 4001  
PORT_ESCALONADOR = 4002  

tarefas = []
tarefas_emitidas = []
ultima_tarefa_enviada = False

def carregar_arquivo(nome):
    lista = []
    with open(nome, 'r') as f:
        for linha in f:
            if linha.strip():
                partes = linha.strip().split(";")
                tarefa = Processo(partes[0], partes[1], partes[2], partes[3])
                lista.append(tarefa)
    return lista

def servidor_clock():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT_CLOCK))
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
            clock = pickle.loads(dados)
            emitir_tarefas(clock)
            if ultima_tarefa_enviada:
                break

def emitir_tarefas(clock):
    global ultima_tarefa_enviada
    enviadas_nesse_tick = [t for t in tarefas if t.tempo_ingresso == clock]
    for tarefa in enviadas_nesse_tick:
        enviar_dado(tarefa, HOST, PORT_ESCALONADOR)
        tarefas_emitidas.append(tarefa)
        print(f"[{clock}] Tarefa {tarefa.id} enviada")
    
    for t in enviadas_nesse_tick:
        tarefas.remove(t)

    if not tarefas and not ultima_tarefa_enviada:
        enviar_dado("FIM", HOST, PORT_ESCALONADOR)
        ultima_tarefa_enviada = True

def main():
    if len(sys.argv) < 2:
        print("Uso: python emissor.py <arquivo_entrada>")
        sys.exit(1)
    global tarefas
    tarefas = carregar_arquivo(sys.argv[1])
    servidor_clock()

if __name__ == "__main__":
    main()
