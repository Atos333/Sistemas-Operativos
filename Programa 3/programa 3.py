import os
import sys
import time
import random
import msvcrt

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

class Proceso:
    def __init__(self, id_prog, operacion_str, resultado_calculado, tme):
        self.id_prog = id_prog
        self.operacion_str = operacion_str
        self.resultado_calculado = resultado_calculado
        self.resultado = None             # Se asignará el valor calculado o "ERROR"
        self.tme = tme                    # Tiempo Máximo Estimado
        self.tt = 0                       # Tiempo Transcurrido en ejecución (CPU)
        
        # Estado bloqueado
        self.tiempo_bloqueado = 0         # Contador en cola de bloqueados (0 a 8)
        
        # Métricas de tiempos (Requerimiento 9)
        self.tiempo_llegada = None        # Hora en que entra al sistema (memoria/listos)
        self.tiempo_finalizacion = None   # Hora en que el proceso terminó
        self.tiempo_retorno = None        # T. Finalización - T. Llegada
        self.tiempo_primera_atencion = None # Momento en que entra por primera vez a CPU
        self.tiempo_respuesta = None      # T. Primera Atención - T. Llegada
        self.tiempo_espera = None         # T. Retorno - T. Servicio
        self.tiempo_servicio = None       # Tiempo total en CPU (tt)
        self.tipo_terminacion = None      # "Normal" o "Error"

def resolver_operacion(n1, op, n2):
    if op == '+':
        return n1 + n2
    elif op == '-':
        return n1 - n2
    elif op == '*':
        return n1 * n2
    elif op == '/':
        return round(n1 / n2, 2)
    elif op in ['%', 'residuo']:
        return n1 % n2
    return 0

def pedir_entero_positivo(msg):
    while True:
        try:
            val = int(input(msg).strip())
            if val > 0:
                return val
            print("Error: El valor debe ser mayor a 0.")
        except ValueError:
            print("Error: Ingresa un número entero válido.")

def generar_procesos(n):
    procesos = []
    operadores = ['+', '-', '*', '/', '%']

    for i in range(1, n + 1):
        id_prog = i
        tme = random.randint(5, 20)
        op = random.choice(operadores)
        num1 = random.randint(0, 100)
        num2 = random.randint(0, 100)

        # Evitar división entre 0
        if op in ['/', '%'] and num2 == 0:
            num2 = random.randint(1, 100)

        res = resolver_operacion(num1, op, num2)
        simbolo = "%" if op == "residuo" else op

        # Formatear números si no tienen decimales
        n1_str = int(num1) if num1 % 1 == 0 else num1
        n2_str = int(num2) if num2 % 1 == 0 else num2
        res_final = int(res) if res % 1 == 0 else res

        operacion_str = f"{n1_str} {simbolo} {n2_str}"
        procesos.append(Proceso(id_prog, operacion_str, res_final, tme))

    return procesos

def leer_tecla():
    if msvcrt.kbhit():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):  # Manejo de teclas especiales o de función
            if msvcrt.kbhit():
                msvcrt.getch()
            return None
        return ch.decode('utf-8', errors='ignore').lower()
    return None

def vaciar_buffer_teclado():
    while msvcrt.kbhit():
        msvcrt.getch()

def admitir_nuevos(cola_nuevos, cola_listos, cola_bloqueados, proceso_actual, reloj, max_memoria=5):
    en_memoria = len(cola_listos) + len(cola_bloqueados) + (1 if proceso_actual is not None else 0)
    while cola_nuevos and en_memoria < max_memoria:
        p = cola_nuevos.pop(0)
        p.tiempo_llegada = reloj
        cola_listos.append(p)
        en_memoria += 1

