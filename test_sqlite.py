import os, csv, sqlite3
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 

from math import log, sqrt, exp
from constants import SQLITE_DIRECTORY, CSV_DIRECTORY
from plot_utils import plot_compare_kde
from cli_utils import tabulate_column
from sqlite_utils import sql_fetch_all, sql_fetch_one

def compute_drug_odds_ratios(conn):

  query = "SELECT drug_name from drug_data"
  drugs = list(set([rec[0] for rec in sql_fetch_all(conn, query)]))

  odds_ratios = []
  for drug in drugs:
    if "'" in drug: continue
    odds = compare_drugs_by_death(conn, drug)
    if odds[0] == -1: continue
    if odds[-1] < 5: continue
    odds_ratios.append([drug, odds])

  odds_ratios.sort(key=lambda x: x[1][0])

  for drug, odds in odds_ratios:
    print('%s - OR = %.2f (%.2f-%.2f), N exposed = %d' % \
         (drug, odds[0], odds[1], odds[2], odds[3]) )

def compare_labs_by_covid(conn, lab_name, min_value=0, max_value=999999):
  return compare_labs_by(conn, 'patient_covid_status', 'positive', 'negative', lab_name, \
                    min_value=min_value, max_value=max_value)

def compare_obs_by_covid(conn, obs_name, min_value=0, max_value=999999):
  return compare_obs_by(conn, 'patient_covid_status', 'positive', 'negative', obs_name, \
                    min_value=min_value, max_value=max_value)

def compare_labs_by_death(conn, lab_name, min_value=0, max_value=999999):
  return compare_labs_by(conn, 'patient_vital_status', 'dead', 'alive', lab_name, \
                    min_value=min_value, max_value=max_value, \
                    query_tail = 'AND patient_data.patient_covid_status = \'positive\'')

def compare_obs_by_death(conn, obs_name, min_value=0, max_value=999999):
  return compare_obs_by(conn, 'patient_vital_status', 'dead', 'alive', obs_name, \
                    min_value=min_value, max_value=max_value, \
                    query_tail = 'AND patient_data.patient_covid_status = \'positive\'')

def compare_obs_by(conn, col, val_pos, val_neg, obs_name, min_value=0, max_value=999999, query_tail=''):
  
  query = "SELECT observation_value from observation_data " + \
    " INNER JOIN patient_data ON " + \
    " observation_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
    " observation_data.observation_name = '"+obs_name+"' AND " + \
    " observation_data.observation_value NOT NULL AND " + \
    " patient_data." + col + " = "
  
  res = sql_fetch_all(conn, query + " '" + val_pos + "' " + query_tail)

  values_pos = [float(value[0]) for value in res]
  
  res = sql_fetch_all(conn, query + " '" + val_neg + "' " + query_tail)
  
  values_neg = [float(value[0]) for value in res]
  
  plot_compare_kde(obs_name, col, val_pos, val_neg, values_pos, \
    values_neg, min_value, max_value)

def compare_labs_by(conn, col, val_pos, val_neg, lab_name, min_value=0, max_value=999999, query_tail=''):
  
  query = "SELECT lab_result_value from lab_data " + \
    " INNER JOIN patient_data ON " + \
    " lab_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
    " lab_data.lab_name = '" + lab_name + "' AND " + \
    " lab_data.lab_result_status = 'resulted' AND " + \
    " patient_data." + col + " = "
  
  res = sql_fetch_all(conn, query + " '" + val_pos + "' " + query_tail)
  values_pos = [float(value[0]) for value in res]
  
  res = sql_fetch_all(conn, query + " '" +  val_neg + "' " + query_tail)
  values_neg = [float(value[0]) for value in res]

  plot_compare_kde(lab_name, col, val_pos, val_neg, values_pos, \
    values_neg, min_value, max_value)

