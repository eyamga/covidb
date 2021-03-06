import os, csv, sqlite3
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 

from math import log, sqrt, exp
from constants import SQLITE_DIRECTORY, CSV_DIRECTORY
from plot_utils import plot_compare_kde
from cli_utils import tabulate_column
from sqlite_utils import sql_fetch_all, sql_fetch_one
from time_utils import get_hours_between_datetimes

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold

from gain import gain

gain_parameters = { 'batch_size': 128,
                    'hint_rate': 0.9,
                    'alpha': 1000,
                    'iterations': 1000}
  
np.set_printoptions(precision=2, suppress=True)

db_file_name = os.path.join(SQLITE_DIRECTORY, 'covidb_version-1.0.0.db')
conn = sqlite3.connect(db_file_name)

def map_age(age):
  if age is None: return 60
  else: return float(age)

def map_sex(sex):
  if sex == 'male': return 1
  else: return 0

query_info = "SELECT patient_site_uid, patient_age, patient_sex from patient_data WHERE " + \
        " patient_data.patient_covid_status = 'positive'"

pt_infos = dict((str(x[0]), [map_age(x[1]), map_sex(x[2])]) for x in sql_fetch_all(conn, query_info))

query_icu = "SELECT episode_data.patient_site_uid from episode_data INNER JOIN " + \
        " patient_data ON episode_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
        " (episode_data.episode_unit_type = 'intensive_care_unit' OR " + \
        "  episode_data.episode_unit_type = 'high_dependency_unit') AND " + \
        " patient_data.patient_covid_status = 'positive'"

query_deaths = "SELECT diagnosis_data.patient_site_uid from diagnosis_data INNER JOIN " + \
        " patient_data ON diagnosis_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
        " diagnosis_data.diagnosis_type = 'death' AND " + \
        " patient_data.patient_covid_status = 'positive'"

icu_pt_ids = set([str(x[0]) for x in sql_fetch_all(conn, query_icu)])
death_pt_ids = set([str(x[0]) for x in sql_fetch_all(conn, query_deaths)])

query = "SELECT episode_data.patient_site_uid, episode_start_time from episode_data INNER JOIN " + \
         " patient_data ON episode_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
         " (episode_data.episode_unit_type = 'inpatient_ward' OR " + \
         "  episode_data.episode_unit_type = 'emergency_room' ) AND " + \
         " patient_data.patient_covid_status = 'positive'"

res = sql_fetch_all(conn, query)

eligible_patients = set()
eligible_episodes = {}

for patient_id, episode_start_time in res:
  patient_id = str(patient_id)
  eligible_patients.add(patient_id)
  episode_start_time = str(episode_start_time)
  if patient_id not in eligible_episodes:
     eligible_episodes[patient_id] = []
  eligible_episodes[patient_id].append(episode_start_time)

query = "SELECT lab_data.patient_site_uid, lab_name, lab_sample_time, lab_result_value from lab_data " + \
  " INNER JOIN patient_data ON " + \
  " lab_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
  " lab_data.lab_result_status = 'resulted' AND " + \
  " patient_data.patient_covid_status = 'positive'"
  
res1 = sql_fetch_all(conn, query)

query = "SELECT observation_data.patient_site_uid, observation_name, observation_time, observation_value from observation_data " + \
  " INNER JOIN patient_data ON " + \
  " observation_data.patient_site_uid = patient_data.patient_site_uid WHERE " + \
  " observation_data.observation_value IS NOT NULL AND " + \
  " patient_data.patient_covid_status = 'positive'"
  
res2 = sql_fetch_all(conn, query)

lab_data = [[str(value[0]), str(value[1]), str(value[2]), float(value[3])] for value in res1] + \
           [[str(value[0]), str(value[1]), str(value[2]), float(value[3])] for value in res2]
lab_bins = {}
lab_names = set()
patients_with_data = {}
patient_ids = []
for patient_id, lab_name, lab_sample_time, lab_value in lab_data:
  if patient_id not in eligible_patients: continue
  lab_names.add(lab_name)
  if patient_id not in lab_bins:
    lab_bins[patient_id] = {}
    patient_ids.append(patient_id)
  if lab_name not in patients_with_data:
    patients_with_data[lab_name] = set()
  if lab_name not in lab_bins[patient_id]:
    lab_bins[patient_id][lab_name] = [None, None, None]
  
  for episode_start_time in eligible_episodes[patient_id]:
    hours_since_admission = get_hours_between_datetimes(episode_start_time, lab_sample_time)
    if hours_since_admission > 0 and hours_since_admission < 24:
      lab_bins[patient_id][lab_name][0] = lab_value
    elif hours_since_admission > 24 and hours_since_admission < 48:
      lab_bins[patient_id][lab_name][1] = lab_value
    elif hours_since_admission > 48 and hours_since_admission < 72:
      lab_bins[patient_id][lab_name][2] = lab_value
    else: continue
  
  patients_with_data[lab_name].add(patient_id)

