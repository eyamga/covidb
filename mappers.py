import re

from constants import DRUG_ROUTE_MAP #, DRUG_FREQUENCY_MAP
from lang_utils import transliterate_string

def map_time(time):
  if time is None: return ''
  return str(time).strip().lower()

def map_patient_ramq(ramq):
  ramq_str = str(ramq).strip()
  if not re.match("[A-Z]{4}[0-9]{8}", ramq_str):
    return ''
  return ramq_str

def map_patient_covid_status(status):
  status_str = str(status).strip().lower()
  if status_str == 'positif':   return 'positive'
  elif status_str == 'négatif': return 'negative'
  elif status_str == 'en attente': return 'pending'
  elif status_str == 'test annulé': return 'unknown'
  elif status_str == 'annulé': return 'unknown'
  elif status_str == 'rapp. numérisé': return 'unknown'
  elif status_str == 'non valide': return 'unknown'
  else: raise Exception('Invalid COVID status: %s' % status)

def map_patient_age(age):
  age_str = str(age).strip()
  if age_str == '': return ''
  age_parsed = int(age_str)
  if age_parsed < 0 or age_parsed > 122:
    raise Exception('Invalid age: %s' % age)
  return age_parsed

def map_patient_sex(sex):
  sex_parsed = (str(sex).strip()).lower()
  if sex_parsed == '': return ''
  if sex_parsed == 'm': return 'male'
  elif sex_parsed == 'f': return 'female'
  elif sex_parsed == 'x': return 'unspecified'
  else: raise Exception('Invalid birth sex: %s' % sex)

def map_lab_name(name):
  name_str = str(name).strip().lower()
  name_str = transliterate_string(name_str)
  return name_str
  
def map_lab_sample_site(code):
  if code is None: return ''
  code = (str(code).strip()).lower()
  if 'veineux' in code: return 'venous_blood'
  elif 'art' in code: return 'arterial_blood'
  elif 'urine' in code: return 'urine'
  elif 'autres' in code: return 'other'
  else:
    print('Unrecognized sample site: ' + code)
    return ''

def map_lab_result_value(result_string):
  result_string = str(result_string) \
    .replace('<', '') \
    .replace('>', '') \
    .replace(',', '.') \
    .strip()
  if result_string == '':
    return ''
  else:
    return float(result_string)

def map_pcr_sample_site(code):
  code = (str(code).strip()).lower()
  if 'couvillon' in code: return 'nasopharyngeal_swab'
  elif 'urine' in code: return 'urine'
  elif 'sang' in code: return 'blood'
  elif 'autres' in code: return 'other'
  elif 'micro' in code: return ''
  elif 'none' in code: return ''
  else:
    print('Unrecognized sample site: ' + code)
    return ''

def map_culture_type(culture_type):
  type_str = str(culture_type).strip().lower()
  if 'myco/f lytic' in type_str: return 'myco_culture'
  elif 'culture virale' in type_str: return 'viral_culture'
  else: return 'bacterial_culture'

