import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from datetime import datetime
import glob

# Category: Extensions
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".odt"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json"],
    "Installers": [".exe", ".msi", ".dmg", ".deb"],
    "Texts": [".txt", ".csv", ".log"],
}


def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)
        list_files(folder_selected)

def list_files(path):
    files_listbox.delete(0, tk.END)  # Clear listbox
    try:
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                files_listbox.insert(tk.END, file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list files:\n{e}")
import shutil

def organize_files():
    path = folder_path.get()
    if not path:
        messagebox.showwarning("No Folder", "Please select a folder first.")
        return

    moved_files = {}

    try:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)

            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                moved = False

                for category, extensions in FILE_CATEGORIES.items():
                    if file_ext in extensions:
                        new_path = move_file_to_category(file_path, path, category)
                        moved_files[new_path] = file_path  # log: new → old
                        moved = True
                        break

                if not moved:
                    new_path = move_file_to_category(file_path, path, "Others")
                    moved_files[new_path] = file_path

        # Save undo log
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = f"logs/organizer_log_{timestamp}.json"
        log_data = {
            "folder": path,
            "moved_files": moved_files,
        }
        with open(log_file, "w") as f:
            json.dump(log_data, f)

        messagebox.showinfo("Success", "Files have been organized!")
        list_files(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to organize files:\n{e}")

    path = folder_path.get()
    if not path:
        messagebox.showwarning("No Folder", "Please select a folder first.")
        return

    try:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)

            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                moved = False

                for category, extensions in FILE_CATEGORIES.items():
                    if file_ext in extensions:
                        move_file_to_category(file_path, path, category)
                        moved = True
                        break

                if not moved:
                    move_file_to_category(file_path, path, "Others")

        messagebox.showinfo("Success", "Files have been organized!")
        list_files(path)  # Refresh the file list
    except Exception as e:
        messagebox.showerror("Error", f"Failed to organize files:\n{e}")

def move_file_to_category(file_path, base_path, category):
    category_path = os.path.join(base_path, category)
    os.makedirs(category_path, exist_ok=True)
    new_path = os.path.join(category_path, os.path.basename(file_path))
    shutil.move(file_path, new_path)
    return new_path

# import glob

def undo_organize():
    log_files = sorted(glob.glob("logs/organizer_log_*.json"), reverse=True)
    
    if not log_files:
        messagebox.showinfo("Nothing to Undo", "No organizer logs found.")
        return

    latest_log = log_files[0]

    try:
        with open(latest_log, "r") as f:
            moved_files = json.load(f)

        for src, dest in moved_files.items():
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(src, dest)

        os.remove(latest_log)
        messagebox.showinfo("Undo Complete", "Files moved back successfully.")
        list_files(folder_path.get())

    except Exception as e:
        messagebox.showerror("Error", f"Undo failed:\n{e}")
def undo_from_selected_log():
    log_files = sorted(glob.glob("logs/organizer_log_*.json"), reverse=True)

    if not log_files:
        messagebox.showinfo("No Logs", "No organizer logs found.")
        return

    # Build display labels
    display_labels = []
    file_map = {}  # maps label to actual filename

    for file in log_files:
        try:
            with open(file, "r") as f:
                log_data = json.load(f)
                folder = log_data.get("folder", "Unknown Folder")
                timestamp_str = os.path.basename(file).replace("organizer_log_", "").replace(".json", "").replace("_", " ")
                label = f"{os.path.basename(folder)} — {timestamp_str}"
                display_labels.append(label)
                file_map[label] = file
        except Exception:
            continue  # skip unreadable logs

    # UI
    window = tk.Toplevel(root)
    window.title("Undo from Log |mikeCodeCraft|")
    window.geometry("500x180")

    tk.Label(window, text="Select a log to undo:").pack(pady=10)

    selected_label = tk.StringVar(value=display_labels[0])
    dropdown = ttk.Combobox(window, values=display_labels, textvariable=selected_label, state="readonly", width=60)
    dropdown.pack(pady=5)

    def perform_undo():
        selected = selected_label.get()
        log_file = file_map.get(selected)
        if not log_file:
            messagebox.showerror("Error", "Log file not found.")
            return

        try:
            with open(log_file, "r") as f:
                log_data = json.load(f)
                moved_files = log_data.get("moved_files", {})

            for src, dest in moved_files.items():
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.move(src, dest)

            os.remove(log_file)
            messagebox.showinfo("Undo Complete", f"Files from {selected} restored.")
            list_files(folder_path.get())
            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Undo failed:\n{e}")

    tk.Button(window, text="Undo", command=perform_undo).pack(pady=10)


