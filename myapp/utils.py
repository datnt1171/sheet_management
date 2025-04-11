import pandas as pd
import numpy as np

def retrieve_consumption(table_data):
    
    # --- Convert data to DataFrame ---
    df = pd.DataFrame(table_data)
    df.columns = [ "Step", "Step Name", "Viscosity & Wet Mill Thickness (EN)", "Viscosity & Wet Mill Thickness (VN)", 
                    "SPEC EN", "SPEC VN", "Hold Time (min)", "Chemical Mixing Code", "Consumption (per m2)", 
                    "Material Code", "Material Name", "Ratio", "Qty (per m2)", "Unit", 
                    "Check Result", "Correct Action", "TE-1's Sign", "Customer's Sign" ]

    df_bak = df.copy()
    df.replace('', None, inplace=True)
    df['Step'] = df['Step'].ffill()
    df['Viscosity'] = df["Viscosity & Wet Mill Thickness (VN)"].str.extract(r"(\d+)\s*giây").astype("float")
    df["Viscosity"] = df.groupby("Step")["Viscosity"].ffill()

    grouped_df = (
        df.dropna(subset=["Material Name"])
        .groupby(["Step", "Viscosity"])["Material Name"]
        .apply(lambda x: sorted(map(str.strip, x.dropna().tolist())))
        .reset_index()
    )

    df_formular = pd.read_excel(r"D:\VL1251\systemsheet\sheet_management\mapper.xlsx", sheet_name="test")

    group_material_map = (
        df_formular
        .groupby(["group", "Viscosity"])["Material Name"]
        .apply(lambda x: sorted(x.tolist()))
        .unstack(fill_value=[])
        .to_dict(orient="index")
    )

    def find_matching_group(material_list, viscosity):
        for group, viscosity_dict in group_material_map.items():
            if viscosity in viscosity_dict and material_list == viscosity_dict[viscosity]:
                return group
        return None

    grouped_df["Group"] = grouped_df.apply(
        lambda row: find_matching_group(row["Material Name"], row["Viscosity"]), axis=1
    )
    df = df.merge(grouped_df[['Step', 'Group']], on="Step", how="left")

    df = df.merge(
        df_formular,
        how='left',
        left_on=['Material Name', 'Group', 'Viscosity'],
        right_on=['Material Name', 'group', 'Viscosity']
    )

    df['Ratio'] = df['ratio']
    df['Qty (per m2)'] = df['per_m2']

    df.drop(columns=['Viscosity', 'Group', 'group', 'ratio', 'per_m2'], inplace=True)
    df.replace(np.nan, '', inplace=True)
    df['Step'] = df_bak['Step']
    
    # --- Convert DataFrame to list of lists ---
    data_2d_array = df.values.tolist()
    return data_2d_array