feature_array = []
complete_lab_names = set()
for patient_id in sorted(lab_bins):
  feature_rows = []
  feature_subarray = []
  #age, sex = pt_infos[patient_id]
  #feature_subarray = [[age, sex, 0]]
  #feature_rows.append('age_sex')
  for lab_name in sorted(lab_names):
    
    pct_with_data = len(patients_with_data[lab_name]) / len(eligible_patients)
    
    if pct_with_data > 0.25:
      complete_lab_names.add(lab_name)
      feature_rows.append(lab_name)
      if lab_name not in lab_bins[patient_id]: 
        feature_subarray.append([None, None, None])
      else:
        lab_values = lab_bins[patient_id][lab_name]
        feature_subarray.append(lab_values)
  feature_array.append(feature_subarray)

feature_array = np.asarray(feature_array)
feature_shape = feature_array.shape

input_array = []
rows = []
for k in range(0, len(feature_rows)):
  row = []
  for i in range(0, feature_shape[0]):
    patient_data = feature_array[i]
    row.extend(patient_data[k])
  rows.append(row)
rows = np.asarray(rows)

input_array_tmp = rows.transpose()
input_array = []
for k in range(0, input_array_tmp.shape[0]):
  n_filled = np.sum([1 \
   for x in input_array_tmp[k,:] \
   if x is not None])
  n_total = input_array_tmp.shape[1]
  print(n_filled / n_total)
  if n_filled / n_total < 0.5: continue
  input_array.append(input_array_tmp[k,:])
  
input_array = np.asarray(input_array)
input_shape = input_array.shape

print('Feature array shape: %s' % str(feature_shape))
print('Input shape for imputer: %s' % str(input_shape))

imputed_array = gain(\
  input_array.astype(np.float), gain_parameters)

from fancyimpute import KNN

imp_mean = KNN(5) # IterativeImputer()
imp_mean.fit_transform(input_array) 
#imp_mean.transform(input_array)

df = pd.DataFrame(imputed_array)

plt.matshow(df.corr())
#plt.title('Correlations between laboratory parameters over time', y=-0.01)
plt.xticks(range(0,len(feature_rows)), feature_rows, rotation='vertical',fontsize='6')
plt.yticks(range(0,len(feature_rows)), feature_rows, fontsize='6')
plt.gca().xaxis.set_ticks_position('top')
plt.colorbar()

plt.tight_layout(pad=2)
plt.show()

imputed_array = imputed_array.transpose()

output_array  = []
for i in range(0, feature_shape[0]):
  rows = []
  for j in range(0, feature_shape[1]):
    rows.append(imputed_array[j,i*3:i*3+3])
  output_array.append(rows)
output_array = np.asarray(output_array)

print('Imputed feature array shape: %s' % str(output_array.shape))


i = 0
for feature_name in feature_rows:
  
  print(feature_name, '\t', 
    str(feature_array[0][i]), '\t', 
    str(output_array[0][i]))
  i += 1

all_pt_ids = []
labels = []
num_patient = 0
for patient_id in sorted(lab_bins):
  all_pt_ids.append(patient_id)
  labels.append( (patient_id in icu_pt_ids or patient_id in death_pt_ids ) )
  num_patient += 1

classifier_labels = np.asarray(labels)
classifier_input = np.asarray([x.flatten() for x in output_array])

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

kfold = KFold(n_splits=5)
X = classifier_input
y = classifier_labels

#X_train, X_test, y_train, y_test = train_test_split( \
#  classifier_input, classifier_labels, test_size=1/3)

print('Classifier input array shape: %s' % str(output_array.shape))
print(labels)

clf = RandomForestClassifier(max_depth=10, random_state=0)

plt.figure()
fold = 0
tprs = []
mean_fpr = np.linspace(0, 1, 100)

for train_index, test_index in kfold.split(X):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]

  y_score = clf.fit(X_train, y_train).predict_proba(X_test)

  fpr, tpr, _ = roc_curve(y_test, y_score[:,1])
  tprs.append(np.interp(mean_fpr, fpr, tpr))
  roc_auc = auc(fpr, tpr)

  plt.plot(fpr, tpr, lw=1, color='gray', linestyle='--', \
    label='Fold %i (AUC = %0.2f)' % (fold, roc_auc))

  fold += 1

mean_tpr = np.mean(tprs, axis=0)
mean_auc = auc(mean_fpr, mean_tpr)

plt.plot(mean_fpr, mean_tpr, lw=2, color='green', \
  label='Average %i (AUC = %0.2f)' % (fold, mean_auc))

plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Prediction of ICU admission or death')
plt.legend(loc="lower right")
plt.show()

print('Number of patients (total): %d' % len(all_pt_ids))
print('Number of patients (unique): %d' % len(np.unique(all_pt_ids)))
print('Number of + events (train): %d' % np.count_nonzero(y_train))
print('Number of + events (test): %d' % np.count_nonzero(y_test))
print('Number of windows (train): %d' % len(X_train))
print('Number of windows (test): %d' % len(X_test))