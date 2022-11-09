from django.contrib.auth.models import Permission

# MODELS_PERMISSIONS = [
#     "account.manage_users",
#     "account.manage_staff",
#     "account.manage_service_accounts",
#     "account.impersonate_users",
#     "discount.manage_discounts",
#     "giftcard.manage_gift_card",
#     "extensions.manage_plugins",
#     "menu.manage_menus",
#     "order.manage_orders",
#     "page.manage_pages",
#     "product.manage_products",
#     "shipping.manage_shipping",
#     "site.manage_settings",
#     "site.manage_translations",
#     "webhook.manage_webhooks",
# ]
MODELS_PERMISSIONS = [
    "account.manage_staff",
    "site.manage_settings",
    "product_stock.manage_E_mark",
    "product_stock.manage_suppliers",
    "product_stock.manage_legalperson",
    "product_stock.manage_shopss",
    "product_stock.manage_product_stock_status",
    "product_stock.manage_extrainformation",
    "product_stock.manage_product_stock",
    "product_stock.manage_product_object_stock",
    "product_stock.change_product_stock",
    "product_stock.change_product_object_stock",
    "product_stock.manual_inventory_manage_permissions",
    "product_stock.manual_inventory_cancel_permissions",
    "product_stock.store_to_store_manage_permissions",
    "product_stock.store_to_store_cancel_permissions",
    "product_stock.barter_manage_permissions",
    "product_stock.barter_cancel_permissions",
    "product_stock.order_manage_permissions",
    "product_stock.order_cancel_permissions",
]

def split_permission_codename(permissions):
    return [permission.split(".")[1] for permission in permissions]


def get_permissions(permissions=None):
    if permissions is None:
        permissions = MODELS_PERMISSIONS
    codenames = split_permission_codename(permissions)
    return (
        Permission.objects.filter(codename__in=codenames)
        .prefetch_related("content_type")
        .order_by("codename")
    )
