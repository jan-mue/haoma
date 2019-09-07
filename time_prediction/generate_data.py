import numpy as np
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from data_categories import *

n_patients = 7_000
n_cases = 8_000
n_procedures = 10_000
has_dependencies = True

# patient data
patient_id_start = np.random.randint(1000)
patient_ids = np.arange(patient_id_start, patient_id_start+n_patients)
patient_sex = np.random.choice(["M", "F"], n_patients)
patient_age = np.empty(n_patients)
patient_age[patient_sex == "M"] = np.random.normal(42.58, 21.7, np.sum(patient_sex == "M"))
patient_age[patient_sex == "F"] = np.random.normal(37.75, 19.4, np.sum(patient_sex == "F"))
patient_age = np.abs(patient_age) + np.ones_like(patient_age)
patient_birthdays = [datetime.today() + relativedelta(days=-years*365) for years in patient_age]

def get_bernoulli(size, dataset):
    k = list(dataset.keys())
    data = np.random.binomial(size=size, n=1, p=dataset[k[0]])
    return np.array([k[0] if x == 1 else k[1] for x in data])

patient_insurance = get_bernoulli(n_patients, pat_insurances)
patient_claustrophobia = get_bernoulli(n_patients, pat_claustrophobias)
patient_infection = get_bernoulli(n_patients, pat_infection)

def rand_weight_height(age, gender):
    if age < 20:
        if age == 0:
            height = 60
        else:
            height = age * 5.1 + 74.8

        height += np.random.normal(0, 5)
        weight = height / 5 + np.random.normal(0,5)

    else:
        height = 165 + np.random.normal(0, 5)
        weight = height / 3 + np.random.normal(0, 10)

    if gender == 'M':
        weight = 1.15 * weight
        height = 1.1 * height

    return weight, height

patient_wh = np.array([rand_weight_height(age, sex) for age, sex in zip(patient_age,patient_sex)])
patient_weight = patient_wh[:,0]
patient_height = patient_wh[:,1]

patients = pd.DataFrame({
    "PATIENT_KEY": patient_ids,
    "PAT_SEX": patient_sex,
    "PAT_BIRTH_DATE": patient_birthdays,
    "PAT_INSURANCE": patient_insurance,
    "PAT_CLAUSTROPHOBIA": patient_claustrophobia,
    "PAT_INFECTION": patient_infection,
    "PAT_WEIGHT": patient_weight,
    "PAT_HEIGHT": patient_height,
})

# case data
case_id_start = np.random.randint(2000)
case_ids = np.arange(case_id_start, case_id_start+n_cases)
case_patients = patients.sample(n_cases, replace=True).reset_index(drop=True)
cases = pd.DataFrame({"CASE_KEY": case_ids}).join(case_patients)

# procedure data
procedure_ids_start = np.random.randint(3000)
procedure_ids = np.arange(procedure_ids_start, procedure_ids_start+n_procedures)
procedure_cases = cases.sample(n_procedures, replace=True).reset_index(drop=True)
procedure_code = np.random.choice(list(procedure_types.keys()), n_procedures)
procedure_name = np.array([procedure_types[code][0] for code in procedure_code])

# Filter out males from breast screening
for i in range(n_procedures):
    if procedure_code[i] == 'bs' and procedure_cases['PAT_SEX'][i] == 'M':
        procedure_code[i] = np.random.choice(list(procedure_types.keys())[1:])

priority_code = np.zeros(n_procedures, dtype=np.uint8)

for i,code in enumerate(procedure_code):
    _, mean, value_range = procedure_types[code]
    priority_code[i] = int(min(max(np.random.randint(value_range * 2) - value_range + mean, 1), 9))

procedure_code = np.char.upper(procedure_code)

admission_type = np.random.choice(list(admission_types.keys()), n_procedures)

pat_condition = np.empty(n_procedures, dtype="<U10")
for i in range(n_procedures):
    r = np.random.uniform()
    n = 0
    for key, value in pat_conditions.items():
        n += value
        if n >= r:
            pat_condition[i] = key
            break

    np.random.choice(list(pat_conditions), n_procedures) #TODO: different distribution