def mostrar_interfaz(cola_nuevos, cola_listos, proceso_actual, cola_bloqueados, terminados, reloj):
    limpiar_pantalla()
    print(f"# Procesos en estado Nuevo: {len(cola_nuevos):<15} Reloj: {reloj}\n")

    # Columna 1: Cola de Listos (ID, TME, TT)
    col1 = ["Cola de Listos", f"{'ID':<5}{'TME':<5}{'TT':<5}"]
    for p in cola_listos:
        col1.append(f"{p.id_prog:<5}{p.tme:<5}{p.tt:<5}")

    # Columna 2: Proceso en Ejecución
    col2 = ["Ejecución"]
    if proceso_actual:
        tr = proceso_actual.tme - proceso_actual.tt
        col2.append(f"ID:   {proceso_actual.id_prog}")
        col2.append(f"Ope:  {proceso_actual.operacion_str}")
        col2.append(f"TME:  {proceso_actual.tme}")
        col2.append(f"TT:   {proceso_actual.tt}")
        col2.append(f"TR:   {tr}")
    else:
        col2.append("ID:   -")
        col2.append("Ope:  -")
        col2.append("TME:  -")
        col2.append("TT:   -")
        col2.append("TR:   -")

    # Columna 3: Cola de Bloqueados (ID, TT Bloq)
    col3 = ["Bloqueados", f"{'ID':<5}{'TT Bloq':<8}"]
    for p in cola_bloqueados:
        col3.append(f"{p.id_prog:<5}{p.tiempo_bloqueado:<8}")

    # Columna 4: Procesos Terminados (ID, Operación, Resultado)
    col4 = ["Terminados", f"{'ID':<5}{'Operación':<14}{'Res':<9}"]
    for p in terminados:
        col4.append(f"{p.id_prog:<5}{p.operacion_str:<14}{str(p.resultado):<9}")

    filas = max(len(col1), len(col2), len(col3), len(col4))
    while len(col1) < filas: col1.append("")
    while len(col2) < filas: col2.append("")
    while len(col3) < filas: col3.append("")
    while len(col4) < filas: col4.append("")

    for i in range(filas):
        print(f"{col1[i]:<15} {col2[i]:<17} {col3[i]:<14} {col4[i]}")

def mostrar_tabla_final(terminados, reloj_total):
    limpiar_pantalla()
    ancho = 102
    print("=" * ancho)
    print(f"{'RESULTADOS FINALES DE LA SIMULACION (PROCESOS TERMINADOS)':^{ancho}}")
    print("=" * ancho)
    
    headers = f"{'ID':<5}{'Operación':<15}{'Resultado':<12}{'Estado':<9}{'TME':<6}{'T.Lleg':<8}{'T.Fin':<7}{'T.Ret':<7}{'T.Resp':<8}{'T.Esp':<7}{'T.Serv':<7}"
    print(headers)
    print("-" * ancho)
    
    suma_retorno = 0
    suma_respuesta = 0
    suma_espera = 0
    suma_servicio = 0
    
    terminados_ordenados = sorted(terminados, key=lambda p: p.id_prog)
    
    for p in terminados_ordenados:
        suma_retorno += p.tiempo_retorno
        suma_respuesta += p.tiempo_respuesta
        suma_espera += p.tiempo_espera
        suma_servicio += p.tiempo_servicio
        
        row = (f"{p.id_prog:<5}"
               f"{p.operacion_str:<15}"
               f"{str(p.resultado):<12}"
               f"{p.tipo_terminacion:<9}"
               f"{p.tme:<6}"
               f"{p.tiempo_llegada:<8}"
               f"{p.tiempo_finalizacion:<7}"
               f"{p.tiempo_retorno:<7}"
               f"{p.tiempo_respuesta:<8}"
               f"{p.tiempo_espera:<7}"
               f"{p.tiempo_servicio:<7}")
        print(row)
        
    print("=" * ancho)
    n = len(terminados)
    if n > 0:
        prom_ret = round(suma_retorno / n, 2)
        prom_resp = round(suma_respuesta / n, 2)
        prom_esp = round(suma_espera / n, 2)
        prom_serv = round(suma_servicio / n, 2)
        print(f"PROMEDIOS: Retorno: {prom_ret} s | Respuesta: {prom_resp} s | Espera: {prom_esp} s | Servicio: {prom_serv} s")
    print(f"Tiempo Total de Simulación: {reloj_total} segundos")
    print("=" * ancho)

