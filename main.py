import tkinter as tk
from tkinter import ttk
import sys
from process import CpuBar
from widget_update import Configure_widjets
import json
import signal
import os

def get_data_folder():
    appdata = os.getenv('APPDATA')
    if not appdata:
        appdata = os.path.expanduser('~')
    data_folder = os.path.join(appdata, 'FeatherClipBoard')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def get_clipboards_path():
    return os.path.join(get_data_folder(), 'clipboards.json')

class EntryFrame(ttk.Entry):
    def __init__(self, master, text):
        ttk.Frame.__init__(self, master)
        self.master = master
        self.entry = ttk.Entry(self)
        self.entry.insert(0, text)
        del_btn = ttk.Button(self, text="X", width=0, command=self.delete)
        del_btn.pack(side="left")
        self.entry.pack(side="left", expand=True, fill="both")
        self.pack(fill=tk.X, ipadx=0, ipady=0)
        self.root = master.master
        self.entry.bind("<Enter>", self.on_enter)
        self.entry.bind("<Leave>", self.on_leave)
    
    def delete(self):
        self.master.master.del_frame()
        self.destroy()

    def on_enter(self, event):
        self.change_text()
        self.entry.configure(style='ChosenField.TEntry')

    def on_leave(self, event):
        self.entry.configure(style='DefualtFieldColor.TEntry')

    def change_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.entry.get())
        self.update()

def find_adjustment_children_of_type(widget, cls):
    found = []
    for child in widget.winfo_children():
        if isinstance(child, cls):
            found.append(child)
    return found

