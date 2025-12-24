"""
Main API configuration using Django Ninja.
"""
from ninja import NinjaAPI
from ninja.security import django_auth
from django.http import JsonResponse

# Import routers from apps
from vendor.api import router as vendor_router
from marketplace.api import router as marketplace_router
from products.api import router as products_router
from export.api import router as export_router

# Create main API instance
api = NinjaAPI(
    title="WEsolucions Backend API",
    version="1.0.0",
    description="Dropshipping and inventory management API",
    csrf=True,  # Enable CSRF protection
)

# Add routers
api.add_router("/vendor", vendor_router, tags=["Vendor"])
api.add_router("/marketplace", marketplace_router, tags=["Marketplace"])
api.add_router("/products", products_router, tags=["Products"])
api.add_router("/export", export_router, tags=["Export"])

# Health check endpoint
@api.get("/health", tags=["System"])
def health_check(request):
    """Health check endpoint."""
    return {"status": "healthy", "api": "operational"}

# Dashboard summary endpoint
@api.get("/dashboard/summary", tags=["Dashboard"])
def dashboard_summary(request):
    """Get dashboard summary statistics."""
    from vendor.models import Vendor
    from marketplace.models import Store, Marketplace
    from products.models import Product, Scrape
    
    return {
        "vendors": Vendor.objects.count(),
        "marketplaces": Marketplace.objects.count(),
        "stores": Store.objects.count(),
        "products": Product.objects.count(),
        "recent_scrapes": Scrape.objects.filter(status="completed").count(),
    }
