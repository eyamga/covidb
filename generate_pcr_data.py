#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: lmullie

"""
import os
import numpy as np
import pandas as pd

from constants import DEBUG, COLUMNS
from sql_utils import sql_query, list_columns, list_tables
from file_utils import write_csv, read_csv
from time_utils import get_hours_between_datetimes
from identity_utils import generate_patient_uid, generate_patient_site_uid
from mappers import map_pcr_sample_site

row_count = 0
patient_data_rows = []
patient_mrns = []
patient_covid_statuses = {}
pcr_sample_times = {}

patient_data_rows = read_csv(os.path.join(CSV_DIRECTORY, 'patient_data.csv'))

for row in patient_data_rows:
  patient_mrn = str(row[0])
  patient_mrns.append(patient_mrn)
  patient_covid_statuses[patient_mrn] = row[-3]
  pcr_sample_times[patient_mrn] = row[1]

pcr_patterns = ['PCR', 'COVID', 'Influenza', 'RSV', 'Coronavirus']

df = sql_query("SELECT * FROM dw_v01.oacis_lb WHERE (" +
    ' OR '.join(["longdesc LIKE '%" + pat + "%'" for pat in pcr_patterns]) + ") AND "
    "specimencollectiondtm > '2020-01-01' AND dossier in (" + ", ".join(patient_mrns) + ")")

pcr_data_rows = []

for index, row in df.iterrows():

  patient_mrn = str(row.dossier)
  pcr_name = row.longdesc
  pcr_sample_site = row.specimencollectionmethodcd
  pcr_sample_time = row.specimencollectiondtm
  pcr_result_time = row.resultdtm
  pcr_result_value = row.lbres_ck
  pcr_result_units = row.resultunit

  if 'COVID' in pcr_name:
    pcr_name = 'COVID-19 PCR'

  pcr_result_value = row.abnormalflagcd

  pcr_data_rows.append([
    patient_mrn, pcr_name, 
    map_pcr_sample_site(pcr_sample_site), pcr_sample_time, 
    pcr_result_time, pcr_result_value, patient_covid_statuses[patient_mrn]
  ])

print('Total rows: %d' % len(pcr_data_rows))
write_csv(COLUMNS['pcr_data'], pcr_data_rows, 
  os.path.join(CSV_DIRECTORY, 'pcr_data.csv'))