import pandas as pd
import numpy as np

from data_categories import *


def one_hot_enc(index, number, zero_entry=False):
    if zero_entry:
        number -= 1

    x = np.zeros(number)
    if not (zero_entry and index == 0):
        x[index] = 1
    return x


def time_enc(stamp):
    # TODO: encode neighborhood between months 1,2 and 12,1...
    month = one_hot_enc(stamp.month - 1, 12)
    day = one_hot_enc(stamp.day - 1, 31)
    hour = one_hot_enc(stamp.hour - 1, 24)
    minute = one_hot_enc(stamp.minute - 1, 60)
    return month, day, hour, minute


def dict_type_enc(dict, type):
    # All dicts should contain lower case keys
    type = type.lower()
    i = list(dict).index(type)
    zero_entry = len(dict) == 2 or list(dict.keys())[0]== 'unknown'
    return one_hot_enc(i, len(dict), zero_entry)


def load_data(file):
    """Load procedure data.

    """
    if file.endswith('.xlsx'):
        df = pd.read_excel(file)
    elif file.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        raise TypeError('Invalid file' + file)

    features = []
    waiting_times = []
    procedure_times = []
    punctuality_times = []

    for idx, row in df.iterrows():

        def get(key):
            return row[key.upper()]

        def get(key):
            return self.wait_times[key.upper()][idx]

        procedure = get('procedure_code')
        # convert special code for breast screening with mammogram
        procedure = 'GBREA' if procedure == 'BS' else procedure

        machine_code, body_code = procedure[0], procedure[1:]
        machine_type = dict_type_enc(machine_types, machine_code)
        body_part = dict_type_enc(body_parts, body_code)

        punctuality = get('appointment_date') - get('registration_arrival')
        punctuality = np.array([punctuality.seconds])
        wait = get('procedure_start') - get('registration_arrival')
        wait = np.array([wait.seconds])
        procedure_time = get('procedure_start') - get('registration_arrival')
        procedure_time = np.array([procedure_time.seconds])

        admission_type = dict_type_enc(admission_types, get('admission_type'))
        priority_code = get('priority_code') / 10
        priority_code = np.array([priority_code])
        pat_condition = dict_type_enc(pat_conditions, get('pat_condition'))
        current_date = pd.datetime.now()
        pat_age = (current_date.year - get('pat_birth_date').year) / 100  # TODO: calc age properly
        pat_age = np.array([pat_age])
        pat_sex = dict_type_enc(pat_sexes, get('pat_sex'))
        pat_insurance = dict_type_enc(pat_insurances, get('pat_insurance'))

        # Concat to feature vector
        # spare = np.zeros(500)
        x = np.concatenate((machine_type, body_part, admission_type, priority_code,
                        pat_condition, pat_age, pat_sex, pat_insurance))

        features.append(x)
        waiting_times.append(wait)
        procedure_times.append(procedure_time)
        punctuality_times.append(punctuality)

    return features, waiting_times, procedure_times, punctuality_times
