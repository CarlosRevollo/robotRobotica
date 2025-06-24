import socket
import threading
import json
import time
from datetime import datetime

class ServidorRobotRecolector:
    def __init__(self, host='0.0.0.0', port=1234):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clientes = {}
        
        # Estados del robot
        self.estados_robot = {}
        
        # Configuración de tamaños
        self.tamaño_minimo = 5000  # Píxeles mínimos para considerar "suficientemente grande"
        self.tamaño_maximo = 30000  # Píxeles máximos para estar "muy cerca"
        
        # Configuración de velocidades por estado
        self.velocidades = {
            "buscar_objeto": {"derecha": 120, "izquierda": 120},      # Velocidad normal para búsqueda
            "ir_al_objeto": {"derecha": 100, "izquierda": 100},       # Velocidad media para acercarse
            "ir_al_objeto_lento": {"derecha": 80, "izquierda": 80},   # Velocidad lenta para precisión
            "buscar_destino": {"derecha": 110, "izquierda": 110},     # Velocidad para buscar destino
            "ir_a_destino": {"derecha": 100, "izquierda": 100},       # Velocidad para ir a destino
            "ir_a_destino_lento": {"derecha": 70, "izquierda": 70},   # Velocidad lenta para llegar al destino
            "exploracion": {"derecha": 90, "izquierda": 90}           # Velocidad para exploración
        }
        
        # Objetos reconocidos
        self.objetos_validos = [
            "cuadrado",
            "cilindro"
        ]
        
        # Destinos reconocidos (donde dejar objetos cuadrado)
        self.destinos_validos_cuadrado = [
            "contenedor_cuadrado", 
        ]
        # Destinos reconocidos (donde dejar objetos cilindro)
        self.destinos_validos_cilindro = [
            "contenedor_cilindro",  # Corregido el typo
        ]
        
    def iniciar_servidor(self):
        """Inicia el servidor TCP"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print("=" * 60)
            print("🤖 SERVIDOR ROBOT RECOLECTOR INICIADO")
            print("=" * 60)
            print(f"📡 Escuchando en: {self.host}:{self.port}")
            print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📏 Tamaño mínimo objeto: {self.tamaño_minimo} píxeles")
            print(f"📏 Tamaño máximo (muy cerca): {self.tamaño_maximo} píxeles")
            
            print("\n⚡ Configuración de velocidades por estado:")
            for estado, vel in self.velocidades.items():
                print(f"   {estado}: D={vel['derecha']}, I={vel['izquierda']}")
            
            print("\n🔄 Estados del robot:")
            print("   1. BUSCAR_OBJETO → Busca objetos para recolectar")
            print("   2. IR_AL_OBJETO → Se acerca al objeto detectado")
            print("   3. RECOGER → Recoge el objeto cuando está cerca")
            print("   4. BUSCAR_DESTINO → Busca dónde dejar el objeto")
            print("   5. IR_A_DESTINO → Va hacia el destino")
            print("   6. DEJAR_OBJETO → Suelta el objeto en el destino")
            print("\n⏳ Esperando conexiones...")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    client_id = f"{address[0]}:{address[1]}"
                    self.clientes[client_id] = client_socket
                    
                    print(f"\n✅ Robot conectado: {client_id}")
                    
                    # Crear hilo para manejar este robot
                    client_thread = threading.Thread(
                        target=self.manejar_robot, 
                        args=(client_socket, client_id)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Error aceptando conexión: {e}")
                        
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
    
    def recibir_datos_camara(self, client_socket):
        """Recibe datos de la cámara del robot"""
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            
            if not data:
                return None
                
            try:
                datos_camara = json.loads(data)
                return datos_camara
            except json.JSONDecodeError:
                # Si no es JSON, intentar parsear como texto simple
                return {"objeto": data.lower(), "tamaño": 0}
                
        except Exception as e:
            print(f"❌ Error recibiendo datos de cámara: {e}")
            return None
    
    def configurar_velocidad(self, client_socket, estado, robot_id):
        """Configura la velocidad del robot según el estado"""
        if estado in self.velocidades:
            vel = self.velocidades[estado]
            
            # Enviar comandos de velocidad
            comando_der = f"VELOCIDADD {vel['derecha']}"
            comando_izq = f"VELOCIDADI {vel['izquierda']}"
            
            try:
                client_socket.send((comando_der + '\n').encode('utf-8'))
                time.sleep(0.05)  # Pequeña pausa entre comandos
                client_socket.send((comando_izq + '\n').encode('utf-8'))
                
                print(f"⚡ [{robot_id}] Velocidad configurada para {estado}: D={vel['derecha']}, I={vel['izquierda']}")
                
            except Exception as e:
                print(f"❌ Error configurando velocidad: {e}")
    
    def inicializar_estado_robot(self, robot_id):
        """Inicializa el estado de un nuevo robot"""
        self.estados_robot[robot_id] = {
            "estado_actual": "buscar_objeto",
            "objeto_detectado": None,
            "tamaño_objeto": 0,
            "tiene_objeto": False,
            "destino_detectado": None,
            "intentos_busqueda": 0,
            "direccion_giro": "derecha",
            "ultimo_comando": None,
            "contador_movimientos": 0,
            "velocidad_actual": None
        }
        print(f"🔄 [{robot_id}] Estado inicial: BUSCAR_OBJETO")
    
    def procesar_estado_buscar_objeto(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de búsqueda de objetos"""
        objeto = datos_camara.get("objeto", "").lower()
        tamaño = datos_camara.get("tamaño", 0)
        
        # Configurar velocidad para búsqueda
        if estado_robot["velocidad_actual"] != "buscar_objeto":
            self.configurar_velocidad(client_socket, "buscar_objeto", robot_id)
            estado_robot["velocidad_actual"] = "buscar_objeto"
        
        # Verificar si detectó un objeto válido
        if objeto in self.objetos_validos and tamaño > 10:
            estado_robot["objeto_detectado"] = objeto
            estado_robot["tamaño_objeto"] = tamaño
            estado_robot["estado_actual"] = "ir_al_objeto"
            estado_robot["intentos_busqueda"] = 0
            
            print(f"🎯 [{robot_id}] ¡Objeto detectado! {objeto.upper()} (tamaño: {tamaño})")
            print(f"🔄 [{robot_id}] Cambiando a estado: IR_AL_OBJETO")
            
            if tamaño < self.tamaño_minimo:
                return "AVANZAR"
            else:
                return "AVANZAR"
        else:
            # No hay objeto, seguir buscando
            estado_robot["intentos_busqueda"] += 1
            
            if estado_robot["intentos_busqueda"] < 3:
                print(f"🔍 [{robot_id}] Buscando... avanzando ({estado_robot['intentos_busqueda']}/3)")
                return "AVANZAR"
            elif estado_robot["intentos_busqueda"] < 8:
                direccion = "DERECHA" if estado_robot["direccion_giro"] == "derecha" else "IZQUIERDA"
                print(f"🔍 [{robot_id}] Buscando... girando {estado_robot['direccion_giro']}")
                return direccion
            else:
                # Cambiar dirección de búsqueda
                estado_robot["direccion_giro"] = "izquierda" if estado_robot["direccion_giro"] == "derecha" else "derecha"
                estado_robot["intentos_busqueda"] = 0
                print(f"🔄 [{robot_id}] Cambiando dirección de búsqueda")
                return "DERECHA" if estado_robot["direccion_giro"] == "derecha" else "IZQUIERDA"
    
    def procesar_estado_ir_al_objeto(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de acercarse al objeto"""
        objeto = datos_camara.get("objeto", "").lower()
        tamaño = datos_camara.get("tamaño", 0)
        
        if objeto not in self.objetos_validos:
            # Perdió el objeto, volver a buscar
            print(f"⚠️ [{robot_id}] Objeto perdido, volviendo a buscar")
            estado_robot["estado_actual"] = "buscar_objeto"
            estado_robot["objeto_detectado"] = None
            return "PARAR"
        
        estado_robot["tamaño_objeto"] = tamaño
        
        if tamaño >= self.tamaño_maximo:
            # Está suficientemente cerca para recoger
            estado_robot["estado_actual"] = "recoger"
            print(f"✋ [{robot_id}] Suficientemente cerca (tamaño: {tamaño})")
            print(f"🔄 [{robot_id}] Cambiando a estado: RECOGER")
            return "PARAR"
        elif tamaño < self.tamaño_minimo:
            # Muy lejos, avanzar normal
            if estado_robot["velocidad_actual"] != "ir_al_objeto":
                self.configurar_velocidad(client_socket, "ir_al_objeto", robot_id)
                estado_robot["velocidad_actual"] = "ir_al_objeto"
            print(f"⬆️ [{robot_id}] Muy lejos, avanzando (tamaño: {tamaño})")
            return "AVANZAR"
        else:
            # Cerca pero no suficiente, avanzar lento
            if estado_robot["velocidad_actual"] != "ir_al_objeto_lento":
                self.configurar_velocidad(client_socket, "ir_al_objeto_lento", robot_id)
                estado_robot["velocidad_actual"] = "ir_al_objeto_lento"
            print(f"🐌 [{robot_id}] Acercándose lentamente (tamaño: {tamaño})")
            return "AVANZAR"
    
    def procesar_estado_recoger(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de recoger objeto"""
        print(f"🤏 [{robot_id}] Recogiendo objeto...")
        estado_robot["tiene_objeto"] = True
        estado_robot["estado_actual"] = "buscar_destino"
        estado_robot["intentos_busqueda"] = 0
        print(f"✅ [{robot_id}] Objeto recogido exitosamente")
        print(f"🔄 [{robot_id}] Cambiando a estado: BUSCAR_DESTINO")
        return "AGARRAR"  # Usa el comando de secuencia completa
    
    def procesar_estado_buscar_destino(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de búsqueda de destino"""
        objeto = datos_camara.get("objeto", "").lower()
        tamaño = datos_camara.get("tamaño", 0)
        
        # Configurar velocidad para búsqueda de destino
        if estado_robot["velocidad_actual"] != "buscar_destino":
            self.configurar_velocidad(client_socket, "buscar_destino", robot_id)
            estado_robot["velocidad_actual"] = "buscar_destino"
        
        # Determinar destinos válidos según el objeto que tiene
        objeto_en_mano = estado_robot["objeto_detectado"]
        destinos_validos = []
        
        if objeto_en_mano == "cuadrado":
            destinos_validos = self.destinos_validos_cuadrado
        elif objeto_en_mano == "cilindro":
            destinos_validos = self.destinos_validos_cilindro
        
        # Verificar si detectó un destino válido
        if objeto in destinos_validos and tamaño > 20:
            estado_robot["destino_detectado"] = objeto
            estado_robot["estado_actual"] = "ir_a_destino"
            estado_robot["intentos_busqueda"] = 0
            
            print(f"🎯 [{robot_id}] ¡Destino detectado! {objeto.upper()} para {objeto_en_mano}")
            print(f"🔄 [{robot_id}] Cambiando a estado: IR_A_DESTINO")
            return "AVANZAR"
        else:
            # No hay destino, seguir buscando (giro 360°)
            estado_robot["intentos_busqueda"] += 1
            
            if estado_robot["intentos_busqueda"] <= 12:  # 12 giros = ~360°
                print(f"🔍 [{robot_id}] Buscando destino para {objeto_en_mano}... giro {estado_robot['intentos_busqueda']}/12")
                return "DERECHA"
            else:
                # Completó 360°, buscar moviéndose
                if estado_robot["intentos_busqueda"] < 20:
                    if estado_robot["velocidad_actual"] != "exploracion":
                        self.configurar_velocidad(client_socket, "exploracion", robot_id)
                        estado_robot["velocidad_actual"] = "exploracion"
                    print(f"🔍 [{robot_id}] Destino no encontrado, explorando...")
                    return "AVANZAR"
                else:
                    # Reiniciar búsqueda
                    estado_robot["intentos_busqueda"] = 0
                    return "DERECHA"
    
    def procesar_estado_ir_a_destino(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de ir al destino"""
        objeto = datos_camara.get("objeto", "").lower()
        tamaño = datos_camara.get("tamaño", 0)
        
        # Determinar destinos válidos según el objeto que tiene
        objeto_en_mano = estado_robot["objeto_detectado"]
        destinos_validos = []
        
        if objeto_en_mano == "cuadrado":
            destinos_validos = self.destinos_validos_cuadrado
        elif objeto_en_mano == "cilindro":
            destinos_validos = self.destinos_validos_cilindro
        
        if objeto not in destinos_validos:
            # Perdió el destino, volver a buscar
            print(f"⚠️ [{robot_id}] Destino perdido, volviendo a buscar")
            estado_robot["estado_actual"] = "buscar_destino"
            estado_robot["destino_detectado"] = None
            return "PARAR"
        
        if tamaño >= self.tamaño_maximo:
            # Llegó al destino
            estado_robot["estado_actual"] = "dejar_objeto"
            print(f"🎯 [{robot_id}] Llegó al destino")
            print(f"🔄 [{robot_id}] Cambiando a estado: DEJAR_OBJETO")
            return "PARAR"
        else:
            # Seguir acercándose
            if tamaño < self.tamaño_minimo:
                if estado_robot["velocidad_actual"] != "ir_a_destino":
                    self.configurar_velocidad(client_socket, "ir_a_destino", robot_id)
                    estado_robot["velocidad_actual"] = "ir_a_destino"
                print(f"➡️ [{robot_id}] Yendo al destino (tamaño: {tamaño})")
                return "AVANZAR"
            else:
                if estado_robot["velocidad_actual"] != "ir_a_destino_lento":
                    self.configurar_velocidad(client_socket, "ir_a_destino_lento", robot_id)
                    estado_robot["velocidad_actual"] = "ir_a_destino_lento"
                print(f"🐌 [{robot_id}] Acercándose lentamente al destino (tamaño: {tamaño})")
                return "AVANZAR"
    
    def procesar_estado_dejar_objeto(self, datos_camara, estado_robot, robot_id, client_socket):
        """Procesa el estado de dejar objeto"""
        print(f"📦 [{robot_id}] Dejando objeto en el destino...")
        estado_robot["tiene_objeto"] = False
        estado_robot["estado_actual"] = "buscar_objeto"
        estado_robot["objeto_detectado"] = None
        estado_robot["destino_detectado"] = None
        estado_robot["intentos_busqueda"] = 0
        estado_robot["velocidad_actual"] = None  # Reset velocidad
        print(f"✅ [{robot_id}] Objeto entregado exitosamente")
        print(f"🔄 [{robot_id}] Cambiando a estado: BUSCAR_OBJETO")
        print(f"🎉 [{robot_id}] ¡Ciclo completado! Buscando nuevo objeto...")
        return "SOLTAR"  # Usa el comando de secuencia completa
    
    def procesar_datos_y_estado(self, datos_camara, robot_id, client_socket):
        """Procesa los datos de la cámara según el estado actual del robot"""
        if robot_id not in self.estados_robot:
            self.inicializar_estado_robot(robot_id)
        
        estado_robot = self.estados_robot[robot_id]
        estado_actual = estado_robot["estado_actual"]
        
        print(f"🔍 [{robot_id}] Estado: {estado_actual.upper()}")
        if datos_camara.get("objeto"):
            print(f"👁️ [{robot_id}] Ve: {datos_camara['objeto'].upper()} (tamaño: {datos_camara.get('tamaño', 0)})")
        
        # Procesar según el estado actual
        if estado_actual == "buscar_objeto":
            comando = self.procesar_estado_buscar_objeto(datos_camara, estado_robot, robot_id, client_socket)
        elif estado_actual == "ir_al_objeto":
            comando = self.procesar_estado_ir_al_objeto(datos_camara, estado_robot, robot_id, client_socket)
        elif estado_actual == "recoger":
            comando = self.procesar_estado_recoger(datos_camara, estado_robot, robot_id, client_socket)
        elif estado_actual == "buscar_destino":
            comando = self.procesar_estado_buscar_destino(datos_camara, estado_robot, robot_id, client_socket)
        elif estado_actual == "ir_a_destino":
            comando = self.procesar_estado_ir_a_destino(datos_camara, estado_robot, robot_id, client_socket)
        elif estado_actual == "dejar_objeto":
            comando = self.procesar_estado_dejar_objeto(datos_camara, estado_robot, robot_id, client_socket)
        else:
            comando = "PARAR"
        
        estado_robot["ultimo_comando"] = comando
        estado_robot["contador_movimientos"] += 1
        
        return comando
    
    def enviar_comando(self, client_socket, comando, robot_id):
        """Envía comando al robot"""
        try:
            # Enviar comando simple como string
            mensaje = comando + '\n'
            client_socket.send(mensaje.encode('utf-8'))
            
            # Mostrar comando enviado con emoji
            emojis_comandos = {
                "AVANZAR": "⬆️",
                "RETROCEDER": "⬇️",
                "IZQUIERDA": "⬅️",
                "DERECHA": "➡️",
                "PARAR": "⏹️",
                "AGARRAR": "🤏",
                "SOLTAR": "📦"
            }
            
            emoji = emojis_comandos.get(comando, "❓")
            print(f"📤 [{robot_id}] Comando: {emoji} {comando}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando comando a {robot_id}: {e}")
            return False
    
    def manejar_robot(self, client_socket, robot_id):
        """Maneja la comunicación con un robot específico"""
        print(f"🤖 [{robot_id}] Iniciando sesión de control")
        self.inicializar_estado_robot(robot_id)
        
        try:
            while self.running:
                # Recibir datos de la cámara
                datos_camara = self.recibir_datos_camara(client_socket)
                
                if datos_camara is None:
                    print(f"⚠️ [{robot_id}] Conexión perdida")
                    break
                
                # Procesar datos y obtener comando
                comando = self.procesar_datos_y_estado(datos_camara, robot_id, client_socket)
                
                # Enviar comando al robot
                if not self.enviar_comando(client_socket, comando, robot_id):
                    break
                
                # Mostrar estado actual
                estado = self.estados_robot[robot_id]
                vel_actual = estado.get('velocidad_actual', 'No configurada')
                print(f"📊 [{robot_id}] Estado: {estado['estado_actual'].upper()} | "
                      f"Objeto: {'✅' if estado['tiene_objeto'] else '❌'} | "
                      f"Velocidad: {vel_actual} | "
                      f"Movimientos: {estado['contador_movimientos']}")
                
                print("-" * 60)
                
                # Pequeña pausa
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ [{robot_id}] Error en sesión: {e}")
        finally:
            # Limpiar al desconectar
            if robot_id in self.clientes:
                del self.clientes[robot_id]
            if robot_id in self.estados_robot:
                del self.estados_robot[robot_id]
                
            client_socket.close()
            print(f"🔌 [{robot_id}] Robot desconectado")
    
    def detener_servidor(self):
        """Detiene el servidor"""
        print("\n🛑 Deteniendo servidor...")
        self.running = False
        
        # Cerrar todas las conexiones
        for client_id, client_socket in self.clientes.items():
            try:
                client_socket.close()
            except:
                pass
        
        if self.socket:
            self.socket.close()
        
        print("✅ Servidor detenido correctamente")

# Ejecutar servidor
if __name__ == "__main__":
    print("🚀 Iniciando Servidor Robot Recolector...")
    servidor = ServidorRobotRecolector()
    
    try:
        servidor.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupción detectada...")
        servidor.detener_servidor()
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        servidor.detener_servidor()