from django.db import models

class Table(models.Model):
    name = models.CharField(max_length=255)
    name_verbose = models.CharField(max_length=255, null=True)
    sheen = models.CharField(max_length=20, null=True)
    dft = models.CharField(max_length=255, null=True)
    chemical = models.CharField(max_length=255, null=True)
    substrate = models.CharField(max_length=255, null=True)
    grain_filling = models.CharField(max_length=255, null=True)
    developer = models.CharField(max_length=255, null=True)
    
    # If these are numerical or more structured, adjust field types as needed
    chemical_waste = models.CharField(max_length=255, null=True)
    conveyor_speed = models.CharField(max_length=255, null=True)
        
    data = models.JSONField(default=list)  # Stores the table's data

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    blueprint = models.ImageField(upload_to='blueprints/', null=True, blank=True)
    panel = models.ImageField(upload_to='panels/', null=True, blank=True)

    factory_name = models.CharField(max_length=255, null=True)
    collection = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        return self.name
