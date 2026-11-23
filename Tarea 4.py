"""
from abc import ABC, abstractmethod  # Importa herramientas para definir clases y métodos abstractos
from datetime import datetime  # Importa datetime para marcar fecha y hora en los logs y registros
from typing import Optional  # Importa Optional para anotar parámetros opcionales con claridad


# ==============================================================================
# 1. EXCEPCIONES PERSONALIZADAS
# ==============================================================================

class ErrorSoftwareFJ(Exception):  # Clase base para todas las excepciones del dominio de Software FJ
    """Excepción base del sistema Software FJ."""  # Documenta la excepción base

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):  # Constructor con mensaje y código de error
        super().__init__(mensaje)  # Inicializa la clase padre Exception con el mensaje
        self.codigo = codigo  # Almacena un código identificador del error


class ErrorValidacion(ErrorSoftwareFJ):  # Excepción específica para datos inválidos o parámetros faltantes
    """Error lanzado cuando fallan validaciones de entrada o datos."""  # Documenta la clase


class ErrorServicioNoDisponible(ErrorSoftwareFJ):  # Excepción cuando un servicio no está disponible o falla
    """Error lanzado ante indisponibilidad o configuración inválida de un servicio."""  # Documenta la clase


class ErrorReserva(ErrorSoftwareFJ):  # Excepción para operaciones inválidas o fallos en reservas
    """Error lanzado en operaciones no permitidas o fallos al procesar reservas."""  # Documenta la clase


# ==============================================================================
# 2. GESTOR DE LOGS (REGISTRO DE EVENTOS Y ERRORES SIN BASE DE DATOS)
# ==============================================================================

class GestorLogs:  # Administra el registro en archivo de texto plano sin usar bases de datos
    """Registra eventos y excepciones en un archivo de log."""  # Documenta la clase

    def __init__(self, ruta_archivo: str = "logs_software_fj.log"):  # Recibe la ruta del archivo de log
        self.ruta_archivo = ruta_archivo  # Guarda la ruta del archivo de log

    def registrar(self, nivel: str, mensaje: str, detalle_error: Optional[str] = None) -> None:  # Escribe una línea de log
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtiene la fecha y hora actuales formateadas
        linea = f"[{marca_tiempo}] [{nivel}] {mensaje}"  # Construye el mensaje base del log
        if detalle_error:  # Verifica si existe información adicional de error o encadenamiento
            linea += f" | Detalle: {detalle_error}"  # Agrega el detalle técnico al registro
        try:  # Intenta escribir en el archivo de log
            with open(self.ruta_archivo, "a", encoding="utf-8") as archivo:  # Abre el archivo en modo anexar (append)
                archivo.write(linea + "\n")  # Escribe la línea con salto de línea
        except OSError as exc:  # Captura fallos de sistema de archivos al escribir el log
            print(f"[AVISO CRITICO] No se pudo escribir en el log: {exc}")  # Informa por consola sin detener el programa


# ==============================================================================
# 3. CLASES ABSTRACTAS BASE Y CLIENTE
# ==============================================================================

class EntidadSistema(ABC):  # Clase abstracta base para entidades generales del sistema
    """Representa una entidad general con identificador y validación."""  # Documenta la clase abstracta

    def __init__(self, id_entidad: str):  # Constructor de la entidad base
        if not isinstance(id_entidad, str) or not id_entidad.strip():  # Valida que el ID sea texto no vacío
            raise ErrorValidacion("El identificador de la entidad es obligatorio y no puede estar vacío.", "ERR_ID")  # Lanza error de validación
        self._id = id_entidad.strip().upper()  # Encapsula el ID normalizado en mayúsculas

    @property  # Expone el ID de forma controlada (solo lectura)
    def id(self) -> str:  # Getter del atributo protegido _id
        return self._id  # Retorna el identificador

    @abstractmethod  # Obliga a las subclases a implementar un resumen descriptivo
    def resumen(self) -> str:  # Método abstracto de resumen
        """Devuelve un resumen de la entidad."""  # Documenta el método abstracto


class Cliente(EntidadSistema):  # Clase Cliente que hereda de EntidadSistema
    """Representa un cliente con encapsulación y validaciones estrictas."""  # Documenta la clase Cliente

    def __init__(self, id_cliente: str, nombre: str, correo: str, activo: bool = True):  # Constructor de Cliente
        super().__init__(id_cliente)  # Valida y asigna el ID mediante la clase padre
        self.nombre = nombre  # Invoca el setter de nombre para validar
        self.correo = correo  # Invoca el setter de correo para validar
        self._activo = bool(activo)  # Almacena el estado de actividad del cliente

    @property  # Getter encapsulado para el nombre
    def nombre(self) -> str:  # Devuelve el nombre del cliente
        return self._nombre  # Retorna el atributo privado/protegido _nombre

    @nombre.setter  # Setter con validación para el nombre
    def nombre(self, valor: str) -> None:  # Valida y asigna el nombre
        if not isinstance(valor, str) or len(valor.strip()) < 3:  # Verifica longitud mínima y tipo string
            raise ErrorValidacion("El nombre del cliente debe tener al menos 3 caracteres.", "ERR_NOMBRE_CLIENTE")  # Lanza error si es inválido
        self._nombre = valor.strip()  # Guarda el nombre limpio

    @property  # Getter encapsulado para el correo electrónico
    def correo(self) -> str:  # Devuelve el correo del cliente
        return self._correo  # Retorna _correo

    @correo.setter  # Setter con validación para el correo electrónico
    def correo(self, valor: str) -> None:  # Valida formato básico de correo
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:  # Valida estructura mínima de email
            raise ErrorValidacion("El correo electrónico del cliente no es válido.", "ERR_CORREO_CLIENTE")  # Lanza error de validación
        self._correo = valor.strip().lower()  # Guarda el correo normalizado en minúsculas

    @property  # Getter para verificar si el cliente está activo
    def activo(self) -> bool:  # Retorna estado activo
        return self._activo  # Devuelve _activo

    def desactivar(self) -> None:  # Cambia el estado del cliente a inactivo
        self._activo = False  # Marca al cliente como inactivo

    def resumen(self) -> str:  # Implementación del método abstracto resumen()
        estado = "Activo" if self._activo else "Inactivo"  # Traduce el booleano a etiqueta legible
        return f"Cliente [{self._id}] {self._nombre} ({self._correo}) - {estado}"  # Retorna descripción formateada


# ==============================================================================
# 4. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
# ==============================================================================

class Servicio(EntidadSistema):  # Clase abstracta para servicios ofrecidos por Software FJ
    """Clase abstracta base para los servicios de Software FJ."""  # Documenta la clase Servicio

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):  # Constructor de Servicio
        super().__init__(codigo_servicio)  # Valida y asigna el código del servicio
        self.nombre = nombre  # Valida y asigna el nombre del servicio
        self.tarifa_base = tarifa_base  # Valida y asigna la tarifa base
        self._disponible = bool(disponible)  # Guarda disponibilidad inicial del servicio

    @property  # Getter del nombre del servicio
    def nombre(self) -> str:  # Retorna el nombre
        return self._nombre  # Devuelve _nombre

    @nombre.setter  # Setter con validación para el nombre del servicio
    def nombre(self, valor: str) -> None:  # Valida el nombre del servicio
        if not isinstance(valor, str) or not valor.strip():  # Verifica que no esté vacío
            raise ErrorValidacion("El nombre del servicio es obligatorio.", "ERR_NOMBRE_SERVICIO")  # Lanza error de validación
        self._nombre = valor.strip()  # Guarda el nombre limpio

    @property  # Getter de la tarifa base
    def tarifa_base(self) -> float:  # Retorna tarifa_base
        return self._tarifa_base  # Devuelve _tarifa_base

    @tarifa_base.setter  # Setter con validación para evitar tarifas negativas o cero
    def tarifa_base(self, valor: float) -> None:  # Valida tarifa numérica positiva
        try:  # Intenta convertir a float
            monto = float(valor)  # Convierte valor a flotante
        except (TypeError, ValueError) as exc:  # Captura error si no es convertible a número
            raise ErrorValidacion("La tarifa base debe ser un valor numérico.", "ERR_TARIFA_TIPO") from exc  # Encadena excepción
        if monto <= 0:  # Verifica que la tarifa sea mayor que cero
            raise ErrorValidacion("La tarifa base debe ser mayor que cero.", "ERR_TARIFA_VALOR")  # Lanza error de validación
        self._tarifa_base = monto  # Asigna la tarifa válida

    @property  # Getter de disponibilidad
    def disponible(self) -> bool:  # Retorna disponibilidad
        return self._disponible  # Devuelve _disponible

    @disponible.setter  # Setter de disponibilidad
    def disponible(self, estado: bool) -> None:  # Actualiza disponibilidad
        self._disponible = bool(estado)  # Convierte y guarda el estado booleano

    @abstractmethod  # Método abstracto para validar parámetros específicos de cada servicio
    def validar_parametros(self, cantidad: float) -> None:  # Recibe duración o cantidad
        """Valida parámetros como horas o unidades según el tipo de servicio."""  # Documenta el método

    @abstractmethod  # Método abstracto para calcular el costo según el tipo de servicio
    def calcular_costo(  # Soporta variantes mediante parámetros opcionales (sobrecarga simulada en Python)
        self,
        cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        recargo_fijo: float = 0.0,
    ) -> float:  # Retorna el costo total calculado
        """Calcula el costo total aplicando reglas, descuentos, recargos e impuestos."""  # Documenta el método

    def resumen(self) -> str:  # Implementa resumen() heredado de EntidadSistema
        estado = "Disponible" if self._disponible else "No disponible"  # Etiqueta de disponibilidad
        return f"Servicio [{self._id}] {self._nombre} | Tarifa base: ${self._tarifa_base:,.2f} | {estado}"  # Retorna resumen


class ReservaSala(Servicio):  # Servicio especializado 1: reserva de salas
    """Servicio para reserva de salas por horas."""  # Documenta ReservaSala

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):  # Constructor con capacidad
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)  # Llama al constructor padre
        if not isinstance(capacidad, int) or capacidad <= 0:  # Valida que la capacidad sea entera y positiva
            raise ErrorValidacion("La capacidad de la sala debe ser un entero positivo.", "ERR_CAPACIDAD_SALA")  # Lanza error
        self.capacidad = capacidad  # Guarda capacidad de personas

    def validar_parametros(self, cantidad: float) -> None:  # Sobrescribe validación para horas de sala
        if not self._disponible:  # Verifica disponibilidad de la sala
            raise ErrorServicioNoDisponible(f"La sala '{self._nombre}' no está disponible.", "ERR_SALA_NODISP")  # Error de disponibilidad
        if cantidad <= 0 or cantidad > 12:  # Valida rango de horas permitidas por reserva
            raise ErrorValidacion("Las horas de reserva de sala deben estar entre 1 y 12.", "ERR_HORAS_SALA")  # Error de rango

    def calcular_costo(  # Sobrescribe calcular_costo con lógica de salas y parámetros opcionales
        self,
        cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        recargo_fijo: float = 0.0,
    ) -> float:  # Retorna costo final
        self.validar_parametros(cantidad)  # Valida disponibilidad y horas antes de calcular
        subtotal = self._tarifa_base * cantidad + recargo_fijo  # Calcula subtotal por horas más recargo opcional
        con_descuento = subtotal * (1 - max(0.0, descuento_pct) / 100.0)  # Aplica porcentaje de descuento
        total = con_descuento * (1 + max(0.0, impuesto_pct) / 100.0)  # Aplica impuesto (por defecto 19%)
        if total < 0:  # Verifica consistencia del cálculo
            raise ErrorReserva("El cálculo del costo resultó negativo.", "ERR_COSTO_INCONSISTENTE")  # Error de cálculo
        return round(total, 2)  # Redondea a dos decimales


class AlquilerEquipo(Servicio):  # Servicio especializado 2: alquiler de equipos
    """Servicio para alquiler de equipos tecnológicos por días."""  # Documenta AlquilerEquipo

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, modelo: str, disponible: bool = True):  # Constructor con modelo
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)  # Inicializa clase padre
        if not isinstance(modelo, str) or not modelo.strip():  # Valida modelo del equipo
            raise ErrorValidacion("El modelo del equipo es obligatorio.", "ERR_MODELO_EQUIPO")  # Lanza error
        self.modelo = modelo.strip()  # Guarda el modelo limpio

    def validar_parametros(self, cantidad: float) -> None:  # Sobrescribe validación para días de alquiler
        if not self._disponible:  # Verifica disponibilidad del equipo
            raise ErrorServicioNoDisponible(f"El equipo '{self._nombre}' no está disponible.", "ERR_EQUIPO_NODISP")  # Error de disponibilidad
        if cantidad <= 0 or cantidad > 30:  # Valida días máximos de alquiler
            raise ErrorValidacion("Los días de alquiler deben estar entre 1 y 30.", "ERR_DIAS_EQUIPO")  # Error de rango

    def calcular_costo(  # Sobrescribe calcular_costo para alquiler de equipos
        self,
        cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        recargo_fijo: float = 5000.0,
    ) -> float:  # Retorna costo total (incluye cargo de revisión/alistamiento por defecto)
        self.validar_parametros(cantidad)  # Valida disponibilidad y días
        subtotal = self._tarifa_base * cantidad + recargo_fijo  # Calcula costo por días más cargo de alistamiento
        con_descuento = subtotal * (1 - max(0.0, descuento_pct) / 100.0)  # Aplica descuento si existe
        total = con_descuento * (1 + max(0.0, impuesto_pct) / 100.0)  # Aplica impuesto
        if total <= 0:  # Valida cálculo consistente
            raise ErrorReserva("El total calculado para el alquiler es inválido.", "ERR_COSTO_INCONSISTENTE")  # Lanza error
        return round(total, 2)  # Retorna valor redondeado


class AsesoriaEspecializada(Servicio):  # Servicio especializado 3: asesorías especializadas
    """Servicio de consultoría o asesoría técnica especializada por horas."""  # Documenta AsesoriaEspecializada

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):  # Constructor con especialidad
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)  # Llama al constructor padre
        if not isinstance(especialidad, str) or not especialidad.strip():  # Valida especialidad
            raise ErrorValidacion("La especialidad de la asesoría es obligatoria.", "ERR_ESPECIALIDAD")  # Lanza error
        self.especialidad = especialidad.strip()  # Guarda especialidad

    def validar_parametros(self, cantidad: float) -> None:  # Sobrescribe validación para horas de asesoría
        if not self._disponible:  # Verifica si el consultor/servicio está disponible
            raise ErrorServicioNoDisponible(f"La asesoría '{self._nombre}' no está disponible.", "ERR_ASESORIA_NODISP")  # Error de disponibilidad
        if cantidad < 0.5 or cantidad > 20:  # Valida duración mínima y máxima de asesoría
            raise ErrorValidacion("La duración de la asesoría debe estar entre 0.5 y 20 horas.", "ERR_HORAS_ASESORIA")  # Error de rango

    def calcular_costo(  # Sobrescribe calcular_costo para asesorías
        self,
        cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        recargo_fijo: float = 0.0,
    ) -> float:  # Retorna costo final de la asesoría
        self.validar_parametros(cantidad)  # Valida parámetros antes de calcular
        subtotal = self._tarifa_base * cantidad + recargo_fijo  # Calcula subtotal de horas de asesoría
        con_descuento = subtotal * (1 - max(0.0, descuento_pct) / 100.0)  # Aplica descuento
        total = con_descuento * (1 + max(0.0, impuesto_pct) / 100.0)  # Aplica impuesto
        if total < 0:  # Verifica consistencia numérica
            raise ErrorReserva("Costo inconsistente en asesoría.", "ERR_COSTO_INCONSISTENTE")  # Lanza error
        return round(total, 2)  # Retorna total redondeado


# ==============================================================================
# 5. CLASE RESERVA Y GESTOR DEL SISTEMA (LISTAS INTERNAS + EXCEPCIONES)
# ==============================================================================

class Reserva(EntidadSistema):  # Clase Reserva que integra cliente, servicio, duración y estado
    """Gestiona una reserva y su ciclo de vida (confirmar, procesar, cancelar)."""  # Documenta Reserva

    ESTADOS_VALIDOS = {"PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA"}  # Conjunto de estados permitidos

    def __init__(  # Constructor de Reserva
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
    ):  # Recibe entidades y parámetros de cálculo
        super().__init__(id_reserva)  # Valida y asigna ID de la reserva
        if not isinstance(cliente, Cliente):  # Verifica que cliente sea instancia válida
            raise ErrorValidacion("Debe proporcionar un objeto Cliente válido.", "ERR_CLIENTE_INVALIDO")  # Lanza error
        if not cliente.activo:  # Impide reservas de clientes inactivos
            raise ErrorReserva(f"El cliente '{cliente.nombre}' está inactivo.", "ERR_CLIENTE_INACTIVO")  # Lanza error de reserva
        if not isinstance(servicio, Servicio):  # Verifica que servicio sea instancia válida
            raise ErrorValidacion("Debe proporcionar un objeto Servicio válido.", "ERR_SERVICIO_INVALIDO")  # Lanza error
        servicio.validar_parametros(duracion)  # Valida disponibilidad y duración según el servicio
        self.cliente = cliente  # Asocia el cliente
        self.servicio = servicio  # Asocia el servicio
        self.duracion = float(duracion)  # Guarda duración/cantidad
        self.descuento_pct = float(descuento_pct)  # Guarda porcentaje de descuento
        self.impuesto_pct = float(impuesto_pct)  # Guarda porcentaje de impuesto
        self.estado = "PENDIENTE"  # Estado inicial de la reserva
        self.total = self.servicio.calcular_costo(  # Calcula el costo usando polimorfismo
            self.duracion,
            descuento_pct=self.descuento_pct,
            impuesto_pct=self.impuesto_pct,
        )  # Guarda el total calculado

    def confirmar(self) -> None:  # Confirma una reserva pendiente
        if self.estado == "CANCELADA":  # Impide confirmar una reserva ya cancelada
            raise ErrorReserva("No se puede confirmar una reserva cancelada.", "ERR_CONF_CANCELADA")  # Lanza error
        if self.estado == "PROCESADA":  # Impide reconfirmar una reserva ya procesada
            raise ErrorReserva("La reserva ya fue procesada.", "ERR_CONF_PROCESADA")  # Lanza error
        self.estado = "CONFIRMADA"  # Actualiza el estado a CONFIRMADA

    def procesar(self) -> float:  # Procesa la reserva confirmada y retorna el total
        if self.estado != "CONFIRMADA":  # Exige que la reserva esté confirmada antes de procesarla
            raise ErrorReserva(  # Lanza error si no está confirmada
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual: {self.estado}.",
                "ERR_PROC_ESTADO",
            )  # Cierra argumentos de ErrorReserva
        try:  # Bloque protegido para recalcular y validar monto final
            total_final = self.servicio.calcular_costo(  # Recalcula el costo al procesar
                self.duracion,
                descuento_pct=self.descuento_pct,
                impuesto_pct=self.impuesto_pct,
            )  # Obtiene monto
        except ErrorSoftwareFJ as exc:  # Captura errores de dominio al recalcular
            raise ErrorReserva("Fallo al procesar el cobro de la reserva.", "ERR_PROC_CALCULO") from exc  # Encadena excepción
        self.total = total_final  # Actualiza el total
        self.estado = "PROCESADA"  # Marca la reserva como PROCESADA
        return self.total  # Retorna el monto procesado

    def cancelar(self, motivo: str = "Cancelación solicitada") -> None:  # Cancela la reserva si no está procesada
        if self.estado == "PROCESADA":  # Impide cancelar una reserva ya procesada
            raise ErrorReserva("No es posible cancelar una reserva ya procesada.", "ERR_CANC_PROCESADA")  # Lanza error
        if not motivo or not motivo.strip():  # Exige un motivo válido para cancelar
            raise ErrorValidacion("Debe indicar un motivo para cancelar la reserva.", "ERR_MOTIVO_VACIO")  # Lanza error
        self.estado = "CANCELADA"  # Actualiza el estado a CANCELADA

    def resumen(self) -> str:  # Implementa resumen() de EntidadSistema
        return (  # Retorna descripción completa de la reserva
            f"Reserva [{self._id}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
            f"Total: ${self.total:,.2f} | Estado: {self.estado}"
        )  # Fin del string de resumen


class SistemaGestionSoftwareFJ:  # Coordina listas internas, operaciones y logs sin base de datos
    """Sistema integral en memoria con registro de eventos y errores en archivo."""  # Documenta el gestor principal

    def __init__(self, archivo_log: str = "logs_software_fj.log"):  # Inicializa listas y gestor de logs
        self.clientes: list[Cliente] = []  # Lista interna de clientes
        self.servicios: list[Servicio] = []  # Lista interna de servicios
        self.reservas: list[Reserva] = []  # Lista interna de reservas
        self.logger = GestorLogs(archivo_log)  # Instancia el gestor de logs

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, activo: bool = True) -> Optional[Cliente]:  # Registra un cliente
        try:  # Intenta crear y almacenar el cliente
            if any(c.id == id_cliente.strip().upper() for c in self.clientes if isinstance(id_cliente, str)):  # Verifica ID duplicado
                raise ErrorValidacion(f"Ya existe un cliente con ID '{id_cliente}'.", "ERR_ID_DUPLICADO")  # Error por duplicado
            cliente = Cliente(id_cliente, nombre, correo, activo)  # Instancia Cliente con validaciones
        except ErrorSoftwareFJ as exc:  # Captura errores de validación o dominio
            self.logger.registrar("ERROR", f"Fallo al registrar cliente '{id_cliente}': {exc}", f"Código={exc.codigo}")  # Registra en log
            return None  # Retorna None sin detener el sistema
        except Exception as exc:  # Captura cualquier error inesperado y lo encadena
            envuelto = ErrorValidacion("Error inesperado al registrar cliente.", "ERR_INESPERADO_CLI")  # Crea excepción envolvente
            self.logger.registrar("ERROR", str(envuelto), f"Causa={exc}")  # Registra causa original en log
            return None  # Mantiene la ejecución activa
        else:  # Se ejecuta solo si no hubo errores
            self.clientes.append(cliente)  # Agrega el cliente a la lista interna
            self.logger.registrar("INFO", f"Cliente registrado: {cliente.resumen()}")  # Registra evento exitoso en log
            return cliente  # Retorna el cliente creado
        finally:  # Se ejecuta siempre al finalizar el intento
            pass  # Punto de control final de la operación

    def agregar_servicio(self, servicio: Servicio) -> Optional[Servicio]:  # Agrega un servicio a la lista interna
        try:  # Intenta agregar el servicio
            if not isinstance(servicio, Servicio):  # Valida tipo de objeto
                raise ErrorValidacion("El objeto proporcionado no es un Servicio válido.", "ERR_TIPO_SERVICIO")  # Lanza error
            if any(s.id == servicio.id for s in self.servicios):  # Evita códigos duplicados
                raise ErrorValidacion(f"Ya existe un servicio con código '{servicio.id}'.", "ERR_SERV_DUPLICADO")  # Lanza error
        except ErrorSoftwareFJ as exc:  # Captura error de dominio
            self.logger.registrar("ERROR", f"Fallo al agregar servicio: {exc}", f"Código={exc.codigo}")  # Registra error en log
            return None  # Continúa sin interrumpir
        else:  # Si no hubo excepciones
            self.servicios.append(servicio)  # Guarda el servicio en la lista
            self.logger.registrar("INFO", f"Servicio agregado: {servicio.resumen()}")  # Registra evento en log
            return servicio  # Retorna servicio agregado
        finally:  # Bloque final obligatorio
            pass  # Cierre del bloque

    def crear_y_procesar_reserva(  # Crea, confirma y procesa una reserva con manejo de excepciones
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        cancelar_en_vez_de_procesar: bool = False,
        motivo_cancelacion: str = "Cancelada por el cliente",
    ) -> Optional[Reserva]:  # Retorna la reserva si tiene éxito
        try:  # Inicia bloque principal de reserva
            cliente = next((c for c in self.clientes if c.id == id_cliente.strip().upper()), None)  # Busca cliente en lista interna
            if cliente is None:  # Verifica si el cliente existe
                raise ErrorReserva(f"Cliente '{id_cliente}' no encontrado.", "ERR_CLI_NO_EXISTE")  # Lanza error de reserva

            servicio = next((s for s in self.servicios if s.id == id_servicio.strip().upper()), None)  # Busca servicio en lista interna
            if servicio is None:  # Verifica si el servicio existe
                raise ErrorReserva(f"Servicio '{id_servicio}' no encontrado.", "ERR_SERV_NO_EXISTE")  # Lanza error de reserva

            reserva = Reserva(id_reserva, cliente, servicio, duracion, descuento_pct, impuesto_pct)  # Crea la reserva
            if cancelar_en_vez_de_procesar:  # Evalúa si se solicita cancelar
                reserva.cancelar(motivo_cancelacion)  # Cancela la reserva
            else:  # Flujo normal: confirmar y procesar
                reserva.confirmar()  # Confirma la reserva
                reserva.procesar()  # Procesa el pago/cobro de la reserva
        except ErrorSoftwareFJ as exc:  # Captura cualquier excepción del sistema
            causa = f"Causa previa: {exc.__cause__}" if exc.__cause__ else f"Código={exc.codigo}"  # Revisa si hay excepción encadenada
            self.logger.registrar("ERROR", f"Fallo en reserva '{id_reserva}': {exc}", causa)  # Registra en el archivo de log
            return None  # Retorna None sin detener el programa
        else:  # Se ejecuta si la reserva se completó sin errores
            self.reservas.append(reserva)  # Guarda la reserva en la lista interna
            self.logger.registrar("INFO", f"Reserva completada: {reserva.resumen()}")  # Registra evento exitoso en log
            return reserva  # Retorna la reserva
        finally:  # Siempre se ejecuta al terminar el intento
            pass  # Fin de la operación de reserva


# ==============================================================================
# 6. SIMULACIÓN DE 10 OPERACIONES COMPLETAS (SIN BASE DE DATOS)
# ==============================================================================

def ejecutar_simulacion() -> None:  # Ejecuta 10 operaciones válidas e inválidas de forma secuencial
    sistema = SistemaGestionSoftwareFJ("logs_software_fj.log")  # Crea el sistema y el archivo de log

    # Operación 1: Registro válido de cliente
    c1 = sistema.registrar_cliente("CLI-01", "Laura Gómez", "laura.gomez@correo.com")  # Cliente válido
    print("Op 1 (Cliente válido):", c1.resumen() if c1 else "Falló (ver log)")  # Imprime resultado

    # Operación 2: Registro inválido de cliente (correo sin dominio válido)
    c2 = sistema.registrar_cliente("CLI-02", "Carlos Ruiz", "correo_invalido")  # Provoca ErrorValidacion
    print("Op 2 (Cliente inválido):", c2.resumen() if c2 else "Error controlado (ver log)")  # Imprime resultado

    # Operación 3: Segundo cliente válido para pruebas adicionales
    c3 = sistema.registrar_cliente("CLI-03", "Andrés Pérez", "andres.perez@empresa.co")  # Cliente válido
    print("Op 3 (Cliente válido):", c3.resumen() if c3 else "Falló (ver log)")  # Imprime resultado

    # Operación 4: Creación correcta de servicios especializados (Sala, Equipo, Asesoría)
    try:  # Bloque protegido para crear servicios
        s_sala = ReservaSala("SRV-SALA", "Sala Ejecutiva A", 45000.0, capacidad=10, disponible=True)  # Crea sala válida
        s_equipo = AlquilerEquipo("SRV-EQ", "Portátil Ingeniería", 30000.0, modelo="ThinkPad X1", disponible=True)  # Crea equipo válido
        s_asesoria = AsesoriaEspecializada("SRV-ASE", "Arquitectura Cloud", 80000.0, especialidad="Nube", disponible=True)  # Crea asesoría válida
        s_nodisp = ReservaSala("SRV-SALA2", "Auditorio Principal", 90000.0, capacidad=50, disponible=False)  # Sala no disponible
        for srv in (s_sala, s_equipo, s_asesoria, s_nodisp):  # Recorre los servicios creados
            sistema.agregar_servicio(srv)  # Agrega cada servicio al sistema
        print("Op 4 (Servicios creados): 4 servicios agregados.")  # Confirma creación
    except ErrorSoftwareFJ as exc:  # Captura error si falla creación
        sistema.logger.registrar("ERROR", f"Error en creación de servicios: {exc}", f"Código={exc.codigo}")  # Registra en log
        print("Op 4 (Servicios creados): Error controlado.")  # Informa error

    # Operación 5: Creación incorrecta de servicio (tarifa negativa)
    try:  # Intenta crear servicio con tarifa inválida
        s_malo = AlquilerEquipo("SRV-BAD", "Proyector HD", -15000.0, modelo="Epson", disponible=True)  # Lanza ErrorValidacion
        sistema.agregar_servicio(s_malo)  # No se ejecuta si falla antes
    except ErrorSoftwareFJ as exc:  # Captura la excepción
        sistema.logger.registrar("ERROR", f"Intento de servicio inválido: {exc}", f"Código={exc.codigo}")  # Registra en log
        print("Op 5 (Servicio inválido): Error controlado (ver log).")  # Informa resultado

    # Operación 6: Reserva exitosa de sala con descuento e impuesto personalizado
    r1 = sistema.crear_y_procesar_reserva("RES-01", "CLI-01", "SRV-SALA", duracion=3, descuento_pct=10.0, impuesto_pct=19.0)  # Reserva válida
    print("Op 6 (Reserva sala exitosa):", r1.resumen() if r1 else "Falló (ver log)")  # Imprime resultado

    # Operación 7: Reserva exitosa de alquiler de equipo
    r2 = sistema.crear_y_procesar_reserva("RES-02", "CLI-03", "SRV-EQ", duracion=2)  # Reserva válida de equipo
    print("Op 7 (Reserva equipo exitosa):", r2.resumen() if r2 else "Falló (ver log)")  # Imprime resultado

    # Operación 8: Reserva exitosa de asesoría especializada
    r3 = sistema.crear_y_procesar_reserva("RES-03", "CLI-01", "SRV-ASE", duracion=4, descuento_pct=5.0)  # Reserva válida de asesoría
    print("Op 8 (Reserva asesoría exitosa):", r3.resumen() if r3 else "Falló (ver log)")  # Imprime resultado

    # Operación 9: Reserva fallida por servicio no disponible
    r4 = sistema.crear_y_procesar_reserva("RES-04", "CLI-01", "SRV-SALA2", duracion=2)  # Falla por ErrorServicioNoDisponible
    print("Op 9 (Reserva servicio no disponible):", r4.resumen() if r4 else "Error controlado (ver log)")  # Imprime resultado

    # Operación 10: Reserva fallida por duración inválida (fuera del rango permitido)
    r5 = sistema.crear_y_procesar_reserva("RES-05", "CLI-03", "SRV-SALA", duracion=25)  # Falla por ErrorValidacion (>12 horas)
    print("Op 10 (Reserva duración inválida):", r5.resumen() if r5 else "Error controlado (ver log)")  # Imprime resultado


if __name__ == "__main__":  # Punto de entrada principal del script
    ejecutar_simulacion()  # Ejecuta las 10 operaciones de prueba
        