import fractions
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from Imports import *
import pickle

mainApp = None
subject = Interpolatable("Subject", {'Example category': 'Example Value'})
cam = Interpolatable("Camera", {'size': '', 'view': ''})
enviro = Interpolatable("Environment", {'Location': ''})
interpolatables = [subject, cam, enviro]  # Array of Interpolatable objects being used
selected_interpolatable = interpolatables[0]  # The Interpolatable object that is selected
selected_frame = 0  # The frame that is selected
lastFrame = 10  # The last frame in the timeline
keyframeMultiplier = 1  # The number of renders/keyframe (static values)
transitionMultiplier = 0  # The number of renders in-between keyframes (interlopating values)
positive_format = '--prompt {}'
negative_format = '--negative_prompt {}'


def Under_100(text: str):
    try:
        num = str(text)
        return num < 100 and num >= 0
    except:
        return True


def add_key(variable, negative):
    name = variable.get()
    if negative.get():
        name = "(Negative) " + name
    selected_interpolatable.data[name] = ''
    # Reload UI
    mainApp.reload_all()


def delete_key(key):
    selected_interpolatable.remove_key(key)
    # Reload UI
    mainApp.reload_all()


class ValueInspector(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.frame = None
        self.items = []
        self.update_values()

    def update_values(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self, bg=navy)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        if selected_interpolatable is None:
            return
        # Name
        name_var = tk.StringVar(value=selected_interpolatable.name)
        frames_entry = tk.Entry(self.frame, width=int(len(selected_interpolatable.name)*1.1), background=white, foreground=black, textvariable=name_var)
        frames_entry.grid(row=0, column=0, sticky='nsew')
        # Save/Load
        tk.Button(self.frame, text='Save As', command=lambda:save_interpolatable(name_var), bg=grey, fg=white).grid(row=0, column=2, sticky='nsew')
        tk.Button(self.frame, text='Load', command=lambda:load_interpolatable(), bg=grey, fg=white).grid(row=0, column=3, sticky='nsew')
        # New Key Name
        key_var = tk.StringVar(value="Category Name")
        key_entry = tk.Entry(self.frame, width=int(len(key_var.get())*1.1), background=white, foreground=black, textvariable=key_var)
        key_entry.grid(row=1, column=0, sticky='nsew')
        # Negative button
        negative = tk.BooleanVar(value=False)
        tk.Checkbutton(self.frame, text='Negative?', variable=negative, bg=grey, fg=white).grid(row=1, column=1, sticky='nsew')
        # New Button
        tk.Button(self.frame, text='Add Category', command=lambda: add_key(key_var, negative), bg=grey, fg=white).grid(row=1, column=2, sticky='nsew')
        # Apply all
        tk.Button(self.frame, text='Apply All', command=lambda: apply_all_values(self.items), bg=grey, fg=white).grid(row=1, column=3,
                                                                                                    sticky='nsew')
        # Change Name
        tk.Button(self.frame, text='Change Name', command=lambda: change_name(name_var), bg=grey, fg=white).grid(row=0, column=1,
                                                                                                   sticky='nsew')
        item_frame = Scrollable(self.frame, 400, 400)
        item_frame.grid(row=2, column=0, sticky="nsew", columnspan=4)
        # Key Value Stuff
        key_count = 0
        for key, value in selected_interpolatable.data.items():
            val = InterpolatableKeyValueFrame(item_frame.interior, key, value, bg=navy)
            self.items.append(val)
            val.grid(row=key_count, column=0, padx=10, pady=10, sticky="nsew")
            key_count += 1


def change_name(val):
    selected_interpolatable.name = val.get()
    mainApp.reload_all()


def apply_all_values(items):
    for item in items:
        selected_interpolatable.data[item.key] = item.val_var.get()
    mainApp.reload_all()


def save_interpolatable(var):
    selected_interpolatable.save_data(var.get())


def load_interpolatable():
    selected_interpolatable.load_data()
    mainApp.reload_all()


class InterpolatableKeyValueFrame(tk.Frame):
    def __init__(self, parent, key, value, *args, **kwargs):
        self.key = key
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text='{}: '.format(key), bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=0, column=0, sticky='nsew')
        self.val_var = tk.StringVar(value=value)
        frames_entry = tk.Entry(self, width=int(len(self.val_var.get())*1.1), background=white, foreground=black, textvariable=self.val_var)
        frames_entry.grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='Apply', command=lambda: apply_value(key, self.val_var), bg=grey, fg=white).grid(row=0, column=3, sticky='nsew')
        tk.Button(self, text='X', command=lambda: delete_key(key), bg=grey, fg=white).grid(row=0, column=4, sticky='nsew')


