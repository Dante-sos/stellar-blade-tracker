import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

CAN_NAMES = [
    "Cryo Original", "Cryo Zero", "Pixie", "Pixie Zero", "Newfoundland Dry", "Newfoundland Dry Zero",
    "Milky Pop", "Milky Pop Zero", "The Machinetta Americano", "The Machinetta Café Latte",
    "The Machinetta Caramel Macchiato", "Cryo Café Original", "Cryo Café Vanilla", "Cryo Café Mocha",
    "The Haven Earl Grey", "The Haven Milk Tea", "The Haven Green Tea", "GrainT Barley",
    "GrainT Oolong", "GrainT Corn", "Nectar Orange", "Nectar Grape", "Nectar Apple", "Nectar Cranberry",
    "Elixir Carrot", "Elixir Green", "Behemoth Red", "Behemoth Green", "Behemoth Black",
    "Liquid Fire", "Liquid Lightning", "Liquid Nuclear", "Potential Blast", "Potential Tempest",
    "Potential Frost", "Dionysus C", "Moonwell", "Starwell", "Mountain Sparkle Mont Blanc",
    "Mountain Sparkle Everest", "Mountain Sparkle Halla", "Cryo the Clear", "Cryo the Malt",
    "Bayern Hefe Weissbier", "Bayern Weissbier Dunkel", "Corsair Lager", "Corsair Ale",
    "Johnson's Highball Lemon", "Johnson's Highball Ginger"
]

CAN_SAVE_FILE = "can_progress.json"
OUTFIT_SAVE_FILE = "skin_progress.json"
FULL_SKIN_LIST_FILE = "full_skin_list.json"

class CanTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stellar Blade Collectibles Tracker")

        self.vars = {}
        self.checkbuttons = []
        self.show_uncollected = tk.BooleanVar()

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.load_progress()

        self.progress_label = tk.Label(self.frame, text="")
        self.progress_label.pack()

        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        for name in CAN_NAMES:
            var = tk.BooleanVar(value=self.progress.get(name, False))
            cb = tk.Checkbutton(self.scrollable_frame, text=name, variable=var, command=self.save_and_update)
            cb.pack(anchor="w")
            self.vars[name] = var
            self.checkbuttons.append(cb)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.filter_cb = tk.Checkbutton(self.frame, text="Show Uncollected Only", variable=self.show_uncollected, command=self.apply_filter)
        self.filter_cb.pack(pady=5)

        self.reset_btn = tk.Button(self.frame, text="Reset All", command=self.reset_all)
        self.reset_btn.pack(pady=5)

        self.skin_tracker_btn = tk.Button(self.frame, text="Open Skin Tracker", command=self.open_skin_tracker)
        self.skin_tracker_btn.pack(pady=10)

        self.update_progress_label()

    def load_progress(self):
        if os.path.exists(CAN_SAVE_FILE):
            with open(CAN_SAVE_FILE, "r") as f:
                self.progress = json.load(f)
        else:
            self.progress = {}

    def save_and_update(self):
        self.progress = {name: var.get() for name, var in self.vars.items()}
        with open(CAN_SAVE_FILE, "w") as f:
            json.dump(self.progress, f, indent=4)
        self.update_progress_label()
        self.apply_filter()

    def update_progress_label(self):
        collected = sum(var.get() for var in self.vars.values())
        self.progress_label.config(text=f"{collected} / {len(CAN_NAMES)} Cans Collected")

    def apply_filter(self):
        for name, cb in zip(CAN_NAMES, self.checkbuttons):
            if self.show_uncollected.get() and self.vars[name].get():
                cb.pack_forget()
            else:
                cb.pack(anchor="w")

    def reset_all(self):
        if messagebox.askyesno("Reset", "Are you sure you want to reset all progress?"):
            for var in self.vars.values():
                var.set(False)
            self.save_and_update()

    def open_skin_tracker(self):
        SkinTrackerWindow()

class SkinTrackerWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Skin Tracker")
        self.window.geometry("500x600")
        self.outfit_vars = {}
        self.outfit_checkbuttons = []
        self.show_uncollected_skins = tk.BooleanVar()

        with open(FULL_SKIN_LIST_FILE, "r") as f:
            self.full_skin_data = json.load(f)

        self.selection_frame = tk.Frame(self.window)
        self.selection_frame.pack(pady=10)

        tk.Label(self.selection_frame, text="Select Playthrough:").grid(row=0, column=0)
        self.pt_var = ttk.Combobox(
            self.selection_frame, 
            values=["NG", "NG+ and PC Patch", "DLC"],  # Added DLC option
            state="readonly"
        )
        self.pt_var.grid(row=0, column=1)
        self.pt_var.current(0)

        tk.Label(self.selection_frame, text="Select Character:").grid(row=1, column=0)
        self.char_var = ttk.Combobox(self.selection_frame, values=["Eve", "Lily", "Adam"], state="readonly")
        self.char_var.grid(row=1, column=1)
        self.char_var.current(0)

        self.load_btn = tk.Button(self.selection_frame, text="Load Skins", command=self.display_skins)
        self.load_btn.grid(row=2, columnspan=2, pady=10)

        # Filter option for skins
        self.skin_filter_frame = tk.Frame(self.window)
        self.skin_filter_frame.pack(pady=5)
        self.filter_skin_cb = tk.Checkbutton(
            self.skin_filter_frame, 
            text="Show Uncollected Only", 
            variable=self.show_uncollected_skins, 
            command=self.apply_skin_filter
        )
        self.filter_skin_cb.pack()

        # Scrollable area for skin list
        self.canvas = tk.Canvas(self.window)
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def display_skins(self):
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.outfit_vars.clear()
        self.outfit_checkbuttons.clear()

        pt = self.pt_var.get()
        char = self.char_var.get()
        
        # Handle different playthrough types
        if pt == "NG+ and PC Patch":
            pt_key = "NG+"
        elif pt == "DLC":
            pt_key = "DLC"
        else:
            pt_key = pt
            
        outfits = self.full_skin_data.get(char, {}).get(pt_key, [])

        if os.path.exists(OUTFIT_SAVE_FILE):
            with open(OUTFIT_SAVE_FILE, "r") as f:
                saved_data = json.load(f)
        else:
            saved_data = {}

        for outfit in outfits:
            key = f"{char}-{pt}-{outfit}"
            var = tk.BooleanVar(value=saved_data.get(key, False))
            cb = tk.Checkbutton(
                self.scrollable_frame, 
                text=outfit, 
                variable=var, 
                command=self.save_outfit_progress
            )
            cb.pack(anchor="w")
            self.outfit_vars[key] = var
            self.outfit_checkbuttons.append(cb)

        # Apply filter if it's active
        if self.show_uncollected_skins.get():
            self.apply_skin_filter()

    # ... rest of the methods remain the same ...

    def apply_skin_filter(self):
        if not hasattr(self, 'outfit_checkbuttons'):
            return
            
        for key, cb in zip(self.outfit_vars.keys(), self.outfit_checkbuttons):
            if self.show_uncollected_skins.get() and self.outfit_vars[key].get():
                cb.pack_forget()
            else:
                cb.pack(anchor="w")

    def save_outfit_progress(self):
        saved_data = {}
        if os.path.exists(OUTFIT_SAVE_FILE):
            with open(OUTFIT_SAVE_FILE, "r") as f:
                saved_data = json.load(f)

        for key, var in self.outfit_vars.items():
            saved_data[key] = var.get()

        with open(OUTFIT_SAVE_FILE, "w") as f:
            json.dump(saved_data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = CanTrackerApp(root)
    root.mainloop()