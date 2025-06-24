


###PRUEBA MANUAL#############


import socket
import threading
import time
from datetime import datetime

class ServidorControlManual:
    def __init__(self, host='0.0.0.0', port=1234):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.robots_conectados = {}
        
    def iniciar_servidor(self):
        """Inicia el servidor TCP"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print("=" * 60)
            print("🤖 SERVIDOR DE CONTROL MANUAL INICIADO")
            print("=" * 60)
            print(f"📡 Escuchando en: {self.host}:{self.port}")
            print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n📋 COMANDOS DISPONIBLES:")
            print("   avanzar     - Robot avanza")
            print("   retroceder  - Robot retrocede")
            print("   derecha     - Robot gira a la derecha")
            print("   izquierda   - Robot gira a la izquierda")
            print("   parar       - Robot se detiene")
            print("   agarrar     - Robot activa brazo para agarrar")
            print("   soltar      - Robot suelta objeto")
            print("   velocidad X - Cambia velocidad (0-255)")
            print("   salir       - Cierra el servidor")
            print("\n⏳ Esperando conexiones de robots...")
            
            # Iniciar hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self.aceptar_conexiones)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Iniciar hilo para comandos de consola
            console_thread = threading.Thread(target=self.manejar_consola)
            console_thread.daemon = True
            console_thread.start()
            
            # Mantener el servidor activo
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
    
    def aceptar_conexiones(self):
        """Acepta nuevas conexiones de robots"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                robot_id = f"{address[0]}:{address[1]}"
                self.robots_conectados[robot_id] = {
                    'socket': client_socket,
                    'address': address,
                    'conectado': True
                }
                
                print(f"\n✅ Robot conectado: {robot_id}")
                print(f"📊 Total robots conectados: {len(self.robots_conectados)}")
                
                # Crear hilo para monitorear este robot
                monitor_thread = threading.Thread(
                    target=self.monitorear_robot, 
                    args=(client_socket, robot_id)
                )
                monitor_thread.daemon = True
                monitor_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"❌ Error aceptando conexión: {e}")
    
    def monitorear_robot(self, client_socket, robot_id):
        """Monitorea la conexión de un robot específico"""
        try:
            while self.running and self.robots_conectados.get(robot_id, {}).get('conectado', False):
                # Verificar si el robot está conectado
                try:
                    client_socket.settimeout(1.0)
                    # Intentar recibir datos (si el robot envía algo)
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    # Si el robot envía datos, los mostramos
                    mensaje = data.decode('utf-8').strip()
                    if mensaje:
                        print(f"📨 [{robot_id}] Mensaje: {mensaje}")
                except socket.timeout:
                    # Timeout normal, continuar
                    continue
                except:
                    # Conexión perdida
                    break
                    
        except Exception as e:
            print(f"❌ [{robot_id}] Error monitoreando: {e}")
        finally:
            self.desconectar_robot(robot_id)
    
    def desconectar_robot(self, robot_id):
        """Desconecta un robot específico"""
        if robot_id in self.robots_conectados:
            try:
                self.robots_conectados[robot_id]['socket'].close()
            except:
                pass
            del self.robots_conectados[robot_id]
            print(f"🔌 Robot desconectado: {robot_id}")
            print(f"📊 Robots conectados restantes: {len(self.robots_conectados)}")
    
    def enviar_comando_a_robots(self, comando):
        """Envía un comando a todos los robots conectados"""
        if not self.robots_conectados:
            print("⚠️ No hay robots conectados")
            return False
        
        robots_desconectados = []
        comando_enviado = False
        
        for robot_id, robot_info in self.robots_conectados.items():
            try:
                socket_robot = robot_info['socket']
                mensaje = comando + '\n'
                socket_robot.send(mensaje.encode('utf-8'))
                print(f"📤 [{robot_id}] Comando enviado: {comando}")
                comando_enviado = True
                
            except Exception as e:
                print(f"❌ [{robot_id}] Error enviando comando: {e}")
                robots_desconectados.append(robot_id)
        
        # Limpiar robots desconectados
        for robot_id in robots_desconectados:
            self.desconectar_robot(robot_id)
        
        return comando_enviado
    
    def procesar_comando_consola(self, comando_input):
        """Procesa comandos ingresados por consola"""
        comando_input = comando_input.strip().lower()
        
        if comando_input == "salir":
            return False
        elif comando_input == "avanzar":
            self.enviar_comando_a_robots("AVANZAR")
        elif comando_input == "retroceder":
            self.enviar_comando_a_robots("RETROCEDER")
        elif comando_input == "derecha":
            self.enviar_comando_a_robots("DERECHA")
        elif comando_input == "izquierda":
            self.enviar_comando_a_robots("IZQUIERDA")
        elif comando_input == "parar":
            self.enviar_comando_a_robots("PARAR")
        elif comando_input == "agarrar":
            self.enviar_comando_a_robots("AGARRAR")
        elif comando_input == "soltar":
            self.enviar_comando_a_robots("SOLTAR")
        # elif comando_input.startswith("velocidad "):
        #     try:
        #         velocidad = int(comando_input.split(" ")[1])
        #         if 0 <= velocidad <= 255:
        #             self.enviar_comando_a_robots(f"VELOCIDAD {velocidad}")
        #         else:
        #             print("⚠️ Velocidad debe estar entre 0 y 255")
        #     except:
        #         print("⚠️ Formato incorrecto. Usar: velocidad 120")
        elif comando_input.startswith("velocidadd"):
            try:
                velocidad = int(comando_input.split(" ")[1])
                if 0 <= velocidad <= 255:
                    self.enviar_comando_a_robots(f"VELOCIDADD {velocidad}")
                else:
                    print("⚠️ Velocidad debe estar entre 0 y 255")
            except:
                print("⚠️ Formato incorrecto. Usar: velocidadd 120")

        elif comando_input.startswith("velocidadi"):
            try:
                velocidad = int(comando_input.split(" ")[1])
                if 0 <= velocidad <= 255:
                    self.enviar_comando_a_robots(f"VELOCIDADI {velocidad}")
                else:
                    print("⚠️ Velocidad debe estar entre 0 y 255")
            except:
                print("⚠️ Formato incorrecto. Usar: velocidadi 120")

        elif comando_input.startswith("angulog"):
            try:
                angulo = int(comando_input.split(" ")[1])
                if 0 <= angulo <= 180:
                    self.enviar_comando_a_robots(f"ANGULOG {angulo}")
                else:
                    print("⚠️ Angulo debe estar entre 0 y 180")
            except:
                print("⚠️ Formato incorrecto. Usar: angulog 120")

        elif comando_input.startswith("angulob"):
            try:
                angulo = int(comando_input.split(" ")[1])
                if -180 <= angulo <= 360:
                    self.enviar_comando_a_robots(f"ANGULOB {angulo}")
                else:
                    print("⚠️ Angulo debe estar entre 0 y 180")
            except:
                print("⚠️ Formato incorrecto. Usar: angulog 120")


        elif comando_input == "robots":
            print(f"📊 Robots conectados: {len(self.robots_conectados)}")
            for robot_id in self.robots_conectados:
                print(f"   🤖 {robot_id}")
        elif comando_input == "ayuda":
            self.mostrar_ayuda()
        else:
            print("⚠️ Comando no reconocido. Escribe 'ayuda' para ver comandos disponibles")
        
        return True
    
    def mostrar_ayuda(self):
        """Muestra la ayuda de comandos"""
        print("\n📋 COMANDOS DISPONIBLES:")
        print("   avanzar     - Robot avanza")
        print("   retroceder  - Robot retrocede")
        print("   derecha     - Robot gira a la derecha")
        print("   izquierda   - Robot gira a la izquierda")
        print("   parar       - Robot se detiene")
        print("   agarrar     - Robot activa brazo para agarrar")
        print("   soltar      - Robot suelta objeto")
        print("   velocidad X - Cambia velocidad (0-255)")
        print("   robots      - Muestra robots conectados")
        print("   ayuda       - Muestra esta ayuda")
        print("   salir       - Cierra el servidor")
    
    def manejar_consola(self):
        """Maneja los comandos ingresados por consola"""
        while self.running:
            try:
                comando = input("\n🎮 Comando: ")
                if not self.procesar_comando_consola(comando):
                    self.detener_servidor()
                    break
            except KeyboardInterrupt:
                self.detener_servidor()
                break
            except Exception as e:
                print(f"❌ Error en consola: {e}")
    
    def detener_servidor(self):
        """Detiene el servidor"""
        print("\n🛑 Deteniendo servidor...")
        self.running = False
        
        # Cerrar todas las conexiones de robots
        for robot_id, robot_info in self.robots_conectados.items():
            try:
                robot_info['socket'].close()
            except:
                pass
        
        self.robots_conectados.clear()
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("✅ Servidor detenido correctamente")

# Ejecutar servidor
if __name__ == "__main__":
    print("🚀 Iniciando Servidor de Control Manual...")
    servidor = ServidorControlManual()
    
    try:
        servidor.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupción detectada...")
        servidor.detener_servidor()
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        servidor.detener_servidor()