def apply_value(key, var):
    selected_interpolatable.data[key] = var.get()
    mainApp.reload_all()


class KeyframeInspector(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.frame = None
        self.items = []
        self.update_values()

    def update_values(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self, bg=navy)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        if selected_interpolatable is None:
            return
        # Name
        tk.Label(self.frame, text='{}: Frame {}'.format(selected_interpolatable.name, selected_frame), bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=0, column=0, sticky='nsew')
        # Save/Load
        tk.Button(self.frame, text='Save As', command=lambda:save_transition(), bg=grey, fg=white).grid(row=0, column=1, sticky='nsew')
        tk.Button(self.frame, text='Load to Frame', command=lambda:load_transition(), bg=grey, fg=white).grid(row=0, column=2, sticky='nsew')
        # On Button
        use_button(self.frame, selected_interpolatable, selected_frame, bg=grey, fg=white).grid(row=1, column=0, sticky='nsew')
        item_frame = Scrollable(self.frame, 400, 400)
        item_frame.grid(row=2, column=0, sticky="nsew", columnspan=4)
        # Apply changed
        tk.Button(self.frame, text='Apply Changed', command=lambda: apply_changed_transitions(self.items), bg=grey, fg=white).grid(row=1, column=1,
                                                                                                   sticky='nsew')
        # Apply all
        tk.Button(self.frame, text='Apply All', command=lambda: apply_all_transitions(self.items), bg=grey, fg=white).grid(row=1, column=2,
                                                                                                   sticky='nsew')
        # Apply to subject
        tk.Button(self.frame, text='Apply to Subject', command=lambda: apply_all_transitions_to_subject(self.items), bg=grey, fg=white).grid(row=1, column=3,
                                                                                                        sticky='nsew')
        # Reset
        tk.Button(self.frame, text='Reset',
                  command=lambda: reset_transitions(), bg=grey, fg=white).grid(row=0, column=3,
                                                                                     sticky='nsew')
        # Key Value Stuff
        key_count = 0
        for key, value in selected_interpolatable.data.items():
            item = InterpolatableAnimFrame(item_frame.interior, key, selected_interpolatable.get_value_on_frame(selected_frame, key), bg=navy)
            self.items.append(item)
            item.grid(row=key_count, column=0, padx=2, pady=2, sticky="nsew")
            key_count += 1

def reset_transitions():
    selected_interpolatable.transitions.pop(selected_frame)
    if selected_frame == 0:
        selected_interpolatable.add_transition(selected_frame, 'On', True)
    mainApp.reload_all()


def apply_all_transitions_to_subject(items):
    for item in items:
        selected_interpolatable.data[item.key] = item.val_var.get()
    mainApp.reload_all()


def apply_all_transitions(items):
    for item in items:
        selected_interpolatable.add_transition(selected_frame, item.key, item.val_var.get())
    mainApp.reload_all()


def apply_changed_transitions(items):
    for item in items:
        val = item.val_var.get()
        if selected_interpolatable.get_value_on_frame(selected_frame, item.key) != val:
            selected_interpolatable.add_transition(selected_frame, item.key, val)
    mainApp.reload_all()


def save_transition():
    selected_interpolatable.save_frame_data(selected_frame)


def load_transition():
    selected_interpolatable.load_frame_data(selected_frame)
    mainApp.reload_all()


class use_button(tk.Checkbutton):
    def __init__(self, parent, interp, frame, *args, **kwargs):
        is_on = interp.get_on(frame)
        checked = tk.BooleanVar(value=is_on)
        tk.Checkbutton.__init__(self, parent, text='Use Subject?', variable=checked,
                                command=lambda: turn_frame_off(interp, frame, checked.get()), *args, **kwargs)


def turn_frame_off(interp, frame, value):
    if frame in interp.transitions:
        interp.transitions[frame]['On'] = value
    else:
        interp.transitions[frame] = {'On': value}
    mainApp.reload_timeline()
    mainApp.reload_keyframe_inspector()


class InterpolatableAnimFrame(tk.Frame):
    def __init__(self, parent, key, value, *args, **kwargs):
        self.key = key
        tk.Frame.__init__(self, parent, *args, **kwargs)
        color = get_key_time_color(selected_interpolatable, selected_frame, key, blue, orange)
        if color is not None:
            color = add_colors_and_adjust_brightness(color, "#222222", 0.8, "#000000")
            self.configure(highlightthickness=8,highlightbackground=color)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text='{}: '.format(key), bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=0, column=0, sticky='nsew')
        self.val_var = tk.StringVar(value=value)
        frames_entry = tk.Entry(self, width=int(len(self.val_var.get())*1.1), background=white, foreground=black, textvariable=self.val_var)
        frames_entry.grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='Apply', command=lambda:apply_keyframe(key, self.val_var), bg=grey, fg=white).grid(row=0, column=3, sticky='nsew')
        tk.Button(self, text='X', command=lambda: clear_transition_from_frame(key), bg=grey, fg=white).grid(row=0, column=4, sticky='nsew')


