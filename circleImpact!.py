import tkinter as tk
from tkinter import messagebox
import random
import math
game_over_shown = False  # Variable de control para mostrar Game Over
nivel_puntuaciones = {i: "???" for i in range(1, 11)}

felicidades_mostrada = False  # Inicializa como False al inicio

def iniciar_juego():
    global canvas, bullets, impact_count, puntuacion, puntuacion_label, vida, level, entities
    global nivel_completado_mostrado, nivel_puntuaciones  # Asegúrate de que se incluya el diccionario

    vida = 100
    puntuacion = 0
    level = 1
    impact_count = {}
    bullets = {}
    entities = [] # Inicializa como False
    nivel_completado_mostrado = False

    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Iniciar Juego")
    nueva_ventana.configure(bg="black")
    nueva_ventana.attributes('-fullscreen', True)
    nueva_ventana.bind("<Escape>", lambda event: nueva_ventana.attributes('-fullscreen', False))

    label = tk.Label(nueva_ventana, text=f"Nivel {level} :D", font=("Arial", 24))
    label.pack(pady=20)

    canvas = tk.Canvas(nueva_ventana, width=900, height=800, bg="black", highlightthickness=0)
    canvas.pack()

    circle_x = 900 / 2
    circle_y = 800 / 2
    circle_radius = 20
    canvas.create_oval(circle_x - circle_radius, circle_y - circle_radius,
                       circle_x + circle_radius, circle_y + circle_radius,
                       fill="black", outline="white")
    vida_text = canvas.create_text(circle_x, circle_y, text=str(vida), fill="white", font=("Arial", 14))

    puntuacion_label = tk.Label(nueva_ventana, text=f"Puntuación: {puntuacion}", font=("Arial", 14), bg="black", fg="white")
    puntuacion_label.place(relx=0.9, rely=0.05, anchor='ne')

    def generar_cuadrados():
        num_cuadrados = 5 + (level - 1) * 10 if level < 10 else 60
        for _ in range(num_cuadrados):
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x = random.randint(0, 800)
                y = 0
            elif edge == 'bottom':
                x = random.randint(0, 800)
                y = 780
            elif edge == 'left':
                x = 0
                y = random.randint(0, 600)
            else:
                x = 880
                y = random.randint(0, 600)

            size_multiplier = 2 if random.random() < 0.12 else 1
            entity_size = 20 * size_multiplier
            entity = canvas.create_rectangle(x, y, x + entity_size, y + entity_size, outline="white", fill="black")
            entities.append((entity, 'cuadrado', 1, size_multiplier))  # Velocidad fija de 1
            impact_count[entity] = 0

    def iniciar_nivel():
        global nivel_completado_mostrado
        nivel_completado_mostrado = False  # Resetea la variable
        generar_cuadrados()
        move_entities()
        label.config(text=f"Nivel {level} :D")

    def move_entities():
        global vida
        for entity, entity_type, _, size_multiplier in entities:
            coords = canvas.coords(entity)

            if coords and len(coords) >= 4:
                entity_center_x = (coords[0] + coords[2]) / 2
                entity_center_y = (coords[1] + coords[3]) / 2

                angle = math.atan2(circle_y - entity_center_y, circle_x - entity_center_x)
                dx = math.cos(angle)
                dy = math.sin(angle)

                # Ajustar la velocidad de acuerdo al nivel
                dx *= 1/ level
                dy *= 1/ level

                canvas.move(entity, dx, dy)

                if (circle_x - circle_radius <= entity_center_x <= circle_x + circle_radius and
                        circle_y - circle_radius <= entity_center_y <= circle_y + circle_radius):
                    daño = 4 if size_multiplier == 2 else 1
                    vida -= daño
                    canvas.delete(entity)
                    entities.remove((entity, entity_type, _, size_multiplier))
                    canvas.itemconfig(vida_text, text=str(vida))

        if vida > 0:
            nueva_ventana.after(50, move_entities)
        else:
            game_over()

        check_next_level()

    def move_bullets():
        for bullet in list(bullets.keys()):
            bullet_data = bullets[bullet]
            coords = canvas.coords(bullet)
            if not coords:
                del bullets[bullet]
                continue

            canvas.move(bullet, bullet_data['speed'] * bullet_data['direction'][0],
                        bullet_data['speed'] * bullet_data['direction'][1])

            for entity, entity_type, _, size_multiplier in entities:
                entity_coords = canvas.coords(entity)
                if (entity_coords and
                        entity_coords[0] < coords[2] and
                        entity_coords[2] > coords[0] and
                        entity_coords[1] < coords[3] and
                        entity_coords[3] > coords[1]):

                    # Modificación: Probabilidad del 50% de contar como 4 impactos
                    if random.random() < 0.5:  # 50% de probabilidad
                        impact_count[entity] += 4  # Cuenta como 4 impactos
                    else:
                        impact_count[entity] += 1  # Cuenta como 1 impacto

                    canvas.delete(bullet)
                    del bullets[bullet]

                    required_impacts = 4 if size_multiplier == 1 else 8
                    if impact_count[entity] >= required_impacts:
                        canvas.delete(entity)
                        entities.remove((entity, entity_type, _, size_multiplier))
                        global puntuacion
                        puntuacion += 500 if size_multiplier == 2 else 100
                        puntuacion_label.config(text=f"Puntuación: {puntuacion}")

                    break

            if (coords[0] < 0 or coords[2] > 900 or
                    coords[1] < 0 or coords[3] > 800):
                canvas.delete(bullet)
                del bullets[bullet]

        if bullets:
            nueva_ventana.after(50, move_bullets)

    def shoot(event):
        global canvas

        if not canvas or not canvas.winfo_exists():
            return

        target_x = event.x
        target_y = event.y
        bullet_x = circle_x
        bullet_y = circle_y
        bullet = canvas.create_oval(bullet_x - 2, bullet_y - 2, bullet_x + 2, bullet_y + 2, fill="red", outline="red")

        dx = target_x - bullet_x
        dy = target_y - bullet_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return
        direction = (dx / distance, dy / distance)

        bullets[bullet] = {'direction': direction, 'speed': 5}
        move_bullets()

    nueva_ventana.bind("<Button-1>", shoot)
    btn_salir_juego = tk.Button(nueva_ventana, text="Salir del Juego", font=("Arial", 14), bg="black", fg="white",
                                command=nueva_ventana.destroy)
    btn_salir_juego.place(relx=1.0, rely=1.0, anchor='se')

    def game_over():
        global game_over_shown
        if not game_over_shown:  # Verifica si ya se mostró la ventana de Game Over
            game_over_shown = True  # Cambia a True para evitar múltiples ventanas
            game_over_window = tk.Toplevel(nueva_ventana)
            game_over_window.title("¡Juego Terminado!")
            game_over_label = tk.Label(game_over_window, text="¡Game Over!", font=("Arial", 40), fg="red", bg="black")
            game_over_label.pack()

            def reiniciar_juego():
                game_over_window.destroy()
                iniciar_juego()

            btn_reiniciar = tk.Button(game_over_window, text="Reiniciar", font=("Arial", 14), command=reiniciar_juego)
            btn_reiniciar.pack(pady=10)
            btn_salir = tk.Button(game_over_window, text="Salir", font=("Arial", 14), command=nueva_ventana.destroy)
            btn_salir.pack(pady=10)

    # Inicializa la variable de control al principio del juego
    game_over_shown = False

    def nivel_completado():
        global nivel_completado_mostrado, puntuacion  # Asegúrate de incluir puntuacion
        if not nivel_completado_mostrado:
            nivel_completado_mostrado = True
            nivel_puntuaciones[level] = puntuacion  # Guardar la puntuación del nivel completado
            puntuacion = 0  # Reinicia la puntuación para el siguiente nivel
            nivel_window = tk.Toplevel(nueva_ventana)
            nivel_window.title("¡Nivel Completo!")
            nivel_label = tk.Label(nivel_window, text=f"¡Nivel {level} completado!", font=("Arial", 24), fg="green",
                                   bg="black")
            nivel_label.pack(pady=20)
            def continuar():
                nivel_window.destroy()
                global level
                level += 1
                iniciar_nivel()

            def salir():
                nivel_window.destroy()
                nueva_ventana.destroy()

            btn_continuar = tk.Button(nivel_window, text="Continuar", font=("Arial", 14), command=continuar)
            btn_continuar.pack(pady=10)
            btn_salir = tk.Button(nivel_window, text="Salir", font=("Arial", 14), command=salir)
            btn_salir.pack(pady=10)

    def mostrar_felicidades():
        global felicidades_mostrada
        if not felicidades_mostrada:  # Verifica si ya se mostró
            felicidades_mostrada = True  # Cambia a True
            nivel_puntuaciones[level] = puntuacion #MALDITA LINEA DE PORQUERIA ME TOMO 8 HORAS SABER PQ NO SE
            # MOSTRABAN LOS PUNTOS DEL NIVEL 10 Y ERA PQ NO ESTAA ESTA LINEA AQUIIIIIIIIIII
            felicidades_window = tk.Toplevel(nueva_ventana)
            felicidades_window.title("¡Felicidades!")
            felicidades_label = tk.Label(felicidades_window, text="¡Has completado todos los niveles!",
                                         font=("Arial", 24), fg="green", bg="black")
            felicidades_label.pack(pady=20)

            btn_salir = tk.Button(felicidades_window, text="Salir del Juego", font=("Arial", 14),
                                  command=nueva_ventana.destroy)
            btn_salir.pack(pady=10)

    def check_next_level():
        if len(entities) == 0 and not nivel_completado_mostrado:
            if level == 10:
                mostrar_felicidades()  # Llama a la función de felicitaciones
                return  # Detiene el flujo
            else:
                nivel_completado()

    iniciar_nivel()

