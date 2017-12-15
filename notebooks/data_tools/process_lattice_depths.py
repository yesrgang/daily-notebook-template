import numpy as np

NU_RECOIL = 3.4e3

def get_lattice_depth_coefficients(data, trap_frequencies):
    return {lattice: (nu / NU_RECOIL + 1.)**2. / 4. / data['sequencer']['*813{}f'.format(lattice)][0] 
            for lattice, nu in trap_frequencies.items()}

def process_lattice_depths(data, depth_coefficients):
    data['lattice'] = {}
    data['lattice']['depth_H1'] = data['sequencer']['*813H1f'][0] * depth_coefficients['H1']
    data['lattice']['depth_H2'] = data['sequencer']['*813H2f'][0] * depth_coefficients['H2']
    data['lattice']['depth_V'] = data['sequencer']['*813Vf'][0] * depth_coefficients['V']
    
    data['lattice']['total_depth'] = np.sum([
                                        data['lattice']['depth_H1'],
                                        data['lattice']['depth_H2'],
                                        data['lattice']['depth_V'],
                                    ])           
    data['lattice']['mean_depth'] = np.prod([
                                        data['lattice']['depth_H1'],
                                        data['lattice']['depth_H2'],
                                        data['lattice']['depth_V'],
                                    ])**(1./3.)
    return data
