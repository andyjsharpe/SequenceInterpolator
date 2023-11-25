import fractions
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from Imports import *

mainApp = None
interpolatables = [Interpolatable("Camera", {'size': 'close-up', 'view': 'from side'}), Interpolatable("Environment", {'Location': 'Outside'})]  # Array of Interpolatable objects being used
selected_interpolatable = interpolatables[0]  # The Interpolatable object that is selected
selected_frame = 0  # The frame that is selected
lastFrame = 10  # The last frame in the timeline
keyframeMultiplier = 1  # The number of renders/keyframe (static values)
transitionMultiplier = 1  # The number of renders in-between keyframes (interlopating values)


def Update_Interpolatable_Name(text):
    return True


def Update_Key_Value(text):
    return True


class ValueInspector(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame = None
        self.update_values()

    def update_values(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self, bg=white)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        # Name
        set_name = self.frame.register(Update_Interpolatable_Name)
        name_var = tk.StringVar(value=selected_interpolatable.name)
        frames_entry = tk.Entry(self.frame, width=6, background=white, foreground=black, textvariable=name_var,
                                validate="key", validatecommand=(set_name, '%P'))
        frames_entry.grid(row=0, column=0, sticky='nsew')
        # Save/Load
        tk.Button(self.frame, text='Save').grid(row=0, column=1, sticky='nsew')
        tk.Button(self.frame, text='Load').grid(row=0, column=2, sticky='nsew')
        # New Key Name
        key_var = tk.StringVar(value="Key Name")
        key_entry = tk.Entry(self.frame, width=2, background=white, foreground=black, textvariable=key_var)
        key_entry.grid(row=1, column=0, sticky='nsew', columnspan=2)
        # New Button
        tk.Button(self.frame, text='Add key').grid(row=1, column=2, sticky='nsew')
        # Key Value Stuff
        key_count = 0
        for key, value in selected_interpolatable.data.items():
            InterpolatableKeyValueFrame(self, key, value).grid(row=2+key_count, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)
            key_count += 1

class InterpolatableKeyValueFrame(tk.Frame):
    def __init__(self, parent, key, value, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text='{}: '.format(key)).grid(row=0, column=0, sticky='nsew')
        set_value = self.register(Update_Interpolatable_Name)
        val_var = tk.StringVar(value=value)
        frames_entry = tk.Entry(self, width=6, background=white, foreground=black, textvariable=val_var,
                                validate="key", validatecommand=(set_value, '%P'))
        frames_entry.grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='Make Interpolated').grid(row=0, column=2, sticky='nsew')
        tk.Button(self, text='X').grid(row=0, column=3, sticky='nsew')


class KeyframeInspector(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame = None
        self.update_values()

    def update_values(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self, bg=white)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        # Name
        tk.Label(self.frame, text='{}: Frame #{}'.format(selected_interpolatable.name, selected_frame)).grid(row=0, column=0, sticky='nsew')
        # Save/Load
        tk.Button(self.frame, text='Save at Frame').grid(row=0, column=1, sticky='nsew')
        tk.Button(self.frame, text='Load to Frame').grid(row=0, column=2, sticky='nsew')
        # On Button
        tk.Checkbutton(self.frame, text='On?').grid(row=1, column=0, sticky='nsew')
        # Key Value Stuff
        key_count = 0
        for key, value in selected_interpolatable.data.items():
            InterpolatableAnimFrame(self, key, value).grid(row=2 + key_count, column=0, padx=10, pady=10,
                                                               sticky="nsew", columnspan=3)
            key_count += 1


class InterpolatableAnimFrame(tk.Frame):
    def __init__(self, parent, key, value, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text='{}: '.format(key)).grid(row=0, column=0, sticky='nsew')
        set_value = self.register(Update_Interpolatable_Name)
        val_var = tk.StringVar(value=value)
        frames_entry = tk.Entry(self, width=6, background=white, foreground=black, textvariable=val_var,
                                validate="key", validatecommand=(set_value, '%P'))
        frames_entry.grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='X').grid(row=0, column=3, sticky='nsew')