# Crear la ventana pnincipal

def instrucciones():

    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Instrucciones")
    nueva_ventana.configure(bg="black")
    instrucciones = ("1. Usa el puntero del mouse para apuntar.\n2. Dispara con click derecho."
                     "\n3. Evita que las demas figuras te destruyan!!")
    label = tk.Label(nueva_ventana, text=instrucciones, font=("Arial", 12), justify="left",bg="black", fg="white")
    label.pack(padx=20, pady=20)

def puntajes():
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Puntajes por Nivel")
    nueva_ventana.configure(bg="black")
    puntajes_text = "\n".join([f"Nivel {i}: {nivel_puntuaciones[i]}" for i in range(1, 11)])
    label = tk.Label(nueva_ventana, text=puntajes_text, font=("Arial", 12), bg="black", fg="white")
    label.pack(padx=20, pady=20)

def salir():
    respuesta = messagebox.askquestion("Salir", "¿Estás seguro de que deseas salir?")
    if respuesta == "yes":
        root.quit()

# Ventana principal
root = tk.Tk()
root.title("Ventana de Inicio del Juego")
root.geometry("500x200")
root.configure(bg="black")  # Cambiar el fondo a negro

# Creación de botones
btn_inicio = tk.Button(root, text="Iniciar Juego", font=("Arial", 12), bg="black", fg="white", command=iniciar_juego)
btn_inicio.pack(pady=10)

btn_instrucciones = tk.Button(root, text="Instrucciones", font=("Arial", 12), bg="black", fg="white",command=instrucciones)
btn_instrucciones.pack(pady=10)

btn_puntajes = tk.Button(root, text="Puntajes", font=("Arial", 12), bg="black", fg="white",command=puntajes)
btn_puntajes.pack(pady=10)

btn_salir = tk.Button(root, text="Salir", font=("Arial", 12),bg="black", fg="white", command=salir)
btn_salir.pack(pady=10)

# Iniciar el bucle principal de la interfaz
root.mainloop()