start_date = time.time() - np.maximum(np.random.randint(365 * 60 * 60 * 24), 100 * 60 * 60 * 24)
appointment_intervals = np.random.normal(60*20, 60*5, n_procedures)
registration_arrival_delays = np.random.normal(-20 * 60, 10 * 60, n_procedures)
appointment_wait = np.maximum(np.random.normal(60 * 60, 5 * 60, n_procedures), 5 * 60)
procedure_duration = np.maximum(np.random.normal(25 * 60, 2 * 60, n_procedures), 15 * 60)

if has_dependencies:
    for i in range(n_procedures):
        appointment_wait[i] -= 60 * priority_code[i]
        if procedure_cases['PAT_INSURANCE'][i] == 'private':
            appointment_wait[i] -= 60 * 10

        d = procedure_duration[i]
        if procedure_cases['PAT_HEIGHT'][i] > 190:
            d += 60 * 5
        if procedure_cases['PAT_CLAUSTROPHOBIA'][i] == 'yes':
            d += 60 * 5
        if procedure_cases['PAT_WEIGHT'][i] > 90:
            d += 60 * 5
        if procedure_cases['PAT_BIRTH_DATE'][i].year < 1950:
            d += 60 * 10
        if pat_condition[i] == 'wheelchair':
            d += 60 * 10
        if pat_condition[i] == 'bed':
            d += 60 * 15

        procedure_duration[i] = d

appointment_date = np.array([pd.Timestamp(0) for x in range(n_procedures)])
registration_arrival = np.zeros_like(appointment_date)
procedure_start = np.zeros_like(appointment_date)
procedure_end = np.zeros_like(appointment_date)

time = start_date
for i, s in enumerate(appointment_intervals):
    time += s
    appointment_date[i] = pd.Timestamp(time, unit='s').round(freq='T')
    if appointment_date[i].hour < 8 or appointment_date[i].hour > 21:
        time += np.random.normal(60 * 30, 60 * 10)
    arrival_time = time + registration_arrival_delays[i]
    registration_arrival[i] = pd.Timestamp(arrival_time, unit='s')
    procedure_start_time = np.maximum(arrival_time + 60 * 2, time + appointment_wait[i])
    procedure_start[i] = pd.Timestamp(procedure_start_time, unit='s')
    procedure_end[i] = pd.Timestamp(procedure_start_time + procedure_duration[i], unit='s')

institutes = np.random.randint(100, 5000, 5)
institute_id = np.random.choice(institutes, n_procedures)
technicians = np.random.randint(5000, 8000, 20)
technician_id = np.random.choice(technicians, n_procedures)
radiologists = np.random.randint(2000, 8000, 15)
radiologist_id = np.random.choice(radiologists, n_procedures)
med_location = np.empty(n_procedures, dtype="<U10")
for i in range(n_procedures):
    c = procedure_code[i][0].lower()
    if c == 'b':
        c = 'g'
    _, possible_med_locations = machine_types[c]
    med_location[i] = np.random.choice(possible_med_locations)

print(np.mean(appointment_wait), np.var(appointment_wait))
print(np.mean(procedure_duration), np.var(procedure_duration))

procedures = pd.DataFrame({
    "PROCEDURE_KEY": procedure_ids,
    "PROCEDURE_CODE": procedure_code,
    "PROCEDURE_NAME": procedure_name,
    "ADMISSION_TYPE": admission_type,
    "PRIORITY_CODE": priority_code,
    "PAT_CONDITION": pat_condition,
    "APPOINTMENT_DATE": appointment_date,
    "REGISTRATION_ARRIVAL": registration_arrival,
    "PROCEDURE_START": procedure_start,
    "PROCEDURE_END": procedure_end,
    "RADIOLOGIST_ID": radiologist_id,
    "TECHNICIAN_ID": technician_id,
    "INSTITUTE_ID": institute_id,
    "MED_LOCATION_KEY": med_location,

}).join(procedure_cases)


if has_dependencies:
    procedures.to_csv("data_dependent.csv", index=False)
else:
    procedures.to_csv("data.csv", index=False)
