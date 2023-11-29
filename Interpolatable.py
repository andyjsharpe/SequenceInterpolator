# This is for saving/loading stuff
import copy
import pickle
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename


# This is intended to be extended by other classes with their own default dictionary values and/or other stuff
class Interpolatable:
    # Defines how it is saved/referenced
    name = ''
    # Stores dict of all prompt pieces
    data = {}
    # Sorted dict of frames containing a dict data to change and their new values
    transitions = {}

    def __init__(self, name: str, data: dict):
        self.name = name
        # Intended to be set to a dictionary with keys representing the object's initial state
        self.data = data
        self.transitions = {0: {'On': True}}

    def save_data(self, initial_name):
        self.name = initial_name
        location = asksaveasfilename(initialfile=initial_name)
        try:
            file = open(location, 'wb')
            pickle.dump(self.data, file)
            file.close()
        except:
            pass

    def load_data(self):
        location = askopenfilename()
        try:
            file = open(location, 'rb')
            name = file.name
            start = name.rfind('/')
            self.name = name[start+1:]
            self.data = pickle.load(file)
            file.close()
        except:
            pass

    def save_frame_data(self, frame_number):
        dictionary = copy.deepcopy(self.data)
        for i in range(0, frame_number + 1):
            if frame_number in self.transitions:
                for key, value in self.transitions[frame_number].items():
                    if key != 'On':
                        dictionary[key] = value
        location = asksaveasfilename(initialfile=self.name)
        try:
            file = open(location, 'wb')
            pickle.dump(self.data, file)
            file.close()
        except:
            pass


    def load_frame_data(self, frame_number):
        location = askopenfilename()
        try:
            file = open(location, 'rb')
            data = pickle.load(file)
            file.close()
            for key, value in data.items():
                if key in self.data:
                    if self.get_value_on_frame(frame_number, key) != data[key]:
                        self.add_transition(frame_number, key, value)
                else:
                    self.data[key] = value
        except:
            pass


    def add_transition(self, frame_number: int, key: str, value: str):
        if frame_number in self.transitions:
            self.transitions[frame_number][key] = value
        else:
            self.transitions[frame_number] = {key: value}

    def get_value_on_frame(self, frame_number: int, key: str):
        value = None
        if key in self.data:
            value = self.data[key]
        for i in range(0, frame_number + 1):
            if i in self.transitions and key in self.transitions[i]:
                value = self.transitions[i][key]
        return value

    def get_data_on_frame(self, frame_number: int):
        data = copy.deepcopy(self.data)
        for key in data:
            data[key] = self.get_value_on_frame(frame_number, key)
        return data

    def get_on(self, frame_number: int):
        return self.get_value_on_frame(frame_number, 'On')

    def get_key(self, frame_number: int, include_on: bool = True):
        if frame_number in self.transitions:
            if 'On' in self.transitions[frame_number]:
                if len(self.transitions[frame_number]) > 1 or (include_on and self.transitions[frame_number]['On']):
                    return True
                else:
                    return None
            elif len(self.transitions[frame_number]) > 0:
                return True
        return False

    # Use if right on a keyframe
    def get_frame_str(self, frame_number: int, last_frame: int):
        if not self.get_on(frame_number):
            return None, None
        positives = []
        negatives = []
        for key in self.data:
            value = None
            # See if there is a keyframe on this frame
            if self.get_key(frame_number, False):
                # if so use the keyframe value
                value = self.get_value_on_frame(frame_number, key)
            elif frame_number == 0:
                value = self.data[key]
            else:
                # if not, find the surrounding keyframes then interpolate
                # there will always be a before value
                before_value, before_frame = self.get_previous_transition(frame_number, key)
                # there will not always be an after value
                after_value, after_frame = self.get_next_transition(frame_number, last_frame, key)
                if after_value is not None:
                    # interpolate between values
                    completion = self.map_range(frame_number, before_frame, after_frame, 0, 1)
                    value = self.mix_values(before_value, after_value, completion)
                else:
                    # set value to before
                    value = before_value
            if value is None:
                continue
            if key.startswith('(Negative)'):
                negatives.append(value)
            else:
                positives.append(value)
        positive_prompt = None
        if len(positives) > 0:
            positive_prompt = ', '.join(positives)
        negative_prompt = None
        if len(negatives) > 0:
            negative_prompt = ', '.join(negatives)
        return positive_prompt, negative_prompt

    # Use if between transition point or not on a keyframe
    def get_interped_str(self, frame_number: int, last_frame: int, extra_completion: float):
        if not self.get_on(frame_number):
            return None, None
        positives = []
        negatives = []
        for key in self.data:
            value = None
            # find the surrounding keyframes then interpolate
            # there will always be a before value
            before_value, before_frame = self.get_previous_transition(frame_number, key)
            # there will not always be an after value
            after_value, after_frame = self.get_next_transition(frame_number, last_frame, key)
            if after_value is not None:
                # interpolate between values
                completion = self.map_range(frame_number + extra_completion, before_frame, after_frame, 0, 1)
                value = self.mix_values(before_value, after_value, completion)
            else:
                # set value to before
                value = before_value
            if value is None:
                continue
            if key.startswith('(Negative)'):
                negatives.append(value)
            else:
                positives.append(value)
        positive_prompt = None
        if len(positives) > 0:
            positive_prompt = ', '.join(positives)
        negative_prompt = None
        if len(negatives) > 0:
            negative_prompt = ', '.join(negatives)
        return positive_prompt, negative_prompt


    def map_range(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    def mix_values(self, value1, value2, completion):
        rounded = round(completion*100)/100
        inverse_rounded = round((1-completion) * 100) / 100
        return '{{{}:{} | {}:{}}}'.format(value1, inverse_rounded, value2, rounded)

    def get_next_transition(self, frame_number: int, last_frame: int, key):
        for frame in range(frame_number + 1, last_frame + 1):
            if frame in self.transitions and key in self.transitions[frame]:
                return self.transitions[frame][key], frame
        return None, frame_number

    def get_previous_transition(self, frame_number: int, key):
        for frame in range(frame_number, -1, -1):
            if frame in self.transitions and key in self.transitions[frame]:
                return self.transitions[frame][key], frame
        return self.data[key], 0

    def remove_key(self, key):
        self.data.pop(key)
        for values in self.transitions.values():
            if key in values:
                values.pop(key)
