import socket
import json
import random
import time

# IP y puerto del servidor (ajusta si es diferente)
SERVER_IP = '192.168.0.109'
SERVER_PORT = 1234

# Objetos simulados que el "robot" puede ver
objetos_simulados = ['cuadrado', 'circulo', 'triangulo', 'contenedor', '']

def generar_dato_falso():
    objeto = random.choice(objetos_simulados)
    tamaño = random.randint(0, 250) if objeto else 0
    return {
        "objeto": objeto,
        "tamaño": tamaño
    }

def cliente_simulado():
    try:
        # Crear socket y conectar
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        print("✅ Cliente conectado al servidor")

        while True:
            # Simular objeto detectado
            datos = generar_dato_falso()
            mensaje = json.dumps(datos)

            print(f"📤 Enviando: {mensaje}")
            sock.sendall(mensaje.encode('utf-8'))

            # Esperar respuesta del servidor
            respuesta = sock.recv(1024)
            if not respuesta:
                print("❌ Conexión cerrada por el servidor")
                break

            print(f"📥 Respuesta del servidor: {respuesta.decode('utf-8')}")
            print("-" * 50)
            time.sleep(1)  # Esperar un segundo antes de enviar otro dato

    except Exception as e:
        print(f"❌ Error en cliente: {e}")
    finally:
        sock.close()
        print("🔌 Cliente desconectado")

if __name__ == "__main__":
    cliente_simulado()