def simular(procesos):
    cola_nuevos = list(procesos)
    cola_listos = []
    cola_bloqueados = []
    proceso_actual = None
    terminados = []
    reloj = 0
    total_procesos = len(procesos)
    max_memoria = 5

    # Admisión inicial de hasta 5 procesos al sistema a reloj = 0
    admitir_nuevos(cola_nuevos, cola_listos, cola_bloqueados, proceso_actual, reloj, max_memoria)

    while len(terminados) < total_procesos:
        # Asegurar admisión si se desocupó espacio en memoria
        admitir_nuevos(cola_nuevos, cola_listos, cola_bloqueados, proceso_actual, reloj, max_memoria)

        # Si el procesador está libre y hay procesos en cola de listos, despachar el siguiente
        if proceso_actual is None and cola_listos:
            proceso_actual = cola_listos.pop(0)
            if proceso_actual.tiempo_primera_atencion is None:
                proceso_actual.tiempo_primera_atencion = reloj
                proceso_actual.tiempo_respuesta = reloj - proceso_actual.tiempo_llegada

        # Mostrar interfaz en pantalla
        mostrar_interfaz(cola_nuevos, cola_listos, proceso_actual, cola_bloqueados, terminados, reloj)

        interrumpido = False
        error = False

        # Intervalo de 1 segundo dividido en 10 partes para lectura de teclas en tiempo real
        for _ in range(10):
            tecla = leer_tecla()
            if tecla == 'p':
                print("\n--- PAUSA (Presione 'C' para continuar) ---")
                while True:
                    t_pausa = leer_tecla()
                    if t_pausa == 'c':
                        vaciar_buffer_teclado()
                        break
                    time.sleep(0.05)
                mostrar_interfaz(cola_nuevos, cola_listos, proceso_actual, cola_bloqueados, terminados, reloj)
            elif tecla == 'e':
                if proceso_actual is not None:
                    interrumpido = True
                    vaciar_buffer_teclado()
                    break
            elif tecla == 'w':
                if proceso_actual is not None:
                    error = True
                    vaciar_buffer_teclado()
                    break
            time.sleep(0.1)

        # Manejo de Interrupción por E/S (Tecla E)
        if interrumpido:
            proceso_actual.tiempo_bloqueado = 0
            cola_bloqueados.append(proceso_actual)
            proceso_actual = None
            continue

        # Manejo de Terminación por Error (Tecla W)
        if error:
            proceso_actual.resultado = "ERROR"
            proceso_actual.tipo_terminacion = "Error"
            proceso_actual.tiempo_finalizacion = reloj
            proceso_actual.tiempo_servicio = proceso_actual.tt
            proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.tiempo_servicio
            terminados.append(proceso_actual)
            proceso_actual = None

            # Al terminar, se admite un nuevo proceso a memoria si existe cupo y en cola_nuevos
            admitir_nuevos(cola_nuevos, cola_listos, cola_bloqueados, proceso_actual, reloj, max_memoria)
            continue

        # Avance normal del reloj simulado de 1 segundo
        reloj += 1

        # Avanzar procesos en cola de bloqueados
        procesos_desbloqueados = []
        restantes_bloqueados = []
        for p_bloq in cola_bloqueados:
            p_bloq.tiempo_bloqueado += 1
            if p_bloq.tiempo_bloqueado >= 8:
                p_bloq.tiempo_bloqueado = 0
                procesos_desbloqueados.append(p_bloq)
            else:
                restantes_bloqueados.append(p_bloq)

        cola_bloqueados = restantes_bloqueados
        cola_listos.extend(procesos_desbloqueados)

        # Avanzar proceso en ejecución (CPU)
        if proceso_actual is not None:
            proceso_actual.tt += 1
            if proceso_actual.tt >= proceso_actual.tme:
                proceso_actual.resultado = proceso_actual.resultado_calculado
                proceso_actual.tipo_terminacion = "Normal"
                proceso_actual.tiempo_finalizacion = reloj
                proceso_actual.tiempo_servicio = proceso_actual.tme
                proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
                proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.tiempo_servicio
                terminados.append(proceso_actual)
                proceso_actual = None

                # Al terminar, admitir de la cola de nuevos
                admitir_nuevos(cola_nuevos, cola_listos, cola_bloqueados, proceso_actual, reloj, max_memoria)

    # Mostrar estado final de la simulación
    mostrar_interfaz(cola_nuevos, cola_listos, None, cola_bloqueados, terminados, reloj)
    print("\n>>> FIN DE LA SIMULACION - TODOS LOS PROCESOS EJECUTADOS <<<")
    input("\nPresione ENTER para ver la tabla final de resultados y tiempos...")

    # Desplegar la tabla final de resultados
    mostrar_tabla_final(terminados, reloj)
    input("\nPresione ENTER para salir del programa...")

def main():
    limpiar_pantalla()
    print("=" * 60)
    print("      SIMULADOR DE GESTIÓN DE PROCESOS (PROGRAMA 3)        ")
    print("                DIAGRAMA DE CINCO ESTADOS                 ")
    print("=" * 60)
    
    n = pedir_entero_positivo("\nIngrese el número inicial de procesos: ")
    procesos = generar_procesos(n)

    limpiar_pantalla()
    print("=" * 60)
    print("  Generación de procesos completada con éxito.")
    print(f"  Total de procesos creados: {len(procesos)}")
    print(f"  Capacidad máxima en memoria: 5 procesos")
    print("=" * 60)
    print("\nTeclas durante la simulación:")
    print("  [E] : Interrupción por E/S (Pasa a Bloqueados por 8 s)")
    print("  [W] : Terminación por Error (Sale del procesador)")
    print("  [P] : Pausa de la simulación")
    print("  [C] : Continuar tras pausa")
    print("=" * 60)
    input("\nPresione ENTER para iniciar la simulación...")

    simular(procesos)

if __name__ == "__main__":
    main()