def map_culture_specimen_type(type_desc, site_desc):

  type_desc = (str(type_desc).strip()).lower()
  site_desc = (str(site_desc).strip()).lower()

  desc = type_desc + ' ' + site_desc
  if 'hémoculture' in desc: return 'blood'
  if 'expectoration' in desc: return 'expectorated_sputum'
  if 'moelle' in desc: return 'bone_marrow'
  if 'prothèse' in desc: return 'prosthesis'
  if 'selles' in desc: return 'stool'
  if 'erv par culture' in desc: return 'rectal_swab'
  if 'sarm par culture' in desc: return 'nasal_swab'
  if 'gorge' in desc: return 'nasal_swab'
  if 'sécrétions nasales' in desc: return 'nasal_secretions'
  if 'céphalo-rachidien' in desc: return 'cerebrospinal_fluid'
  if 'biopsie d\'os' in desc: return 'bone_biopsy'
  if 'biopsie pulmonaire' in desc: return 'lung_biopsy'
  if 'biopsie pulmonaire' in desc: return 'lung_biopsy'
  if 'biopsie cutanée' in desc: return 'skin_biopsy'
  if 'biopsie de ganglion cutané' in desc: return 'lymph_node_biopsy'
  if 'corps étransfer' in desc: return 'foreign_body'
  if 'intravasculaire' in desc: return 'intravascular_catheter'
  if 'liq préservation' in desc: return 'preservation_liquid'
  if 'ascite' in desc: return 'ascites_fluid'
  if 'pleural' in desc: return 'pleural_fluid'
  if 'abcès du cerveau' in desc: return 'cerebral_abscess'
  if 'pus superficiel' in desc: return 'superficial_pus'
  if 'pus profond' in desc: return 'deep_pus'
  if 'urine' in desc: return 'urine'
  if 'bronchique' in desc: return 'bronchial_secretions'
  if 'sang' in desc: return 'blood'
  if 'urine' in desc: return 'urine'
  if 'lavage broncho-alvéolaire' in desc: return 'bronchoalveolar_lavage'
  if 'bronchique' in desc: return 'bronchial_secretions'
  if 'cimen micro' in desc: return 'other'
  if 'autres' in site_desc: return 'other'
  else:
    print('Unrecognized sample site: ' + desc)
    exit()

def map_culture_growth_value(value):
  if value is None: return ''
  value_str = str(value).strip().lower()
  if value_str == 'pos': return 'positive'
  elif value_str == 'neg': return 'negative'
  else: 
    print('Unrecognized growth result')
    return ''

def map_episode_unit_type(unit_code):
  unit_code_str = str(unit_code)
  if '10S' in unit_code_str or '10N' in unit_code_str:
    return 'intensive_care'
  elif 'ER' in unit_code_str:
    return 'emergency_room'
  else: 
    return 'inpatient_ward'

def map_observation_name(name):
  if name == 'FIO2': return 'fraction_inspired_oxygen'
  if name == 'Sat O2 Art': return 'arterial_oxygen_saturation'
  if name == 'Température': return 'temperature'
  return None

def map_drug_name(name):
  name_str = str(name).strip().lower()
  name_str = transliterate_string(name_str)
  return name_str
  
def map_drug_route(route_code):

  route_code_str = str(route_code)

  if 'routecd' in route_code_str:
    route_code_str = route_code_str.replace('\n', ' ')
    route_code_parts = route_code_str.split('routecd')
    route_code_parts = [d.strip() for d in route_code_parts]
    route_code_parts = [d for d in route_code_parts if d != '']
    route_code_str = route_code_parts[0].replace('CY', '')

  route_code_str = route_code_str.lower().strip()
  
  if route_code_str in DRUG_ROUTE_MAP:
    return DRUG_ROUTE_MAP[route_code_str]
  else: 
    print('Invalid drug route: %s' % route_code_str)

