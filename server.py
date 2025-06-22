# import socket
# import threading
# import json
# import time
# from datetime import datetime

# class ServidorRobotRecolector:
#     def __init__(self, host='0.0.0.0', port=1234):
#         self.host = host
#         self.port = port
#         self.socket = None
#         self.running = False
#         self.clientes = {}
        
#         # Estados del robot
#         self.estados_robot = {}
        
#         # Configuración de tamaños
#         self.tamaño_minimo = 50  # Píxeles mínimos para considerar "suficientemente grande"
#         self.tamaño_maximo = 200  # Píxeles máximos para estar "muy cerca"
        
#         # Objetos reconocidos
#         self.objetos_validos = [
#             "circulo",
#             "cuadrado", "square", "caja", "box",
#             "triangulo", "triangle", 
#             "rectangulo", "rectangle"
#         ]
        
#         # Destinos reconocidos (donde dejar objetos)
#         self.destinos_validos = [
#             "contenedor", "container", "basket", "canasta",
#             "deposito", "deposit", "base", "home"
#         ]
        
#     def iniciar_servidor(self):
#         """Inicia el servidor TCP"""
#         try:
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             self.socket.bind((self.host, self.port))
#             self.socket.listen(5)
#             self.running = True
            
#             print("=" * 60)
#             print("🤖 SERVIDOR ROBOT RECOLECTOR INICIADO")
#             print("=" * 60)
#             print(f"📡 Escuchando en: {self.host}:{self.port}")
#             print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             print(f"📏 Tamaño mínimo objeto: {self.tamaño_minimo} píxeles")
#             print(f"📏 Tamaño máximo (muy cerca): {self.tamaño_maximo} píxeles")
#             print("\n🔄 Estados del robot:")
#             print("   1. BUSCAR_OBJETO → Busca objetos para recolectar")
#             print("   2. IR_AL_OBJETO → Se acerca al objeto detectado")
#             print("   3. RECOGER → Recoge el objeto cuando está cerca")
#             print("   4. BUSCAR_DESTINO → Busca dónde dejar el objeto")
#             print("   5. IR_A_DESTINO → Va hacia el destino")
#             print("   6. DEJAR_OBJETO → Suelta el objeto en el destino")
#             print("\n⏳ Esperando conexiones...")
            
#             while self.running:
#                 try:
#                     client_socket, address = self.socket.accept()
#                     client_id = f"{address[0]}:{address[1]}"
#                     self.clientes[client_id] = client_socket
                    
#                     print(f"\n✅ Robot conectado: {client_id}")
                    
#                     # Crear hilo para manejar este robot
#                     client_thread = threading.Thread(
#                         target=self.manejar_robot, 
#                         args=(client_socket, client_id)
#                     )
#                     client_thread.daemon = True
#                     client_thread.start()
                    
#                 except Exception as e:
#                     if self.running:
#                         print(f"❌ Error aceptando conexión: {e}")
                        
#         except Exception as e:
#             print(f"❌ Error iniciando servidor: {e}")
    
#     def recibir_datos_camara(self, client_socket):
#         """Recibe datos de la cámara del robot"""
#         try:
#             data = client_socket.recv(1024).decode('utf-8').strip()
            
#             if not data:
#                 return None
                
#             try:
#                 datos_camara = json.loads(data)
#                 return datos_camara
#             except json.JSONDecodeError:
#                 # Si no es JSON, intentar parsear como texto simple
#                 return {"objeto": data.lower(), "tamaño": 0}
                
#         except Exception as e:
#             print(f"❌ Error recibiendo datos de cámara: {e}")
#             return None
    
#     def inicializar_estado_robot(self, robot_id):
#         """Inicializa el estado de un nuevo robot"""
#         self.estados_robot[robot_id] = {
#             "estado_actual": "buscar_objeto",
#             "objeto_detectado": None,
#             "tamaño_objeto": 0,
#             "tiene_objeto": False,
#             "destino_detectado": None,
#             "intentos_busqueda": 0,
#             "direccion_giro": "derecha",
#             "ultimo_comando": None,
#             "contador_movimientos": 0
#         }
#         print(f"🔄 [{robot_id}] Estado inicial: BUSCAR_OBJETO")
    
#     def procesar_estado_buscar_objeto(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de búsqueda de objetos"""
#         objeto = datos_camara.get("objeto", "").lower()
#         tamaño = datos_camara.get("tamaño", 0)
        
