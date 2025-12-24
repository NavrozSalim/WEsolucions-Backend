"""
Marketplace models for managing stores and pricing/inventory settings.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Marketplace(models.Model):
    """
    Represents a marketplace platform (e.g., eBay, Amazon, MyDeal).
    """
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Marketplace'
        verbose_name_plural = 'Marketplaces'
    
    def __str__(self):
        return self.name


class Store(models.Model):
    """
    Represents a store within a marketplace.
    """
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name='stores'
    )
    name = models.CharField(max_length=255)
    api_key_enc = models.TextField(blank=True)
    settings = models.JSONField(default=dict, blank=True)
    
    # Scraping configuration
    scraping_enabled = models.BooleanField(default=True)
    scraping_interval_hours = models.IntegerField(default=24)
    last_scrape_time = models.DateTimeField(null=True, blank=True)
    price_update_enabled = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'
    
    def __str__(self):
        return f"{self.name} ({self.marketplace.name})"


class PriceRange(models.Model):
    """
    Reusable price range model for both price and inventory settings.
    """
    from_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    to_value = models.CharField(max_length=20, default="MAX")  # "MAX" or numeric value
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_value', 'to_value']
        ordering = ['from_value']
        verbose_name = 'Price Range'
        verbose_name_plural = 'Price Ranges'
    
    def __str__(self):
        return f"${self.from_value} - {self.to_value}"


class StorePriceSettings(models.Model):
    """
    Store- and vendor-specific price settings.
    """
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='price_settings_by_vendor'
    )
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='store_price_settings'
    )
    
    # Tax and fees
    purchase_tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    marketplace_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Minimum margin
    min_margin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['store', 'vendor']
        verbose_name = 'Store Price Settings'
        verbose_name_plural = 'Store Price Settings'
    
    def __str__(self):
        return f"{self.store.name} - {self.vendor.name} Price Settings"


class PriceRangeMargin(models.Model):
    """
    Margin settings for specific price ranges.
    """
    price_settings = models.ForeignKey(
        StorePriceSettings,
        on_delete=models.CASCADE,
        related_name='price_range_margins'
    )
    price_range = models.ForeignKey(
        PriceRange,
        on_delete=models.CASCADE
    )
    margin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    dont_pay_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        unique_together = ['price_settings', 'price_range']
        ordering = ['price_range__from_value']
        verbose_name = 'Price Range Margin'
        verbose_name_plural = 'Price Range Margins'
    
    def __str__(self):
        return f"{self.price_range} - {self.margin_percentage}% margin"


class StoreInventorySettings(models.Model):
    """
    Store- and vendor-specific inventory settings.
    """
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='inventory_settings_by_vendor'
    )
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='store_inventory_settings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['store', 'vendor']
        verbose_name = 'Store Inventory Settings'
        verbose_name_plural = 'Store Inventory Settings'
    
    def __str__(self):
        return f"{self.store.name} - {self.vendor.name} Inventory Settings"


class InventoryRangeMultiplier(models.Model):
    """
    Inventory multipliers for specific price ranges.
    """
    inventory_settings = models.ForeignKey(
        StoreInventorySettings,
        on_delete=models.CASCADE,
        related_name='inventory_range_multipliers'
    )
    price_range = models.ForeignKey(
        PriceRange,
        on_delete=models.CASCADE
    )
    inventory_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        unique_together = ['inventory_settings', 'price_range']
        ordering = ['price_range__from_value']
        verbose_name = 'Inventory Range Multiplier'
        verbose_name_plural = 'Inventory Range Multipliers'
    
    def __str__(self):
        return f"{self.price_range} - {self.inventory_multiplier}x multiplier"