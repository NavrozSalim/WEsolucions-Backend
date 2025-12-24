"""
Marketplace API endpoints using Django Ninja.
"""
from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import Marketplace, Store, StorePriceSettings, StoreInventorySettings, PriceRange, PriceRangeMargin
from vendor.models import Vendor

router = Router()

# Marketplace endpoints
@router.get("/marketplaces")
def list_marketplaces(request):
    """List all marketplaces."""
    marketplaces = Marketplace.objects.filter(is_active=True).values(
        'id', 'code', 'name', 'created_at'
    )
    return list(marketplaces)

@router.post("/marketplaces")
def create_marketplace(request, code: str, name: str):
    """Create a new marketplace."""
    marketplace = Marketplace.objects.create(code=code, name=name)
    return {'id': marketplace.id, 'code': marketplace.code, 'name': marketplace.name}

# Store endpoints
@router.get("/stores")
def list_stores(request):
    """List all stores."""
    stores = Store.objects.filter(is_active=True).select_related('marketplace').values(
        'id', 'name', 'marketplace__name', 'marketplace__code',
        'scraping_enabled', 'price_update_enabled', 'created_at'
    )
    return list(stores)

@router.get("/stores/{store_id}")
def get_store(request, store_id: int):
    """Get a specific store with settings."""
    store = get_object_or_404(Store.objects.select_related('marketplace'), id=store_id)
    
    # Get vendor-specific settings
    price_settings = StorePriceSettings.objects.filter(store=store).select_related('vendor').values(
        'vendor__id', 'vendor__name', 'purchase_tax_percentage',
        'marketplace_fee_percentage', 'min_margin_percentage'
    )
    
    return {
        'id': store.id,
        'name': store.name,
        'marketplace': {
            'id': store.marketplace.id,
            'code': store.marketplace.code,
            'name': store.marketplace.name,
        },
        'scraping_enabled': store.scraping_enabled,
        'scraping_interval_hours': store.scraping_interval_hours,
        'price_update_enabled': store.price_update_enabled,
        'is_active': store.is_active,
        'price_settings': list(price_settings),
    }

@router.post("/stores")
def create_store(request, marketplace_id: int, name: str):
    """Create a new store."""
    marketplace = get_object_or_404(Marketplace, id=marketplace_id)
    store = Store.objects.create(marketplace=marketplace, name=name)
    return {'id': store.id, 'name': store.name, 'marketplace': marketplace.name}

@router.put("/stores/{store_id}")
def update_store(request, store_id: int, name: str = None, 
                scraping_enabled: bool = None, price_update_enabled: bool = None):
    """Update a store."""
    store = get_object_or_404(Store, id=store_id)
    if name:
        store.name = name
    if scraping_enabled is not None:
        store.scraping_enabled = scraping_enabled
    if price_update_enabled is not None:
        store.price_update_enabled = price_update_enabled
    store.save()
    return {'id': store.id, 'name': store.name, 'updated': True}

@router.delete("/stores/{store_id}")
def delete_store(request, store_id: int):
    """Delete (deactivate) a store."""
    store = get_object_or_404(Store, id=store_id)
    store.is_active = False
    store.save()
    return {'success': True}

# Store Price Settings endpoints
@router.get("/stores/{store_id}/price-settings")
def get_store_price_settings(request, store_id: int):
    """Get price settings for a store."""
    settings = StorePriceSettings.objects.filter(store_id=store_id).select_related('vendor').values(
        'id', 'vendor__id', 'vendor__name', 'purchase_tax_percentage',
        'marketplace_fee_percentage', 'min_margin_percentage'
    )
    return list(settings)

@router.post("/stores/{store_id}/price-settings")
def create_price_settings(request, store_id: int, vendor_id: int,
                         purchase_tax_percentage: float = 10.0,
                         marketplace_fee_percentage: float = 10.0,
                         min_margin_percentage: float = 15.0):
    """Create price settings for a store-vendor combination."""
    store = get_object_or_404(Store, id=store_id)
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    settings, created = StorePriceSettings.objects.update_or_create(
        store=store,
        vendor=vendor,
        defaults={
            'purchase_tax_percentage': purchase_tax_percentage,
            'marketplace_fee_percentage': marketplace_fee_percentage,
            'min_margin_percentage': min_margin_percentage,
        }
    )
    
    return {
        'id': settings.id,
        'created': created,
        'vendor': vendor.name,
        'store': store.name,
    }