#         # Verificar si detectó un objeto válido
#         if objeto in self.objetos_validos and tamaño > 10:
#             estado_robot["objeto_detectado"] = objeto
#             estado_robot["tamaño_objeto"] = tamaño
#             estado_robot["estado_actual"] = "ir_al_objeto"
#             estado_robot["intentos_busqueda"] = 0
            
#             print(f"🎯 [{robot_id}] ¡Objeto detectado! {objeto.upper()} (tamaño: {tamaño})")
#             print(f"🔄 [{robot_id}] Cambiando a estado: IR_AL_OBJETO")
            
#             if tamaño < self.tamaño_minimo:
#                 return "AVANZAR"
#             else:
#                 return "AVANZAR_LENTO"
#         else:
#             # No hay objeto, seguir buscando
#             estado_robot["intentos_busqueda"] += 1
            
#             if estado_robot["intentos_busqueda"] < 3:
#                 print(f"🔍 [{robot_id}] Buscando... avanzando ({estado_robot['intentos_busqueda']}/3)")
#                 return "AVANZAR"
#             elif estado_robot["intentos_busqueda"] < 8:
#                 direccion = "GIRAR_DERECHA" if estado_robot["direccion_giro"] == "derecha" else "GIRAR_IZQUIERDA"
#                 print(f"🔍 [{robot_id}] Buscando... girando {estado_robot['direccion_giro']}")
#                 return direccion
#             else:
#                 # Cambiar dirección de búsqueda
#                 estado_robot["direccion_giro"] = "izquierda" if estado_robot["direccion_giro"] == "derecha" else "derecha"
#                 estado_robot["intentos_busqueda"] = 0
#                 print(f"🔄 [{robot_id}] Cambiando dirección de búsqueda")
#                 return "GIRAR_DERECHA" if estado_robot["direccion_giro"] == "derecha" else "GIRAR_IZQUIERDA"
    
#     def procesar_estado_ir_al_objeto(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de acercarse al objeto"""
#         objeto = datos_camara.get("objeto", "").lower()
#         tamaño = datos_camara.get("tamaño", 0)
        
#         if objeto not in self.objetos_validos:
#             # Perdió el objeto, volver a buscar
#             print(f"⚠️ [{robot_id}] Objeto perdido, volviendo a buscar")
#             estado_robot["estado_actual"] = "buscar_objeto"
#             estado_robot["objeto_detectado"] = None
#             return "PARAR"
        
#         estado_robot["tamaño_objeto"] = tamaño
        
#         if tamaño >= self.tamaño_maximo:
#             # Está suficientemente cerca para recoger
#             estado_robot["estado_actual"] = "recoger"
#             print(f"✋ [{robot_id}] Suficientemente cerca (tamaño: {tamaño})")
#             print(f"🔄 [{robot_id}] Cambiando a estado: RECOGER")
#             return "PARAR"
#         elif tamaño < self.tamaño_minimo:
#             # Muy lejos, avanzar normal
#             print(f"⬆️ [{robot_id}] Muy lejos, avanzando (tamaño: {tamaño})")
#             return "AVANZAR"
#         else:
#             # Cerca pero no suficiente, avanzar lento
#             print(f"🐌 [{robot_id}] Acercándose lentamente (tamaño: {tamaño})")
#             return "AVANZAR_LENTO"
    
#     def procesar_estado_recoger(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de recoger objeto"""
#         print(f"🤏 [{robot_id}] Recogiendo objeto...")
#         estado_robot["tiene_objeto"] = True
#         estado_robot["estado_actual"] = "buscar_destino"
#         estado_robot["intentos_busqueda"] = 0
#         print(f"✅ [{robot_id}] Objeto recogido exitosamente")
#         print(f"🔄 [{robot_id}] Cambiando a estado: BUSCAR_DESTINO")
#         return "RECOGER"
    
#     def procesar_estado_buscar_destino(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de búsqueda de destino"""
#         objeto = datos_camara.get("objeto", "").lower()
#         tamaño = datos_camara.get("tamaño", 0)
        
#         # Verificar si detectó un destino válido
#         if objeto in self.destinos_validos and tamaño > 20:
#             estado_robot["destino_detectado"] = objeto
#             estado_robot["estado_actual"] = "ir_a_destino"
#             estado_robot["intentos_busqueda"] = 0
            
