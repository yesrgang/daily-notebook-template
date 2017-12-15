def process_pmt(data):
    """ shift picoscope data and populate 'exc' and 'gnd' """
    
    data['pmt'] = {}
    data['pmt']['tot'] = data['pico']['tot'][1:]    
    data['pmt']['frac'] = data['pico']['frac'][1:]
    data['pmt']['exc'] = data['pmt']['frac'] * data['pmt']['tot']
    data['pmt']['gnd'] = data['pmt']['tot'] - data['pmt']['exc']
    
    return data
