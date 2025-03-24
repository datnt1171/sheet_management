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
# List all tables
def table_list(request):
    tables = Table.objects.all()
    return render(request, 'myapp/index.html', {'tables': tables})

# Create a new table with a 5x5 empty grid
def create_table(request):
    if request.method == 'POST':
        table_name = request.POST.get('name')
        if table_name:
            empty_data = [['' for _ in range(5)] for _ in range(5)]
            new_table = Table.objects.create(name=table_name, data=empty_data)
            return redirect('edit_table', table_id=new_table.id)
    return render(request, 'myapp/create_table.html')

# Edit table data
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table_data_json = json.dumps(table.data)  # Convert to JSON for safe rendering
    return render(request, 'myapp/edit_table.html', {'table': table, 'table_data_json': table_data_json})

# Save table data
@api_view(['POST'])
def save_table(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TableSerializer(table, data={'data': request.data}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Table saved successfully!'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_table_with_temp_name(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
        temp_table = Table.objects.create(
            name=f"{table.name}_temp",
            data=request.data
        )
        df = pd.DataFrame(request.data)
        df.columns = [ "Step", "Step Name", "Viscosity & Wet Mill Thickness (EN)", "Viscosity & Wet Mill Thickness (VN)", 
                                "SPEC EN", "SPEC VN", "Hold Time (min)", "Chemical Mixing Code", "Consumption (per m2)", 
                                "Material Code","Material Name", "Ratio", "Qty (per m2)", "Unit", 
                                "Check Result", "Correct Action", "TE-1's Sign", "Customer's Sign" ]
        df['Step'].ffill(inplace=True)
        grouped_df = df.groupby('Step')['Material Code'].apply(lambda x: x.dropna().tolist()).reset_index()
        df_formular = pd.read_excel(r"D:\VL1251\sheet\mapper.xlsx", sheet_name='test')
        group_material_map = df_formular.groupby("group")["Material Name"].apply(lambda x: sorted(x.tolist())).to_dict()
        def find_matching_group(material_list):
            for group, materials in group_material_map.items():
                if sorted(material_list) == materials:
                    return group
            return None
        grouped_df["Matched Group"] = grouped_df["Material Code"].apply(find_matching_group)
        df_1 = df_1.merge(df_formular, how='left', left_on=['Matched Group','Material Code'], right_on=['group','Material Name'])
        return Response({'success': True, 'new_table_id': temp_table.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