def clear_transition_from_frame(key):
    if selected_frame in selected_interpolatable.transitions and key in selected_interpolatable.transitions[selected_frame]:
        selected_interpolatable.transitions[selected_frame].pop(key)
        mainApp.reload_all()


def apply_keyframe(key, var):
    selected_interpolatable.add_transition(selected_frame, key, var.get())
    mainApp.reload_keyframe_inspector()


class Settings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg=navy, *args, **kwargs)
        # self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        # Top Buttons
        tk.Button(self,text='Generate', command=lambda: generate(), bg=grey, fg=white).grid(row=0, column=0, sticky='nsew')
        tk.Button(self, text='Save', command=lambda: save_sequence(), bg=grey, fg=white).grid(row=0, column=1, sticky='nsew')
        tk.Button(self, text='Load', command=lambda: load_sequence(), bg=grey, fg=white).grid(row=0, column=2, sticky='nsew')
        # Last Frame
        tk.Label(self, text='Last Frame: ', bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=1, column=0, sticky='nsew')
        last_var = tk.IntVar(value=lastFrame)
        last_value = self.register(Under_100)
        last_entry = tk.Entry(self, width=int(len(str(lastFrame))*1.1), background=white, foreground=black, textvariable=last_var,
                                validate="key", validatecommand=(last_value, '%d'))
        last_entry.grid(row=1, column=1, sticky='nsew')
        tk.Button(self, text='Apply', command=lambda:apply_last_frame(last_var), bg=grey, fg=white).grid(row=1, column=2, sticky='nsew')
        # Keyframe Multiplier
        tk.Label(self, text='Keyframe Multiplier: ', bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=2, column=0, sticky='nsew')
        key_mult_value = self.register(Under_100)
        key_mult_var = tk.IntVar(value=keyframeMultiplier)
        key_mult_entry = tk.Entry(self, width=int(len(str(keyframeMultiplier))*1.1), background=white, foreground=black, textvariable=key_mult_var,
                              validate="key", validatecommand=(key_mult_value, '%P'))
        key_mult_entry.grid(row=2, column=1, sticky='nsew')
        tk.Button(self, text='Apply', command=lambda:apply_keyframe_multiplier(key_mult_var), bg=grey, fg=white).grid(row=2, column=2, sticky='nsew')
        # Transition Multiplier
        tk.Label(self, text='Transition Multiplier: ', bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=3, column=0, sticky='nsew')
        interp_mult_value = self.register(Under_100)
        interp_mult_var = tk.IntVar(value=transitionMultiplier)
        interp_mult_entry = tk.Entry(self, width=int(len(str(transitionMultiplier))*1.1), background=white, foreground=black, textvariable=interp_mult_var,
                                  validate="key", validatecommand=(interp_mult_value, '%P'))
        interp_mult_entry.grid(row=3, column=1, sticky='nsew')
        tk.Button(self, text='Apply', command=lambda:apply_transition_multiplier(interp_mult_var), bg=grey, fg=white).grid(row=3, column=2, sticky='nsew')
        tk.Label(self, text='Total Frames: {}'.format((lastFrame+1)*keyframeMultiplier + (lastFrame)*transitionMultiplier), bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=4, column=0, sticky='nsew')
        tk.Button(self, text='Reset', command=lambda: reset_all(), bg=grey, fg=white).grid(row=4,column=1,sticky='nsew', columnspan=2)

def reset_all():
    global interpolatables
    global lastFrame
    global keyframeMultiplier
    global transitionMultiplier
    global selected_interpolatable
    global selected_frame
    subject = Interpolatable("Subject", {'Example category': 'Example Value'})
    cam = Interpolatable("Camera", {'size': '', 'view': ''})
    enviro = Interpolatable("Environment", {'Location': ''})
    interpolatables = [subject, cam, enviro]  # Array of Interpolatable objects being used
    selected_interpolatable = interpolatables[0]  # The Interpolatable object that is selected
    selected_frame = 0  # The frame that is selected
    lastFrame = 10  # The last frame in the timeline
    keyframeMultiplier = 1  # The number of renders/keyframe (static values)
    transitionMultiplier = 0  # The number of renders in-between keyframes (interlopating values)
    mainApp.reload_all()
    mainApp.reload_settings()


