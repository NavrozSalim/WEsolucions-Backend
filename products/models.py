"""
Product models for managing marketplace inventory and scraping.
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Product(models.Model):
    """
    Represents a product in the marketplace with vendor and marketplace details.
    """
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='products',
        help_text='The vendor who supplies this product'
    )
    vendor_sku = models.CharField(
        max_length=255,
        help_text='Vendor SKU/item number'
    )
    variation_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='Product variation identifier if applicable'
    )
    marketplace_child_sku = models.CharField(
        max_length=255,
        help_text='Marketplace-specific child SKU'
    )
    marketplace_parent_sku = models.CharField(
        max_length=255,
        blank=True,
        help_text='Marketplace-specific parent SKU'
    )
    marketplace_external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='External ID from marketplace (eBay ID, Amazon ASIN, etc.)'
    )
    marketplace = models.ForeignKey(
        'marketplace.Marketplace',
        on_delete=models.CASCADE,
        related_name='products',
        help_text='The marketplace where this product is listed'
    )
    store = models.ForeignKey(
        'marketplace.Store',
        on_delete=models.CASCADE,
        related_name='products',
        help_text='The store where this product is listed'
    )
    upload = models.ForeignKey(
        'Upload',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text='The upload batch that created this product'
    )
    
    # Product details
    title = models.CharField(max_length=500, blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    
    # Pricing fields
    vendor_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    calculated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Inventory fields
    vendor_stock = models.IntegerField(null=True, blank=True)
    calculated_stock = models.IntegerField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    scrape_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'vendor_sku', 'store']
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.vendor_sku} - {self.title or 'No title'}"


class Upload(models.Model):
    """
    Tracks CSV file uploads for bulk product creation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    store = models.ForeignKey(
        'marketplace.Store',
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Processing statistics
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Upload'
        verbose_name_plural = 'Uploads'
    
    def __str__(self):
        return f"{self.filename} - {self.status}"


class Scrape(models.Model):
    """
    Tracks scraping operations for products.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    store = models.ForeignKey(
        'marketplace.Store',
        on_delete=models.CASCADE,
        related_name='scrapes'
    )
    vendor = models.ForeignKey(
        'vendor.Vendor',
        on_delete=models.CASCADE,
        related_name='scrapes',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Statistics
    total_products = models.IntegerField(default=0)
    successful_scrapes = models.IntegerField(default=0)
    failed_scrapes = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scrape'
        verbose_name_plural = 'Scrapes'
    
    def __str__(self):
        return f"Scrape {self.id} - {self.status}"


class ScrapeResult(models.Model):
    """
    Individual scrape result for a product.
    """
    scrape = models.ForeignKey(
        Scrape,
        on_delete=models.CASCADE,
        related_name='results'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='scrape_results'
    )
    
    # Scraped data
    scraped_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    scraped_stock = models.IntegerField(null=True, blank=True)
    scraped_title = models.CharField(max_length=500, blank=True)
    scraped_data = models.JSONField(default=dict, blank=True)
    
    # Status
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scrape Result'
        verbose_name_plural = 'Scrape Results'
    
    def __str__(self):
        return f"Result for {self.product.vendor_sku} - {'Success' if self.success else 'Failed'}"