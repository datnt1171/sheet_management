from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from myapp.serializers import TableSerializer

from .models import Table
import json

import pandas as pd
import numpy as np
# List all tables
def index(request):
    tables = Table.objects.all().order_by('-updated_at')  # optional ordering
    return render(request, 'myapp/index.html', {'tables': tables})

# Create a new table with a 5x5 empty grid
def create_table(request):
    if request.method == 'POST':
        table_name = request.POST.get('name')

        if Table.objects.filter(name=table_name).exists():
            return render(request, 'myapp/create_table.html', {
                'error': 'Table name already exists'
            })

        new_table = Table.objects.create(name=table_name)
        return redirect('edit_table', table_id=new_table.id)

    return render(request, 'myapp/create_table.html')

# Edit table data
@csrf_exempt
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    # Handle image upload
    if request.method == 'POST' and request.FILES:
        if 'blueprint' in request.FILES:
            table.blueprint = request.FILES['blueprint']
        if 'panel' in request.FILES:
            table.panel = request.FILES['panel']
        table.save()
        return redirect('edit_table', table_id=table.id)

    # Convert table data to JSON
    table_data_json = json.dumps(table.data or [])

    # Prepare header data for rendering
    header_data = {
        'name_verbose': table.name_verbose,
        'sheen': table.sheen,
        'dft': table.dft,
        'chemical': table.chemical,
        'substrate': table.substrate,
        'grain_filling': table.grain_filling,
        'developer': table.developer,
        'chemical_waste': table.chemical_waste,
        'conveyor_speed': table.conveyor_speed,
        'factory_name': table.factory_name,
        'collection': table.collection
    }

    return render(request, 'myapp/edit_table.html', {
        'table': table,
        'table_data_json': table_data_json,
        'header_data': header_data,
    })

# Save table data
@api_view(['POST'])
def save_table(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Get headerData from the nested dict
    header_data = request.data.get('headerData', {})  # get returns {} if not found


    for field in [
        'name',
        'name_verbose', 'sheen', 'dft', 'chemical', 'substrate',
        'grain_filling', 'developer', 'chemical_waste', 'conveyor_speed',
        'factory_name', 'collection'
    ]:
        setattr(table, field, header_data.get(field, ''))

    # ✅ Get and set the table data
    table_data = request.data.get('data', [])
    table.data = table_data

    table.save()

    return Response({'message': 'Table saved successfully!'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_table_with_consumption(request, table_id):
    try:
        # --- Extract incoming data ---
        header_data = request.data.get("headerData", {})
        table_data = request.data.get("data", [])

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

        # --- Get original table ---
        table = Table.objects.get(id=table_id)

        # --- Create temp table with copied + new header data ---
        consumption_table = Table.objects.create(
            name=f"{table.name}_consumption",
            name_verbose=header_data.get("name_verbose", ""),
            sheen=header_data.get("sheen", ""),
            dft=header_data.get("dft", ""),
            chemical=header_data.get("chemical", ""),
            substrate=header_data.get("substrate", ""),
            grain_filling=header_data.get("grain_filling", ""),
            developer=header_data.get("developer", ""),
            chemical_waste=header_data.get("chemical_waste", ""),
            conveyor_speed=header_data.get("conveyor_speed", ""),
            data=data_2d_array,
            factory_name=header_data.get("factory_name", ""),
            collection=header_data.get("collection", ""),
        )

        return Response({'success': True, 'new_table_id': consumption_table.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

