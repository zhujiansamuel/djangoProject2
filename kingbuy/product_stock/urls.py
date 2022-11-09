from django.urls import path, re_path
from . import views

app_name = 'product_stock'

urlpatterns = [

    re_path( r"^product-change-history/$", views.product_change_history, name="product-change-history" ),
    re_path( r"^correcte-inventory-quantity/$", views.correcte_inventory_quantity, name="correcte-inventory-quantity" ),
    re_path( r"^add-imei/$", views.add_imei, name="add-imei" ),

    re_path( r"^shops/$", views.shop_list, name="shop-list" ),
    re_path( r"^add-shop/$", views.shop_create, name="shop-create" ),
    re_path( r"^(?P<shop_pk>\d+)/edit-shop/$", views.shop_edit, name="shop-edit" ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------

    re_path( r"^stocktakings/$", views.stock_taking.as_view(), name="stocktakings" ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^E-markets/$", views.E_market_list, name="E-market-list" ),
    re_path( r"^add-E-market/$", views.E_market_create, name="E-market-create" ),
    re_path( r"^(?P<E_market_pk>\d+)/edit-E-market/$", views.E_market_edit,
         name="E-market-edit"
         ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path(
        r"^ajax/product-object-stock_s/$",
        views.ajax_product_object_stock_list,
        name="ajax-product-object-stock-s",
        ),
    re_path(
        r"^ajax/product-object-stock/$",
        views.ajax_product_object_stock,
        name="ajax-product-object-stock-single",
        ),

    re_path(
        r"^ajax/product-stock-s/$",
        views.ajax_product_stock_list,
        name="ajax-product-stock",
        ),
    re_path(
        r"^ajax/suppliers/$",
        views.ajax_suppliers_list,
        name="ajax-suppliers-list",
        ),
    re_path(
        r"^ajax/legal-person/$",
        views.ajax_legal_person_list,
        name="ajax-legal-person-list",
        ),
    re_path(
        r"^ajax/product-stock/$",
        views.ajax_product_stock,
        name="ajax-product-stock-single",
        ),
    re_path(
        r"^ajax/suppliers-single/$",
        views.ajax_suppliers,
        name="ajax-suppliers-single",
        ),
    re_path(
        r"^ajax/legal-person-single/$",
        views.ajax_legal_person,
        name="ajax-legal-person-single",
        ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------

    re_path( r"^extra-information/$",
         views.extra_information_list,
         name="extra-information-list"
         ),
    re_path( r"^add-extra-information/$",
         views.extra_information_create,
         name="extra-information-create"
         ),
    re_path( r"^(?P<extra_information_pk>\d+)/edit-extra-information/$",
         views.extra_information_edit,
         name="extra-information-edit"
         ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^product-stock-status/$",
         views.product_stock_status_list,
         name="product-stock-status-list"
         ),
    re_path( r"^add-product-stock-status/$",
         views.product_stock_status_create,
         name="product-stock-status-create"
         ),
    re_path( r"^(?P<product_stock_status_pk>\d+)/edit-product-stock-status/$",
         views.product_stock_status_edit,
         name="product-stock-status-edit"
         ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^suppliers/$",
         views.suppliers_list,
         name="suppliers-list"
         ),
    re_path( r"^add-suppliers/$",
         views.suppliers_create,
         name="suppliers-create"
         ),
    re_path( r"^(?P<suppliers_pk>\d+)/edit-suppliers/$",
         views.suppliers_edit,
         name="suppliers-edit"
         ),
    re_path( r"^(?P<suppliers_pk>\d+)/details-suppliers/$",
         views.suppliers_details,
         name="suppliers-details"
         ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^legal-person/$",
         views.legal_person_list,
         name="legal-person-list"
         ),
    re_path( r"^add-legal-person/$",
         views.legal_person_create,
         name="legal-person-create"
         ),
    re_path( r"^(?P<legal_person_pk>\d+)/edit-legal-person/$",
         views.legal_person_edit,
         name="legal-person-edit"
         ),
    re_path( r"^(?P<legal_person_pk>\d+)/details-legal-person/$",
         views.legal_person_details,
         name="legal-person-details"
         ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^product-stock-temp/$",
         views.product_stock_temp_list,
         name="product-stock-temp-list"
         ),
    re_path( r"^add-product-stock-temp/$",
         views.product_stock_temp_create,
         name="product-stock-temp-create"
         ),
    re_path( r"^(?P<product_stock_temp_pk>\d+)/edit-product-stock-temp/$",
         views.product_stock_temp_edit,
         name="product-stock-temp-edit"
         ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^(?P<product_stock_temp_pk>\d+)/product-object-stock-temp/$",
         views.product_object_stock_temp_list,
         name="product-object-stock-temp-list"
         ),
    re_path( r"^(?P<product_stock_temp_pk>\d+)/add-product-object-stock-temp/$",
         views.product_object_stock_temp_create,
         name="product-object-stock-temp-create"
         ),
    re_path(
        r"^(?P<product_stock_temp_pk>\d+)/(?P<product_object_stock_temp_pk>\d+)/edit-product-object-stock-temp/$",
        views.product_object_stock_temp_edit,
        name="product-object-stock-temp-edit"
        ),
    re_path(
        r"^(?P<product_stock_temp_pk>\d+)/(?P<product_object_stock_temp_pk>\d+)/product-object-stock-temp/details/$",
        views.product_object_stock_temp_details,
        name="product-object-stock-temp-details"
        ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------

    re_path( r"^order-manage/$",
         views.order_manage_list,
         name="order-manage-list"
         ),
    re_path( r"^add-order-manage/(?P<order_manage_type_No>\d+)/$",
         views.order_manage_create,
         name="order-manage-create"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/$",
         views.order_manage_details,
         name="order-manage-details"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/remove/$",
         views.remove_draft_order_manage,
         name="remove-draft-order-manage"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/cancel/$",
         views.remove_order_manage,
         name="remove-order-manage"
         ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/select-product-object-stock/$",
        views.select_product_object_stock_to_order_manage,
        name="select-product-object-stock-to-order-manage",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/select-product-stock-s/$",
        views.select_product_stock_to_order_manage,
        name="select-product-stock-to-order-manage",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/add-new-product-no-iemi/$",
        views.add_new_product_to_order_manage_no_iemi,
        name="add-new-product-to-order-manage-no-iemi",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/remove-line/(?P<order_manage_line_pk>\d+)/$",
        views.remove_order_manage_line,
        name="remove-order-manage-line",
        ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/add-note/$",
         views.order_manage_add_note,
         name="order-manage-add-note"
         ),

    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/add-slip/$",
         views.order_manage_add_slip_number,
         name="order-manage-add-slip-number"
         ),

    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/add-suppliers/$",
         views.order_manage_add_suppliers,
         name="order-manage-add-suppliers"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/add-legal-person/$",
         views.order_manage_add_legal_person,
         name="order-manage-add-legal-person"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/edit-legal-person/$",
         views.order_manage_edit_legal_person,
         name="order-manage-edit-legal-person"
         ),
    re_path( r"^(?P<order_manage_pk>\d+)/order-manage/edit-suppliers/$",
         views.order_manage_edit_suppliers,
         name="order-manage-edit-suppliers"
         ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/create/$",
        views.create_order_manage_from_draft,
        name="create-order-manage-from-draft",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/fulfill/$",
        views.fulfill_order_manage_lines,
        name="fulfill-order-manage",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/(?P<product_stock_temp_pk>\d+)/input-iemi/(?P<quantity>\d+)/$",
        views.input_iemi_to_order_manage,
        name="input-iemi-to-order-manage",
        ),
    re_path(
        r"^(?P<order_manage_pk>\d+)/order-manage/add-new-product-to-order-manage-numerous/$",
        views.add_new_product_to_order_manage_numerous,
        name="add-new-product-to-order-manage-numerous",
        ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^barter-manage/$",
         views.barter_manage_list,
         name="barter-manage-list"
         ),
    re_path( r"^add-barter-manage/$",
         views.barter_manage_create,
         name="barter-manage-create"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/$",
         views.barter_manage_details,
         name="barter-manage-details"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/remove/$",
         views.remove_draft_barter_manage,
         name="remove-draft-barter-manage"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/cancel/$",
         views.remove_barter_manage,
         name="remove-barter-manage"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/add-suppliers/$",
         views.barter_manage_add_suppliers,
         name="barter-manage-add-suppliers"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/add-legal-person/$",
         views.barter_manage_add_legal_person,
         name="barter-manage-add-legal-person"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/edit-legal-person/$",
         views.barter_manage_edit_legal_person,
         name="barter-manage-edit-legal-person"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/edit-suppliers/$",
         views.barter_manage_edit_suppliers,
         name="barter-manage-edit-suppliers"
         ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/(?P<product_stock_temp_pk>\d+)/input-iemi/(?P<quantity>\d+)/$",
        views.input_iemi_to_barter_manage,
        name="input-iemi-to-barter-manage",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/add-new-product-to-barter-manage-numerous/$",
        views.add_new_product_to_barter_manage_numerous,
        name="add-new-product-to-barter-manage-numerous",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/select-product-object-stock/$",
        views.select_product_object_stock_to_barter_manage,
        name="select-product-object-stock-to-barter-manage",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/select-product-stock/$",
        views.select_product_stock_to_barter_manage,
        name="select-product-stock-to-barter-manage",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/add-new-product/$",
        views.add_new_product_to_barter_manage,
        name="add-new-product-to-barter-manage",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/remove-product-object-stock/(?P<barter_manage_line_pk>\d+)/$",
        views.remove_barter_manage_line,
        name="remove-barter-manage-line",
        ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/add-note/$",
         views.barter_manage_add_note,
         name="barter-manage-add-note"
         ),
    re_path( r"^(?P<barter_manage_pk>\d+)/barter-manage/add-slip/$",
         views.barter_manage_add_slip_number,
         name="barter-manage-add-slip-number"
         ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/create/barter-manage/$",
        views.create_barter_manage_from_draft,
        name="create-barter-manage-from-draft",
        ),
    re_path(
        r"^(?P<barter_manage_pk>\d+)/barter-manage/fulfill/$",
        views.fulfill_barter_manage_lines,
        name="fulfill-barter-manage",
        ),
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^store-to-store-manage/$",
         views.store_to_store_manage_list,
         name="store-to-store-manage-list"
         ),
    re_path( r"^add-store-to-store-manage/$",
         views.store_to_store_manage_create,
         name="store-to-store-manage-create"
         ),
    re_path( r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/$",
         views.store_to_store_manage_details,
         name="store-to-store-manage-details"
         ),
    re_path( r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/remove/$",
         views.remove_draft_store_to_store_manage,
         name="remove-draft-store-to-store-manage"
         ),
    re_path( r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/cancel/$",
         views.remove_store_to_store_manage,
         name="remove-store-to-store-manage"
         ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/select-product-object-stock/$",
        views.select_product_object_stock_to_store_to_store_manage,
        name="select-product-object-stock-to-store-to-store-manage",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/select-product-stock/$",
        views.select_product_stock_to_store_to_store_manage,
        name="select-product-stock-to-store-to-store-manage",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/select-product-stock/$",
        views.select_product_stock_to_store_to_store_manage,
        name="select-product-stock-to-store-to-store-manage",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/remove-product-object-stock/(?P<store_to_store_manage_line_pk>\d+)/$",
        views.remove_store_to_store_manage_line,
        name="remove-store-to-store-manage-line",
        ),
    re_path( r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/add-note/$",
         views.store_to_store_manage_add_note,
         name="store-to-store-manage-add-note"
         ),
    re_path( r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/add-slip/$",
         views.store_to_store_manage_add_slip_number,
         name="store-to-store-manage-add-slip-number"
         ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/create/store-to-store-manage/$",
        views.create_store_to_store_manage_from_draft,
        name="create-store-to-store-manage-from-draft",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/add-to-shops/$",
        views.store_to_store_manage_add_to_shops,
        name="store-to-store-manage-add-to-shops",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/fulfill-MOVEOUT/$",
        views.fulfill_store_manage_lines_MOVEOUT,
        name="fulfill-store-to-store-manage-MOVEOUT",
        ),
    re_path(
        r"^(?P<store_to_store_manage_pk>\d+)/store-to-store-manage/fulfill-MOVEIN/$",
        views.fulfill_store_manage_lines_MOVEIN,
        name="fulfill-store-to-store-manage-MOVEIN",
        ),

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    re_path( r"^manual-inventory-manage/$", views.manual_inventory_manage_list,
         name="manual-inventory-manage-list"
         ),
    re_path( r"^add-manual-inventory-manage/$", views.manual_inventory_manage_create,
         name="manual-inventory-manage-create"
         ),
    re_path( r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/$",
         views.manual_inventory_manage_details,
         name="manual-inventory-manage-details"
         ),
    re_path( r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/remove/$",
         views.remove_draft_manual_inventory_manage,
         name="remove-draft-manual-inventory-manage"
         ),
    re_path( r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/cancel/$",
         views.remove_manual_inventory_manage,
         name="remove-manual-inventory-manage"
         ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/remove-product-object-stock/(?P<manual_inventory_manage_line_pk>\d+)/$",
        views.remove_manual_inventory_manage_line,
        name="remove-manual-inventory-manage-line",
        ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/select-product-object-stock/$",
        views.select_product_object_stock_to_manual_inventory_manage,
        name="select-product-object-stock-to-manual-inventory-manage",
        ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/select-product-stock/$",
        views.select_product_stock_to_manual_inventory_manage,
        name="select-product-stock-to-manual-inventory-manage",
        ),
    re_path( r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/add-note/$",
         views.manual_inventory_manage_add_note,
         name="manual-inventory-manage-add-note"
         ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/create/manual-inventory-manage/$",
        views.create_manual_inventory_manage_from_draft,
        name="create-manual-inventory-manage-from-draft",
        ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/fulfill-LOCK/$",
        views.fulfill_manual_manage_lines_LOCK,
        name="fulfill-manual-inventory-manage-LOCK",
        ),
    re_path(
        r"^(?P<manual_inventory_manage_pk>\d+)/manual-inventory-manage/fulfill-UNLOCK/$",
        views.fulfill_manual_manage_lines_UNLOCK,
        name="fulfill-manual-inventory-manage-UNLOCK",
        ),
    ]