#             print(f"🎯 [{robot_id}] ¡Destino detectado! {objeto.upper()}")
#             print(f"🔄 [{robot_id}] Cambiando a estado: IR_A_DESTINO")
#             return "AVANZAR"
#         else:
#             # No hay destino, seguir buscando (giro 360°)
#             estado_robot["intentos_busqueda"] += 1
            
#             if estado_robot["intentos_busqueda"] <= 12:  # 12 giros = ~360°
#                 print(f"🔍 [{robot_id}] Buscando destino... giro {estado_robot['intentos_busqueda']}/12")
#                 return "GIRAR_DERECHA"
#             else:
#                 # Completó 360°, buscar moviéndose
#                 if estado_robot["intentos_busqueda"] < 20:
#                     print(f"🔍 [{robot_id}] Destino no encontrado, explorando...")
#                     return "AVANZAR"
#                 else:
#                     # Reiniciar búsqueda
#                     estado_robot["intentos_busqueda"] = 0
#                     return "GIRAR_DERECHA"
    
#     def procesar_estado_ir_a_destino(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de ir al destino"""
#         objeto = datos_camara.get("objeto", "").lower()
#         tamaño = datos_camara.get("tamaño", 0)
        
#         if objeto not in self.destinos_validos:
#             # Perdió el destino, volver a buscar
#             print(f"⚠️ [{robot_id}] Destino perdido, volviendo a buscar")
#             estado_robot["estado_actual"] = "buscar_destino"
#             estado_robot["destino_detectado"] = None
#             return "PARAR"
        
#         if tamaño >= self.tamaño_maximo:
#             # Llegó al destino
#             estado_robot["estado_actual"] = "dejar_objeto"
#             print(f"🎯 [{robot_id}] Llegó al destino")
#             print(f"🔄 [{robot_id}] Cambiando a estado: DEJAR_OBJETO")
#             return "PARAR"
#         else:
#             # Seguir acercándose
#             print(f"➡️ [{robot_id}] Yendo al destino (tamaño: {tamaño})")
#             return "AVANZAR" if tamaño < self.tamaño_minimo else "AVANZAR_LENTO"
    
#     def procesar_estado_dejar_objeto(self, datos_camara, estado_robot, robot_id):
#         """Procesa el estado de dejar objeto"""
#         print(f"📦 [{robot_id}] Dejando objeto en el destino...")
#         estado_robot["tiene_objeto"] = False
#         estado_robot["estado_actual"] = "buscar_objeto"
#         estado_robot["objeto_detectado"] = None
#         estado_robot["destino_detectado"] = None
#         estado_robot["intentos_busqueda"] = 0
#         print(f"✅ [{robot_id}] Objeto entregado exitosamente")
#         print(f"🔄 [{robot_id}] Cambiando a estado: BUSCAR_OBJETO")
#         print(f"🎉 [{robot_id}] ¡Ciclo completado! Buscando nuevo objeto...")
#         return "SOLTAR"
    
#     def procesar_datos_y_estado(self, datos_camara, robot_id):
#         """Procesa los datos de la cámara según el estado actual del robot"""
#         if robot_id not in self.estados_robot:
#             self.inicializar_estado_robot(robot_id)
        
#         estado_robot = self.estados_robot[robot_id]
#         estado_actual = estado_robot["estado_actual"]
        
#         print(f"🔍 [{robot_id}] Estado: {estado_actual.upper()}")
#         if datos_camara.get("objeto"):
#             print(f"👁️ [{robot_id}] Ve: {datos_camara['objeto'].upper()} (tamaño: {datos_camara.get('tamaño', 0)})")
        
#         # Procesar según el estado actual
#         if estado_actual == "buscar_objeto":
#             comando = self.procesar_estado_buscar_objeto(datos_camara, estado_robot, robot_id)
#         elif estado_actual == "ir_al_objeto":
#             comando = self.procesar_estado_ir_al_objeto(datos_camara, estado_robot, robot_id)
#         elif estado_actual == "recoger":
#             comando = self.procesar_estado_recoger(datos_camara, estado_robot, robot_id)
#         elif estado_actual == "buscar_destino":
#             comando = self.procesar_estado_buscar_destino(datos_camara, estado_robot, robot_id)
#         elif estado_actual == "ir_a_destino":
#             comando = self.procesar_estado_ir_a_destino(datos_camara, estado_robot, robot_id)
#         elif estado_actual == "dejar_objeto":
#             comando = self.procesar_estado_dejar_objeto(datos_camara, estado_robot, robot_id)
#         else:
#             comando = "PARAR"
        