class Application(tk.Tk, Configure_widjets):

    def __init__(self):
        """Create window."""
        tk.Tk.__init__(self)
        self.attributes('-alpha', 1)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.resizable(False, False)

        self.title(f'CPU-RAM usage monitor bar - pid:{os.getpid()}')

        self.cpu = CpuBar()
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('DefualtFieldColor.TEntry', fieldbackground='white')
        self.style.configure('ChosenField.TEntry', fieldbackground='red')

        self.run_set_ui()

    def run_set_ui(self):
        """Start building widgets."""
        self.set_ui()
        self.make_word_list()
        
        self.make_bar_cpu_usage()
        self.make_minimal_win()
        self.bar.pack_forget()
        self.configure_cpu_bar()

    def set_ui(self):
        """Build basic widgets and events."""
        ttk.Label(self, text=f'Featherclip + mini CPU RAM - pid:{os.getpid()}').pack(fill=tk.X)
        self.bar2 = ttk.Frame(self)
        self.bar2.pack(fill=tk.X, ipady=0, ipadx=10)

        self.combo_win = ttk.Combobox(self.bar2,
                                    values=["hide", "don't hide"],
                                    width=9, state='readonly')

        self.combo_win.current(1)
        self.combo_win.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5,0), pady=(3,0))

        self.after(2000, self.auto_hide)

        ttk.Button(self.bar2, text='move',
                    command=self.configure_win).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5,5), pady=(3,0))

        self.exit =ttk.Button(self.bar2, text='X', command=self.app_exit, width=2)

        self.barManager = ttk.Frame(self)
        self.barManager.pack(fill=tk.BOTH)
        self.bar1 = ttk.LabelFrame(self, text='Clipboards:')
        self.bar1.pack(fill=tk.BOTH)

        self.bar = ttk.LabelFrame(self, text='Usage:')
        #self.bar.config(borderwidth=25, relief="solid")
        self.bar.pack(pady=10, padx=10)

        self.bind_class('Tk', '<Enter>', self.enter_mouse)
        self.bind_class('Tk', '<Leave>', self.leave_mouse)
        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)

        self.barDetails = ttk.LabelFrame(self, text='Details')
    
    def auto_hide(self):
        self.geometry(f'{self.winfo_width()}x1')
        self.combo_win.current(0)
    def make_word_list(self):
        """Creation of progress bars and labels to indicate the load of the CPU and RAM."""
        self.cnt=0
        
        self.clipborad_count = ttk.Label(self.bar1, text=f'{self.cnt} inputs:', anchor=tk.CENTER)
        self.clipborad_count.pack(fill=tk.X)
        path = get_clipboards_path()
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("{}")
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
        for text in history:
            self.add_new_frame(text)
        add = ttk.Button(self.barManager, text="add new from clipboard", command=self.add_from_clipboard)
        add.pack(fill=tk.X, padx=5, pady=5)

    def add_new_frame(self, text=""):
        fr = EntryFrame(self.bar1, text)
        self.cnt += 1
        self.clipborad_count.configure(text=f'{self.cnt} inputs:')
        fr.pack(fill=tk.X)

    def del_frame(self):
        self.cnt -= 1
        self.clipborad_count.configure(text=f'{self.cnt} inputs:')

    def add_from_clipboard(self):
        text = self.clipboard_get()
        self.add_new_frame(text)

    def make_bar_cpu_usage(self):
        """Creation of progress bars and labels to indicate the load of the CPU and RAM."""
        ttk.Label(self.bar,
                text=f'physical cores: {self.cpu.cpu_count}, logical cores: {self.cpu.cpu_count_logical}',
                anchor=tk.CENTER).pack(fill=tk.X)

        self.list_label = []
        self.list_pbar = []

        for i in range(self.cpu.cpu_count_logical):
            self.list_label.append(ttk.Label(self.bar, anchor=tk.CENTER))
            self.list_pbar.append(ttk.Progressbar(self.bar, length=100))
        for i in range(self.cpu.cpu_count_logical):
            self.list_label[i].pack(fill=tk.X)
            self.list_pbar[i].pack(fill=tk.X)

        self.ram_lab = ttk.Label(self.bar, text='', anchor=tk.CENTER)
        self.ram_lab.pack(fill=tk.X)
        self.ram_bar = ttk.Progressbar(self.bar, length=100)
        self.ram_bar.pack(fill=tk.X)

    def make_minimal_win(self):
        """Create widgets for a small window."""
        self.bar_one = ttk.Progressbar(self, length=95)
        self.bar_one.pack(side=tk.LEFT)

        self.ram_bar_hide = ttk.Progressbar(self, length=95)
        self.ram_bar_hide.pack(side=tk.LEFT)

        self.full = tk.Button(self, text='full', width=5, height=1,font=("Arial", 8), pady=0,
                    command=self.full_details)

        self.full.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.update()
        self.configure_minimal_win()

    def full_details(self):
        if self.bar.winfo_ismapped():
            self.bar.pack_forget()
            self.bar_one.pack(side=tk.LEFT)
            self.ram_bar_hide.pack(side=tk.LEFT)
            self.full.pack_forget()
            self.full.config(text="full")
            self.full.pack(side=tk.LEFT)
            self.combo.pack_forget()
            self.save.pack_forget()
            self.combo_chose_color.pack_forget()
            self.top_hide.pack_forget()
            self.save_top.pack_forget()
            self.exit.pack_forget()
        else:
            self.bar_one.pack_forget()
            self.ram_bar_hide.pack_forget()
            self.top_hide = ttk.Button(self.bar2, text='Hide', command=self.full_details, width=4)
            self.top_hide.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=(2,0))
            self.bar.pack(side=tk.TOP, fill=tk.BOTH)
            self.full.pack_forget()
            self.full.config(text="hide details")
            self.full.pack(side=tk.BOTTOM, fill=tk.BOTH)

            self.save_top =ttk.Button(self.bar2, text='S', command=self.save_all, width=2)

            self.save = ttk.Button(self, text='save', command=self.save_all)
            self.save.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=2)

            themes = self.style.theme_names()
            self.combo = ttk.Combobox(self, values=themes, state="readonly")
            self.combo.set(self.style.theme_use())
            
            self.combo.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, pady=(2,0))
            self.combo.bind("<<ComboboxSelected>>", self.change_theme)
            self.save_top.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5,0), pady=(2,0))
            self.exit.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=(2,0))

            color_names = [
    'white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
    'gray', 'orange', 'purple', 'pink', 'brown', 'lightblue', 'lightgreen',
    'navy', 'gold', 'silver', 'maroon', 'lime'
]

            self.combo_chose_color = ttk.Combobox(self, values=color_names, state="readonly")
            self.combo_chose_color.set('red')
            self.combo_chose_color.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, pady=(2,0))
            self.combo_chose_color.bind("<<ComboboxSelected>>", self.change_chose_color)

    def enter_mouse(self, event):
        """Mouse enter event."""
        if self.combo_win.current() == 0 or 1:
            self.geometry('')

    def leave_mouse(self, event):
        """Mouse leave event."""
        if self.combo_win.current() == 0:
            self.geometry(f'{self.winfo_width()}x1')

    def change_chose_color(self, event):
        selected = self.combo_chose_color.get()
        self.style.configure('ChosenField.TEntry', fieldbackground=selected)

    def change_theme(self, event):
        selected = self.combo.get()

        self.style.theme_use(selected)
        self.style.configure('DefualtFieldColor.TEntry', fieldbackground='white')
        self.style.configure('ChosenField.TEntry', fieldbackground='red')

    def choise_combo(self, event):
        if self.combo_win.current() == 2:
            self.enter_mouse('')
            self.unbind_class('Tk', '<Enter>')
            self.unbind_class('Tk', '<Leave>')
            self.combo_win.unbind('<<ComboboxSelected>>')
            self.after_cancel(self.wheel)
            self.clear_win()
            self.update()
            self.make_minimal_win()

    def save_all(self, reserve=False):
        path = get_clipboards_path()
        entries = find_adjustment_children_of_type(self.bar1, EntryFrame)
        history = [entry.entry.get() for entry in entries]
        if not reserve:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f)
    def app_exit(self):
        self.save_all()
        self.destroy()
        sys.exit()

if __name__ == '__main__':
    root = Application()
    root.protocol("WM_DELETE_WINDOW", root.app_exit)
    def handle_sigint(signum, frame):
        root.save_all(reserve=True)
        root.destroy()

    signal.signal(signal.SIGINT, handle_sigint)
    
    root.mainloop()