def generate():
    all_text = ''
    # for each frame
    for frame in range(0, lastFrame + 1):
        # for each additional output from the frame multiplier
        for kf in range(0, keyframeMultiplier):
            positives = []
            negatives = []
            line = ''
            for interp in interpolatables:
                # Get value at frame
                interp_positives, interp_negatives = interp.get_frame_str(frame, lastFrame)
                if interp_positives is not None and interp_positives != ', ':
                    positives.append(interp_positives)
                if interp_negatives is not None and interp_negatives != ', ':
                    negatives.append(interp_negatives)
            if len(positives) > 0:
                string = ', '.join(positives)
                line = positive_format.format(string)
            if len(negatives) > 0:
                if len(positives) > 0:
                    line = line + ' '
                string = ', '.join(negatives)
                line = line + negative_format.format(string)
            line = line + "\n"
            all_text = all_text + line

        # for each additional output from the transition multiplier
        if frame < lastFrame:
            for kf in range(0, transitionMultiplier):
                positives = []
                negatives = []
                line = ''
                for interp in interpolatables:
                    # Get value at frame
                    interp_positives, interp_negatives = interp.get_interped_str(frame, lastFrame, (kf+1)/(transitionMultiplier+1))
                    if interp_positives is not None and interp_positives != ', ':
                        positives.append(interp_positives)
                    if interp_negatives is not None and interp_negatives != ', ':
                        negatives.append(interp_negatives)
                if len(positives) > 0:
                    string = ', '.join(positives)
                    line = positive_format.format(string)
                if len(negatives) > 0:
                    if len(positives) > 0:
                        line = line + ' '
                    string = ', '.join(negatives)
                    line = line + negative_format.format(string)
                line = line + "\n"
                all_text = all_text + line
    location = asksaveasfilename(defaultextension='.txt')
    try:
        file = open(location, 'w')
        file.write(all_text)
        file.close()
    except:
        pass


def save_sequence():
    sequence = [interpolatables, lastFrame, keyframeMultiplier, transitionMultiplier]
    location = asksaveasfilename(initialfile='Sequence')
    try:
        file = open(location, 'wb')
        pickle.dump(sequence, file)
        file.close()
    except:
        pass


def load_sequence():
    location = askopenfilename()
    try:
        file = open(location, 'rb')
        sequence = pickle.load(file)
        file.close()
        global interpolatables
        global lastFrame
        global keyframeMultiplier
        global transitionMultiplier
        interpolatables = sequence[0]
        lastFrame = sequence[1]
        keyframeMultiplier = sequence[2]
        transitionMultiplier = sequence[3]
        mainApp.reload_all()
        mainApp.reload_settings()
    except:
        pass


def apply_last_frame(var):
    global lastFrame
    try:
        lastFrame = int(var.get())
        mainApp.reload_all()
        mainApp.reload_settings()
    except:
        pass


def apply_keyframe_multiplier(var):
    global keyframeMultiplier
    try:
        keyframeMultiplier = int(var.get())
        mainApp.reload_settings()
    except:
        pass


def apply_transition_multiplier(var):
    global transitionMultiplier
    try:
        transitionMultiplier = int(var.get())
        mainApp.reload_settings()
    except:
        pass


def new_interpolatable(var):
    name = var.get()
    if name is None or len(name.split()) == 0:
        name = "Interpolatable {}".format(len(interpolatables))
    interp = Interpolatable(name, {})
    interpolatables.append(interp)
    global selected_interpolatable
    selected_interpolatable = interp
    # Reload UI
    mainApp.reload_all()


def delete_Interpolatable(interpolatable: Interpolatable):
    global interpolatables
    index = interpolatables.index(interpolatable)
    interpolatables.remove(interpolatable)
    global selected_interpolatable
    newIndex = max(index - 1,0)
    if len(interpolatables) == 0:
        selected_interpolatable = None
    else:
        selected_interpolatable = interpolatables[newIndex]
    # Reload UI
    mainApp.reload_all()


