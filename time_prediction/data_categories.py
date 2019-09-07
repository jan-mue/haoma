# type: name, med_locations
machine_types = {
    'x': ('xr', ['xr1','xr2']),
    'c': ('ct', ['ct1','ct2','ct3','ct4']),
    'm': ('mri', ['mri1', 'mri2']),
    'u': ('us', ['us1', 'us2', 'us3', 'us4', 'us5', 'us6']),
    'g': ('mammogram', ['mg1', 'mg2']),
}

body_parts = {
    'ches': 'chest',
    'abdo': 'abdomen',
    'skuh': 'head',
    'knel': 'knee left',
    'kner': 'knee right',
    'brea': 'breast',
    'arml': 'arm left',
    'armr': 'arm right',
}

# procedure type: name, priority avg, priority dev
procedure_types = {
    'bs': ('Breast Screening', 2, 1),
    'xches': ('XR Chest', 3, 3),
    'xabdo': ('XR Abdomen', 4, 4),
    'uabdo': ('US Abdomen', 6, 3),
    'xknel': ('XR Knee Lt', 2, 1),
    'xkner': ('XR Knee Rt', 2, 1),
    'xarml': ('XR arm Lt', 3, 1),
    'xarmr': ('XR arm Rt', 3, 1),
    'mskuh': ('MRI Head', 5, 3),
    'cskuh': ('CT Head', 4, 3),
}

# admission type: likelihood
admission_types = {
    'outpatient': 3,
    'inpatient': 1,
}

pat_claustrophobias = {
    'unknown': 0.95,
    'yes': 0.05
}

pat_conditions = {
    'unknown': 0.2,
    'walk': 0.6,
    'wheelchair': 0.1,
    'bed': 0.1,
}


pat_sexes = {
    'f': 0.5,
    'm': 0.5,
}

pat_insurances = {
    'public': 0.9,
    'private': 0.1,
}

pat_infection = {
    'unknown': 0.95,
    'yes': 0.05,
}
