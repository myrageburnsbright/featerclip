"""The main module. The module builds the GUI and application events."""

import tkinter as tk
from tkinter import ttk
import sys
from process import CpuBar
from widget_update import Configure_widjets


class Application(tk.Tk, Configure_widjets):
    """Builds GUI."""

    def __init__(self):
        """Create window."""
        tk.Tk.__init__(self)
        self.attributes('-alpha', 1)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.resizable(False, False)
        self.title('CPU-RAM usage monitor bar')

        self.cpu = CpuBar()
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
        ttk.Label(self, text='Featherclip + mini CPU RAM').pack(fill=tk.X)
        self.bar2 = ttk.LabelFrame(self, text='Manual')
        self.bar2.pack(fill=tk.X)

        self.combo_win = ttk.Combobox(self.bar2,
                                    values=["hide", "don't hide"],
                                    width=9, state='readonly')

        self.combo_win.current(1)
        self.combo_win.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.after(2000, self.auto_hide)

        ttk.Button(self.bar2, text='move',
                    command=self.configure_win).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        ttk.Button(self.bar2, text='Exit', command=self.app_exit).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.bar1 = ttk.LabelFrame(self, text='Clipboard')
        self.bar1.pack(fill=tk.BOTH)
        self.barManager = ttk.LabelFrame(self, text='Manager')
        self.barManager.pack(fill=tk.BOTH)

        self.bar = ttk.LabelFrame(self, text='Power')
        self.bar.pack(fill=tk.BOTH)

        self.bind_class('Tk', '<Enter>', self.enter_mouse)
        self.bind_class('Tk', '<Leave>', self.leave_mouse)
        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)

        self.barDetails = ttk.LabelFrame(self, text='Details')
    
    def auto_hide(self):
        self.geometry(f'{self.winfo_width()}x1')
        self.combo_win.current(0)
    def make_word_list(self):
        """Creation of progress bars and labels to indicate the load of the CPU and RAM."""
        self.cnt = 0
        self.clipborad_count = ttk.Label(self.bar1, text=f'{self.cnt} inputs:', anchor=tk.CENTER)
        self.clipborad_count.pack(fill=tk.X)

        self.buttons = []
        self.inputs = []
        default_cnt=5
        for i in range(default_cnt):
            self.add_new_copy_frame(i)
        add = ttk.Button(self.barManager, text="add from clipboard", command=self.add_from_clipboard)
        add.pack(fill=tk.X)

    def add_new_copy_frame(self, i, text=""):
        fr = ttk.Frame(self.bar1)
        
        entry = ttk.Entry(fr)
        entry.insert(0, text)
        self.inputs.append(entry)
        self.buttons.append(ttk.Button(fr,text="copy", command= lambda x=i: self.change_text(x)))
        self.cnt += 1
        self.clipborad_count.configure(text=f'{self.cnt} inputs')

        self.buttons[i].pack(side="left", expand=True, fill="both")
        self.inputs[i].pack(side="left", expand=True, fill="both")
        fr.pack(fill=tk.X)

    def add_from_clipboard(self):
        text = self.clipboard_get()
        self.add_new_copy_frame(len(self.inputs), text)

    def change_text(self, i):
        self.clipboard_clear()
        self.clipboard_append(self.inputs[i].get())
        self.update()
        # self.inputs[i].delete(0, tk.END)
        # self.inputs[i].insert(0, "ssssss")

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

        self.full = ttk.Button(self, text='full', width=5,
                    command=self.full_details)
        
        self.full.pack(side=tk.RIGHT)

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
        else:
            self.bar_one.pack_forget()
            self.ram_bar_hide.pack_forget()
            self.bar.pack(side=tk.TOP, fill=tk.BOTH)
            self.full.pack_forget()
            self.full.config(text="hide details")
            self.full.pack(side=tk.BOTTOM, fill=tk.BOTH)
            
    def enter_mouse(self, event):
        """Mouse enter event."""
        if self.combo_win.current() == 0 or 1:
            self.geometry('')

    def leave_mouse(self, event):
        """Mouse leave event."""
        if self.combo_win.current() == 0:
            self.geometry(f'{self.winfo_width()}x1')

    def choise_combo(self, event):
        """
        ComboboxSelected event.
        Interruption of the cycle of updating widgets.
        Unbinding events, removing widgets.
        Create small window widgets.
        """
        if self.combo_win.current() == 2:
            self.enter_mouse('')
            self.unbind_class('Tk', '<Enter>')
            self.unbind_class('Tk', '<Leave>')
            self.combo_win.unbind('<<ComboboxSelected>>')
            self.after_cancel(self.wheel)
            self.clear_win()
            self.update()
            self.make_minimal_win()

    def make_full_win(self): 
        """
        Interruption of the cycle of updating widgets.
        Removing small window widgets.
        Renewal of the main GUI.
        """
        self.after_cancel(self.wheel)
        self.clear_win()
        self.update()
        self.run_set_ui()
        self.enter_mouse('')
        self.combo_win.current(1)

    def app_exit(self):
        """Exit."""
        self.destroy()
        sys.exit()


if __name__ == '__main__':
    root = Application()
    root.mainloop()