class Timeline(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=1, column=0, sticky="nsew", columnspan=3, padx=2, pady=2)

        self.frame = None
        self.update_timeline()

    def update_timeline(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = Scrollable(self, 1028, 200)
        # self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame = self.frame.interior
        # New frame
        new_frame = tk.Frame(self.frame, bg=navy)
        new_frame.grid(row=0, column=0)
        # New Name
        name_var = tk.StringVar(value='Subject Name')
        name_entry = tk.Entry(new_frame, width=int(len(name_var.get())*1.1), background=white, foreground=black,
                                textvariable=name_var)
        name_entry.grid(row=0, column=0, sticky='nsew')
        # New Button
        tk.Button(new_frame, text='Add Subject', command=lambda:new_interpolatable(name_var), bg=grey, fg=white).grid(row=0, column=1)
        # Top section
        for frame in range(0, lastFrame + 1):
            tk.Label(self.frame, text=str(frame), bg=grey, fg=white, highlightbackground=navy, highlightthickness=1).grid(row=0, column=frame + 1)
        # Grid section
        interp_count = 0
        for interp in interpolatables:
            InterpolatableFrame(self.frame, interp, bg=navy).grid(row=interp_count + 1, column=0, sticky='nsew')

            for frame in range(0, lastFrame + 1):

                TimelineButton(self.frame, interp, frame).grid(row=interp_count + 1, column=frame + 1)

            interp_count += 1


def TimelineSelect(interp, frame):
    global selected_interpolatable
    selected_interpolatable = interp
    global selected_frame
    selected_frame = frame
    mainApp.reload_all()


def get_key_time_color(interp: Interpolatable, frame, key, key_color, on_color) -> str:
    color = on_color
    if frame in interp.transitions and key in interp.transitions[frame]:
        color = key_color
    return color


def get_time_color(interp, frame, use_selected, selected_color, key_color, on_color, off_color, off_key_color) -> str:
    color = off_color
    if use_selected and interp is selected_interpolatable and frame is selected_frame:
        color = selected_color
    else:
        if interp.get_on(frame):
            key_val = interp.get_key(frame)
            match key_val:
                case True:
                    color = key_color
                case False:
                    color = on_color
                case None:
                    color = on_color
        elif interp.get_key(frame) is None:
            color = off_key_color
    return color

class Scrollable(tk.Frame):
    def __init__(self, parent, width, height, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        self.width = width
        self.height = height

        vscrollbar = ttk.Scrollbar(self, orient='vertical')
        vscrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar = ttk.Scrollbar(self, orient='horizontal')
        hscrollbar.grid(row=1, column=0, sticky="we")

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set, bg=navy)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = tk.Frame(self.canvas, bg=navy)
        interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor='nw')

        # Bind and unbind wheel
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        self.canvas.config(width=self.width)
        self.canvas.config(height=self.height)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
        self.interior.bind('<Configure>', _configure_interior)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll_y)
        self.canvas.bind_all("<Shift - MouseWheel>", self.mouse_scroll_x)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift - MouseWheel>")

    def mouse_scroll_y(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def mouse_scroll_x(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


class TimelineButton(tk.Button):
    def __init__(self, parent, interp, frame, *args, **kwargs):
        color = get_time_color(interp, frame, True, white, blue, orange, black, lightGrey)
        tk.Button.__init__(self, parent, text='   ', bg=color, command=lambda: TimelineSelect(interp, frame), *args, **kwargs)

class InterpolatableFrame(tk.Frame):
    def __init__(self, parent, interp, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        tk.Label(self, text=interp.name, bg=grey, fg=white, highlightbackground=navy, highlightthickness=4).grid(row=0, column=0, sticky='nsew')
        tk.Button(self, text='X', command=lambda: delete_Interpolatable(interp), bg=grey, fg=white).grid(row=0, column=1, sticky='nsew')


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.configure_gui()

        self.valueInspector = None
        self.keyframeInspector = None
        self.settings = None
        self.timeline = None
        self.create_widgets()

    def configure_gui(self):
        self.parent.title("Sequence Interpolator")
        self.parent.geometry("1047x695")

    def create_widgets(self):
        # UI Contains Value Inspector, Keyframe inspector, Settings, and Timeline:
        self.valueInspector = ValueInspector(self)
        self.keyframeInspector = KeyframeInspector(self)
        self.settings = Settings(self)
        self.timeline = Timeline(self)

    def reload_value_inspector(self):
        self.valueInspector.destroy()
        self.valueInspector = ValueInspector(self)

    def reload_keyframe_inspector(self):
        self.keyframeInspector.destroy()
        self.keyframeInspector = KeyframeInspector(self)

    def reload_timeline(self):
        self.timeline.destroy()
        self.timeline = Timeline(self)

    def reload_settings(self):
        self.settings.destroy()
        self.settings = Settings(self)

    def reload_all(self):
        self.reload_keyframe_inspector()
        self.reload_value_inspector()
        self.reload_timeline()
        #self.reload_settings()


def create_ui():
    root = tk.Tk()
    global mainApp
    mainApp = MainApplication(root, bg=black)
    mainApp.pack(side="top", fill="both", expand=True)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
