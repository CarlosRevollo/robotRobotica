import socket

# IP local del servidor (puede ser '0.0.0.0' para aceptar de cualquier IP)
HOST = '0.0.0.0'
PORT = 12345

# Crear socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servidor escuchando en {HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    print(f"Conexión desde {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Recibido: {data.decode()}")
        conn.sendall(b"ACK")  # enviar respuesta opcional

    conn.close()
    print("Cliente desconectado.")
