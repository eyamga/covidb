from file_utils import read_csv

import pandas as pd
pd.set_option('display.max_rows', 250)

DEBUG = True

PATIENT_GLOBAL_SALT = '1fd5789d7ef4287fd8acfc765061e10eb3e7c093ff9150978695fb83692e4a87d55c4abf83c7ad9bcc3305ab03a4d28a5c404db6b84886c1665f949215e75a2b'
PATIENT_SITE_SALT = '243460170aec12b2cb4ce6e92d1293ebe8bbc83b4a860681ecfd4b653961f253fc3cb7ae833de5a4faca2d98ed9789e061e95aea7335901e6c84c7c05feee85f'
LIVE_SHEET_FILENAME = "/var/www/html/mchasse/covid19/data_all.csv"
CSV_DIRECTORY = "/data8/projets/Mila_covid19/output/covidb_full/csv"
BLOB_DIRECTORY = "/data8/projets/Mila_covid19/output/covidb_full/blob"
IMAGING_LIST_FILENAME = "/data8/projets/Mila_covid19/data/studies_to_extract.csv"
DICOM_MAP_FILENAME = "/data8/projets/Mila_covid19/data/patient_infos/dicom_id_map_v2.csv"
DICOM_DIRECTORY = "/data8/projets/Mila_covid19/data/covid_citadel_pacs_v2/covid_citadel_pacs_take2"
SQLITE_DIRECTORY = "/data8/projets/Mila_covid19/output/covidb_full/sqlite"
CODE_DIRECTORY = "/data8/projets/Mila_covid19/code/lmullie/git_Mila_covid19"

dicom_id_map_rows = read_csv(DICOM_MAP_FILENAME)
DICOM_PATIENT_ID_MAP = {}
DICOM_STUDY_ID_MAP = {}

for dicom_id_map_row in dicom_id_map_rows:
  if len(dicom_id_map_row) == 0: continue
  DICOM_PATIENT_ID_MAP[str(dicom_id_map_row[2])] = str(dicom_id_map_row[0])
  DICOM_STUDY_ID_MAP[str(dicom_id_map_row[2])] = str(dicom_id_map_row[1])

TABLE_COLUMNS = {

  'patient_data': [
    'patient_site_uid', 'patient_uid', 'pcr_sample_time', 
    'patient_site_code', 'patient_covid_status', 'patient_age', 
    'patient_sex', 'patient_vital_status'
  ],

  'episode_data': [
    'patient_site_uid', 'episode_id', 'episode_unit_type', 'episode_start_time', 
    'episode_end_time', 'episode_description',
  ],

  'diagnosis_data': [
    'patient_site_uid', 'episode_id', 'diagnosis_type',
    'diagnosis_name', 'diagnosis_icd_code', 'diagnosis_time'
  ],

  'drug_data': [
    'patient_site_uid', 'drug_name', 
    'drug_start_time', 'drug_end_time',
    'drug_frequency', 'drug_roa'
  ],

  'lab_data': [
    'patient_site_uid', 'lab_name', 'lab_sample_site', 'lab_sample_time',
    'lab_result_time', 'lab_result_status', 'lab_result_units',
    'lab_result_string', 'lab_result_value'
  ],

  'observation_data': [
    'patient_site_uid', 'observation_name', 'observation_time', 
    'observation_value', #'observation_units'
  ],

  'pcr_data': [
    'patient_site_uid', 'pcr_name', 'pcr_sample_site', 'pcr_sample_time', 
    'pcr_result_time', 'pcr_result_value', 'pcr_result_status'
  ],

  'culture_data': [
    'patient_site_uid', 'culture_type', 'culture_specimen_type', 'culture_sample_time', 
    'culture_result_time', 'culture_growth_positive', 'culture_result_status'
  ],

  'imaging_data': [
    'patient_site_uid', 'imaging_accession_uid', 'imaging_modality', 'imaging_site'
  ],

  'slice_data': [
    'patient_site_uid', 'imaging_accession_uid', 'slice_study_instance_uid', 
    'slice_series_instance_uid', 'slice_data_uri', 'slice_view_position', 
    'slice_patient_position', 'slice_image_orientation', 'slice_image_position', 
    'slice_window_center', 'slice_window_width', 'slice_pixel_spacing', 
    'slice_thickness', 'slice_rows', 'slice_columns', 'slice_rescale_intercept', 
    'slice_rescale_slope'
  ]
}

