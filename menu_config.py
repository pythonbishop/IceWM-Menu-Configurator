import os
import tkinter
import tkinter.ttk
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox

apps_dir = "./applications"
menu_path = "./menu"
#apps_dir = "/usr/share/applications"
#menu_dir = "~/.icewm/menu"
encode = "utf-8"

def load_apps_list(dir):
    desktop_files = []
    apps = {}

    for f_name in os.listdir(dir):
        if ".desktop" in f_name:
            desktop_files.append(f_name)

    for f_name in desktop_files:
        fpath = dir+"/"+f_name
        name = None
        icon = None
        exec = None
        in_desk_entry = False
        with open(fpath, encoding=encode, errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                if line == "[Desktop Entry]":
                    in_desk_entry = True
                if in_desk_entry and line.startswith("["):
                    lines = lines[:lines.index(line)]

            for line in lines:
                if line.startswith("Name="):
                    name = line[5:].rstrip("\n")
                if line.startswith("Icon="):
                    icon = line[5:].rstrip("\n")
                if line.startswith("Exec="):
                    exec = line[5:].rstrip("\n")
        if not icon:
            icon = name

        apps[name] = "prog" + """ "{n}" """.format(n = name) + icon + " " + exec + "\n"
    return apps

def load_from_menu_file(file): pass
    # todo
    # this will suck

class Application:
    def __init__(self) -> None:
        self.apps_by_iid = {}
        self.apps_by_name = {}
        self.apps_dir = apps_dir
        self.tk = tkinter.Tk()
        self.tk.resizable(0,0)
        self.tk.title("IceWM Menu Configurator")

        self.tk.option_add('*tearOff', False)
        self.menu_bar = tkinter.Menu(self.tk)
        self.tk["menu"] = self.menu_bar
        self.options_menu = tkinter.Menu(self.menu_bar)
        self.menu_bar.add_command(label="About", command=self.about_dialog)
        self.menu_bar.add_command(label="Save As", command=self.saveas_dialog)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)
        self.menu_bar.add_command(label="Help", command=self.help_dialog)

        self.options_menu.add_command(label="Load File", command=self.loadfile_dialog)
        self.options_menu.add_command(label="Change .desktop Directory", command=self.change_apps_dir)

        self.output = ""
        self.parsed_in_folder = 0

        self.menu_tree = tkinter.ttk.Treeview(self.tk, height=20)
        self.menu_tree.tag_configure("folder", font=("Arial", "10", "bold"))
        self.menu_tree.tag_configure("file", font=("Arial", "10", "normal"))
        self.menu_tree.grid(column=0, row=1)

        self.line_label = tkinter.Label(self.tk, text="_____________________________", wraplength=200, justify="left")
        self.line_label.grid(row=0, column=0)

        self.apps_label = tkinter.Label(self.tk, text="_____________________________", wraplength=200, justify="left")
        self.apps_label.grid(row=0, column=1)

        self.refresh_button = tkinter.Button(self.tk, text="refresh list", command=self.refresh_list)
        self.refresh_button.grid(column=1, row=2)

        self.button_frame = tkinter.Frame(self.tk)
        self.button_frame.grid(column=0, row=2)

        self.folder_button = tkinter.Button(self.button_frame, text="add folder", command=self.add_folder)
        self.delete_button = tkinter.Button(self.button_frame, text="delete", command=self.delete_selected)
        self.app_button = tkinter.Button(self.button_frame, text="add app", command=self.add_app)
        self.rename_button = tkinter.Button(self.button_frame, text="rename", command=self.rename_app)

        self.folder_button.grid(column=0, row=0)
        self.app_button.grid(column=1, row=0)
        self.delete_button.grid(column=2, row=0)
        self.rename_button.grid(column=3, row=0)

        self.applications_listbox = tkinter.ttk.Treeview(self.tk, height=20)
        self.applications_listbox.tag_configure("file", font=("Arial", "10", "normal"))
        self.applications_listbox.grid(column=1, row=1)

        self.tk.bind_all("<Delete>", self.delete_selected_keybind)
        self.tk.bind_all("<Return>", self.add_app_selected_keybind)
        self.tk.bind("<Control-Up>", self.move_item_up)
        self.tk.bind("<Control-Down>", self.move_item_down)
        self.tk.bind("<Right>", self.shift_list_focus)
        self.tk.bind("<Left>", self.shift_list_focus)
        self.menu_tree.bind("<<TreeviewSelect>>", self.update_line_label)
        self.applications_listbox.bind("<<TreeviewSelect>>", self.update_apps_label)

        self.refresh_list()

    def update_line_label(self, event):
        focused = self.menu_tree.focus()
        name = self.menu_tree.item(focused, "text")
        if self.menu_tree.tag_has("file", focused):
            parts = self.apps_by_iid[focused].split("\"")
            text = parts[0] + f"\"{name}\"" + parts[2]
        else:
            text = "menu " + f"\"{name}\"" + " folder {\n"
        
        self.line_label.configure(text=text)

    def update_apps_label(self, event):
        focused = self.applications_listbox.focus()
        name = self.applications_listbox.item(focused, "text")
        
        self.apps_label.configure(text=self.apps_by_name[name])
        
    def move_item_up(self, event):
        iid = self.menu_tree.focus()
        new_index = self.menu_tree.index(iid) - 1
        self.menu_tree.move(iid, new_index)

    def move_item_down(self, event):
        iid = self.menu_tree.focus()
        new_index = self.menu_tree.index(iid) + 1
        self.menu_tree.move(iid, new_index)

    def rename_app(self):
        iid = self.menu_tree.focus()
        new_name = tkinter.simpledialog.askstring("Rename App", "Name: ")
        if new_name:
            self.menu_tree.item(iid, text=new_name)
    
    def shift_list_focus(self, event):
        if self.tk.focus_get() == self.applications_listbox:
            self.menu_tree.focus_set()
            children = self.menu_tree.get_children()
            if len(children) > 0:
                self.menu_tree.focus(children[0])
        else:
            self.applications_listbox.focus_set()
            children = self.applications_listbox.get_children()
            if len(children) > 0:
                self.applications_listbox.focus(children[0])

    def add_app_selected_keybind(self, event):
        self.add_app()

    def delete_selected_keybind(self, event):
        self.delete_selected()

    def refresh_list(self):
        apps = load_apps_list(self.apps_dir)
        self.apps_by_name = apps
        for item in self.applications_listbox.get_children():
            self.applications_listbox.delete(item)
        for name in apps.keys():
            self.applications_listbox.insert("", 0, text=name, tags="file")
    
    def about_dialog(self):
        top = tkinter.Toplevel(self.tk, width=100, height=50)
        top.resizable(0, 0)
        top.title("About")
        tkinter.Label(top, text="created by pythonbishop").grid(column=0, row=0)
        tkinter.Label(top, text="released 12/2/2022 (no versioning system yet)").grid(column=0, row=1)

    def help_dialog(self):
        top = tkinter.Toplevel(self.tk, width=100, height=50)
        top.resizable(0, 0)
        top.title("Help")
        tkinter.Label(top, text="WIP").grid(column=0, row=0)
        tkinter.Label(top, text="mash keys till you find what the keybinds are").grid(column=0, row=1)
    
    def save_failed(self):
        top = tkinter.Toplevel(self.tk, width=100, height=50)
        top.resizable(0, 0)
        top.title("Save Failed")
        tkinter.Label(top, text="\t\t\toops  :(\t\t\t").grid(column=0, row=0)
    
    def save_success(self):
        top = tkinter.Toplevel(self.tk, width=100, height=50)
        top.resizable(0, 0)
        top.title("")
        tkinter.Label(top, text="File Saved").grid(column=0, row=0)
        tkinter.Label(top, text="\t\t\t:)\t\t\t").grid(column=0, row=1)

    def loadfile_dialog(self):
        menu_file = tkinter.filedialog.askopenfile("r")
        if menu_file:
            menu_file.close()
    
    def saveas_dialog(self):
        try:
            self.output = ""
            self.parse_tree("")
            filepath = tkinter.filedialog.asksaveasfilename()
            with open(filepath, "w") as f:
                f.write(self.output)
            self.save_success()
        except:
            self.save_failed()
        
    def change_apps_dir(self):
        self.apps_dir = tkinter.filedialog.askdirectory()

    def parse_tree(self, item):
        root_children = self.menu_tree.get_children(item)

        for child in root_children:
            name = self.menu_tree.item(child, "text")
            if self.menu_tree.tag_has("file", child):
                parts = self.apps_by_iid[child].split("\"")
                self.output += parts[0] + f"\"{name}\"" + parts[2]
            else:
                self.parsed_in_folder += 1
                self.output += "menu " + f"\"{name}\"" + " folder {\n"
                self.parse_tree(child)

        if self.parsed_in_folder > 0:
            self.parsed_in_folder -= 1
            self.output += "}\n"

    def add_folder(self):
        focused = self.menu_tree.focus()

        name = tkinter.simpledialog.askstring(None, "Enter a folder name")

        if not self.menu_tree.tag_has("file", focused):
            iid = self.menu_tree.insert(focused, 0, text=name, tags="folder")
        else:
            iid = self.menu_tree.insert(self.menu_tree.parent(focused), 0, text=name, tags="folder")

        self.apps_by_iid[iid] = "menu " + """ "{n}" """.format(n = name) + " folder {\n"

    def add_app(self):
        iid = self.applications_listbox.focus()
        focused = self.menu_tree.focus()
        if not self.menu_tree.tag_has("file", focused):
            name = self.applications_listbox.item(iid, "text")
            iid = self.menu_tree.insert(focused, 0, text=name, tags="file")
        else:
            name = self.applications_listbox.item(iid, "text")
            iid = self.menu_tree.insert(self.menu_tree.parent(focused), 0, text=name, tags="file")
        
        self.apps_by_iid[iid] = self.apps_by_name[name]

    def delete_selected(self):
        focus = self.menu_tree.focus()
        if focus != "":
            self.menu_tree.delete(focus)
        children = self.menu_tree.get_children()
        if len(children):
            self.menu_tree.focus(children[0])
        
        del self.apps_by_iid[focus]

try:
    gui = Application()
    gui.tk.mainloop()
except BaseException as e:
    print(e)