class Settings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        # Top Buttons
        tk.Button(self,text='Generate').grid(row=0, column=0, sticky='nsew')
        tk.Button(self, text='Save').grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='Load').grid(row=0, column=2, sticky='nsew')
        # Last Frame
        tk.Label(self, text='Last Frame: ').grid(row=1, column=0, sticky='nsew')
        last_value = self.register(Update_Interpolatable_Name)
        last_var = tk.IntVar(value=lastFrame)
        last_entry = tk.Entry(self, width=6, background=white, foreground=black, textvariable=last_var,
                                validate="key", validatecommand=(last_value, '%P'))
        last_entry.grid(row=1, column=1, sticky='nsew')
        tk.Button(self, text='Confirm').grid(row=1, column=2, sticky='nsew')
        # Keyframe Multiplier
        tk.Label(self, text='Keyframe Multiplier: ').grid(row=2, column=0, sticky='nsew')
        key_mult_value = self.register(Update_Interpolatable_Name)
        key_mult_var = tk.IntVar(value=keyframeMultiplier)
        key_mult_entry = tk.Entry(self, width=6, background=white, foreground=black, textvariable=key_mult_var,
                              validate="key", validatecommand=(key_mult_value, '%P'))
        key_mult_entry.grid(row=2, column=1, sticky='nsew')
        tk.Button(self, text='Confirm').grid(row=2, column=2, sticky='nsew')
        # Transition Multiplier
        tk.Label(self, text='Transition Multiplier: ').grid(row=3, column=0, sticky='nsew')
        interp_mult_value = self.register(Update_Interpolatable_Name)
        interp_mult_var = tk.IntVar(value=transitionMultiplier)
        interp_mult_entry = tk.Entry(self, width=6, background=white, foreground=black, textvariable=interp_mult_var,
                                  validate="key", validatecommand=(interp_mult_value, '%P'))
        interp_mult_entry.grid(row=3, column=1, sticky='nsew')
        tk.Button(self, text='Confirm').grid(row=3, column=2, sticky='nsew')


class Timeline(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)
        self.frame = None
        self.update_timeline()

    def update_timeline(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self, bg=white)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        # New Button
        tk.Button(self.frame, text='Add new interpolatable').grid(row=0, column=0)
        # Top section
        for frame in range(0, lastFrame + 1):
            tk.Label(self.frame, text=str(frame)).grid(row=0, column=frame + 1)
        # Grid section
        interp_count = 0
        for interp in interpolatables:
            interp_frame = tk.Frame(self.frame)
            interp_frame.grid_columnconfigure(0, weight=1)
            interp_frame.grid(row=interp_count + 1, column=0, sticky='nsew')
            tk.Label(interp_frame, text='Interp {}'.format(interp_count)).grid(row=0, column=0, sticky='nsew')
            tk.Button(interp_frame, text='X'.format(interp_count)).grid(row=0, column=1, sticky='nsew')

            for frame in range(0, lastFrame + 1):
                tk.Button(self.frame, text=str(frame)).grid(row=interp_count + 1, column=frame + 1)

            interp_count += 1


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.congigure_gui()

        self.valueInspector = None
        self.keyframeInspector = None
        self.settings = None
        self.timeline = None
        self.create_widgets()

    def congigure_gui(self):
        self.parent.title("Sequence Interpolator")
        self.parent.geometry("1000x500")

    def create_widgets(self):
        # UI Contains Value Inspector, Keyframe inspector, Settings, and Timeline:
        self.valueInspector = ValueInspector(self)
        self.keyframeInspector = KeyframeInspector(self)
        self.settings = Settings(self)
        self.timeline = Timeline(self)


# ...

def create_ui():
    root = tk.Tk()
    global mainApp
    mainApp = MainApplication(root, bg=black)
    mainApp.pack(side="top", fill="both", expand=True)
    root.mainloop()
