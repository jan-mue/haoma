import numpy as np
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from data_categories import *

n_patients = 70_000
n_cases = 80_000
n_procedures = 100_000

# patient data
patient_id_start = np.random.randint(1000)
patient_ids = np.arange(patient_id_start, patient_id_start+n_patients)
patient_sex = np.random.choice(["M", "F"], n_patients)
patient_age = np.empty(n_patients)
patient_age[patient_sex == "M"] = np.random.normal(43.58, 21.7, np.sum(patient_sex == "M"))
patient_age[patient_sex == "F"] = np.random.normal(38.75, 19.4, np.sum(patient_sex == "F"))
patient_age = np.abs(patient_age)
patient_birthdays = [datetime.today() + relativedelta(days=-years*365) for years in patient_age]
patient_insurance = np.random.binomial(size=n_patients, n=1, p=0.1)
patient_insurance = np.array(['PRIVATE' if x == 1 else 'PUBLIC' for x in patient_insurance])

patients = pd.DataFrame({
    "PATIENT_KEY": patient_ids,
    "PAT_SEX": patient_sex,
    "PAT_BIRTH_DATE": patient_birthdays,
    "PAT_INSURANCE": patient_insurance,
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
procedure_name = np.array([procedure_types[code] for code in procedure_code])

# Filter out males from breast screening
for i in range(n_procedures):
    if procedure_code[i] == 'bs' and procedure_cases['PAT_SEX'][i] == 'M':
        procedure_code[i] = np.random.choice(list(procedure_types.keys())[1:])

priority_code = np.zeros_like(procedure_code)
for i, code in enumerate(procedure_code):
    priority_code[i] = np.random.randint(3) - 1 + priority_codes[code]

procedure_code = np.char.upper(procedure_code)

admission_type = np.random.choice(list(admission_types.keys()), n_procedures)
pat_condition = np.random.choice(list(pat_conditions), n_procedures)

start_date = time.time() - np.maximum(np.random.randint(365 * 60 * 60 * 24), 100 * 60 * 60 * 24)
appointment_intervals = np.maximum(np.random.normal(60*15, 60*5, n_procedures), 60*10)
registration_arrival_delays = np.random.normal(-20 * 60, 10 * 60, n_procedures)
appointment_wait = np.maximum(np.random.normal(60 * 60, 20 * 60, n_procedures), 5 * 60)
procedure_duration = np.maximum(np.random.normal(30 * 60, 10 * 60, n_procedures), 15 * 60)

appointment_date = np.array([pd.Timestamp(0) for x in range(n_procedures)])
registration_arrival = np.zeros_like(appointment_date)
procedure_start = np.zeros_like(appointment_date)
procedure_end = np.zeros_like(appointment_date)

time = start_date
for i, s in enumerate(appointment_intervals):
    time += s
    appointment_date[i] = pd.Timestamp(time, unit='s').round(freq='T')
    arrival_time = time + registration_arrival_delays[i]
    registration_arrival[i] = pd.Timestamp(arrival_time, unit='s')
    procedure_start_time = np.maximum(arrival_time + 60 * 2, time + appointment_wait[i])
    procedure_start[i] = pd.Timestamp(procedure_start_time, unit='s')
    procedure_end[i] = pd.Timestamp(procedure_start_time + procedure_duration[i], unit='s')


procedures = pd.DataFrame({
    "PROCEDURE_KEY": procedure_ids,
    "PROCEDURE_CODE": procedure_code,
    "ADMISSION_TYPE": admission_type,
    "PRIORITY_CODE": priority_code,
    "PAT_CONDITION": pat_condition,
    "APPOINTMENT_DATE": appointment_date,
    "REGISTRATION_ARRIVAL": registration_arrival,
    "PROCEDURE_START": procedure_start,
    "PROCEDURE_END": procedure_end,
}).join(procedure_cases)

procedures.to_csv("data.csv", index=False)
