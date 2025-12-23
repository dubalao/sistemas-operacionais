import pickle

class Processo:
    def __init__(self, id, tempo_ingresso, duracao_prevista, prioridade):
        self.id = id
        self.tempo_ingresso = int(tempo_ingresso)
        self.duracao_prevista = int(duracao_prevista)
        self.prioridade = int(prioridade)
        self.inicio_execucao = None
        self.fim_execucao = None
        self.turnaround_time = None
        self.waiting_time = None

def enviar_dado(dado, host, porta):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, porta))
            s.sendall(pickle.dumps(dado))
        except ConnectionRefusedError:
            pass

def salvar_saida(fila, sequencia):
    with open('saida.txt', 'w') as f:
        f.write(";".join(sequencia) + "\n")

        turnaround_total = 0
        waiting_total = 0
        num = len(fila)

        for processo in fila:
            processo.turnaround_time = processo.fim_execucao - processo.tempo_ingresso
            processo.waiting_time = processo.turnaround_time - processo.duracao_prevista
            turnaround_total += processo.turnaround_time
            waiting_total += processo.waiting_time
            f.write(f"{processo.id};{processo.inicio_execucao};{processo.fim_execucao};{processo.turnaround_time};{processo.waiting_time}\n")
        
        if num > 0:
            media_turnaround = round((turnaround_total / num) + 0.0499, 1)
            media_waiting = round((waiting_total / num) + 0.0499, 1)
        else:
            media_turnaround = 0.0
            media_waiting = 0.0

        f.write(f"{media_turnaround};{media_waiting}\n")
