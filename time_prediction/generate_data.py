import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from data_categories import *

n_patients = 2000
n_cases = 2500
n_procedures = 3000

# patient data
patient_id_start = np.random.randint(1000)
patient_ids = np.arange(patient_id_start, patient_id_start+n_patients)
patient_sex = np.random.choice(["M", "F"], n_patients)
patient_age = np.empty(n_patients)
patient_age[patient_sex == "M"] = np.random.normal(43.58, 21.7, np.sum(patient_sex == "M"))
patient_age[patient_sex == "F"] = np.random.normal(38.75, 19.4, np.sum(patient_sex == "F"))
patient_age[patient_age < 0] = -patient_age[patient_age < 0]
patient_birthdays = [datetime.today() + relativedelta(days=-years*365) for years in patient_age]
patients = pd.DataFrame({
    "PATIENT_KEY": patient_ids,
    "PAT_SEX": patient_sex,
    "PAT_BIRTH_DATE": patient_birthdays
})


# case data
case_id_start = np.random.randint(2000)
case_ids = np.arange(case_id_start, case_id_start+n_cases)
case_patients = patients.sample(n_cases, replace=True)
cases = pd.concat([pd.DataFrame({"CASE_KEY": case_ids}), case_patients], axis=0)

# procedure data
procedure_ids_start = np.random.randint(3000)
procedure_ids = np.arange(procedure_ids_start, procedure_ids_start+n_procedures)
procedure_cases = cases.sample(n_cases, replace=True)

procedures = pd.DataFrame({
    "PROCEDURE_KEY": procedure_ids,
})

procedures.to_csv("data.csv")
