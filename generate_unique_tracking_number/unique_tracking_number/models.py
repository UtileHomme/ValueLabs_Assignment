from django.db import models
import uuid

# Create your models here.

class GenerateUniqueTrackingNumber(models.Model):
    tracking_number = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    origin_country_id = models.CharField(max_length=2)
    destination_country_id = models.CharField(max_length=2)
    weight = models.DecimalField(max_digits=6, decimal_places=3)
    customer_id = models.UUIDField(default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_slug = models.SlugField(max_length=255)
    
    class Meta:  
        indexes = [
            models.Index(fields=['tracking_number']),
        ]
    
    def __str__(self):
        return self.tracking_number