#         estado_robot["ultimo_comando"] = comando
#         estado_robot["contador_movimientos"] += 1
        
#         return comando
    
#     def enviar_comando(self, client_socket, comando, robot_id):
#         """Envía comando al robot"""
#         try:
#             # Crear respuesta JSON
#             respuesta = {
#                 "comando": comando,
#                 "estado": self.estados_robot[robot_id]["estado_actual"],
#                 "tiene_objeto": self.estados_robot[robot_id]["tiene_objeto"],
#                 "timestamp": datetime.now().isoformat(),
#                 "status": "ok"
#             }
            
#             mensaje = json.dumps(respuesta, ensure_ascii=False).encode('utf-8')
#             client_socket.send(mensaje)
            
#             # Mostrar comando enviado con emoji
#             emojis_comandos = {
#                 "AVANZAR": "⬆️",
#                 "AVANZAR_LENTO": "🐌",
#                 "RETROCEDER": "⬇️",
#                 "GIRAR_IZQUIERDA": "⬅️",
#                 "GIRAR_DERECHA": "➡️",
#                 "PARAR": "⏹️",
#                 "RECOGER": "🤏",
#                 "SOLTAR": "📦"
#             }
            
#             emoji = emojis_comandos.get(comando, "❓")
#             print(f"📤 [{robot_id}] Comando: {emoji} {comando}")
#             return True
            
#         except Exception as e:
#             print(f"❌ Error enviando comando a {robot_id}: {e}")
#             return False
    
#     def manejar_robot(self, client_socket, robot_id):
#         """Maneja la comunicación con un robot específico"""
#         print(f"🤖 [{robot_id}] Iniciando sesión de control")
#         self.inicializar_estado_robot(robot_id)
        
#         try:
#             while self.running:
#                 # Recibir datos de la cámara
#                 datos_camara = self.recibir_datos_camara(client_socket)
                
#                 if datos_camara is None:
#                     print(f"⚠️ [{robot_id}] Conexión perdida")
#                     break
                
#                 # Procesar datos y obtener comando
#                 comando = self.procesar_datos_y_estado(datos_camara, robot_id)
                
#                 # Enviar comando al robot
#                 if not self.enviar_comando(client_socket, comando, robot_id):
#                     break
                
#                 # Mostrar estado actual
#                 estado = self.estados_robot[robot_id]
#                 print(f"📊 [{robot_id}] Estado: {estado['estado_actual'].upper()} | "
#                       f"Objeto: {'✅' if estado['tiene_objeto'] else '❌'} | "
#                       f"Movimientos: {estado['contador_movimientos']}")
                
#                 print("-" * 50)
                
#                 # Pequeña pausa
#                 time.sleep(0.1)
                
#         except Exception as e:
#             print(f"❌ [{robot_id}] Error en sesión: {e}")
#         finally:
#             # Limpiar al desconectar
#             if robot_id in self.clientes:
#                 del self.clientes[robot_id]
#             if robot_id in self.estados_robot:
#                 del self.estados_robot[robot_id]
                
#             client_socket.close()
#             print(f"🔌 [{robot_id}] Robot desconectado")
    
#     def detener_servidor(self):
#         """Detiene el servidor"""
#         print("\n🛑 Deteniendo servidor...")
#         self.running = False
        
#         # Cerrar todas las conexiones
#         for client_id, client_socket in self.clientes.items():
#             try:
#                 client_socket.close()
#             except:
#                 pass
        
#         if self.socket:
#             self.socket.close()
        
#         print("✅ Servidor detenido correctamente")

# # Ejecutar servidor
# if __name__ == "__main__":
#     print("🚀 Iniciando Servidor Robot Recolector...")
#     servidor = ServidorRobotRecolector()
    
#     try:
#         servidor.iniciar_servidor()
#     except KeyboardInterrupt:
#         print("\n\n⚠️ Interrupción detectada...")
#         servidor.detener_servidor()
#     except Exception as e:
#         print(f"\n❌ Error crítico: {e}")
#         servidor.detener_servidor()
















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
        elif comando_input.startswith("velocidad "):
            try:
                velocidad = int(comando_input.split(" ")[1])
                if 0 <= velocidad <= 255:
                    self.enviar_comando_a_robots(f"VELOCIDAD {velocidad}")
                else:
                    print("⚠️ Velocidad debe estar entre 0 y 255")
            except:
                print("⚠️ Formato incorrecto. Usar: velocidad 120")
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