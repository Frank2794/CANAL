class AnayansiIA:
    """Sistema IA completo para el Canal de Panamá con aprendizaje automático"""
    
    def __init__(self):
        self.nombre = "Anayansi"
        self.significado = "Sabiduria del mar"
        self.version = "3.0"
        self.confianza = 0.93
        self.aprendizaje = []
        self.logs = []
        self.patrones = {}
        self.historial_conversaciones = []
        self.conocimiento = self._inicializar_conocimiento()
        self.aprendizaje_automatico = True
        self.predicciones_previas = []
        
    def _inicializar_conocimiento(self):
        return {
            "esclusas": {
                "Gatun": {"capacidad": 3, "nivel_agua": 26.0, "tiempo_prom": 1.5, "estado": "Operativa"},
                "Pedro Miguel": {"capacidad": 1, "nivel_agua": 13.5, "tiempo_prom": 1.0, "estado": "Operativa"},
                "Miraflores": {"capacidad": 2, "nivel_agua": 16.5, "tiempo_prom": 1.2, "estado": "Operativa"}
            },
            "clima": {
                "viento_critico": 30,
                "ola_critica": 3.0,
                "temperatura_optima": (22, 28),
                "lluvia_critica": 50
            },
            "operaciones": {
                "max_barcos_espera": 15,
                "cwt_critico": 22,
                "tiempo_espera_max": 3
            }
        }
    
    def _registrar_log(self, accion, datos):
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "accion": accion,
            "datos": datos
        }
        self.logs.append(entrada)
        return entrada
    
    # ==========================================
    # MÉTODO AGREGADO - APRENDIZAJE AUTOMÁTICO
    # ==========================================
    
    def aprender_automaticamente(self, df, stats):
        """Aprendizaje automático basado en datos actuales"""
        nuevos_aprendizajes = []
        
        # Aprender patrones de tráfico
        if stats["total"] > 70:
            nuevo = f"Alto tráfico detectado: {stats['total']} barcos. Recomendar protocolos especiales."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        if stats["cwt"] > 20:
            nuevo = f"CWT crítico: {stats['cwt']:.1f}h. Recomendar acciones inmediatas."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        if stats["espera"] > 12:
            nuevo = f"Congestión en esclusas: {stats['espera']} barcos en espera."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        # Aprender patrones climáticos
        if stats.get("viento_prom", 0) > 20:
            nuevo = f"Vientos fuertes detectados: {stats['viento_prom']:.1f} nudos. Precaución."
            self.aprender(nuevo)
            nuevos_aprendizajes.append(nuevo)
        
        # Aprender sobre eficiencia de esclusas
        for nombre, datos in stats["esclusas"].items():
            if datos["espera"] > 5:
                nuevo = f"Esclusa {nombre} con {datos['espera']} barcos en espera. Considerar optimización."
                self.aprender(nuevo)
                nuevos_aprendizajes.append(nuevo)
        
        return nuevos_aprendizajes
    
    def aprender(self, nuevo_conocimiento):
        self.aprendizaje.append({
            "fecha": datetime.now().isoformat(),
            "conocimiento": nuevo_conocimiento
        })
        self._registrar_log("aprendizaje", nuevo_conocimiento)
        return "Anayansi ha aprendido: " + nuevo_conocimiento[:100] + "..."
    
    def analizar_barco(self, barco):
        analisis = {
            "nombre": barco["nombre"],
            "tipo": barco["tipo"],
            "direccion": barco["direccion"],
            "estado": barco["estado"],
            "velocidad": barco["velocidad"],
            "esclusa": barco["esclusa"],
            "eta": barco["eta_horas"],
            "prioridad": barco["prioridad"],
            "analisis": self._generar_analisis_barco(barco)
        }
        self._registrar_log("analisis_barco", analisis)
        return analisis
    
    def _generar_analisis_barco(self, barco):
        resultado = []
        if barco["velocidad"] < 2:
            resultado.append("Velocidad muy baja - Posible congestion o espera")
        elif barco["velocidad"] < 5:
            resultado.append("Velocidad reducida - Navegando con precaucion")
        elif barco["velocidad"] > 15:
            resultado.append("Alta velocidad - Buque prioritario o en ruta exprés")
        else:
            resultado.append("Velocidad normal - Navegacion fluida")
        
        if barco["estado"] == "En espera en esclusa":
            resultado.append("En espera - Tiempo estimado de espera: 1-3 horas")
        elif barco["estado"] == "Entrando a esclusa":
            resultado.append("Entrando a esclusa - Operacion en curso")
        else:
            resultado.append("Navegando - Sin incidencias")
        
        if barco["prioridad"] == "Alta":
            resultado.append("Prioridad Alta - Dar preferencia en esclusas")
        
        return " | ".join(resultado)
    
    def preguntar(self, pregunta, df, stats):
        pregunta_lower = pregunta.lower()
        self._registrar_log("pregunta", pregunta)
        
        if "cwt" in pregunta_lower:
            return f"El CWT actual es de {stats['cwt']:.1f} horas con una congestion {stats['nivel'].lower()}."
        
        if "barco" in pregunta_lower:
            return f"Hay {stats['total']} barcos activos. {stats['norte']} van al Norte y {stats['sur']} al Sur."
        
        if "espera" in pregunta_lower:
            return f"Hay {stats['espera']} barcos en espera en las esclusas."
        
        if "velocidad" in pregunta_lower:
            return f"La velocidad promedio es de {stats['velocidad_prom']:.1f} nudos."
        
        if "esclusa" in pregunta_lower:
            partes = []
            for nombre, datos in stats["esclusas"].items():
                partes.append(f"{nombre}: {datos['total']} barcos, {datos['espera']} en espera")
            return " | ".join(partes)
        
        if "clima" in pregunta_lower:
            temp = df["temperatura"].mean() if "temperatura" in df.columns else 25
            viento = df["viento"].mean() if "viento" in df.columns else 15
            return f"Temperatura: {temp:.1f}°C, Viento: {viento:.1f} nudos. Condiciones favorables para navegacion."
        
        return f"He analizado tu consulta. El Canal opera con {stats['total']} barcos y un CWT de {stats['cwt']:.1f}h."
    
    def generar_reporte_completo(self, df, stats):
        lineas = []
        lineas.append("=" * 80)
        lineas.append("ANAYANSI - REPORTE EJECUTIVO DEL CANAL DE PANAMA")
        lineas.append("=" * 80)
        lineas.append(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append(f"Version del sistema: {self.version}")
        lineas.append(f"Nivel de confianza: {int(self.confianza*100)}%")
        lineas.append(f"Registros de aprendizaje: {len(self.aprendizaje)}")
        lineas.append("=" * 80)
        lineas.append("")
        lineas.append("RESUMEN OPERATIVO")
        lineas.append("-" * 80)
        lineas.append(f"Barcos activos: {stats['total']}")
        lineas.append(f"Norte: {stats['norte']} | Sur: {stats['sur']}")
        lineas.append(f"CWT: {stats['cwt']:.1f} horas ({stats['nivel']})")
        lineas.append(f"Velocidad promedio: {stats['velocidad_prom']:.1f} nudos")
        lineas.append(f"Barcos en espera: {stats['espera']}")
        lineas.append(f"Prioridad Alta: {stats['prioridad_alta']}")
        lineas.append("")
        lineas.append("ESTADO DE ESLUSCAS")
        lineas.append("-" * 80)
        for nombre, datos in stats["esclusas"].items():
            lineas.append(f"{nombre}:")
            lineas.append(f"  - Total: {datos['total']} barcos")
            lineas.append(f"  - En espera: {datos['espera']}")
            lineas.append(f"  - Norte: {datos['norte']} | Sur: {datos['sur']}")
            lineas.append(f"  - Eficiencia: {datos['eficiencia']}")
        lineas.append("")
        lineas.append("DISTRIBUCION POR TIPO DE BARCO")
        lineas.append("-" * 80)
        for tipo, cantidad in stats["tipos"].items():
            lineas.append(f"  - {tipo}: {cantidad}")
        lineas.append("")
        lineas.append("ORIGEN DE BARCOS")
        lineas.append("-" * 80)
        for origen, cantidad in stats["origenes"].items():
            lineas.append(f"  - {origen}: {cantidad}")
        lineas.append("")
        lineas.append("=" * 80)
        lineas.append("PREDICCIONES Y RECOMENDACIONES")
        lineas.append("=" * 80)
        lineas.append(f"Prediccion de congestion: {stats['nivel']}")
        if stats["cwt"] < 18:
            lineas.append("Recomendacion: Mantener operaciones normales")
        else:
            lineas.append("Recomendacion: Activar protocolos de congestion")
        lineas.append("")
        lineas.append("ANAYANSI - Sabiduria del mar")
        lineas.append("=" * 80)
        
        return "\n".join(lineas)
