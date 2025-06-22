import socket
import json
import time
from datetime import datetime
import random

class EscenarioCompleto:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.robot_id = "ROBOT_SIM_001"
        self.estado_actual = "buscar_objeto"
        self.tiene_objeto = False
        self.contador_movimientos = 0
        
        # Configuración de simulación
        self.objetos_validos = ["pelota", "cuadrado", "triangulo", "caja"]
        self.destinos_validos = ["contenedor", "deposito", "canasta"]
        
        # Secuencia de prueba más realista con variabilidad
        self.escenarios = {
            "exito_normal": self.crear_escenario_exito(),
            "objeto_perdido": self.crear_escenario_fallo(),
            "multiple_objetos": self.crear_escenario_multiple()
        }
    
    def conectar_servidor(self):
        """Establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ [{self.robot_id}] Conectado al servidor en {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ [{self.robot_id}] Error de conexión: {e}")
            return False
    
    def enviar_datos(self, datos):
        """Envía datos al servidor y recibe respuesta"""
        try:
            # Añadir metadatos a los datos enviados
            datos_completos = {
                **datos,
                "robot_id": self.robot_id,
                "timestamp": datetime.now().isoformat(),
                "bateria": random.randint(20, 100)
            }
            
            mensaje = json.dumps(datos_completos).encode('utf-8')
            self.socket.send(mensaje)
            
            # Esperar y procesar respuesta
            respuesta = self.socket.recv(1024).decode('utf-8')
            
            try:
                respuesta_json = json.loads(respuesta)
                self.procesar_respuesta(respuesta_json)
                return respuesta_json
            except json.JSONDecodeError:
                print(f"📥 [{self.robot_id}] Respuesta no JSON: {respuesta}")
                return None
                
        except Exception as e:
            print(f"❌ [{self.robot_id}] Error en comunicación: {e}")
            return None
    
    def procesar_respuesta(self, respuesta):
        """Procesa la respuesta del servidor y actualiza estado interno"""
        if not respuesta:
            return
            
        print("\n" + "="*50)
        print(f"📥 RESPUESTA DEL SERVIDOR [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"🔄 Estado actual: {respuesta.get('estado', 'desconocido').upper()}")
        print(f"📌 Comando recibido: {respuesta.get('comando', 'NINGUNO')}")
        print(f"📦 Tiene objeto: {'✅' if respuesta.get('tiene_objeto', False) else '❌'}")
        print(f"⏱️ Timestamp: {respuesta.get('timestamp', '')}")
        print("="*50 + "\n")
        
        # Actualizar estado interno del robot simulado
        self.estado_actual = respuesta.get('estado', self.estado_actual)
        self.tiene_objeto = respuesta.get('tiene_objeto', self.tiene_objeto)
        self.contador_movimientos += 1
    
    def crear_escenario_exito(self):
        """Crea un escenario de éxito normal"""
        return [
            # Fase 1: Búsqueda inicial
            {"objeto": "nada", "tamaño": 0, "delay": 1.2},
            {"objeto": "nada", "tamaño": 0, "delay": 1.2},
            {"objeto": "pelota", "tamaño": 30, "delay": 0.8},
            
            # Fase 2: Acercamiento
            {"objeto": "pelota", "tamaño": 60, "delay": 0.6},
            {"objeto": "pelota", "tamaño": 90, "delay": 0.6},
            {"objeto": "pelota", "tamaño": 140, "delay": 0.5},
            {"objeto": "pelota", "tamaño": 190, "delay": 0.5},
            {"objeto": "pelota", "tamaño": 220, "delay": 0.5},
            
            # Fase 3: Recoger
            {"objeto": "pelota", "tamaño": 250, "delay": 1.5},
            
            # Fase 4: Buscar destino
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "contenedor", "tamaño": 40, "delay": 0.7},
            
            # Fase 5: Acercamiento a destino
            {"objeto": "contenedor", "tamaño": 80, "delay": 0.6},
            {"objeto": "contenedor", "tamaño": 130, "delay": 0.5},
            {"objeto": "contenedor", "tamaño": 180, "delay": 0.5},
            {"objeto": "contenedor", "tamaño": 230, "delay": 0.5},
            
            # Fase 6: Dejar objeto
            {"objeto": "contenedor", "tamaño": 250, "delay": 2.0}
        ]
    
    def crear_escenario_fallo(self):
        """Crea un escenario con pérdida de objeto"""
        return [
            # Búsqueda inicial
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "cuadrado", "tamaño": 40, "delay": 0.8},
            
            # Acercamiento
            {"objeto": "cuadrado", "tamaño": 70, "delay": 0.7},
            {"objeto": "cuadrado", "tamaño": 120, "delay": 0.6},
            
            # Pérdida del objeto
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            
            # Re-búsqueda
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "cuadrado", "tamaño": 30, "delay": 0.8},
            
            # Continuación normal
            {"objeto": "cuadrado", "tamaño": 80, "delay": 0.7},
            {"objeto": "cuadrado", "tamaño": 160, "delay": 0.6},
            {"objeto": "cuadrado", "tamaño": 220, "delay": 0.5},
            
            # Recoger
            {"objeto": "cuadrado", "tamaño": 250, "delay": 1.5},
            
            # Buscar destino
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "deposito", "tamaño": 50, "delay": 0.8},
            
            # Acercamiento a destino
            {"objeto": "deposito", "tamaño": 100, "delay": 0.7},
            {"objeto": "deposito", "tamaño": 170, "delay": 0.6},
            {"objeto": "deposito", "tamaño": 240, "delay": 0.5},
            
            # Dejar objeto
            {"objeto": "deposito", "tamaño": 250, "delay": 2.0}
        ]
    
    def crear_escenario_multiple(self):
        """Crea un escenario con múltiples objetos"""
        return [
            # Primer objeto
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "pelota", "tamaño": 40, "delay": 0.8},
            {"objeto": "pelota", "tamaño": 90, "delay": 0.7},
            {"objeto": "pelota", "tamaño": 160, "delay": 0.6},
            {"objeto": "pelota", "tamaño": 220, "delay": 0.5},
            {"objeto": "pelota", "tamaño": 250, "delay": 1.5},
            
            # Buscar destino
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "contenedor", "tamaño": 60, "delay": 0.8},
            {"objeto": "contenedor", "tamaño": 120, "delay": 0.7},
            {"objeto": "contenedor", "tamaño": 190, "delay": 0.6},
            {"objeto": "contenedor", "tamaño": 250, "delay": 0.5},
            {"objeto": "contenedor", "tamaño": 250, "delay": 2.0},
            
            # Segundo objeto
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "triangulo", "tamaño": 30, "delay": 0.8},
            {"objeto": "triangulo", "tamaño": 80, "delay": 0.7},
            {"objeto": "triangulo", "tamaño": 150, "delay": 0.6},
            {"objeto": "triangulo", "tamaño": 210, "delay": 0.5},
            {"objeto": "triangulo", "tamaño": 250, "delay": 1.5},
            
            # Buscar destino
            {"objeto": "nada", "tamaño": 0, "delay": 1.0},
            {"objeto": "canasta", "tamaño": 50, "delay": 0.8},
            {"objeto": "canasta", "tamaño": 110, "delay": 0.7},
            {"objeto": "canasta", "tamaño": 180, "delay": 0.6},
            {"objeto": "canasta", "tamaño": 240, "delay": 0.5},
            {"objeto": "canasta", "tamaño": 250, "delay": 2.0}
        ]
    
    def ejecutar_escenario(self, nombre_escenario="exito_normal"):
        """Ejecuta el escenario seleccionado"""
        if not self.conectar_servidor():
            return
            
        escenario = self.escenarios.get(nombre_escenario, self.escenarios["exito_normal"])
        
        print(f"\n🚀 Iniciando escenario: {nombre_escenario.upper()}")
        print(f"📌 Total pasos: {len(escenario)}")
        print("="*60 + "\n")
        
        for i, paso in enumerate(escenario, 1):
            print(f"\n🔹 PASO {i}/{len(escenario)} - Estado actual: {self.estado_actual.upper()}")
            print(f"📤 Enviando datos:")
            print(f"   Objeto: {paso['objeto']}")
            print(f"   Tamaño: {paso['tamaño']}")
            print(f"   Delay: {paso['delay']}s")
            
            datos = {
                "objeto": paso["objeto"],
                "tamaño": paso["tamaño"],
                "estado": self.estado_actual,
                "tiene_objeto": self.tiene_objeto,
                "movimientos": self.contador_movimientos
            }
            
            respuesta = self.enviar_datos(datos)
            
            if not respuesta:
                print("⚠️ No se recibió respuesta válida, terminando escenario")
                break
                
            time.sleep(paso["delay"])
        
        print("\n🎉 Escenario completado!")
        self.socket.close()

if __name__ == "__main__":
    simulador = EscenarioCompleto()
    
    print("🤖 SIMULADOR DE ROBOT RECOLECTOR")
    print("1. Escenario éxito normal")
    print("2. Escenario con pérdida de objeto")
    print("3. Escenario múltiples objetos")
    
    opcion = input("Seleccione escenario (1-3): ").strip()
    
    if opcion == "1":
        simulador.ejecutar_escenario("exito_normal")
    elif opcion == "2":
        simulador.ejecutar_escenario("objeto_perdido")
    elif opcion == "3":
        simulador.ejecutar_escenario("multiple_objetos")
    else:
        print("Opción no válida, ejecutando escenario por defecto")
        simulador.ejecutar_escenario("exito_normal")