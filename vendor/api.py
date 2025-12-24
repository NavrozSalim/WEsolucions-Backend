"""
Vendor API endpoints using Django Ninja.
"""
from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from .models import Vendor, VendorPrice

router = Router()

# Vendor endpoints
@router.get("/vendors")
def list_vendors(request):
    """List all vendors."""
    vendors = Vendor.objects.filter(is_active=True).values(
        'id', 'name', 'code', 'created_at'
    )
    return list(vendors)

@router.get("/vendors/{vendor_id}")
def get_vendor(request, vendor_id: int):
    """Get a specific vendor."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    return {
        'id': vendor.id,
        'name': vendor.name,
        'code': vendor.code,
        'is_active': vendor.is_active,
        'created_at': vendor.created_at,
        'updated_at': vendor.updated_at,
    }

@router.post("/vendors")
def create_vendor(request, name: str, code: str):
    """Create a new vendor."""
    vendor = Vendor.objects.create(name=name, code=code)
    return {'id': vendor.id, 'name': vendor.name, 'code': vendor.code}

@router.put("/vendors/{vendor_id}")
def update_vendor(request, vendor_id: int, name: str = None, code: str = None, is_active: bool = None):
    """Update a vendor."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if name:
        vendor.name = name
    if code:
        vendor.code = code
    if is_active is not None:
        vendor.is_active = is_active
    vendor.save()
    return {'id': vendor.id, 'name': vendor.name, 'code': vendor.code, 'is_active': vendor.is_active}

@router.delete("/vendors/{vendor_id}")
def delete_vendor(request, vendor_id: int):
    """Delete a vendor."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_active = False
    vendor.save()
    return {'success': True}

# Vendor Price endpoints
@router.get("/vendor-prices/{vendor_id}")
def list_vendor_prices(request, vendor_id: int):
    """List prices for a vendor."""
    prices = VendorPrice.objects.filter(vendor_id=vendor_id).values(
        'id', 'vendor_sku', 'price', 'currency', 'last_updated'
    )
    return list(prices)
