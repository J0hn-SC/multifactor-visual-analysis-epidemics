import pandas as pd
import re

cases_df_dirty = pd.read_csv('./original_data/20200221-Upate-LGA-NSW.csv')
# covid_df = cases_df_dirty.dropna().convert_dtypes()

cases_df_dirty['check_male'] = cases_df_dirty[[c for c in cases_df_dirty.columns if 'MaleAge' in c]].sum(axis=1)
cases_df_dirty['diff'] = cases_df_dirty['check_male'] - cases_df_dirty['TotalMale(allages)']
print(cases_df_dirty['diff'])


cases_df_dirty['totalpop'] = cases_df_dirty['Female'] + cases_df_dirty['Male']
cases_df_dirty['diffpop'] = cases_df_dirty['Population'] - cases_df_dirty['totalpop']
print(cases_df_dirty['totalpop'])