def compare_drugs_by_death(conn, drug_name):
  
  query = "SELECT patient_site_uid from patient_data WHERE " + \
          "patient_covid_status = 'positive'"
  all_patients = set([rec[0] for rec in sql_fetch_all(conn, query)])

  query = "SELECT patient_site_uid from patient_data WHERE " + \
          "patient_covid_status = 'positive' AND patient_vital_status = 'dead'"
  dead_patients = set([rec[0] for rec in sql_fetch_all(conn, query)])
  alive_patients = all_patients.difference(dead_patients)

  query = "SELECT drug_data.patient_site_uid from drug_data INNER JOIN " + \
          " patient_data ON patient_data.patient_site_uid = " + \
          " drug_data.patient_site_uid WHERE " + \
          " patient_data.patient_covid_status = 'positive' AND " + \
          " drug_name = '" + drug_name + "'"
  
  exposed_patients = set([rec[0] for rec in sql_fetch_all(conn, query)])
  
  nonexposed_patients = all_patients.difference(exposed_patients)

  a = len(list(exposed_patients & dead_patients))
  b = len(list(exposed_patients & alive_patients))
  c = len(list(nonexposed_patients & dead_patients))
  d = len(list(nonexposed_patients & alive_patients))
  
  if len(exposed_patients) == 0: return [-1, None, None, None]

  odds_ratio = (float(0.5+a)/float(0.5+c)) / \
               (float(0.5+b) / float(0.5+d))
  odds_ratio = round(odds_ratio, 2)


  log_or = log(odds_ratio)
  se_log_or = sqrt(1/float(0.5+a) + 1/float(0.5+b) + \
                   1/float(0.5+c) + 1/float(0.5+d))
  lower_ci = exp(log_or - 1.96 * se_log_or)
  upper_ci = exp(log_or + 1.96 * se_log_or)

  return [odds_ratio, lower_ci, upper_ci, len(exposed_patients)]

db_file_name = os.path.join(SQLITE_DIRECTORY, 'covidb_version-1.0.0.db')
conn = sqlite3.connect(db_file_name)

compute_drug_odds_ratios(conn)

#tabulate_column('patient_age', res, -3)
#tabulate_column('patient_sex', res, -2)
#tabulate_column('patient_covid_status', res, -4)
#tabulate_column('patient_death_status', res, -1)

#compare_by_covid(conn, 'Température', min_value=35, max_value=40)
compare_labs_by_covid(conn, 'c_reactive_protein', max_value=500)
compare_labs_by_covid(conn, 'd_dimer', max_value=30000)
compare_labs_by_covid(conn, 'lactate_dehydrogenase', max_value=10000)
compare_labs_by_covid(conn, 'ferritin', min_value=5, max_value=10000)
compare_labs_by_covid(conn, 'lymphocyte_count', max_value=10)
compare_labs_by_covid(conn, 'phosphate', max_value=5)
compare_labs_by_covid(conn, 'mean_platelet_volume', max_value=10)

#compare_by_covid(conn, 'VPM', max_value=18)
#compare_by_covid(conn, 'Protéine C Réac.', max_value=500)
#compare_by_covid(conn, 'Procalcitonine', max_value=100)
#compare_by_covid(conn, 'D-Dimère', max_value=50000)

compare_obs_by_covid(conn, 'fraction_inspired_oxygen')
compare_obs_by_death(conn, 'fraction_inspired_oxygen')
compare_obs_by_death(conn, 'systolic_blood_pressure')

#query = "SELECT imaging_accession_uid from imaging_data " + \
#    " INNER JOIN patient_data ON " + \
#    " imaging_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
#    " patient_data.patient_covid_status = 2"

res = sql_fetch_all(conn, "SELECT * from patient_data WHERE patient_vital_status='dead'")

#res = sql_fetch_all(conn, query)
#print(len(res))
#imaging_accession_uid = res[1]

# Fetch all imaging tests
#res = sql_fetch_one(conn, "SELECT * from slice_data")
#file = res[-13]

import numpy as np
pix = pd.read_csv(file).to_numpy()

from PIL import Image
dat = (pix / (np.max(pix)) * 255).astype(np.uint8)
im = Image.fromarray(dat)
im.save('test.jpeg')
