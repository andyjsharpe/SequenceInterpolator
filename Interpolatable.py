# This is for saving/loading stuff
import copy
import pickle
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename

scaleFormat = '({}:{})'
mixFormat = '(({}) AND ({}))'

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

    def get_key_exists(self, frame_number: int, key):
        if frame_number in self.transitions:
            if 'On' in self.transitions[frame_number]:
                return key in self.transitions[frame_number]
        return False

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
        pre_positives = []
        post_positives = []
        const_positives = []
        pre_negatives = []
        post_negatives = []
        const_negatives = []
        for key in self.data:
            pre_value = post_value = None
            # See if there is a keyframe on this frame
            if self.get_key_exists(frame_number, key):
                # if so use the keyframe value
                pre_value = self.get_value_on_frame(frame_number, key)
            elif frame_number == 0:
                pre_value = self.data[key]
            else:
                # if not, find the surrounding keyframes then interpolate
                # there will always be a before value
                before_value, before_frame = self.get_previous_transition(frame_number, key)
                # there will not always be an after value
                after_value, after_frame = self.get_next_transition(frame_number, last_frame, key)
                if after_value is not None:
                    # interpolate between values
                    completion = self.map_range(frame_number, before_frame, after_frame, 0, 1)
                    pre_value, post_value = self.mix_values(before_value, after_value, completion)
                else:
                    # set value to before
                    pre_value = before_value
            if key.startswith('(Negative)'):
                if pre_value == post_value:
                    if pre_value is not None and len(pre_value) > 0:
                        const_negatives.append(pre_value)
                else:
                    if pre_value is not None and len(pre_value) > 0:
                        pre_negatives.append(pre_value)
                    if post_value is not None and len(post_value) > 0:
                        post_negatives.append(post_value)
            else:
                if pre_value == post_value:
                    if pre_value is not None and len(pre_value) > 0:
                        const_positives.append(pre_value)
                else:
                    if pre_value is not None and len(pre_value) > 0:
                        pre_positives.append(pre_value)
                    if post_value is not None and len(post_value) > 0:
                        post_positives.append(post_value)
        pp_string = ', '.join(pre_positives)
        if pp_string is None or pp_string == ', ':
            pp_string = None
        po_string = ', '.join(post_positives)
        if po_string is None or po_string == ', ':
            po_string = None
        cp_string = ', '.join(const_positives)
        if cp_string is None or cp_string == ', ':
            cp_string = None
        np_string = ', '.join(pre_negatives)
        if np_string is None or np_string == ', ':
            np_string = None
        no_string = ', '.join(post_negatives)
        if no_string is None or no_string == ', ':
            no_string = None
        cn_string = ', '.join(const_negatives)
        if cn_string is None or cn_string == ', ':
            cn_string = None
        return pp_string, po_string, cp_string, np_string, no_string, cn_string

    # Use if between transition point or not on a keyframe
    def get_interped_str(self, frame_number: int, last_frame: int, extra_completion: float):
        if not self.get_on(frame_number):
            return None, None
        pre_positives = []
        post_positives = []
        const_positives = []
        pre_negatives = []
        post_negatives = []
        const_negatives = []
        for key in self.data:
            pre_value = post_value = None
            # find the surrounding keyframes then interpolate
            # there will always be a before value
            before_value, before_frame = self.get_previous_transition(frame_number, key)
            # there will not always be an after value
            after_value, after_frame = self.get_next_transition(frame_number, last_frame, key)
            if after_value is not None:
                # interpolate between values
                completion = self.map_range(frame_number + extra_completion, before_frame, after_frame, 0, 1)
                pre_value, post_value = self.mix_values(before_value, after_value, completion)
            else:
                # set value to before
                pre_value = post_value = before_value
            if key.startswith('(Negative)'):
                if pre_value == post_value:
                    if pre_value is not None and len(pre_value) > 0:
                        const_negatives.append(pre_value)
                else:
                    if pre_value is not None and len(pre_value) > 0:
                        pre_negatives.append(pre_value)
                    if post_value is not None and len(post_value) > 0:
                        post_negatives.append(post_value)
            else:
                if pre_value == post_value:
                    if pre_value is not None and len(pre_value) > 0:
                        const_positives.append(pre_value)
                else:
                    if pre_value is not None and len(pre_value) > 0:
                        pre_positives.append(pre_value)
                    if post_value is not None and len(post_value) > 0:
                        post_positives.append(post_value)
        pp_string = ', '.join(pre_positives)
        if pp_string is None or pp_string == ', ':
            pp_string = None
        po_string = ', '.join(post_positives)
        if po_string is None or po_string == ', ':
            po_string = None
        cp_string = ', '.join(const_positives)
        if cp_string is None or cp_string == ', ':
            cp_string = None
        np_string = ', '.join(pre_negatives)
        if np_string is None or np_string == ', ':
            np_string = None
        no_string = ', '.join(post_negatives)
        if no_string is None or no_string == ', ':
            no_string = None
        cn_string = ', '.join(const_negatives)
        if cn_string is None or cn_string == ', ':
            cn_string = None
        return pp_string, po_string, cp_string, np_string, no_string, cn_string


    def map_range(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    # Return the prompt for a set of pre and post values
    def mix_with_and(self, pre, post, const):
        pre_string = None
        if pre is not None and len(pre) > 0:
            pre_string = ', '.join(filter(None, pre))
            if len(pre_string) < 1:
                pre_string = None
        post_string = None
        if post is not None and len(post) > 0:
            post_string = ', '.join(filter(None, post))
            if len(post_string) < 1:
                post_string = None
        const_string = None
        if const is not None and len(const) > 0:
            const_string = ', '.join(filter(None, const))
            if len(const_string) < 1:
                const_string = None
        line = None
        if pre_string is not None:
            if post_string is not None:
                line = mixFormat.format(pre_string, post_string)
            else:
                line = pre_string
        elif post_string is not None:
            line = post_string
        if const_string is not None:
            if line is None:
                return const_string
            else:
                return line + ', ' + const_string
        else:
            return line

    # Return the scaled before and after values
    def mix_values(self, value1, value2, completion):
        rounded = round(completion*100)/100
        inverse_rounded = round((1 - completion) * 100) / 100
        if value1 == value2 or rounded == 0:
            return value1, value1
        elif rounded == 1:
            return value2, value2
        if value1 is None or value1 == '':
            scaled2 = scaleFormat.format(value2, rounded)
            return None, scaled2
        if value2 is None or value2 == '':
            scaled1 = scaleFormat.format(value1, inverse_rounded)
            return scaled1, None
        scaled1 = scaleFormat.format(value1, inverse_rounded)
        scaled2 = scaleFormat.format(value2, rounded)
        return scaled1, scaled2

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
