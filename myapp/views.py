from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Table
import json
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
