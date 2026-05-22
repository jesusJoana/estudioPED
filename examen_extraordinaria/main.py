import sys

from src.cliente import ClienteUDP
from src.servidor import ServidorUDP


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py servidor|cliente")
        return 1

    modo = sys.argv[1]

    if modo == "servidor":
        servidor = ServidorUDP()
        servidor.ejecutar()
        return 0

    if modo == "cliente":
        ClienteUDP.ejecutar_desde_terminal()
        return 0

    print("Uso: python main.py servidor|cliente")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