CENSOR_COLUMNS = {
  'patient_data': [],
  'episode_data': ['episode_description'],
  'diagnosis_data': ['diagnosis_name', 'diagnosis_icd_code'],
  'drug_data': ['drug_name', 'drug_frequency', 'drug_roa'],
  'lab_data': ['lab_name', 'lab_sample_site'],
  'observation_data': ['observation_name'],
  'pcr_data': ['pcr_name', 'pcr_sample_site'],
  'culture_data': ['culture_type', 'culture_specimen_type'],
  'imaging_data': ['imaging_modality', 'imaging_site'],
  'slice_data': []
}

DRUG_SKIP_VALUES = [
  '*** rx a domicile', 
  '*attention: patient anticoagulé*',
  '*attention: catheter epidural en place*',
  'bilan comparatif des médicaments (bcm) au dossier.',
  '** protocole remap-cap (covid-19) **'
]

DRUG_ROUTE_MAP = {
  'sous-cutané': 'sc',
  'sous-cutané:': 'sc',
  'dans les oreilles': 'otic',
  'dans oreille droite': 'otic',
  'dans oreille gauche': 'otic',
  'ophthalmique': 'i-ocul',
  'dans les yeux': 'i-ocul',
  'dans l\'oeil droit': 'i-ocul',
  'dans l\'oeil gauche': 'i-ocul',
  'per os': 'po',
  'per os ou sublingual': 'po/sl',
  'via jéjunostomie': 'ng',
  'via gastrostomie': 'ng',
  'via tube nasogastro.': 'ng',
  'via levin': 'ng',
  'rince-bouche': 'buccal',
  'en gargarisme': 'buccal',
  'buccale': 'buccal',
  'irr.nasale': 'nasal',
  'dans une narine': 'nasal',
  'dans les narines': 'nasal',
  'nasale': 'nasal',
  'infiltration': 'infil',
  'transdermique': 't-dermal',
  'intra-dermique': 'i-dermal',
  'en injection locale': 'i-epidermal',
  'cathéter': 'iv',
  'i.v.': 'iv',
  'mini-perfuseur': 'iv',
  'i.v. perfusion': 'iv',
  'i.v. tubulure': 'iv',
  'i.v. soluté': 'iv',
  'i.v. / s.c.': 'iv/sc',
  'par voie centrale': 'iv',
  'i.m.': 'im',
  'i.m./i.v./s.c.': 'im/iv/sc',
  'i.m. / s.c.': 'im/sc',
  'i.m. / i.v.': 'im/iv',
  'perfusion s.c.': 'sc',
  'en appl. locale': 'topic',
  'en compresses': 'topic',
  'topique': 'topic',
  'intra-rectal': 'rectal',
  'voir directives': 'unknown',
  'transdermale': 't-dermal',
  'transmucosale': 't-mucos',
  'épidurale': 'epidur',
  'intra-rachidienne': 'i-spinal',
  'orale(s)': 'po',
  'sublinguale': 'sl',
  'sous la langue': 'sl',
  'nébulisation orale': 'respir',
  'en inhalation orale': 'respir',
  'en aérosol': 'respir',
  'vaginale': 'vagin',
  'dans le dialysat': 'hemo',
}

SIURG_OBSERVATION_NAMES = [
  'temperature', 'pouls', 'tension_systol', 
  'tension_diastol', 'sat_o2', 'rythme_resp'
]

LAB_PENDING_FLAGS = [
  'En attente'
]

