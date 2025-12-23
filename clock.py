import time
from comun import enviar_dado

HOST = 'localhost'
PORT_EMISSOR = 4001
PORT_ESCALONADOR = 4003  

def main():
    clock = 0
    while True:
        enviar_dado(clock, HOST, PORT_EMISSOR)
        time.sleep(0.005)
        enviar_dado(clock, HOST, PORT_ESCALONADOR)
        time.sleep(0.1)  
        clock += 1

if __name__ == "__main__":
    main()
