"""
Export models for managing data exports to marketplaces.
"""
from django.db import models
from django.utils import timezone


class ExportArtifact(models.Model):
    """
    Tracks generated export files for marketplaces.
    """
    EXPORT_TYPES = [
        ('price', 'Price Export'),
        ('inventory', 'Inventory Export'),
        ('full', 'Full Export'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    store = models.ForeignKey(
        'marketplace.Store',
        on_delete=models.CASCADE,
        related_name='exports'
    )
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='exports',
        null=True,
        blank=True
    )
    export_type = models.CharField(
        max_length=20,
        choices=EXPORT_TYPES,
        default='full'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # File information
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.IntegerField(default=0)  # in bytes
    
    # Statistics
    total_products = models.IntegerField(default=0)
    exported_products = models.IntegerField(default=0)
    skipped_products = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Export Artifact'
        verbose_name_plural = 'Export Artifacts'
    
    def __str__(self):
        return f"{self.filename} - {self.status}"