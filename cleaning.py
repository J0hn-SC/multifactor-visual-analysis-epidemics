import pandas as pd
import re

# Carga
cases_df_dirty = pd.read_csv('cases_NSW.csv')
covid_df = cases_df_dirty.dropna().convert_dtypes()

census_df = pd.read_csv('20200221-Upate-LGA-NSW.csv')
census_df = census_df.dropna().convert_dtypes()

# Extraer área numérica
def extraer_area(valor):
    if isinstance(valor, (int, float)):
        return valor
    if pd.isna(valor):
        return None
    try:
        valor = str(valor).replace(",", "").strip()
        match = re.search(r"(\d+(?:\.\d+)?)$", valor)
        if match:
            return float(match.group(1))
    except:
        pass
    return None

census_df['Area'] = census_df['Area'].apply(extraer_area)
census_df["lga_code19"] = census_df["LGA_code"].astype(str).str.extract("(\d+)")

census_df.loc[census_df["Population"] == 0, "Population"] = None
census_df["Population_Density"] = census_df["Population"] / census_df["Area"]

total_cases = covid_df.groupby("lga_code19").size()
total_cases_df = total_cases.reset_index(name="TotalCases")
census_df = census_df.merge(total_cases_df, on="lga_code19", how="left")
census_df["TotalCases"] = census_df["TotalCases"].fillna(0)
census_df["CasesPerPerson"] = census_df["TotalCases"] / census_df["Population"]
census_df["CasesPer100k"] = census_df["CasesPerPerson"] * 100_000


census_df["Pct_0_1_Bedroom"] = (census_df["NoneBedroom"] + census_df["1Bedroom"]) / (
    census_df["NoneBedroom"] + census_df["1Bedroom"] + census_df["2Bedrooms"] +
    census_df["3Bedrooms"] + census_df["4Bedrooms"] + census_df["5Bedrooms"] +
    census_df["Bedrooms(Over6)"] + census_df["NotStated"]
)

# Personas por habitación (si AverageBedroom no es cero)
census_df["Persons_per_Bedroom"] = census_df["AverageHouseSize"] / census_df["AverageBedroom"]

census_df["Young"] = census_df[["MaleAge(0-14)", "MaleAge(15-24)", "FemaleAge(0-14)", "FemaleAge(15-24)"]].sum(axis=1)
census_df["Adult"] = census_df[["MaleAge(25-34)", "MaleAge(35-44)", "MaleAge(45-54)",
                                "FemaleAge(25-34)", "FemaleAge(35-44)", "FemaleAge(45-54)"]].sum(axis=1)
census_df["Elderly"] = census_df[["MaleAge(55-64)", "MaleAge(65-74)", "MaleAge(75-84)", "MaleAge(0ver85)",
                                  "FemaleAge(55-64)", "FemaleAge(65-74)", "FemaleAge(75-84)", "FemaleAge(0ver85)"]].sum(axis=1)


covid_df.to_csv("covid_clean.csv", index=False)
census_df["lga_code19_2"] = census_df["LGA_code"].astype(str).str.extract("(\d+)")
census_df.to_csv("census_clean.csv", index=False)