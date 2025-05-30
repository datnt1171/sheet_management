from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Table
import json

from .utils import retrieve_consumption


def is_crud_user(user):
    return user.groups.filter(name='CRUD').exists()


# List all tables
@login_required
def index(request):
    tables = list(Table.objects.values(
        'id', 'name', 'factory_name', 'collection',
        'chemical', 'developer', 'created_at', 'updated_at'
    ))

    for table in tables:
        table['created_at'] = table['created_at'].strftime('%Y-%m-%d %H:%M') if table['created_at'] else ''
        table['updated_at'] = table['updated_at'].strftime('%Y-%m-%d %H:%M') if table['updated_at'] else ''

    is_crud_user_flag = is_crud_user(request.user)

    return render(request, 'myapp/index.html', {
        'tables': tables,
        'is_crud_user': is_crud_user_flag,
    })

# Create a new table with a 5x5 empty grid
@login_required
@user_passes_test(is_crud_user)
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
@login_required
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
@login_required
@user_passes_test(is_crud_user)
@api_view(['POST'])
def save_table(request, table_id):
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

    #  Get headerData from the nested dict
    header_data = request.data.get('headerData', {})  # get returns {} if not found


    for field in [
        'name',
        'name_verbose', 'sheen', 'dft', 'chemical', 'substrate',
        'grain_filling', 'developer', 'chemical_waste', 'conveyor_speed',
        'factory_name', 'collection'
    ]:
        setattr(table, field, header_data.get(field, ''))

    #  Get and set the table data
    table_data = request.data.get('data', [])
    table.data = table_data

    table.save()

    return Response({'message': 'Table saved successfully!'}, status=status.HTTP_200_OK)

@login_required
@user_passes_test(is_crud_user)
@api_view(['POST'])
def save_table_with_consumption(request, table_id):
    try:
        # --- Extract incoming data ---
        header_data = request.data.get("headerData", {})
        table_data = request.data.get("data", [])

        # --- Get original table ---
        table = Table.objects.get(id=table_id)
        data_2d_array = retrieve_consumption(table_data)
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

