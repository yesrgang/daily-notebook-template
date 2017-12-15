import json
import numpy as np

class Data(object):
    """ helper class for processing data
    
    load: data = Data(filename)
    features...
    trim: makes sure entries all have same length
    cuts: remove data from ends
     
    combine: data = data1 + data2
    """
    def __init__(self, filename=None, cuts=None, bad_points = [], data={}):
        if type(filename).__name__ == 'list':
            with open(filename[0], 'r') as infile:
                data = Data(data=json.load(infile))            
            for fn in filename[1:]:
                with open(fn, 'r') as infile:
                    data += Data(data=json.load(infile))
            #self.data = self.cut(data.data, cuts)
            self.data = data.data
        elif filename:
            with open(filename, 'r') as infile:
                data = json.load(infile)
                self.data = self.cut(data, cuts)
        else:
            self.data = data
            
    def trim(self, data):
        """ makes sure entries all have same length """
        lengths = []
        
        def find_lengths(x):
            if type(x).__name__ == 'dict':
                for v in x.values():
                    find_lengths(v)
            elif type(x).__name__ in ['list', 'numpy.ndarray']:
                lengths.append(len(x))
        
        find_lengths(data)
        minimum_length = min(lengths)
                
        def do_trim(x):
            if type(x).__name__ == 'dict':
                return {k: do_trim(v) for k, v in x.items()}
            elif type(x).__name__ in ['list', 'numpy.ndarray']:
                return x[:minimum_length]
            else:
                return x
            
        return do_trim(data)
    
    def cut(self, data, cuts):
        if type(data).__name__ == 'dict':
            return {k: self.cut(v, cuts) for k, v in data.items()}
        elif type(data).__name__ == 'list':
            if cuts:
                tmp = sum([data[c[0]:c[1]] for c in cuts], [])
            else:
                tmp = data
            return np.array(tmp)

    
    def add(self, data1, data2):
        if type(data1).__name__ == 'dict':
            try:
                return {k: self.add(data1[k], data2[k]) for k in data1}
            except KeyError, k:
                data1.pop(k)
                self.add(data1, data2)
        else:
            try:
                return np.concatenate((data1, data2))
            except:
                return None
    
    def __add__(self, data2):
        return Data(data=self.add(self.data, data2))
    
    def __getitem__(self, kw):
        return self.data[kw]
    
    def __setitem__(self, kw, item):
        self.data[kw] = item