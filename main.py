import json
import time
import websocket
import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox

# Global variables
POS_X = 0
POS_Y = 0
file_path = ""
lines = []
trame = 1
x = 0
y = 0
is_paused = False
is_running = False
ws = None


def send_data():
    global trame, x, y, is_running, is_paused, ws

    while is_running:
        if is_paused:
            time.sleep(0.1)
            continue

        # Position data
        position = json.dumps({
            "kind": "position",
            "request_id": trame,
            "position": {"x": POS_X // 16, "y": POS_Y // 8}
        })
        ws.send(position)
        trame += 1

        # Cursor data
        cursor = json.dumps({
            "kind": "cursor",
            "request_id": trame,
            "positions": [{
                "tileX": POS_X // 16,
                "tileY": POS_Y // 8,
                "charX": POS_X % 16,
                "charY": POS_Y % 8
            }]
        })
        console_log(cursor)
        ws.send(cursor)
        trame += 1

        # Write data
        write_object = {"kind": "write", "request_id": trame, "edits": []}
        nbr = 1
        while nbr < 201 and is_running:
            if is_paused:
                time.sleep(0.1)
                continue

            pos_x = POS_X + x
            pos_y = POS_Y + y
            write_object["edits"].append([
                pos_y // 8, pos_x // 16, pos_y % 8, pos_x % 16, int(time.time() * 1000),
                lines[y][x], nbr
            ])
            nbr += 1

            x += 1
            if x >= len(lines[y]):
                y += 1
                x = 0
                if y >= len(lines):
                    y = 0
        write = json.dumps(write_object)
        ws.send(write)
        trame += 1
        


def on_open(websocket):
    console_log('WebSocket connection established.')
    threading.Thread(target=send_data, daemon=True).start()


def on_error(websocket, error):
    pass


def on_close(websocket, close_status_code, close_msg):
    time.sleep(0.1)  # Add a slight delay to avoid overwhelming the server
    create_websocket()


def create_websocket():
    global ws
    ws = websocket.WebSocketApp(
        'wss://www.yourworldoftext.com/ws/',
        on_open=on_open,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()


def start_websocket():
    global POS_X, POS_Y, lines, is_running

    try:
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            image = f.read()
        lines = [line for line in image.split("\n") if line.strip()]

        POS_X = int(entry_x.get())
        POS_Y = int(entry_y.get())

        is_running = True
        threading.Thread(target=create_websocket, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def pause_bot():
    global is_paused
    is_paused = not is_paused
    button_pause.configure(text="Resume" if is_paused else "Pause")
    console_log("Bot paused." if is_paused else "Bot resumed.")


def stop_bot():
    global is_running, ws
    is_running = False
    if ws:
        ws.close()
    console_log("Bot stopped.")


def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        file_entry.delete(0, ctk.END)
        file_entry.insert(0, file_path)


def console_log(message):
    console.insert(ctk.END, message + "\n")
    console.see(ctk.END)

# Fonction pour afficher les crédits
def show_credits():
    messagebox.showinfo(
        "Crédits",
        "Développeurs :\n- Codealuxz \n- Guerric \n- 𝑅𝑒𝒹𝓌𝒶𝓁𝓁𝓎 \n\nTOW TEAM © !"
    )



# CustomTkinter Configuration
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("blue")  # Blue theme

app = ctk.CTk()
app.title("ASCII Art WebSocket Bot")
app.geometry("800x600")
app.resizable(False, False)

# Title
title_label = ctk.CTkLabel(app, text="ASCII Art WebSocket Bot", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

title_label = ctk.CTkLabel(app, text="Tow Team Bot\ndsc.gg/towteam", font=("Arial", 20), text_color="white")
title_label.pack(side="bottom", pady=20)
# File selection
file_frame = ctk.CTkFrame(app)
file_frame.pack(pady=10, fill="x", padx=20)

file_entry = ctk.CTkEntry(file_frame, placeholder_text="Select a file")
file_entry.pack(side="left", expand=True, fill="x", padx=5)
file_button = ctk.CTkButton(file_frame, text="Browse", command=select_file)
file_button.pack(side="right", padx=5)

# Coordinates
coord_frame = ctk.CTkFrame(app)
coord_frame.pack(pady=10)

label_x = ctk.CTkLabel(coord_frame, text="X Coordinate:", font=("Arial", 12))
label_x.grid(row=0, column=0, padx=10)

entry_x = ctk.CTkEntry(coord_frame, width=100, placeholder_text="X Coordinate")
entry_x.insert(0, str(POS_X))
entry_x.grid(row=0, column=1, padx=10)

label_y = ctk.CTkLabel(coord_frame, text="Y Coordinate:", font=("Arial", 12))
label_y.grid(row=0, column=2, padx=10)

entry_y = ctk.CTkEntry(coord_frame, width=100, placeholder_text="Y Coordinate")
entry_y.insert(0, str(POS_Y))
entry_y.grid(row=0, column=3, padx=10)

# Start button (larger and on its own row)
button_start = ctk.CTkButton(app, text="Start", command=start_websocket, fg_color="green", font=("Arial", 18))
button_start.pack(pady=20, padx=10)

# Pause and Stop buttons
button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=10)

button_pause = ctk.CTkButton(button_frame, text="Pause", command=pause_bot, fg_color="orange", width=120)
button_pause.grid(row=0, column=0, padx=10)

button_stop = ctk.CTkButton(button_frame, text="Stop", command=stop_bot, fg_color="red", width=120)
button_stop.grid(row=0, column=1, padx=10)

# Encapsuler la console et le bouton "Clear Console" dans un cadre
console_frame = ctk.CTkFrame(app)
console_frame.pack(pady=10, fill="both", expand=True)


# Ajouter un bouton "Crédits" en bas de l'application
credits_button = ctk.CTkButton(
    app,
    text="Crédits",
    font=("Arial", 12),
    command=show_credits
)
credits_button.pack(side="bottom", pady=10)

# Bouton pour effacer la console, aligné en haut à gauche
clear_button = ctk.CTkButton(
    console_frame,
    text="Clear Console",
    font=("Arial", 12),
    width=120,
    fg_color="red",
    command=lambda: console.delete("1.0", ctk.END)
)
clear_button.pack(anchor="nw", padx=5, pady=5)

# Console pour les messages
console = ctk.CTkTextbox(
    console_frame,
    wrap="word",
    width=70,
    height=10,
    font=("Courier", 12),
    fg_color="#1e1e1e",
    text_color="green"
)
console.pack(fill="both", expand=True, padx=5, pady=(0, 5))


# Run the application
app.mainloop()
