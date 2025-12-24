"""
Vendor models for managing suppliers and their pricing.
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Vendor(models.Model):
    """
    Represents a vendor/supplier who provides products.
    """
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
    
    def __str__(self):
        return self.name


class VendorPrice(models.Model):
    """
    Tracks the latest scraped price for a vendor's product.
    """
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='prices'
    )
    vendor_sku = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='AUD')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'vendor_sku']
        ordering = ['-last_updated']
        verbose_name = 'Vendor Price'
        verbose_name_plural = 'Vendor Prices'
    
    def __str__(self):
        return f"{self.vendor.name} - {self.vendor_sku}: ${self.price}"