def view_log_history():
    log_files = sorted(glob.glob("logs/organizer_log_*.json"), reverse=True)

    if not log_files:
        messagebox.showinfo("Log History", "No logs found.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Log History |mikeCodeCraft|")
    history_window.geometry("700x400")

    # --- Title ---
    tk.Label(history_window, text="📜 Organizer Log History |mikeCodeCraft|", font=("Arial", 16)).pack(pady=5)

    frame = tk.Frame(history_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # --- Log List ---
    log_listbox = tk.Listbox(frame, width=40)
    log_listbox.pack(side=tk.LEFT, fill=tk.Y)

    # --- Scrollbar ---
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=log_listbox.yview)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    log_listbox.config(yscrollcommand=scrollbar.set)

    # --- Preview Area ---
    preview_box = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
    preview_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    # --- Log Metadata ---
    display_labels = []
    file_map = {}

    for file in log_files:
        try:
            with open(file, "r") as f:
                data = json.load(f)
                folder = os.path.basename(data.get("folder", "Unknown"))
                moved = data.get("moved_files", {})
                timestamp = os.path.basename(file).replace("organizer_log_", "").replace(".json", "").replace("_", " ")
                label = f"{folder} — {timestamp} — {len(moved)} file{'s' if len(moved) != 1 else ''}"
                display_labels.append(label)
                file_map[label] = file
        except:
            continue

    for label in display_labels:
        log_listbox.insert(tk.END, label)

    # --- On Select Show Preview ---
    def show_preview(event):
        selection = log_listbox.curselection()
        if not selection:
            return
        selected_label = log_listbox.get(selection[0])
        filepath = file_map[selected_label]
    
        preview_box.config(state=tk.NORMAL)
        preview_box.delete(1.0, tk.END)
    
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                moved_files = data.get("moved_files", {})
                for src, dest in moved_files.items():
                    filename = os.path.basename(src)
                    folder_name = os.path.basename(os.path.dirname(dest))
                    preview_box.insert(tk.END, f"🔹 {filename} → {folder_name}\n")
        except Exception as e:
            preview_box.insert(tk.END, f"⚠️ Error loading preview: {e}")
        
        preview_box.config(state=tk.DISABLED)
    

    log_listbox.bind("<<ListboxSelect>>", show_preview)



# --- GUI Setup ---
root = tk.Tk()
root.title("File Organizer |mikeCodeCraft|")
root.geometry("500x400")

folder_path = tk.StringVar()

frame = tk.Frame(root)
frame.pack(pady=20)

tk.Label(frame, text="Selected Folder:").pack()
tk.Entry(frame, textvariable=folder_path, width=60).pack(pady=5)
tk.Button(frame, text="Browse Folder", command=select_folder).pack(pady=5)
tk.Button(frame, text="Organize Files", command=organize_files).pack(pady=5)
tk.Button(frame, text="Undo Last Organize", command=undo_organize).pack(pady=5)
tk.Button(frame, text="Undo from Log...", command=undo_from_selected_log).pack(pady=5)
tk.Button(frame, text="View Log History", command=view_log_history).pack(pady=5)


tk.Label(root, text="Files in Folder:").pack()
files_listbox = tk.Listbox(root, width=60, height=15)
files_listbox.pack(pady=10)

root.mainloop()
