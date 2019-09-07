import numpy as np

machine_types = {
    'x': 'xr',
    'c': 'ct',
    'm': 'mri',
    'u': 'us',
    'g': 'mammogram'
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

procedure_types = {
    'bs': 'Breast Screening',
    'xches': 'XR Chest',
    'xabdo': 'XR Abdomen',
    'uabdo': 'US Abdomen',
    'xknel': 'XR Knee Lt',
    'xkner': 'XR Knee Rt',
    'xarml': 'XR arm Lt',
    'xarmr': 'XR arm Rt',
    'mskuh': 'MRI Head',
    'cskuh': 'CT Head',
}

priority_codes = {
    'bs': 2,
    'xches': 3,
    'xabdo': 3,
    'uabdo': 5,
    'xknel': 2,
    'xkner': 2,
    'xarml': 3,
    'xarmr': 3,
    'mskuh': 5,
    'cskuh': 3,
}


admission_types = {
    'outpatient': 0,
    'inpatient': 1,
}

pat_conditions = {
    'unknown': 0,
    'walk': 1,
    'wheelchair': 2,
    'bed': 3,
}


pat_sexes = {
    'f': 0,
    'm': 1,
}

pat_insurances = {
    'public': 0,
    'private': 1,
}