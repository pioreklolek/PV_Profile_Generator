import tkinter.ttk
from tkinter import *
from tkinter import messagebox

from engine.graph_generator import GraphGenerator
from engine.simulator import PvSimulator


class GuiApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Generator Profili PV")

        self.p_south_var = StringVar(value="0")
        self.p_ew_var = StringVar(value="0")

        Label(self.root, text='Maxymalna moc P_South [kWp]:').grid(row=0, column=0, padx=10, pady=10, sticky=E)
        Label(self.root, text='Maxymalna moc P_East-West [kWp]:').grid(row=1, column=0, padx=10, pady=10, sticky=E)

        self.e1 = Entry(self.root, textvariable=self.p_south_var)
        self.e2 = Entry(self.root, textvariable=self.p_ew_var)

        self.e1.grid(row=0, column=1, padx=10, pady=10)
        self.e2.grid(row=1, column=1, padx=10, pady=10)

        self.generate_button = Button(self.root, text="GENERUJ", command=self.generate)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.progress = tkinter.ttk.Progressbar(self.root,orient=HORIZONTAL,length=300,mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.p_south_var.trace_add("write", self.validate_inputs)
        self.p_ew_var.trace_add("write", self.validate_inputs)

        self.generate_button.config(state=DISABLED)

    def validate_inputs(self, *args):
        try:
            p_south = self.float_or_zero(self.p_south_var)
            p_ew = self.float_or_zero(self.p_ew_var)
            if p_south > 0 or p_ew > 0:
                self.generate_button.config(state=NORMAL)
            else:
                self.generate_button.config(state=DISABLED)
        except ValueError:
            self.generate_button.config(state=DISABLED)

    def generate(self):
        try:
            p_max_south = self.float_or_zero(self.p_south_var)
            p_max_ew = self.float_or_zero(self.p_ew_var)

            simulator = PvSimulator()
            simulator.sundata.load_data()
            simulator.irradiance.load()

            simulator.generate_profile(p_max_south, p_max_ew,self.update_progress)
            #simulator.generate_daily_kWh()
            #simulator.generate_stats()

            graph = GraphGenerator(p_max_south, p_max_ew)
            #graph.generate_graph()
            #graph.generate_graph_daily_maxkW_png()
            #graph.generate_graph_daily_maxKw_svg()
            graph.generate_15_min_graph_plotly()


            messagebox.showinfo("Sukces", "Wygenerowano dane i wykresy!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił problem:\n{str(e)}")
            self.root.destroy()

    def float_or_zero(self,str):
        value = str.get().strip()
        if value == "":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0

    def update_progress(self, percent):
        self.progress['value'] = percent
        self.root.update_idletasks()

    def startApp(self):
        self.root.mainloop()