def map_drug_frequency(frequency_code):

  #if frequency_code is None: return ''

  cd = str(frequency_code).lower().strip()
  
  if 'die' in cd or 'hs' in cd: return 'die'
  elif 'bid' in cd: return 'bid'
  elif 'tid' in cd: return 'tid'
  elif 'qid' in cd: return 'qid'
  elif 'q1j' in cd: return 'q1j'
  elif 'q2j' in cd: return 'q2j'
  elif 'q3j' in cd: return 'q3j'
  elif 'q5min' in cd: return 'q5min'
  elif 'q10min' in cd: return 'q10min'
  elif 'q15min' in cd: return 'q15min'
  elif 'q1-2' in cd: return 'q1-2h'
  elif 'q1-4' in cd: return 'q1-4h'
  elif 'q2-3' in cd: return 'q2-3h'
  elif 'q4-6' in cd: return 'q4-6h'
  elif 'q2' in cd: return 'q2h'
  elif 'q3' in cd: return 'q3h'
  elif 'q4' in cd: return 'q4h'
  elif 'q5' in cd: return 'q5h'
  elif 'q6' in cd: return 'q6h'
  elif 'q7' in cd: return 'q7h'
  elif 'q8' in cd: return 'q8h'
  elif 'q9' in cd: return 'q9h'
  elif 'q10' in cd: return 'q10h'
  elif 'q12' in cd: return 'q12h'
  elif 'q13' in cd: return 'q13h'
  elif 'q14' in cd: return 'q14h'
  elif 'q15' in cd: return 'q15h'
  elif 'q16' in cd: return 'q16h'
  elif 'q17' in cd: return 'q17h'
  elif 'q19' in cd: return 'q19h'
  elif 'q24' in cd: return 'q24h'
  elif 'qmois' in cd: return '1x monthly'
  elif cd in ['induc', 'induc0', '1dose']: return '1x'
  elif 'appel' in cd: return '1x'
  elif 'insam' in cd: return 'die'
  elif 'insmi' in cd: return 'die'
  elif 'insampm' in cd: return 'bid'
  elif 'ins820' in cd: return 'bid'
  elif 'inspm' in cd: return 'die'
  elif 'instid' in cd: return 'tid'
  elif 'qh' in cd: return 'die'
  elif 'pnuit' in cd: return 'die'
  elif 'perf' in cd: return 'perf'
  elif 'vaccin' in cd: return '1x'
  elif 'cejour' in cd: return '1x'
  elif cd in ['prechim', 'culots', 'gluco1/2', 'postculo', \
    'postdial', 'cvvhprot', 'directiv', 'test', 'prot', \
    'selh', 'selc', 'tqp', 'tqpa', 'tqpp', 'protp', \
    'acpiv', 'epidb']:
    return 'cond' # according to a protocol
  elif '1-2fpjp' in cd: return 'die-bid'
  elif '2-3fpjp' in cd: return 'bid-tid'
  elif '2-4fpjp' in cd: return 'bid-qid'
  elif '3-4fpjp' in cd: return 'tid-qid'
  elif cd in ['6fj2-21' '6fj6-21' '6fj8-22', '6fj6-21', \
    '6fj2-21', '6fj8-22']:
    return '6x daily'
  elif cd in ['l10', 'l19', 'l21', 'l6', 'l7', 'l9']: 
    return '1x weekly'
  elif cd in ['m10', 'm17', 'm21', 'm6', 'm7', 'm9']:
    return '1x weekly'
  elif cd in ['me10', 'me21', 'me6', 'me7', 'me9']:
    return '1x weekly'
  elif cd in ['j10', 'j21', 'j6', 'j7', 'j9']:
    return '1x weekly'
  elif cd in ['v10', 'v21', 'v6', 'v7', 'v9']: 
    return '1x weekly'
  elif cd in ['s10', 's21', 's6', 's7', 's9']:
    return '1x weekly'
  elif cd in ['d10', 'd12', 'd21', 'd6', 'd7', 'd9']:
    return '1x weekly'
  elif cd in ['lj10', 'lj21', 'lj9', 'lme21', 'lme9', \
    'lv21', 'lv9', 'mes9', 'mev9', 'mj21', 'mj9', \
    'ms9', 'mv10', 'mv9', 'mme9', 'dme9', 'ds19']:
    return '2x weekly'
  elif cd in ['lmev10', 'lmev12', 'lmev17', 'lmev21', \
    'lmv9', 'mjs17', 'mjs21', 'mjs9', 'lmev9', 'mmej9', 'dvs9']:
    return '3x weekly'
  elif cd in ['lmjs21', 'lmjvs9', 'lmmej9', 'dmjs19', \
    'dmjs21', 'dmjs8', 'dlmev21', 'dlmev9']:
    return '4x weekly'
  elif cd in ['lmmejv10', 'lmmejv9', 'lmmevs9', 'lmejvs9', \
    'dljvs9']:
    return '5x weekly'
  elif cd in ['6fs-d9', '6fs-j21', '6fs-l9', '6fs-m9', \
    '6fs-me9', '6fs-s9', '6fs-v21']:
    return '6x weekly'
  elif cd in ['p', 'prn']:
    return '' # PRN, unspecified frequency
  else: 
    return None
    print('Invalid drug frequency: %s' % cd)