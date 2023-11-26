# This is for saving/loading stuff
import copy
import pickle


# This is intended to be extended by other classes with their own default dictionary values and/or other stuff
class Interpolatable:
    # Defines how it is saved/referenced
    name = ''
    # Stores dict of all prompt pieces
    data = {}
    # Sorted dict of frames containing a dict data to change and their new values
    transitions = []

    def __init__(self, name: str, data: dict):
        self.name = name
        # Intended to be set to a dictionary with keys representing the object's initial state
        self.data = data
        self.transitions = {0: {'On': True}}

    def save_data(self, file_folder: str):
        file_name = '{}/{}-data'.format(file_folder, self.name)
        file = open(file_name, 'wb')
        pickle.dump(self.data, file)
        file.close()

    def load_data(self, file_folder: str):
        file_name = '{}/{}-data'.format(file_folder, self.name)
        file = open(file_name, 'rb')
        self.data = pickle.load(file)
        file.close()

    def save_transitions(self, file_folder: str):
        file_name = '{}/{}-transitions'.format(file_folder, self.name)
        file = open(file_name, 'wb')
        pickle.dump(self.transitions, file)
        file.close()

    def load_transitions(self, file_folder: str):
        file_name = '{}/{}-transitions'.format(file_folder, self.name)
        file = open(file_name, 'rb')
        self.transitions = pickle.load(file)
        file.close()

    def add_transition(self, frame_number: int, key: str, value: str):
        if frame_number in self.transitions:
            self.transitions[frame_number][key] = value
        else:
            self.transitions[frame_number] = {key: value}

    def apply_frame(self, frame_number: int, dictionary: dict):
        if frame_number in self.transitions:
            for key, value in self.transitions[frame_number].items():
                dictionary[key] = value

    def apply_up_to_frame(self, frame_number):
        dictionary = copy.deepcopy(self.data)
        for i in range(0, frame_number + 1):
            self.apply_frame(i, dictionary)
        return dictionary

    def get_on(self, frame_number):
        on = True
        for i in range(0, frame_number + 1):
            if i in self.transitions and 'On' in self.transitions[i]:
                on = self.transitions[i]['On']
        return on

    def get_key(self, frame_number):
        if frame_number in self.transitions:
            if 'On' in self.transitions[frame_number]:
                if len(self.transitions[frame_number]) > 1 or self.transitions[frame_number]['On']:
                    return True
                else:
                    return None
            elif len(self.transitions[frame_number]) > 0:
                return True
        return False