LAB_CANCELLED_FLAGS = [
  'Test annulé', 'Test Annulé', 'ANN', 
  'ann', 'annulé', 'ANNULE', 'ANNULÉ',
  'test annulé', 'Annulé', 'ANNULe', 'annule'
]

LAB_SKIP_VALUES = [
  '.', '..', 
  '*00.0', '9*', '*9', 
  'att. hémolyse', 
  'durée gross. (sem.)', 
  'g10_sorgho d\'alep', 
  'volume 24 heures',
  'gb cell.souches',
  'hb cell.souches',
  'plt cell.souches',
  'cell.mononucléées (c.s.)',
  'cell.polynucléées (c.s.)',
  'gb cell.souches',
  'hb cell.souches',
  'plt cell.souches',
  'cell.mononucléées (c.s.)',
  'cell.polynucléées (c.s.)',
  'hb semi-quantitatif',
  'po2 sg cord.tc',
  'pco2 sg cord.tc',
  'sat o2 cordon art',
  'hco3 act.sg c.',
  'po2 sg cord.v.tc',
  'pco2 sg cord.tc',
  'sat o2 cordon vein',
  'hco3 act.sg c.v.',
  'bil.t.cordon',
  'ex.base sg cord.',
  'ex.base sg c. v.'
]

LAB_NAMES_MAP = {
  '% éosino.urin.': 'urinary_eosinophil_percent', 
  '25(oh)-vit. d': '25_oh_vitamin_d', 
  'a-1-antitryps. %': 'alpha1_antitrypsin_percent', 
  'a-1-glycoprot. %': 'alpha1_glycoprotein_percent', 
  'a-1-glycoprot., élec': 'alpha1_glycoprotein', #
  'a.foetoprotéine': 'alpha_fetoprotein', 
  'a.lactique (rés.prélim.)': 'lactic_acid', 
  'a1 antitrypsine': 'alpha_1_antitrypsin', 
  'a1-antitrypsine, élec': 'alpha1_antitrypsin', 
  'a2-macroglob. %': 'alpha2_macroglobulin_percent', 
  'a2-macroglob., élec': 'alpha2_macroglobulin', 
  'acth': 'adrenocorticotropic_hormone', 
  'alt': 'alanine_aminotransferase', 
  'arn vih-1': 'hiv1_rna', 
  'arn vih-1/log': 'hiv1_rna_log', 
  'ast': 'ast', 
  'ac fac.intrins.': 'intrinsic_factor_antibody', 
  'ac. valproïque': 'valproic_acid', 
  'acide folique': 'folic_acid', 
  'acide lac.art. ser.': 'arterial_lactic_acid', 
  'acide lactique': 'lactic_acid', 
  'acide urique': 'uric_acid', 
  'acides biliaires': 'biliary_acids', 
  'act. anti-xa bpm': 'anti_xa_bpm_activity', 
  'act. anti-xa rivaro.': 'anti_xa_rivaro_activity', 
  'acétaminophène': 'acetaminophen', 
  'ag carcino emb.': 'carcinoembryonic_antigen', 
  'albumine': 'albumin', 
  'albumine %': 'albumin_percent', 
  'albumine, liq.': 'albumin', 
  'albumine, urine': 'albumin', 
  'albumine, élec.': 'albumin', 
  'albumine-u 24 h': 'albumin', 
  'albumine-u mict.': 'albumin', 
  'ammoniac': 'ammonia', 
  'amylase, liq.': 'amylase', 
  'anti dna unité': 'anti_dna', 
  'anti héparine': 'anti_heparin', 
  'anti jo-1': 'anti_jo1', 
  'anti-ccp igg': 'anti_ccp_igg', 
  'anti-hbs unités': 'anti_hbs', 
  'anti-hcv s/co': 'anti_hcv', 
  'anti-microsomiaux (anti-tpo)': 'anti_tpo)', 
  'anti-récep.tsh': 'anti_tshr', 
  'anti-thyroglobuline (sér.)': 'anti_thyroglobulin', 
  'anti-transglutaminase (iga)': 'anti_transglutaminase', 
  'anticardio.igg': 'anticardiolipin_igg', 
  'anticardio.igm': 'anticardiolipin_igm', 
  'anticorps anti-gad': 'anti_gad', 
  'antigène prost.': 'prostate_specific_antigen', 
  'b-hcg (quant.)': 'beta_hcg', 
  'b2 microglob.': 'beta2_microglobulin', 
  'b2-glycopro.igg': 'beta2_glycoprotein', 
  'baso #': 'basophil_count', 
  'baso # (man)': 'basophil_count', 
  'benzo. (urine)*': 'benzodiazepines', 
  'benzo. totales*': 'benzodiazepines', 
  'bilirubine dir.': 'direct_bilirubin', 
  'bilirubine ind.': 'indirect_bilirubin', 
  'bilirubine tot.': 'total_bilirubin', 
  'bilirubine directe, liquide': 'direct_bilirubin', 
  'bilirubine, liq.': 'total_bilirubin', 
  'blaste # (man)': 'blast_count', 
  'c télopeptide s': 'c_telopeptide', 
  'c-anca pr3 val.': 'c_anca_pr3', 
  'c3': 'c3', 
  'c3/iga': 'c3/iga', 
  'c3/iga %': 'c3/iga %', 
  'c4': 'c4', 
  'ca 125': 'cancer_antigen_125', 
  'ca 15-3': 'cancer_antigen_15_3', 
  'ca 19-9': 'cancer_antigen_19_9', 
  'cd16+56 absolu': 'cd16_56_count', 
  'cd19 absolu': 'cd19_count', 
  'cd3 absolu': 'cd3_count', 
  'cd4 absolu': 'cd4_count', 
  'cd8 absolu': 'cd8_count', 
  'cenp-b': 'cenp_b', 
  'cgmh': 'mean_corpuscular_hemoglobin_concentration',
  'ck (au)': 'creatine_kinase', 
  'ckmb masse': 'ck_mb', 
  'cmv (charge virale)': 'cmv_rna', 
  'cmv igg unités': 'cmv_igg', 
  'cmv igm index': 'cmv_igm', 
  'co2 total': 'bicarbonate', 
  'ca ion.(ph:7.4).': 'ionized_calcium_ph74', 
  'ca ionisé act.': 'ionized_calcium', 
  'calcitonine': 'calcitonin', 
  'calcium total': 'total_calcium', 
  'calcium total corrigé': 'corrected_total_calcium', 
  'carbamazépine': 'carbamazepine', 
  'carboxyhb vein': 'carboxyhemoglobin', 
  'chlorure': 'chloride', 
  'chlorure (lcr)': 'chloride', 
  'chlorure veineux': 'chloride', 
  'chlorure, liq.': 'chloride', 
  'chlorure, mict.': 'chloride', 
  'cholestérol': 'cholesterol', 
  'cl seringue': 'chloride', 
  'cortisol (s)': 'cortisol', 
  'créatinine': 'creatinine', 
  'créatinine 24 h': 'creatinine', 
  'créatinine urine': 'creatinine', 
  'créatinine, liq.': 'creatinine', 
  'créatinine,mict.': 'creatinine', 
  'cryoglobuline': 'cryoglobulin',
  'cyclo.2 h post-d': 'cyclosporin_2h_post_dose', 
  'cyclos. pré-dose': 'cyclosporin_pre_dose', 
  'céruloplasmine': 'ceruloplasmin', 
  'd-dimère': 'd_dimer', 
  'digoxine': 'digoxin', 
  'décompte cell.tot. lba': 'cell_count', 
  'ebv-vca igm ind': 'anti_ebv_vca_igm', 
  'ebna1 igg index': 'anti_ebna1_igg', 
  'excès de base': 'base_excess', 
  'excès de base (v)': 'base_excess', 
  'ethyl glucuron.': 'ethyl_glucuronide',
  'f.rhumatoïde': 'rheumatoid_factor', 
  'fsh': 'follicle_stimulating_hormone', 
  'facteur ii': 'factor_ii', 
  'facteur v': 'factor_v', 
  'facteur vii': 'factor_vii', 
  'facteur viii': 'factor_viii', 
  'fer sérique': 'serum_iron', 
  'ferritine': 'ferritin', 
  'fibrinogène': 'fibrinogen', 
  'fibrinogène imm.': 'fibrinogen', 
  'gb': 'white_blood_cell_count', 
  'ggt': 'gamma_glutamyl_transferase', 
  'gr': 'red_blood_cell_count', 
  'gamma glob. %': 'gamma_globulin_percent', 
  'gamma globuline, élec': 'gamma_globulin', 
  'gap anion.': 'anion_gap', 
  'gl.blancs l.asc': 'white_blood_cell_count', 
  'gl.blancs l.bio': 'white_blood_cell_count', 
  'gl.blancs l.ple': 'white_blood_cell_count', 
  'gl.blancs lcr': 'white_blood_cell_count', 
  'gl.rou. l.bio': 'red_blood_cell_count', 
  'gl.rou. lcr': 'red_blood_cell_count', 
  'gl.rou.l.asc': 'red_blood_cell_count', 
  'globulines': 'globulins', 
  'glucose': 'glucose', 
  'glucose (lcr)': 'glucose', 
  'glucose ac': 'glucose', 
  'glucose adbd': 'glucose', 
  'glucose, liq.': 'glucose', 
  'hbv dna': 'hbv_dna', 
  'hco3 actuel': 'bicarbonate', 
  'hco3 actuel (v)': 'bicarbonate', 
  'hdl-cholestérol': 'hdl_cholesterol', 
  'hsv-1 index': 'anti_hsv1_igg', 
  'hsv-2 index': 'anti_hsv2_igg', 
  'haptoglobine': 'haptoglobin', 
  'haptoglobine %': 'haptoglobin_percent', 
  'haptoglobine, élec.': 'haptoglobin', 
  'hb': 'hemoglobin', 
  'hb l.bio': 'hemoglobin', 
  'homocystéine': 'homocysteine', 
  'iga': 'iga', 
  'ige': 'ige', 
  'igg': 'igg', 
  'igm': 'igm', 
  'indice alb/créa': 'albumin_creatinine_ratio', 
  'k seringue': 'potassium', 
  'k, selles': 'potassium', 
  'kappa libre': 'free_kappa', 
  'ld': 'lactate_dehydrogenase', 
  'ld, liq.': 'lactate_dehydrogenase', 
  'ldl-c (calc)': 'ldl_cholesterol', 
  'lh': 'luteinizing_hormone', 
  'lambda libre': 'free_lambda', 
  'lipase.': 'lipase', 
  'lympho #': 'lymphocyte_count', 
  'lympho # (man)': 'lymphocyte_count', 
  'lympho % lba': 'lymphocyte_count', 
  'magnésium': 'magnesium', 
  'memb. basale glom.': 'anti_gbm_igg', 
  'mono #': 'monocyte_count', 
  'mono # (man)': 'monocyte_count', 
  'mono-macro lba': 'mono_macro_count', 
  'myélocyte # (man)': 'myelocyte_count', 
  'métamyélocyte # (man)': 'metamyelocyte_count', 
  'métanéphrine libre': 'free_metanephrine', 
  'méthémoglob vein': 'methemoglobin', 
  'nt pro-bnp': 'nt_pro_bnp', 
  'na seringue': 'sodium', 
  'nb cellules/ml': 'total_cell_count', 
  'neutro #': 'neutrophil_count', 
  'neutro # (man)': 'neutrophil_count', 
  'neutro % lba': 'neutrophil_count', 
  'non-hdl cholest': 'non_hdl_cholesterol', 
  'norépinéphrine': 'norepinephrine',
  'normétanéphrine libre': 'free_normetanephrine', 
  'osm.calc.selles': 'osmolality', 
  'osmo. (plasma)': 'osmolality', 
  'osmolalité calculée': 'osmolality', 
  'osmolalité urine': 'osmolality', 
  'oxycodone qual. (mict.)': 'oxycodone', 
  'p-anca mpo val.': 'p_anca_mpo', 
  'plt': 'platelets', 
  'plt sur lame': 'platelets', 
  'pth intacte': 'intact_pth', 
  'ptt-la': 'ptt_lupus_anticoagulant', 
  'ptt-la (1:1)': 'ptt_lupus_anticoagulant_11', 
  'parvo b19 igg index': 'anti_parvo_b19_igg', 
  'peptide-c': 'c_peptide', 
  'phosphatase alc.': 'alkaline_phosphatase', 
  'phosphore': 'phosphate', 
  'phénobarbital': 'phenobarbital', 
  'phénytoïne': 'phenytoin', 
  'pic mono. 1': 'monoclonal_peak', 
  'pic mono. 1 %': 'monoclonal_peak_percent', 
  'potassium': 'potassium', 
  'potassium veineux': 'potassium', 
  'potassium, mict.': 'potassium', 
  'procalcitonine': 'procalcitonin', 
  'prolactine': 'prolactin', 
  'promyélocyte # (man)': 'promyelocyte_count', 
  'prot u/créat u': 'protein_creatinine_ratio', 
  'protéine c réac.': 'c_reactive_protein', 
  'protéines (lcr)': 'total_protein', 
  'protéines 24 h': 'total_protein', 
  'protéines tot.mict.': 'total_protein', 
  'protéines totales': 'total_protein', 
  'protéines urine': 'total_protein', 
  'protéines, liq.': 'total_protein', 
  'rnp': 'anti_rnp_igg', 
  'rvvt 1:1': 'rvvt_11', 
  'rvvt confirme': 'rvvt_confirmation', 
  'rvvt dépistage': 'rvvt_screen', 
  'rétic#': 'reticulocyte_count', 
  'scl70': 'anti_scl70_igg', 
  'shbg': 'sex_hormone_binding_globulin', 
  'sm': 'sm', 
  'ssa': 'anti_ssa', 
  'ssb': 'anti_ssb', 
  'salicylates': 'salicylates', 
  'sat o2 art': 'arterial_o2_sat', 
  'sat o2 vein': 'venous_o2_sat', 
  'sodium': 'sodium', 
  'sodium veineux': 'sodium', 
  'sodium, mict.': 'sodium', 
  'sodium, selles': 'sodium', 
  'stab # (man)': 'stab_count', 
  'staclot-la: buffer': 'staclot_la_buffer', 
  'staclot-la: phospho': 'staclot_la_phospho', 
  't.céph.(1:1)': 'partial_thromboplastin_time_11', 
  't.céphaline sec': 'partial_thromboplastin_time', 
  't.thrombine': 'thrombin_time', 
  't3 libre': 'free_t3', 
  't4 libre': 'free_t4', 
  'tgmh': 'mean_corpuscular_hemoglobin_concentration', 
  'tsh': 'thyroid_stimulating_hormone', 
  'tacrolimus': 'tacrolimus', 
  'testostérone t': 'total_testosterone', 
  'thyroglobuline': 'thyroglobulin', 
  'toxo igm(index)': 'anti_toxoplasma_igm', 
  'toxoplasma igg': 'anti_toxoplasma_igg', 
  'transferrine': 'transferrin', 
  'transferrine %': 'transferrine_saturation', 
  'transferrine, élec.': 'transferrin', 
  'transthyrétine': 'transthyretin', 
  'triglycérides': 'triglycerides', 
  'triglycérides, liq.': 'triglycerides', 
  'tropt hs sous réserve': 'hs_troponin_t', 
  'troponine-t hs': 'hs_troponin_t', 
  'urée': 'urea', 
  'urée, mict.': 'urea', 
  'vgm': 'mean_cell_volume', 
  'vpm': 'mean_platelet_volume', 
  'vs': 'erythrocyte_sedimentation_rate', 
  'vanco post dose': 'vancomycin_post_dose', 
  'vanco pré dose': 'vancomycin_pre_dose', 
  'vancomycine': 'vancomycin', 
  'vitamine a': 'vitamin_a', 
  'vitamine b12': 'vitamin_b12', 
  'vitamine e': 'vitamin_e', 
  'voriconazole': 'voriconazole', 
  'pco2 tc': 'pco2', 
  'pco2 veineux tc': 'pco2', 
  'po2 tc': 'po2', 
  'po2 veineux tc': 'po2', 
  'éosino #': 'eosinophil_count', 
  'éosino # (man)': 'eosinophil_count', 
  'éosino lba %': 'eosinophil_percent', 
  'éthanol': 'ethanol',
  'éthanol (ur)': 'ethanol',
  'aldostérone sér.': 'aldosterone',
  'phosphore, mict.': 'phosphate',
  'arn-hcv/copies': 'hcv_rna',
  'arn-hcv/log': 'hcv_rna_log',
  'magnésium, mict': 'magnesium',
  'dhea-so4': 'dhea_so4',
  'gl.rou. l.ple': 'red_blood_cell_count',
  'carboxyhb art': 'carboxyhemoglobin',
  'méthémoglob art': 'methemoglobin',
  'gl.rou. l.ple': 'red_blood_cell_count',
  'fructosamine': 'fructosamine',
  'fructo/prot': 'fructosamine_prot',
  'm3_asper.fumig.': 'aspergillus_antibodies',
  'lamotrigine': 'lamotrigine',
  'atiii fonc.': 'antithrombin_iii',
  'hbs ag quantitatif': 'hbv_sag',
  'varicelle igg index': 'anti_vzv_igg',
  'hb semi-quantitatif': 'free_hemogloin',
  'hb plasmat. dosage': 'plasma_hemoglobin',
  'act.anti-xa hép.std': 'anti_xa',
  'hb semi-quantitatif': 'hemoglobin_semiquant',
  'tobra post dose': 'tobramycin_post_dose',
  'po2 art ecmo': 'po2',
  'pco2 art ecmo': 'pco2',
  'sat o2 art ecmo': 'arterial_o2_sat',
  'excès base art ecmo': 'base_excess',
  'excès base vein ecmo': 'base_excess',
  'po2 art ecmo': 'po2',
  'pco2 art ecmo': 'pco2',
  'sat o2 art ecmo': 'arterial_o2_sat',
  'hco3 art ecmo': 'bicarbonate',
  'pco2 vein ecmo': 'venous_pco2',
  'po2 vein ecmo': 'venous_po2',
  'sat o2 vein ecmo': 'venous_o2_sat',
  'hco3 vein ecmo': 'bicarbonate',
  'g6pd quantit.': 'g6pd_quantitative',
  '6pgd quantit.': 'g6pd_quantitative',
  'enz.conversion': 'angiotensin_converting_enzyme',
  'éthanol (p)': 'ethanol',
  'amylase, mict.': 'amylase'
}

NP_TO_FIO2_MAP = {
  '0.5': '22',
  '1.0': '24',
  '1.5': '26',
  '2.0': '28',
  '2.5': '30',
  '3.0': '32',
  '3.5': '34',
  '4.0': '36',
  '4.5': '38', 
  '5.0': '40',
  '5.5': '42',
  '6.0': '44',
  '6.5': '46',
  '7.0': '48',
  '7.5': '50',
  '8.0': '52',
  '8.5': '54',
  '9.0': '56',
  '9.5': '58',
  '10.0': '60'
}
