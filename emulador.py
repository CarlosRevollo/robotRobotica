import socket
import json
import time
import random
import threading
from datetime import datetime

class ESP32RobotEmulator:
    def __init__(self, server_ip='192.168.100.92', server_port=8888, robot_name="ESP32-Emulador"):
        self.server_ip = server_ip
        self.server_port = server_port
        self.robot_name = robot_name
        self.socket = None
        self.connected = False
        self.running = False
        
        # Simulación de detecciones posibles
        self.possible_detections = [
            {"detection": "circulo", "confidence": 0.95},
            {"detection": "cuadrado", "confidence": 0.88},
            {"detection": "triangulo", "confidence": 0.92},
            {"detection": "rectangulo", "confidence": 0.85},
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "desconocido", "confidence": 0.45}
        ]
        
        # Modo de simulación
        self.simulation_modes = {
            1: "random",      # Detecciones aleatorias
            2: "sequence",    # Secuencia predefinida
            3: "interactive", # Control manual
            4: "scenario"     # Escenario específico
        }
        
        self.current_mode = 1
        self.sequence_index = 0
        
        # Secuencia predefinida para testing
        self.test_sequence = [
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "cuadrado", "confidence": 0.9},
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "circulo", "confidence": 0.95},
            {"detection": "circulo", "confidence": 0.98},
            {"detection": "triangulo", "confidence": 0.88}
        ]
    
    def connect_to_server(self):
        """Conecta al servidor de visión robótica"""
        try:
            print("🔌 Intentando conectar al servidor...")
            print(f"📡 Servidor: {self.server_ip}:{self.server_port}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # Timeout de 10 segundos
            self.socket.connect((self.server_ip, self.server_port))
            
            self.connected = True
            print(f"✅ Conectado exitosamente como {self.robot_name}")
            print(f"🕐 Hora de conexión: {datetime.now().strftime('%H:%M:%S')}")
            return True
            
        except socket.timeout:
            print("⏰ Timeout: No se pudo conectar al servidor")
            return False
        except ConnectionRefusedError:
            print("❌ Conexión rechazada: El servidor no está disponible")
            return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def send_detection(self, detection_data):
        """Envía datos de detección al servidor"""
        try:
            if not self.connected:
                return False
                
            # Agregar información adicional
            detection_data["robot_id"] = self.robot_name
            detection_data["timestamp"] = datetime.now().isoformat()
            
            message = json.dumps(detection_data)
            self.socket.send(message.encode('utf-8'))
            
            # Mostrar lo que se envió
            detection = detection_data["detection"]
            confidence = detection_data["confidence"]
            
            print(f"📤 Enviado: {detection.upper()} (confianza: {confidence:.2f})")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando detección: {e}")
            self.connected = False
            return False
    
    def receive_command(self):
        """Recibe comandos del servidor"""
        try:
            if not self.connected:
                return None
                
            self.socket.settimeout(5)  # Timeout para recepción
            data = self.socket.recv(1024).decode('utf-8')
            
            if not data:
                return None
                
            try:
                command_data = json.loads(data)
                return command_data
            except json.JSONDecodeError:
                # Si no es JSON, asumir texto simple
                return {"command": data.strip()}
                
        except socket.timeout:
            print("⏰ Timeout esperando respuesta del servidor")
            return None
        except Exception as e:
            print(f"❌ Error recibiendo comando: {e}")
            self.connected = False
            return None
    
    def process_command(self, command_data):
        """Procesa el comando recibido del servidor"""
        if not command_data:
            return
            
        command = command_data.get("command", "UNKNOWN")
        
        # Emojis para los comandos
        command_emojis = {
            "FORWARD": "⬆️ ADELANTE",
            "BACKWARD": "⬇️ ATRÁS", 
            "LEFT": "⬅️ IZQUIERDA",
            "RIGHT": "➡️ DERECHA",
            "STOP": "⏹️ PARAR"
        }
        
        emoji_command = command_emojis.get(command, f"❓ {command}")
        print(f"📥 Comando recibido: {emoji_command}")
        
        # Simular tiempo de ejecución del comando
        execution_time = random.uniform(0.5, 1.5)
        print(f"⚙️ Ejecutando comando... ({execution_time:.1f}s)")
        time.sleep(execution_time)
        print("✅ Comando ejecutado")
    
    # def get_next_detection(self):
    #     """Obtiene la siguiente detección según el modo actual"""
    #     if self.current_mode == 1:  # Random
    #         return random.choice(self.possible_detections).copy()
            
    #     elif self.current_mode == 2:  # Sequence
    #         detection = self.test_sequence[self.sequence_index].copy()
    #         self.sequence_index = (self.sequence_index + 1) % len(self.test_sequence)
    #         return detection
            
    #     elif self.current_mode == 3:  # Interactive
    #         return self.get_interactive_detection()
            
    #     elif self.current_mode == 4:  # Scenario
    #         return self.get_scenario_detection()
            
    #     else:
    #         return {"detection": "vacio", "confidence": 1.0}


    def get_next_detection(self):

        if self.current_mode == 1:
            detection = random.choice(self.possible_detections).copy()
        elif self.current_mode == 2:
            detection = self.test_sequence[self.sequence_index].copy()
            self.sequence_index = (self.sequence_index + 1) % len(self.test_sequence)
        elif self.current_mode == 3:
            detection = self.get_interactive_detection()
        elif self.current_mode == 4:
            detection = self.get_scenario_detection()
        else:
            detection = {"detection": "vacio", "confidence": 1.0}

        # ✅ Simula una distancia entre 5 cm y 100 cm
        detection["distance"] = random.randint(5, 100)
        return detection


    
    def get_interactive_detection(self):
        """Permite al usuario elegir la detección manualmente"""
        print("\n" + "="*40)
        print("🎮 MODO INTERACTIVO")
        print("Elige qué detectar:")
        print("1. Círculo (objetivo)")
        print("2. Cuadrado (obstáculo)")
        print("3. Triángulo (marcador)")
        print("4. Rectángulo (obstáculo)")
        print("5. Vacío (nada)")
        print("6. Desconocido")
        print("0. Volver a modo automático")
        
        try:
            choice = input("Tu elección (1-6, 0 para auto): ").strip()
            
            if choice == "0":
                self.current_mode = 1
                return self.get_next_detection()
            elif choice == "1":
                return {"detection": "circulo", "confidence": 0.95}
            elif choice == "2":
                return {"detection": "cuadrado", "confidence": 0.90}
            elif choice == "3":
                return {"detection": "triangulo", "confidence": 0.88}
            elif choice == "4":
                return {"detection": "rectangulo", "confidence": 0.85}
            elif choice == "5":
                return {"detection": "vacio", "confidence": 1.0}
            elif choice == "6":
                return {"detection": "desconocido", "confidence": 0.50}
            else:
                return {"detection": "vacio", "confidence": 1.0}
                
        except KeyboardInterrupt:
            return None
        except:
            return {"detection": "vacio", "confidence": 1.0}
    
    def get_scenario_detection(self):
        """Simula un escenario específico de navegación"""
        # Implementar diferentes escenarios aquí
        scenarios = [
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "cuadrado", "confidence": 0.9},
            {"detection": "vacio", "confidence": 1.0},
            {"detection": "circulo", "confidence": 0.95}
        ]
        
        detection = scenarios[self.sequence_index % len(scenarios)].copy()
        self.sequence_index += 1
        return detection
    
    def show_menu(self):
        """Muestra el menú de opciones"""
        print("\n" + "="*50)
        print("🤖 EMULADOR ESP32 - MENÚ DE CONTROL")
        print("="*50)
        print("1. Modo Aleatorio (automático)")
        print("2. Modo Secuencia (predefinida)")
        print("3. Modo Interactivo (manual)")
        print("4. Modo Escenario (navegación)")
        print("5. Cambiar velocidad de simulación")
        print("6. Mostrar estadísticas")
        print("0. Salir")
        print("="*50)
    
    def run_emulation(self):
        """Ejecuta la emulación principal"""
        if not self.connect_to_server():
            return
            
        self.running = True
        detection_count = 0
        start_time = time.time()
        
        # Velocidad de simulación (segundos entre detecciones)
        simulation_speed = 2.0
        
        print(f"\n🚀 Iniciando emulación en modo: {self.simulation_modes[self.current_mode].upper()}")
        print("💡 Presiona Ctrl+C para acceder al menú")
        
        try:
            while self.running and self.connected:
                # Obtener siguiente detección
                detection_data = self.get_next_detection()
                
                if detection_data is None:  # Usuario canceló
                    break
                
                # Enviar detección
                if self.send_detection(detection_data):
                    detection_count += 1
                    
                    # Recibir y procesar comando
                    command_data = self.receive_command()
                    if command_data:
                        self.process_command(command_data)
                    else:
                        print("⚠️ No se recibió comando del servidor")
                        break
                else:
                    print("❌ Error enviando detección, reintentando...")
                    time.sleep(1)
                    continue
                
                # Pausa entre detecciones
                if self.current_mode != 3:  # No pausar en modo interactivo
                    time.sleep(simulation_speed)
                
                print("-" * 30)
                
        except KeyboardInterrupt:
            self.handle_menu(detection_count, start_time, simulation_speed)
        except Exception as e:
            print(f"❌ Error durante emulación: {e}")
        finally:
            self.disconnect()
    
    def handle_menu(self, detection_count, start_time, simulation_speed):
        """Maneja el menú interactivo"""
        while True:
            try:
                self.show_menu()
                choice = input("\nElige una opción: ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    self.current_mode = 1
                    print("✅ Modo aleatorio activado")
                    return self.continue_emulation(simulation_speed)
                elif choice == "2":
                    self.current_mode = 2
                    self.sequence_index = 0
                    print("✅ Modo secuencia activado")
                    return self.continue_emulation(simulation_speed)
                elif choice == "3":
                    self.current_mode = 3
                    print("✅ Modo interactivo activado")
                    return self.continue_emulation(simulation_speed)
                elif choice == "4":
                    self.current_mode = 4
                    self.sequence_index = 0
                    print("✅ Modo escenario activado")
                    return self.continue_emulation(simulation_speed)
                elif choice == "5":
                    simulation_speed = self.change_speed(simulation_speed)
                elif choice == "6":
                    self.show_stats(detection_count, start_time)
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                break
        
        self.running = False
    
    def continue_emulation(self, simulation_speed):
        """Continúa la emulación después del menú"""
        print("🔄 Continuando emulación...")
        print("💡 Presiona Ctrl+C para volver al menú")
        return self.run_emulation()
    
    def change_speed(self, current_speed):
        """Cambia la velocidad de simulación"""
        print(f"\nVelocidad actual: {current_speed}s entre detecciones")
        try:
            new_speed = float(input("Nueva velocidad (segundos): "))
            if new_speed > 0:
                print(f"✅ Velocidad cambiada a {new_speed}s")
                return new_speed
            else:
                print("❌ La velocidad debe ser mayor a 0")
                return current_speed
        except:
            print("❌ Valor no válido")
            return current_speed
    
    def show_stats(self, detection_count, start_time):
        """Muestra estadísticas de la emulación"""
        elapsed_time = time.time() - start_time
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"⏱️ Tiempo transcurrido: {elapsed_time:.1f}s")
        print(f"📤 Detecciones enviadas: {detection_count}")
        if elapsed_time > 0:
            print(f"📈 Promedio: {detection_count/elapsed_time:.2f} detecciones/s")
        print(f"🎮 Modo actual: {self.simulation_modes[self.current_mode].upper()}")
        input("\nPresiona Enter para continuar...")
    
    def disconnect(self):
        """Desconecta del servidor"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
                print("🔌 Desconectado del servidor")
            except:
                pass

# Función principal
def main():
    print("🤖 EMULADOR ESP32 - CLIENTE ROBOT")
    print("=" * 40)
    
    # Configuración
    server_ip = "192.168.100.92"  # IP 
    server_port = 8888
    robot_name = f"ESP32-Emulador-{random.randint(1000,9999)}"
    
    print(f"🎯 Servidor objetivo: {server_ip}:{server_port}")
    print(f"🤖 Nombre del robot: {robot_name}")
    
    # Crear y ejecutar emulador
    emulator = ESP32RobotEmulator(server_ip, server_port, robot_name)
    
    try:
        emulator.run_emulation()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        emulator.disconnect()
        print("👋 Emulación terminada")

if __name__ == "__main__":
    main()