"""
Export API endpoints using Django Ninja.
"""
from ninja import Router
from typing import Optional
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import ExportArtifact
from products.models import Product
from marketplace.models import Store
from vendor.models import Vendor
import csv
import io
import os

router = Router()

@router.post("/generate")
def generate_export(request, store_id: int, vendor_id: Optional[int] = None, 
                   export_type: str = "full"):
    """Generate an export file for a store."""
    store = get_object_or_404(Store, id=store_id)
    
    # Create export record
    export = ExportArtifact.objects.create(
        store=store,
        vendor_id=vendor_id,
        export_type=export_type,
        status='processing',
        started_at=timezone.now(),
    )
    
    try:
        # Get products to export
        query = Product.objects.filter(store=store, is_active=True)
        if vendor_id:
            query = query.filter(vendor_id=vendor_id)
        
        products = query.select_related('vendor', 'marketplace')
        
        # Create CSV in memory
        output = io.StringIO()
        
        if export_type == 'price':
            # Price export format
            writer = csv.writer(output)
            writer.writerow(['SKU', 'Price', 'Currency'])
            
            for product in products:
                if product.calculated_price:
                    writer.writerow([
                        product.marketplace_child_sku,
                        product.calculated_price,
                        'AUD'
                    ])
        
        elif export_type == 'inventory':
            # Inventory export format
            writer = csv.writer(output)
            writer.writerow(['SKU', 'Quantity'])
            
            for product in products:
                if product.calculated_stock is not None:
                    writer.writerow([
                        product.marketplace_child_sku,
                        product.calculated_stock
                    ])
        
        else:  # full export
            writer = csv.writer(output)
            writer.writerow([
                'Vendor SKU', 'Marketplace SKU', 'Title', 
                'Vendor Price', 'Calculated Price',
                'Vendor Stock', 'Calculated Stock'
            ])
            
            for product in products:
                writer.writerow([
                    product.vendor_sku,
                    product.marketplace_child_sku,
                    product.title,
                    product.vendor_price,
                    product.calculated_price,
                    product.vendor_stock,
                    product.calculated_stock,
                ])
        
        # Save export
        content = output.getvalue()
        filename = f"{store.name}_{export_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Save to media directory
        media_dir = os.path.join('media', 'exports')
        os.makedirs(media_dir, exist_ok=True)
        file_path = os.path.join(media_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update export record
        export.status = 'completed'
        export.filename = filename
        export.file_path = file_path
        export.file_size = len(content)
        export.total_products = products.count()
        export.exported_products = products.count()
        export.completed_at = timezone.now()
        export.save()
        
    except Exception as e:
        export.status = 'failed'
        export.error_message = str(e)
        export.completed_at = timezone.now()
        export.save()
        return {'success': False, 'error': str(e)}
    
    return {
        'success': True,
        'export_id': export.id,
        'filename': export.filename,
        'products_exported': export.exported_products,
    }

@router.get("/exports")
def list_exports(request, store_id: Optional[int] = None, limit: int = 20):
    """List recent exports."""
    query = ExportArtifact.objects.all()
    
    if store_id:
        query = query.filter(store_id=store_id)
    
    exports = query.select_related('store', 'vendor')[:limit].values(
        'id', 'filename', 'export_type', 'status',
        'store__name', 'vendor__name', 'total_products',
        'created_at', 'completed_at'
    )
    
    return list(exports)

@router.get("/exports/{export_id}")
def get_export(request, export_id: int):
    """Get export details."""
    export = get_object_or_404(ExportArtifact, id=export_id)
    
    return {
        'id': export.id,
        'filename': export.filename,
        'export_type': export.export_type,
        'status': export.status,
        'store': export.store.name,
        'vendor': export.vendor.name if export.vendor else None,
        'total_products': export.total_products,
        'exported_products': export.exported_products,
        'file_size': export.file_size,
        'created_at': export.created_at,
        'completed_at': export.completed_at,
        'error_message': export.error_message,
    }

@router.get("/exports/{export_id}/download")
def download_export(request, export_id: int):
    """Download an export file."""
    export = get_object_or_404(ExportArtifact, id=export_id)
    
    if export.status != 'completed' or not export.file_path:
        return HttpResponse("Export not available", status=404)
    
    try:
        with open(export.file_path, 'r', encoding='utf-8') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{export.filename}"'
            return response
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
