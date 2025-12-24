"""
Products API endpoints using Django Ninja.
"""
from ninja import Router, File
from ninja.files import UploadedFile
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Product, Upload, Scrape, ScrapeResult
from marketplace.models import Store
from vendor.models import Vendor
import csv
import io
import uuid
import os

router = Router()

# Product endpoints
@router.get("/")
def list_products(request, store_id: Optional[int] = None, vendor_id: Optional[int] = None, 
                  search: Optional[str] = None, limit: int = 100, offset: int = 0):
    """List products with filters."""
    query = Product.objects.select_related('vendor', 'marketplace', 'store')
    
    if store_id:
        query = query.filter(store_id=store_id)
    if vendor_id:
        query = query.filter(vendor_id=vendor_id)
    if search:
        query = query.filter(
            Q(vendor_sku__icontains=search) |
            Q(title__icontains=search) |
            Q(marketplace_child_sku__icontains=search)
        )
    
    total = query.count()
    products = query[offset:offset+limit].values(
        'id', 'vendor_sku', 'title', 'vendor__name', 'store__name',
        'marketplace__name', 'vendor_price', 'calculated_price',
        'vendor_stock', 'calculated_stock', 'last_scraped', 'is_active'
    )
    
    return {
        'total': total,
        'products': list(products),
        'limit': limit,
        'offset': offset,
    }

@router.get("/{product_id}")
def get_product(request, product_id: int):
    """Get a specific product."""
    product = get_object_or_404(Product.objects.select_related('vendor', 'marketplace', 'store'), id=product_id)
    
    return {
        'id': product.id,
        'vendor_sku': product.vendor_sku,
        'title': product.title,
        'source_url': product.source_url,
        'vendor': {
            'id': product.vendor.id,
            'name': product.vendor.name,
        },
        'store': {
            'id': product.store.id,
            'name': product.store.name,
        },
        'marketplace': {
            'id': product.marketplace.id,
            'name': product.marketplace.name,
        },
        'vendor_price': product.vendor_price,
        'calculated_price': product.calculated_price,
        'vendor_stock': product.vendor_stock,
        'calculated_stock': product.calculated_stock,
        'last_scraped': product.last_scraped,
        'is_active': product.is_active,
    }

@router.post("/")
def create_product(request, vendor_id: int, store_id: int, vendor_sku: str,
                  marketplace_child_sku: str, title: str = "", source_url: str = ""):
    """Create a single product."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    store = get_object_or_404(Store.objects.select_related('marketplace'), id=store_id)
    
    product = Product.objects.create(
        vendor=vendor,
        store=store,
        marketplace=store.marketplace,
        vendor_sku=vendor_sku,
        marketplace_child_sku=marketplace_child_sku,
        title=title,
        source_url=source_url,
    )
    
    return {'id': product.id, 'vendor_sku': product.vendor_sku, 'title': product.title}

@router.delete("/{product_id}")
def delete_product(request, product_id: int):
    """Delete (deactivate) a product."""
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    return {'success': True}

# Upload endpoints
@router.post("/upload")
def upload_products(request, file: UploadedFile = File(...), vendor_id: int = None, store_id: int = None):
    """Upload products from CSV file."""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    store = get_object_or_404(Store.objects.select_related('marketplace'), id=store_id)
    
    # Create upload record
    upload = Upload.objects.create(
        vendor=vendor,
        store=store,
        filename=file.name,
        status='processing',
        started_at=timezone.now(),
    )
    
    try:
        # Process CSV
        content = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        created_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Create product from CSV row
                Product.objects.update_or_create(
                    vendor=vendor,
                    vendor_sku=row.get('vendor_sku', '').strip(),
                    store=store,
                    defaults={
                        'marketplace': store.marketplace,
                        'marketplace_child_sku': row.get('marketplace_child_sku', '').strip(),
                        'marketplace_parent_sku': row.get('marketplace_parent_sku', '').strip(),
                        'title': row.get('title', '').strip(),
                        'source_url': row.get('source_url', '').strip(),
                        'upload': upload,
                    }
                )
                created_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Update upload status
        upload.status = 'completed'
        upload.total_rows = created_count + error_count
        upload.successful_rows = created_count
        upload.failed_rows = error_count
        upload.error_details = {'errors': errors} if errors else {}
        upload.completed_at = timezone.now()
        upload.save()
        
    except Exception as e:
        upload.status = 'failed'
        upload.error_message = str(e)
        upload.completed_at = timezone.now()
        upload.save()
        return {'success': False, 'error': str(e)}
    
    return {
        'success': True,
        'upload_id': upload.id,
        'created': created_count,
        'errors': error_count,
        'error_details': errors[:10],  # Return first 10 errors
    }

# Scrape endpoints
@router.post("/scrape")
def start_scrape(request, store_id: int, vendor_id: Optional[int] = None):
    """Start a scraping job for products."""
    store = get_object_or_404(Store, id=store_id)
    
    # Create scrape record
    scrape = Scrape.objects.create(
        store=store,
        vendor_id=vendor_id,
        status='pending',
    )
    
    # Get products to scrape
    query = Product.objects.filter(store=store, is_active=True)
    if vendor_id:
        query = query.filter(vendor_id=vendor_id)
    
    scrape.total_products = query.count()
    scrape.save()
    
    # TODO: Trigger async scraping job here
    # For now, just return the scrape ID
    
    return {
        'scrape_id': scrape.id,
        'status': scrape.status,
        'total_products': scrape.total_products,
    }

@router.get("/scrapes/{scrape_id}")
def get_scrape_status(request, scrape_id: int):
    """Get scrape job status."""
    scrape = get_object_or_404(Scrape, id=scrape_id)
    
    return {
        'id': scrape.id,
        'status': scrape.status,
        'total_products': scrape.total_products,
        'successful_scrapes': scrape.successful_scrapes,
        'failed_scrapes': scrape.failed_scrapes,
        'started_at': scrape.started_at,
        'completed_at': scrape.completed_at,
        'error_message': scrape.error_message,
    }

# Upload history endpoint
@router.get("/uploads/")
def list_uploads(request, page: int = 1, page_size: int = 10):
    """List uploads with pagination."""
    from django.core.paginator import Paginator
    
    uploads_query = Upload.objects.select_related('vendor', 'store', 'store__marketplace').order_by('-created_at')
    
    paginator = Paginator(uploads_query, page_size)
    page_obj = paginator.get_page(page)
    
    uploads_data = []
    for upload in page_obj:
        uploads_data.append({
            'id': upload.id,
            'filename': upload.filename,
            'vendor': {
                'id': upload.vendor.id,
                'name': upload.vendor.name,
            },
            'store': {
                'id': upload.store.id,
                'name': upload.store.name,
                'marketplace': upload.store.marketplace.name,
            },
            'status': upload.status,
            'total_rows': upload.total_rows,
            'processed_rows': upload.processed_rows,
            'successful_rows': upload.successful_rows,
            'failed_rows': upload.failed_rows,
            'error_message': upload.error_message,
            'started_at': upload.started_at,
            'completed_at': upload.completed_at,
            'created_at': upload.created_at,
        })
    
    return {
        'success': True,
        'uploads': uploads_data,
        'pagination': {
            'current_page': page_obj.number,
            'page_size': page_size,
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
        }
    }
