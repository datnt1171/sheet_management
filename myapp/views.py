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
def table_list(request):
    tables = Table.objects.all()
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
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table_data_json = json.dumps(table.data)

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
    }

    return render(request, 'myapp/edit_table.html', {
        'table': table,
        'table_data_json': table_data_json,
        'header_data': header_data,
    })

# Save table data
@api_view(['POST'])
@api_view(['POST'])
def save_table(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

    # Extract header fields from the request
    header_data = {
        'name_verbose': request.data.get('name_verbose'),
        'sheen': request.data.get('sheen'),
        'dft': request.data.get('dft'),
        'chemical': request.data.get('chemical'),
        'substrate': request.data.get('substrate'),
        'grain_filling': request.data.get('grain_filling'),
        'developer': request.data.get('developer'),
        'chemical_waste': request.data.get('chemical_waste'),
        'conveyor_speed': request.data.get('conveyor_speed'),
    }

    # Update the header fields in the table
    for field, value in header_data.items():
        setattr(table, field, value)
    
    # Save the updated header fields
    table.save()

    # Extract the table data from the request
    table_data = request.data.get('data')

    # Update the table's data field
    if table_data:
        table.data = table_data

    # Save the table data
    table.save()

    return Response({'message': 'Table saved successfully!'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_table_with_temp_name(request, table_id):
    try:
        
        df = pd.DataFrame(request.data)

        df.columns = [ "Step", "Step Name", "Viscosity & Wet Mill Thickness (EN)", "Viscosity & Wet Mill Thickness (VN)", 
                                        "SPEC EN", "SPEC VN", "Hold Time (min)", "Chemical Mixing Code", "Consumption (per m2)", 
                                        "Material Code","Material Name", "Ratio", "Qty (per m2)", "Unit", 
                                        "Check Result", "Correct Action", "TE-1's Sign", "Customer's Sign"]
        df_bak = df.copy()
        df.replace('', None, inplace=True)
        df['Step'] = df['Step'].ffill()
        df['Viscosity'] = df["Viscosity & Wet Mill Thickness (VN)"].str.extract(r"(\d+)\s*giây").astype("float")
        df["Viscosity"] = df.groupby("Step")["Viscosity"].ffill()
        grouped_df = (
            df.dropna(subset=["Material Name"])  # Remove rows where Material Name is NaN
            .groupby(["Step", "Viscosity"])["Material Name"]
            .apply(lambda x: sorted(map(str.strip, x.dropna().tolist())))  # Trim spaces & sort
            .reset_index()
        )

        df_formular = pd.read_excel(r"D:\VL1251\systemsheet\sheet_management\mapper.xlsx", sheet_name="test")

        group_material_map = (
            df_formular
            .groupby(["group", "Viscosity"])["Material Name"]
            .apply(lambda x: sorted(x.tolist()))  # Sort Material Names
            .unstack(fill_value=[])  # Convert to dictionary-like structure
            .to_dict(orient="index")  # Convert to dictionary
        )

        def find_matching_group(material_list, viscosity):
            for group, viscosity_dict in group_material_map.items():
                if viscosity in viscosity_dict and material_list == viscosity_dict[viscosity]:
                    return group
            return None  # Return None if no match is found

        grouped_df["Group"] = grouped_df.apply(lambda row: find_matching_group(row["Material Name"], row["Viscosity"]), axis=1)
        df = df.merge(grouped_df[['Step','Group']], on="Step", how="left")
        
        df = df.merge(df_formular,
        how='left',
        left_on = ['Material Name','Group','Viscosity'],
        right_on= ['Material Name','group','Viscosity'])
        
        df['Ratio'] = df['ratio']
        df['Qty (per m2)'] = df['per_m2']

        df.drop(columns=['Viscosity','Group','group','ratio','per_m2'], inplace=True)
        df.replace(np.nan, '', inplace=True)
        df['Step'] = df_bak['Step']
        data_2d_array = df.values.tolist()
        table = Table.objects.get(id=table_id)
        temp_table = Table.objects.create(
            name=f"{table.name}_temp",
            data=data_2d_array
        )
        return Response({'success': True, 'new_table_id': temp_table.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
