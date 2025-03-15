from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
def save_table(request, table_id):
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        try:
            # Parse the incoming data only once
            table_data = json.loads(request.POST.get('data'))
            table.data = table_data
            table.save()
            return JsonResponse({'message': 'Table saved successfully!'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def save_table_with_temp_name(request, table_id):
    if request.method == 'POST':
        try:
            # Parse the request data
            request_data = json.loads(request.body)
            new_table_name = request_data.get('name')
            table_data = request_data.get('data')
            
            # Create a new table with the modified name and data
            new_table = Table.objects.create(name=new_table_name, data=table_data)

            # Return the ID of the new table
            return JsonResponse({
                'success': True,
                'new_table_id': new_table.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)
