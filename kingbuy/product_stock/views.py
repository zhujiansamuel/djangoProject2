import csv
import io
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.forms import modelformset_factory, inlineformset_factory
from django.forms.models import model_to_dict
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.response import TemplateResponse
from django.utils.translation import npgettext_lazy, pgettext_lazy
from django.views.decorators.http import require_POST
from django.template.context_processors import csrf
from ..core.utils import get_paginator_items
from ..account.models import Address

from .filters import *

from ..product_stock import (
    events,
    FulfillmentStatus,
    InventoryStatus,
    InventoryFundsStatus,
    ProductStockManageStatus,
    StoreToStoreType,
    StoreToStoreStatus,
    BarterManageType,
    BarterManageStatus,
    OrderManageType,
    OrderManageStatus,
    ManualInventoryType,
    ManualInventoryStatus,
    )

from .models import (
    E_mark,
    Address,
    Suppliers,
    LegalPerson,
    Shops,
    ProductStockStatus,
    ExtraInformation,
    ProductStock,
    ProductObjectStock,
    ProductStockChangeEvent,
    ProductObjectStockChangeEvent,
    ProductStockEvent,
    ManualInventoryManage,
    ManualInventoryManageLine,
    ManualInventoryManageFulfillment_LOCK,
    ManualInventoryManageFulfillmentLine_LOCK,
    ManualInventoryManageFulfillment_UNLOCK,
    ManualInventoryManageFulfillmentLine_UNLOCK,
    ManualInventoryManageEvent,
    StoreToStoreManage,
    StoreToStoreManageLine,
    StoreToStoreManageFulfillment_MOVEOUT,
    StoreToStoreManageFulfillmentLine_MOVEOUT,
    StoreToStoreManageFulfillment_MOVEIN,
    StoreToStoreManageFulfillmentLine_MOVEIN,
    StoreToStoreManageEvent,
    BarterManage,
    BarterManageLine,
    BarterManageFulfillment,
    BarterManageFulfillmentLine,
    BarterManageEvent,
    OrderManage,
    OrderManageLine,
    OrderManageFulfillment,
    OrderManageFulfillmentLine,
    OrderManageEvent,
    )

from . import forms
from ..core.views import staff_member_required
from .utils import (
    add_product_object_stock_s_to_manual_inventory_manage,
    add_product_object_stock_s_to_barter_manage,
    add_product_object_stock_s_to_order_manage,
    add_product_object_stock_s_to_store_to_store_manage,

    add_product_stock_s_to_order_manage,
    add_product_stock_s_to_manual_inventory_manage,
    add_product_stock_s_to_barter_manage,
    add_product_stock_s_to_store_to_store_manage,

    change_product_stock_quantity_s,
    change_product_object_stock_manage_status,
    delete_store_manage_line,
    delete_manage_line,
    delete_barter_manage_line,
    delete_manual_manage_line,

    update_order_manage_status,
    update_barter_manage_status,
    change_product_stock_ststus,
    change_product_object_stock_store,
    update_store_to_store_manage_status,
    update_manual_inventory_manage_status,

    change_avarage_price,
    update_stock_temp,
    )





# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "site.manage_settings" )
def correcte_inventory_quantity(request):
    status = 200
    ctx = {}
    template = "product_stock/addition/correcte_inventory_quantity.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.change_product_stock" )
def add_imei(request):
    status = 200
    ctx = {}
    template = "product_stock/addition/add_imei.html"
    return TemplateResponse( request, template, ctx, status=status )


# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# 入庫商品を追加
@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def add_new_product_to_order_manage_no_iemi(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    form = forms.OrderManageAddProductForm_with_iemi(
        request.POST or None, order_manage=order_manage, no_imei=True
        )
    status = 200
    if request.POST and form.is_valid():
        quantity = form.cleaned_data['quantity']
        jan_search = request.POST["jan_code"]

        try:
            product_stock_temp = ProductStock.objects.get( jan_code=jan_search )
        except ProductStock.DoesNotExist:
            product_stock_temp = ProductStock(
                name=form.cleaned_data['name'],
                jan_code=jan_search,
                description=form.cleaned_data['description'],
                is_temp=True
                )
            product_stock_temp.save()
        line = add_product_stock_s_to_order_manage( order_manage,
                                                    product_stock_temp,
                                                    form.cleaned_data["quantity"],
                                                    OrderManageType.STORAGE,
                                                    OrderManageStatus.ORDER_STORAGE_PREDESTINATE,
                                                    form.cleaned_data["price_to_cal"]
                                                    )

        change_product_stock_quantity_s(
            product_stock_temp,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=True,
            quantity_locking_dif=0,
            quantity_allocated_dif=0,
            quantity_predestinate_dif=form.cleaned_data['quantity'],
            )
        events.draft_order_manage_added_product_stock_s_event(
            order_manage=order_manage, user=request.user,
            order_manage_lines=[(line.quantity, line)]
            )

        msg_dict = {
            "order_manage": order_manage,
            "quantity": 1,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(order_manage)sへ %(quantity)d 種類商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "order_manage": order_manage,
        "form": form,
        "no_imei":True
        }
    template = "product_stock/order_manage/add_new_product_numenous.html"
    return TemplateResponse( request, template, ctx, status=status )


# 数量变更--有
@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def add_new_product_to_barter_manage(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.BarterManageAddProductForm(
        request.POST or None, barter_manage=barter_manage
        )
    status = 200
    if form.is_valid():
        if form.cleaned_data['product_stock']:
            product_stock_temp = form.cleaned_data['product_stock']
        else:
            product_stock_temp = ProductStock(
                name=form.cleaned_data['name'],
                jan_code=form.cleaned_data['jan_code'],
                description=form.cleaned_data['description'],
                is_temp=True
                )
            product_stock_temp.save()
        product_object_stock_temp = ProductObjectStock(
            imei_code=form.cleaned_data['imei_code'],
            product_stock=product_stock_temp,
            notion=form.cleaned_data['notion'],
            price_override_amount=form.cleaned_data['price_override_amount'],
            shops=form.cleaned_data['shops'],
            extra_informations=form.cleaned_data['extra_informations'],
            status=form.cleaned_data['status'],
            manage_status=ProductStockManageStatus.BARTER_MOVE_IN_PREDESTINATE
            )
        product_object_stock_temp.save()

        line = add_product_object_stock_s_to_barter_manage( barter_manage,
                                                            product_object_stock_temp,
                                                            BarterManageType.MOVEIN,
                                                            BarterManageStatus.BARTER_MOVE_IN_PREDESTINATE
                                                            )
        change_product_stock_quantity_s(
            product_stock_temp,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=False,
            quantity_locking_dif=0,
            quantity_allocated_dif=0,
            quantity_predestinate_dif=1,
            )
        events.draft_barter_manage_added_product_object_stock_s_event(
            barter_manage=barter_manage, user=request.user,
            barter_manage_lines=[(line.quantity, line)]
            )

        msg_dict = {
            "barter_manage": form.cleaned_data.get( "barter_manage" ),
            "quantity": 1,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(barter_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )

    ctx = {
        "barter_manage": barter_manage,
        "form": form,
        }
    template = "product_stock/barter_manage/modal/add_new_product.html"
    return TemplateResponse( request, template, ctx, status=status )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

# 出庫商品を追加(IMEI確定)
@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def select_product_object_stock_to_order_manage(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    form = forms.ProductObjectStockBulkSelectForm(
        request.POST or None, order_manage=order_manage
        )
    status = 200
    if form.is_valid():
        count = 0
        for _, product_object_stock in enumerate(
                form.cleaned_data['product_object_stock_s']
                ):
            line = add_product_object_stock_s_to_order_manage( order_manage,
                                                               product_object_stock,
                                                               OrderManageType.DELIVERY,
                                                               OrderManageStatus.ORDER_DELIVERY_PREDESTINATE
                                                               )
            change_product_object_stock_manage_status( product_object_stock,
                                                       ProductStockManageStatus.ORDER_DELIVERY_PREDESTINATE
                                                       )
            change_product_stock_quantity_s(
                product_object_stock.product_stock,
                is_cancel=False,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )
            events.draft_order_manage_added_product_object_stock_s_event(
                order_manage=order_manage, user=request.user,
                order_manage_lines=[(line.quantity, line)]
                )
            count += 1

        msg_dict = {
            "order_manage": order_manage,
            "quantity": count,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(order_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "order_manage": order_manage,
        "form": form,
        }
    template = "product_stock/order_manage/select_product_object_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def select_product_object_stock_to_barter_manage(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.BarterManageProductObjectStockSelectForm(
        request.POST or None, barter_manage=barter_manage
        )
    status = 200
    if form.is_valid():
        count = 0
        for _, product_object_stock in enumerate(
                form.cleaned_data['product_object_stock_s']
                ):
            line = add_product_object_stock_s_to_barter_manage( barter_manage,
                                                                product_object_stock,
                                                                BarterManageType.MOVEOUT,
                                                                BarterManageStatus.BARTER_MOVE_OUT_PREDESTINATE
                                                                )
            change_product_stock_quantity_s(
                product_object_stock.product_stock,
                is_cancel=False,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )
            change_product_object_stock_manage_status( product_object_stock,
                                                       ProductStockManageStatus.BARTER_MOVE_OUT_PREDESTINATE
                                                       )
            events.draft_barter_manage_added_product_object_stock_s_event(
                barter_manage=barter_manage, user=request.user,
                barter_manage_lines=[(line.quantity, line)]
                )
            count += 1

        msg_dict = {
            "barter_manage": form.cleaned_data.get( "barter_manage" ),
            "quantity": count,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(barter_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "barter_manage": barter_manage,
        "form": form,
        }
    template = "product_stock/barter_manage/select_product_object_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def select_product_object_stock_to_store_to_store_manage(
        request, store_to_store_manage_pk
        ):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    form = forms.StoreToStoreManageProductObjectStockSelectForm(
        request.POST or None, store_to_store_manage=store_to_store_manage
        )
    status = 200
    if form.is_valid():
        count = 0
        for _, product_object_stock in enumerate(
                form.cleaned_data['product_object_stock_s']
                ):
            change_product_object_stock_manage_status( product_object_stock,
                                                       ProductStockManageStatus.STORE_MOVE_OUT_PREDESTINATE
                                                       )

            change_product_stock_quantity_s(
                product_object_stock.product_stock,
                is_cancel=False,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )

            line = add_product_object_stock_s_to_store_to_store_manage(
                store_to_store_manage,
                product_object_stock,
                StoreToStoreType.MOVEOUT,
                StoreToStoreStatus.STORE_MOVE_OUT_PREDESTINATE
                )
            events.draft_store_to_store_manage_added_product_object_stock_s_event(
                store_to_store_manage=store_to_store_manage, user=request.user,
                store_to_store_manage_lines=[(line.quantity, line)]
                )
            count += 1

        msg_dict = {
            "store_to_store_manage": form.cleaned_data.get( "store_to_store_manage" ),
            "quantity": count,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(store_to_store_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "store_to_store_manage": store_to_store_manage,
        "form": form,
        }
    template = "product_stock/store_to_store_manage/modal/select_product_object_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# 数量变更--有
@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def select_product_object_stock_to_manual_inventory_manage(
        request, manual_inventory_manage_pk
        ):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    form = forms.ManualInventoryManageProductObjectStockSelectForm(
        request.POST or None, manual_inventory_manage=manual_inventory_manage
        )
    status = 200
    if form.is_valid():
        count = 0
        for _, product_object_stock in enumerate(
                form.cleaned_data['product_object_stock_s']
                ):

            line = add_product_object_stock_s_to_manual_inventory_manage(
                manual_inventory_manage,
                product_object_stock,
                ManualInventoryType.LOCK,
                ManualInventoryStatus.MANUAL_LOCK_PREDESTINATE
                )
            change_product_object_stock_manage_status( product_object_stock,
                                                       ProductStockManageStatus.MANUAL_LOCK_PREDESTINATE
                                                       )
            change_product_stock_quantity_s(
                product_object_stock.product_stock,
                is_cancel=False,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=1,
                quantity_allocated_dif=0,
                quantity_predestinate_dif=0,
                )
            events.draft_manual_inventory_manage_added_product_object_stock_s_event(
                manual_inventory_manage=manual_inventory_manage, user=request.user,
                manual_inventory_manage_lines=[(line.quantity, line)]
                )
            count += 1

        msg_dict = {
            "manual_inventory_manage": form.cleaned_data.get(
                "manual_inventory_manage"
                ),
            "quantity": count,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(manual_inventory_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "manual_inventory_manage": manual_inventory_manage,
        "form": form,
        }
    template = "product_stock/manual_inventory_manage/modal/select_product_object_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

# 出庫商品を追加

# 数量变更--有
@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def select_product_stock_to_order_manage(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    form = forms.AddProductStockToOrderManageForm(
        request.POST or None, order_manage=order_manage
        )
    status = 200
    if form.is_valid():
        product_stock = form.cleaned_data['product_stock']
        quantity = form.cleaned_data['quantity']
        line = add_product_stock_s_to_order_manage( order_manage,
                                                    product_stock,
                                                    quantity,
                                                    OrderManageType.DELIVERY,
                                                    OrderManageStatus.ORDER_DELIVERY_PREDESTINATE
                                                    )
        change_product_stock_quantity_s(
            product_stock,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=True,
            quantity_locking_dif=0,
            quantity_allocated_dif=quantity,
            quantity_predestinate_dif=0,
            )
        events.draft_order_manage_added_product_object_stock_s_event(
            order_manage=order_manage, user=request.user,
            order_manage_lines=[(line.quantity, line)]
            )
        msg_dict = {
            "quantity": quantity,
            "order_manage": order_manage,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(order_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "order_manage": order_manage,
        "form": form,
        }
    template = "product_stock/order_manage/select_product_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# 数量变更--有
@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def select_product_stock_to_barter_manage(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.AddProductStockToBarterManageForm(
        request.POST or None, barter_manage=barter_manage
        )
    status = 200
    if form.is_valid():
        product_stock = form.cleaned_data['product_stock']
        quantity = form.cleaned_data['quantity']
        line = add_product_stock_s_to_barter_manage( barter_manage,
                                                     product_stock,
                                                     quantity,
                                                     BarterManageType.MOVEOUT,
                                                     BarterManageStatus.BARTER_MOVE_OUT_PREDESTINATE
                                                     )
        change_product_stock_quantity_s(
            product_stock,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=False,
            quantity_locking_dif=0,
            quantity_allocated_dif=quantity,
            quantity_predestinate_dif=0,
            )
        events.draft_barter_manage_added_product_object_stock_s_event(
            barter_manage=barter_manage, user=request.user,
            barter_manage_lines=[(line.quantity, line)]
            )
        msg_dict = {
            "quantity": quantity,
            "barter_manage": barter_manage,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(barter_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "barter_manage": barter_manage,
        "form": form,
        }
    template = "product_stock/barter_manage/modal/add_product_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# 数量变更--有
@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def select_product_stock_to_store_to_store_manage(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    form = forms.AddProductStockToStoreToStoreManageForm(
        request.POST or None, store_to_store_manage=store_to_store_manage
        )
    status = 200
    if form.is_valid():
        product_stock = form.cleaned_data['product_stock']
        quantity = form.cleaned_data['quantity']
        line = add_product_stock_s_to_store_to_store_manage( store_to_store_manage,
                                                             product_stock,
                                                             quantity,
                                                             StoreToStoreType.MOVEOUT,
                                                             StoreToStoreStatus.STORE_MOVE_OUT_PREDESTINATE
                                                             )
        change_product_stock_quantity_s(
            product_stock,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=False,
            quantity_locking_dif=0,
            quantity_allocated_dif=quantity,
            quantity_predestinate_dif=0,
            )
        events.draft_store_to_store_manage_added_product_object_stock_s_event(
            store_to_store_manage=store_to_store_manage, user=request.user,
            store_to_store_manage_lines=[(line.quantity, line)]
            )
        msg_dict = {
            "quantity": quantity,
            "store_to_store_manage": store_to_store_manage,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(store_to_store_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "store_to_store_manage": store_to_store_manage,
        "form": form,
        }
    template = "product_stock/store_to_store_manage/modal/add_product_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# --------------------------------------------------------------------------------------------

# 数量变更--有
@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def select_product_stock_to_manual_inventory_manage(
        request, manual_inventory_manage_pk
        ):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    form = forms.AddProductStockToManualInventoryManageForm(
        request.POST or None, manual_inventory_manage=manual_inventory_manage
        )
    status = 200
    if form.is_valid():
        product_stock = form.cleaned_data['product_stock']
        quantity = form.cleaned_data['quantity']
        line = add_product_stock_s_to_manual_inventory_manage( manual_inventory_manage,
                                                               product_stock,
                                                               quantity,
                                                               ManualInventoryType.LOCK,
                                                               ManualInventoryStatus.MANUAL_LOCK_PREDESTINATE
                                                               )
        change_product_stock_quantity_s(
            product_stock,
            is_cancel=False,
            is_Fulfillment=False,
            is_no_imei=True,
            quantity_locking_dif=quantity,
            quantity_allocated_dif=0,
            quantity_predestinate_dif=0,
            )
        events.draft_manual_inventory_manage_added_product_object_stock_s_event(
            manual_inventory_manage=manual_inventory_manage, user=request.user,
            manual_inventory_manage_lines=[(line.quantity, line)]
            )
        msg_dict = {
            "quantity": quantity,
            "manual_inventory_manage": manual_inventory_manage,
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(manual_inventory_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "manual_inventory_manage": manual_inventory_manage,
        "form": form,
        }
    template = "product_stock/manual_inventory_manage/modal/add_product_stock_list.html"
    return TemplateResponse( request, template, ctx, status=status )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def add_new_product_to_barter_manage_numerous(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.BarterManageAddProductForm_with_iemi(
        request.POST or None, barter_manage=barter_manage
        )
    status = 200
    if request.POST and form.is_valid():
        quantity = form.cleaned_data['quantity']
        jan_search = request.POST["jan_code"]

        try:
            product_stock_temp = ProductStock.objects.get( jan_code=jan_search )
        except ProductStock.DoesNotExist:
            product_stock_temp = ProductStock(
                name=form.cleaned_data['name'],
                jan_code=jan_search,
                description=form.cleaned_data['description'],
                is_temp=True
                )
            product_stock_temp.save()

        redirect_url = reverse(
            "input-iemi-to-barter-manage",
            kwargs={ "barter_manage_pk": barter_manage_pk,
                     "product_stock_temp_pk": product_stock_temp.pk,
                     "quantity": quantity
                     },
            )

        return (
            JsonResponse( { "redirectUrl": redirect_url } )
            if request.is_ajax()
            else redirect( redirect_url )
        )

    ctx = {
        "barter_manage": barter_manage,
        "form": form,
        }
    template = "product_stock/barter_manage/add_new_product_numenous.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def input_iemi_to_barter_manage(
        request, barter_manage_pk, product_stock_temp_pk, quantity
        ):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    product_stock_temp = get_object_or_404( ProductStock.objects.all(),
                                            pk=product_stock_temp_pk
                                            )

    ProductObjectFormSet = inlineformset_factory(
        ProductStock,
        ProductObjectStock,
        fields=("imei_code",
                "price_override_amount",
                "extra_informations",
                "status",
                "shops",
                "notion",
                ),
        extra=int( quantity ),
        can_delete=False,
        labels={
            "imei_code": "IMEI",
            "notion": "備考",
            "price_override_amount": "買取価格",
            "extra_informations": "追加情報",
            "status": "状態",
            "shops": "店舗",
            }
        )

    formset = ProductObjectFormSet( queryset=ProductObjectStock.objects.none(),
                                    instance=product_stock_temp
                                    )
    formbulk = forms.BulkChangeForm( request.POST or None )
    status = 200
    if request.method == "POST":
        formset = ProductObjectFormSet( request.POST, instance=product_stock_temp )
        if formset.is_valid():
            product_object_stock_s = formset.save( commit=False )
            for object_instance in product_object_stock_s:
                object_instance.is_temp = True
                object_instance.is_available_M = False
                object_instance.save()
                line = add_product_object_stock_s_to_barter_manage( barter_manage,
                                                                    object_instance,
                                                                    BarterManageType.MOVEIN,
                                                                    BarterManageStatus.BARTER_MOVE_IN_PREDESTINATE
                                                                    )
                change_product_stock_quantity_s(
                    product_stock_temp,
                    is_cancel=False,
                    is_Fulfillment=False,
                    is_no_imei=False,
                    quantity_locking_dif=0,
                    quantity_allocated_dif=0,
                    quantity_predestinate_dif=1,
                    )
        events.draft_barter_manage_added_product_object_stock_s_with_IEMI_event(
            barter_manage=barter_manage, user=request.user
            )

        msg_dict = {
            "barter_manage": barter_manage,
            "quantity": int( quantity ),
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(barter_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )

    ctx = {
        "barter_manage": barter_manage,
        "product_stock_temp": product_stock_temp,
        "formset": formset,
        "formbulk": formbulk,
        }
    template = "product_stock/barter_manage/add_product_input_IEMI.html"
    return TemplateResponse( request, template, ctx, status=status )

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

# 入庫商品を追加(IMEI確定)(大量追加)
@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def add_new_product_to_order_manage_numerous(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )

    form = forms.OrderManageAddProductForm_with_iemi(
        request.POST or None, order_manage=order_manage, no_imei=False
        )
    status = 200
    if request.POST and form.is_valid():
        quantity = form.cleaned_data['quantity']
        jan_search = request.POST["jan_code"]

        try:
            product_stock_temp = ProductStock.objects.get( jan_code=jan_search )
        except ProductStock.DoesNotExist:
            product_stock_temp = ProductStock(
                name=form.cleaned_data['name'],
                jan_code=jan_search,
                description=form.cleaned_data['description'],
                is_temp=True
                )
            product_stock_temp.save()

        redirect_url = reverse(
            "input-iemi-to-order-manage",
            kwargs={ "order_manage_pk": order_manage_pk,
                     "product_stock_temp_pk": product_stock_temp.pk,
                     "quantity": quantity
                     },
            )

        return (
            JsonResponse( { "redirectUrl": redirect_url } )
            if request.is_ajax()
            else redirect( redirect_url )
        )

    ctx = {
        "order_manage": order_manage,
        "form": form,

        }
    template = "product_stock/order_manage/add_new_product_numenous.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def input_iemi_to_order_manage(
        request, order_manage_pk, product_stock_temp_pk, quantity
        ):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    product_stock_temp = get_object_or_404( ProductStock.objects.all(),
                                            pk=product_stock_temp_pk
                                            )

    ProductObjectFormSet = inlineformset_factory(
        ProductStock,
        ProductObjectStock,
        fields=("imei_code",
                "price_override_amount",
                "extra_informations",
                "status",
                "shops",
                "notion",
                ),
        extra=int( quantity ),
        can_delete=False,
        labels={
            "imei_code": "IMEI",
            "notion": "備考",
            "price_override_amount": "買取価格",
            "extra_informations": "追加情報",
            "status": "状態",
            "shops": "店舗",
            },
        )

    formset = ProductObjectFormSet( queryset=ProductObjectStock.objects.none(),
                                    instance=product_stock_temp
                                    )
    formbulk = forms.BulkChangeForm( request.POST or None )
    status = 200
    if request.method == "POST":
        formset = ProductObjectFormSet( request.POST, instance=product_stock_temp )
        if formset.is_valid():
            product_object_stock_s = formset.save( commit=False )
            for object in product_object_stock_s:
                object.is_temp = True
                object.is_available_M = False
                object.save()
                line = add_product_object_stock_s_to_order_manage( order_manage,
                                                                   object,
                                                                   OrderManageType.STORAGE,
                                                                   OrderManageStatus.ORDER_STORAGE_PREDESTINATE
                                                                   )
                change_product_stock_quantity_s(
                    product_stock_temp,
                    is_cancel=False,
                    is_Fulfillment=False,
                    is_no_imei=False,
                    quantity_locking_dif=0,
                    quantity_allocated_dif=0,
                    quantity_predestinate_dif=1,
                    )
        events.draft_order_manage_added_product_object_stock_s_with_IEMI_event(
            order_manage=order_manage, user=request.user
            )

        msg_dict = {
            "order_manage": order_manage,
            "quantity": int( quantity ),
            }
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order",
                    "%(order_manage)sへ %(quantity)d 個商品を追加",
                    )
                % msg_dict
        )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )

    ctx = {
        "order_manage": order_manage,
        "product_stock_temp": product_stock_temp,
        "formset": formset,
        "formbulk": formbulk,
        }
    template = "product_stock/order_manage/add_product_input_IEMI.html"
    return TemplateResponse( request, template, ctx, status=status )

# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_list(request):
    order_manage_s = OrderManage.objects.prefetch_related( "order_manage_lines",
                                                           "suppliers",
                                                           "legal_person",
                                                           "responsible_person"
                                                           )
    order_manage_s = order_manage_s.order_by( "id" )
    order_manage_s_filter = OrderManageFilter( request.GET, queryset=order_manage_s )
    order_manage_s = get_paginator_items(
        order_manage_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )

    ctx = {
        "order_manage_s": order_manage_s,
        "order_manage_s_filter": order_manage_s_filter,
        "is_empty": not order_manage_s_filter.queryset.exists(),
        }
    return TemplateResponse( request, "product_stock/order_manage/list.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_list(request):
    barter_manage_s = BarterManage.objects.prefetch_related( "barter_manage_lines",
                                                             "responsible_person"
                                                             )

    barter_manage_s = barter_manage_s.order_by( "id" )
    barter_manage_s_filter = BarterManageFilter( request.GET, queryset=barter_manage_s )
    barter_manage_s = get_paginator_items(
        barter_manage_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )

    ctx = {
        "barter_manage_s": barter_manage_s,
        "barter_manage_s_filter": barter_manage_s_filter,
        "is_empty": not barter_manage_s_filter.queryset.exists(),
        }

    return TemplateResponse( request, "product_stock/barter_manage/list.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_list(request):
    store_to_store_manage_s = StoreToStoreManage.objects.prefetch_related(
        "store_to_store_manage_lines",
        "responsible_person"
        )

    store_to_store_manage_s = store_to_store_manage_s.order_by( "id" )
    store_to_store_manage_s_filter = StoreToStoreManageFilter( request.GET,
                                                               queryset=store_to_store_manage_s
                                                               )
    store_to_store_manage_s = get_paginator_items(
        store_to_store_manage_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )

    ctx = {
        "store_to_store_manage_s": store_to_store_manage_s,
        "store_to_store_manage_s_filter": store_to_store_manage_s_filter,
        "is_empty": not store_to_store_manage_s_filter.queryset.exists(),
        }
    return TemplateResponse( request,
                             "product_stock/store_to_store_manage/list.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def manual_inventory_manage_list(request):
    manual_inventory_manage_s = ManualInventoryManage.objects.prefetch_related(
        "manual_inventory_manage_lines",
        "responsible_person"
        )

    manual_inventory_manage_s = manual_inventory_manage_s.order_by( "id" )
    manual_inventory_manage_s_filter = ManualInventoryManageFilter( request.GET,
                                                                    queryset=manual_inventory_manage_s
                                                                    )
    manual_inventory_manage_s = get_paginator_items(
        manual_inventory_manage_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )

    ctx = {
        "manual_inventory_manage_s": manual_inventory_manage_s,
        "manual_inventory_manage_s_filter": manual_inventory_manage_s_filter,
        "is_empty": not manual_inventory_manage_s_filter.queryset.exists(),
        }

    return TemplateResponse( request,
                             "product_stock/manual_inventory_manage/list.html",
                             ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.manage_shopss" )
def shop_list(request):
    shops = Shops.objects.prefetch_related()
    ctx = {
        "shops": shops,
        }
    return TemplateResponse( request, "product_stock/shops/shops.html", ctx )


@staff_member_required
@permission_required( "product_stock.manage_shopss" )
def shop_create(request):
    shop = Shops()
    form = forms.ShopsForm( request.POST or None, instance=shop )
    if form.is_valid():
        shop = form.save()
        msg = pgettext_lazy( "Dashboard message", "店舗を新規追加" )
        messages.success( request, msg )
        return redirect( "shop-list" )
    ctx = { "shop": shop, "form": form }
    return TemplateResponse( request, "product_stock/shops/forms.html", ctx )


@staff_member_required
@permission_required( "product_stock.manage_shopss" )
def shop_edit(request, shop_pk):
    shop = get_object_or_404( Shops, pk=shop_pk )
    form = forms.ShopsForm( request.POST or None, instance=shop )
    if form.is_valid():
        shop = form.save()
        msg = pgettext_lazy( "Dashboard message", "店舗を編集済" )
        messages.success( request, msg )
        return redirect( "shop-list" )
    ctx = { "shop": shop, "form": form }
    return TemplateResponse( request, "product_stock/shops/forms.html", ctx )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.manage_E_mark" )
def E_market_list(request):
    E_market_s = E_mark.objects.prefetch_related()
    ctx = {
        "E_market_s": E_market_s,
        }
    return TemplateResponse( request, "product_stock/E_market/E_market.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_E_mark" )
def E_market_create(request):
    E_market = E_mark()
    form = forms.EmarketForm( request.POST or None, instance=E_market )
    if form.is_valid():
        E_market = form.save()
        msg = pgettext_lazy( "Dashboard message", "Eマーケットを新規追加" )
        messages.success( request, msg )
        return redirect( "E-market-list" )
    ctx = { "E_market": E_market, "form": form }
    return TemplateResponse( request, "product_stock/E_market/forms.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_E_mark" )
def E_market_edit(request, E_market_pk):
    E_market = get_object_or_404( E_mark, pk=E_market_pk )
    form = forms.EmarketForm( request.POST or None, instance=E_market )
    if form.is_valid():
        E_market = form.save()
        msg = pgettext_lazy( "Dashboard message", "Eマーケットを編集済" )
        messages.success( request, msg )
        return redirect( "E-market-list" )
    ctx = { "E_market": E_market, "form": form }
    return TemplateResponse( request, "product_stock/E_market/forms.html",
                             ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.manage_extrainformation" )
def extra_information_list(request):
    extra_informations = ExtraInformation.objects.prefetch_related()
    ctx = {
        "extra_informations": extra_informations,
        }
    return TemplateResponse( request,
                             "product_stock/ExtraInformation/extrainformationlist.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_extrainformation" )
def extra_information_create(request):
    extra_information = ExtraInformation()
    form = forms.ExtraInformationForm( request.POST or None,
                                       instance=extra_information
                                       )
    if form.is_valid():
        extra_information = form.save()
        msg = pgettext_lazy( "Dashboard message", "追加情報を追加" )
        messages.success( request, msg )
        return redirect( "extra-information-list" )
    ctx = { "extra_information": extra_information, "form": form }
    return TemplateResponse( request,
                             "product_stock/ExtraInformation/forms.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_extrainformation" )
def extra_information_edit(request, extra_information_pk):
    extra_information = get_object_or_404( ExtraInformation, pk=extra_information_pk )
    form = forms.ExtraInformationForm( request.POST or None,
                                       instance=extra_information
                                       )
    if form.is_valid():
        extra_information = form.save()
        msg = pgettext_lazy( "Dashboard message", "追加情報を編集済" )
        messages.success( request, msg )
        return redirect( "extra-information-list" )
    ctx = { "extra_information": extra_information, "form": form }
    return TemplateResponse( request,
                             "product_stock/ExtraInformation/forms.html", ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.manage_suppliers" )
def suppliers_list(request):
    suppliers_s = Suppliers.objects.prefetch_related()
    suppliers_s_filter = SuppliersFilter( request.GET,
                                          queryset=suppliers_s
                                          )
    suppliers_s = get_paginator_items(
        suppliers_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )
    ctx = {
        "suppliers_s": suppliers_s,
        "suppliers_s_filter": suppliers_s_filter,
        "is_empty": not suppliers_s_filter.queryset.exists(),
        }
    return TemplateResponse( request,
                             "product_stock/Suppliers/suppliers.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_suppliers" )
def suppliers_create(request):
    suppliers = Suppliers()
    form = forms.SuppliersForm( request.POST or None
                                )
    if form.is_valid():
        new_supplier = Suppliers.objects.create(
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            phone=form.cleaned_data["phone"],
            first_name_kannji=form.cleaned_data["first_name_kannji"],
            last_name_kannji=form.cleaned_data["last_name_kannji"],
            age=form.cleaned_data["age"],
            gender=form.cleaned_data["gender"],
            birth=form.cleaned_data["birth"],
            work=form.cleaned_data["work"],
            note=form.cleaned_data["note"],
            )
        new_address = Address.objects.create(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            phone=form.cleaned_data["phone"],
            postal_code=form.cleaned_data["postal_code"],
            city_area=form.cleaned_data["city_area"],
            city=form.cleaned_data["city"],
            street_address_1=form.cleaned_data["street_address_1"],
            street_address_2=form.cleaned_data["street_address_2"],
            )
        new_address.save()
        new_supplier.save()
        supplier = get_object_or_404(
            Suppliers.objects.filter( id=new_supplier.id )
            )
        supplier.address.add( new_address )
        msg = (
            pgettext_lazy( "Dashboard message", "取引先(個人)を追加" )
        )
        messages.success( request, msg )
        return redirect( "suppliers-details", suppliers_pk=suppliers.pk )
    ctx = { "suppliers": suppliers, "form": form }
    return TemplateResponse( request,
                             "product_stock/Suppliers/forms.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_suppliers" )
def suppliers_edit(request, suppliers_pk):
    suppliers = get_object_or_404( Suppliers, pk=suppliers_pk )
    address = suppliers.address.all().last()
    if not address:
        address = Address.objects.create( suppliers_addresses=suppliers )
    suppliers_dict = model_to_dict( suppliers )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **suppliers_dict }
    form = forms.SuppliersForm( request.POST or None,
                                initial=initial_dict
                                )
    if form.is_valid():
        suppliers.email = form.cleaned_data["email"]
        suppliers.first_name = form.cleaned_data["first_name"]
        suppliers.last_name = form.cleaned_data["last_name"]
        suppliers.phone = form.cleaned_data["phone"]
        suppliers.first_name_kannji = form.cleaned_data["first_name_kannji"]
        suppliers.last_name_kannji = form.cleaned_data["last_name_kannji"]
        suppliers.age = form.cleaned_data["age"]
        suppliers.gender = form.cleaned_data["gender"]
        suppliers.birth = form.cleaned_data["birth"]
        suppliers.work = form.cleaned_data["work"]
        suppliers.note = form.cleaned_data["note"]
        suppliers.save()
        address.first_name = form.cleaned_data["first_name"]
        address.last_name = form.cleaned_data["last_name"]
        address.phone = form.cleaned_data["phone"]
        address.postal_code = form.cleaned_data["postal_code"]
        address.city_area = form.cleaned_data["city_area"]
        address.city = form.cleaned_data["city"]
        address.street_address_1 = form.cleaned_data["street_address_1"]
        address.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()
        msg = (
            pgettext_lazy( "Dashboard message", "取引先(個人)を編集済" )
        )
        messages.success( request, msg )
        return redirect( "suppliers-details", suppliers_pk=suppliers.pk )

    ctx = { "suppliers": suppliers, "form": form }
    return TemplateResponse( request,
                             "product_stock/Suppliers/forms.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_suppliers" )
def suppliers_details(request, suppliers_pk):
    qs = Suppliers.objects.prefetch_related(
        "order_manage_suppliers",
        )
    suppliers = get_object_or_404( qs, pk=suppliers_pk )
    address = suppliers.address.all().last()
    order_manage_suppliers = OrderManage.objects.filter(
        suppliers=suppliers
        )
    barter_manage_suppliers = BarterManage.objects.filter(
        suppliers=suppliers
        )
    ctx = { "suppliers": suppliers,
            "order_manage_suppliers": order_manage_suppliers,
            "barter_manage_suppliers": barter_manage_suppliers,
            "address": address
            }
    return TemplateResponse( request,
                             "product_stock/Suppliers/detail.html", ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.manage_legalperson" )
def legal_person_list(request):
    legal_person = LegalPerson.objects.prefetch_related()
    legal_person_s_filter = LegalPersonFilter( request.GET,
                                               queryset=legal_person
                                               )
    legal_person = get_paginator_items(
        legal_person_s_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )
    ctx = {
        "legal_person_s": legal_person,
        "legal_person_s_filter": legal_person_s_filter,
        "is_empty": not legal_person_s_filter.queryset.exists(),
        }
    return TemplateResponse( request,
                             "product_stock/LegalPerson/legal_person.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_legalperson" )
def legal_person_create(request):
    legal_person = LegalPerson()
    form = forms.LegalPersonForm( request.POST or None
                                  )
    if form.is_valid():
        new_legalperson = LegalPerson.objects.create(
            email=form.cleaned_data["email"],
            company_name=form.cleaned_data["company_name"],
            phone=form.cleaned_data["phone"],
            fax=form.cleaned_data["fax"],
            homepage=form.cleaned_data["homepage"],
            note=form.cleaned_data["note"],
            )
        new_address = Address.objects.create(
            first_name=form.cleaned_data["company_name"],
            phone=form.cleaned_data["phone"],
            postal_code=form.cleaned_data["postal_code"],
            city_area=form.cleaned_data["city_area"],
            city=form.cleaned_data["city"],
            street_address_1=form.cleaned_data["street_address_1"],
            street_address_2=form.cleaned_data["street_address_2"],
            )
        new_address.save()
        new_legalperson.save()
        legal_person = get_object_or_404(
            LegalPerson.objects.filter( id=new_legalperson.id )
            )
        legal_person.address.add( new_address )
        legal_person.save()
        msg = pgettext_lazy( "Dashboard message", "取引先(個人)を編集済" )
        messages.success( request, msg )
        return redirect( "legal-person-details",
                         legal_person_pk=legal_person.pk
                         )

    ctx = { "legal_person": legal_person, "form": form }
    return TemplateResponse( request,
                             "product_stock/LegalPerson/forms.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_legalperson" )
def legal_person_edit(request, legal_person_pk):
    legal_person = get_object_or_404( LegalPerson, pk=legal_person_pk )
    address = legal_person.address.all().last()
    if not address:
        address = Address.objects.create( legal_person_addresses=legal_person )
    legal_person_dict = model_to_dict( legal_person )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **legal_person_dict }
    form = forms.LegalPersonForm( request.POST or None,
                                  initial=initial_dict
                                  )
    if form.is_valid():
        legal_person.email = form.cleaned_data["email"]
        legal_person.company_name = form.cleaned_data["company_name"]
        legal_person.phone = form.cleaned_data["phone"]
        legal_person.fax = form.cleaned_data["fax"]
        legal_person.homepage = form.cleaned_data["homepage"]
        legal_person.note = form.cleaned_data["note"]
        legal_person.save()

        address.first_name = form.cleaned_data["company_name"]
        address.phone = form.cleaned_data["phone"]
        address.postal_code = form.cleaned_data["postal_code"]
        address.city_area = form.cleaned_data["city_area"]
        address.city = form.cleaned_data["city"]
        address.street_address_1 = form.cleaned_data["street_address_1"]
        address.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()

        msg = pgettext_lazy( "Dashboard message", "取引先(法人)を編集済" )
        messages.success( request, msg )
        return redirect( "legal-person-details",
                         legal_person_pk=legal_person.pk
                         )
    ctx = { "legal_person": legal_person, "form": form }
    return TemplateResponse( request,
                             "product_stock/LegalPerson/forms.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_legalperson" )
def legal_person_details(request, legal_person_pk):
    qs = LegalPerson.objects.prefetch_related(
        "order_manage_legal_person",
        )
    legal_person = get_object_or_404( qs, pk=legal_person_pk )
    address = legal_person.address.all().last()
    order_manage_legal_person = OrderManage.objects.filter(
        legal_person=legal_person
        )
    barter_manage_legal_person = BarterManage.objects.filter(
        legal_person=legal_person
        )
    ctx = { "legal_person": legal_person,
            "order_manage_legal_person": order_manage_legal_person,
            "barter_manage_legal_person": barter_manage_legal_person,
            "address": address,
            }
    return TemplateResponse( request,
                             "product_stock/LegalPerson/detail.html", ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.manage_product_stock_status" )
def product_stock_status_list(request):
    product_stock_status_s = ProductStockStatus.objects.prefetch_related()
    ctx = {
        "product_stock_status_s": product_stock_status_s,
        }
    return TemplateResponse( request,
                             "product_stock/product_stock_status/product_stock_status.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_stock_status" )
def product_stock_status_create(request):
    product_stock_status = ProductStockStatus()
    form = forms.ProductStockStatusForm( request.POST or None,
                                         instance=product_stock_status
                                         )
    if form.is_valid():
        product_stock_status = form.save()
        msg = pgettext_lazy( "Dashboard message", "商品状態を追加" )
        messages.success( request, msg )
        return redirect( "product-stock-status-list" )
    ctx = { "product_stock_status": product_stock_status, "form": form }
    return TemplateResponse( request,
                             "product_stock/product_stock_status/forms.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_stock_status" )
def product_stock_status_edit(request, product_stock_status_pk):
    product_stock_status = get_object_or_404( ExtraInformation,
                                              pk=product_stock_status_pk
                                              )
    form = forms.ProductStockStatusForm( request.POST or None,
                                         instance=product_stock_status
                                         )
    if form.is_valid():
        product_stock_status = form.save()
        msg = pgettext_lazy( "Dashboard message", "商品状態を編集" )
        messages.success( request, msg )
        return redirect( "product-stock-status-list" )
    ctx = { "product_stock_status": product_stock_status, "form": form }
    return TemplateResponse( request,
                             "product_stock/product_stock_status/forms.html",
                             ctx
                             )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def create_order_manage_from_draft(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    status = 200
    form = forms.CreateOrderManageFromDraftForm( request.POST or None,
                                                 instance=order_manage
                                                 )
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            "Dashboard message related to an order", "注文出入庫執行表を作成"
            )
        events.order_manage_created_event( order_manage=order_manage,
                                           user=request.user
                                           )
        # TODO:资金状况变更

        messages.success( request, msg )
        if form.cleaned_data.get( "notify_customer" ):
            pass
        # TODO:email

        # emails.send_order_manage_confirmation.delay(order_manage.pk, request.user.pk)
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    template = "product_stock/order_manage/model/create_order_manage.html"
    ctx = { "form": form, "order_manage": order_manage }
    return TemplateResponse( request, template, ctx, status=status )

@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def create_barter_manage_from_draft(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    status = 200
    form = forms.CreateBarterManageFromDraftForm( request.POST or None,
                                                  instance=barter_manage
                                                  )
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            "Dashboard message related to an order", "店舗間移動執行表を作成"
            )
        events.barter_manage_created_event(
            barter_manage=barter_manage,
            user=request.user
            )
        # TODO:资金状况变更

        messages.success( request, msg )
        if form.cleaned_data.get( "notify_customer" ):
            pass
        # TODO:email

        # emails.send_barter_manage_confirmation.delay(barter_manage.pk, request.user.pk)
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    template = "product_stock/barter_manage/modal/create_barter_manage.html"
    ctx = { "form": form, "barter_manage": barter_manage }
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def create_store_to_store_manage_from_draft(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    status = 200
    form = forms.CreateStoreToStoreManageFromDraftForm( request.POST or None,
                                                        instance=store_to_store_manage
                                                        )
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            "Dashboard message related to an order", "店舗間移動執行表を作成"
            )
        events.store_to_store_manage_created_event(
            store_to_store_manage=store_to_store_manage,
            user=request.user
            )
        # TODO:资金状况变更

        messages.success( request, msg )
        if form.cleaned_data.get( "notify_customer" ):
            pass
        # TODO:email

        # emails.send_store_to_store_manage_confirmation.delay(store_to_store_manage.pk, request.user.pk)
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    template = "product_stock/store_to_store_manage/modal/create_store_to_store_manage.html"
    ctx = { "form": form, "store_to_store_manage": store_to_store_manage }
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def create_manual_inventory_manage_from_draft(request, manual_inventory_manage_pk):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    status = 200
    form = forms.CreateManualInventoryManageFromDraftForm( request.POST or None,
                                                           instance=manual_inventory_manage
                                                           )
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            "Dashboard message related to an order", "商品ロック執行表を作成"
            )
        events.manual_inventory_manage_created_event(
            manual_inventory_manage=manual_inventory_manage,
            user=request.user
            )
        # TODO:资金状况变更

        messages.success( request, msg )
        if form.cleaned_data.get( "notify_customer" ):
            pass
        # TODO:email

        # emails.send_manual_inventory_manage_confirmation.delay(manual_inventory_manage.pk, request.user.pk)
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    template = "product_stock/manual_inventory_manage/modal/create_manual_inventory_manage.html"
    ctx = { "form": form, "manual_inventory_manage": manual_inventory_manage }
    return TemplateResponse( request, template, ctx, status=status )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_create(request, order_manage_type_No=0):
    msg = pgettext_lazy( "Dashboard message related to an order",
                         "注文出入庫下書き作成"
                         )
    if int( order_manage_type_No ) == 0:
        order_manage = OrderManage.objects.create(
            order_status=InventoryStatus.DRAFT,
            funds_status=InventoryFundsStatus.OTHER,
            responsible_person=request.user,
            type_No=0
            )
    elif int( order_manage_type_No ) == 1:
        order_manage = OrderManage.objects.create(
            order_status=InventoryStatus.DRAFT,
            funds_status=InventoryFundsStatus.OTHER,
            responsible_person=request.user,
            type_No=1
            )
    else:
        order_manage = OrderManage.objects.create(
            order_status=InventoryStatus.DRAFT,
            funds_status=InventoryFundsStatus.OTHER,
            responsible_person=request.user,
            type_No=2
            )
    events.draft_order_manage_created_event( order_manage=order_manage,
                                             user=request.user
                                             )
    messages.success( request, msg )
    return redirect( "order-manage-details", order_manage_pk=order_manage.pk )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_create(request):
    msg = pgettext_lazy( "Dashboard message related to an order",
                         "物々交換下書き作成"
                         )
    barter_manage = BarterManage.objects.create(
        barter_status=InventoryStatus.DRAFT,
        responsible_person=request.user
        )
    # Create the draft creation event
    events.draft_barter_manage_created_event( barter_manage=barter_manage,
                                              user=request.user
                                              )
    # Send success message and redirect to the draft details
    messages.success( request, msg )
    return redirect( "barter-manage-details",
                     barter_manage_pk=barter_manage.pk
                     )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_create(request):
    msg = pgettext_lazy( "Dashboard message related to an order",
                         "物々交換下書き作成"
                         )
    store_to_store_manage = StoreToStoreManage.objects.create(
        store_to_store_status=InventoryStatus.DRAFT,
        funds_status=InventoryFundsStatus.OTHER,
        responsible_person=request.user
        )
    # Create the draft creation event
    events.draft_store_to_store_manage_created_event(
        store_to_store_manage=store_to_store_manage, user=request.user
        )
    # Send success message and redirect to the draft details
    messages.success( request, msg )
    return redirect( "store-to-store-manage-details",
                     store_to_store_manage_pk=store_to_store_manage.pk
                     )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def manual_inventory_manage_create(request):
    msg = pgettext_lazy( "Dashboard message related to an order",
                         "商品ロック執行表下書き作成"
                         )
    manual_inventory_manage = ManualInventoryManage.objects.create(
        manual_inventory_status=InventoryStatus.DRAFT,
        funds_status=InventoryFundsStatus.OTHER,
        responsible_person=request.user
        )
    # Create the draft creation event
    events.draft_manual_inventory_manage_created_event(
        manual_inventory_manage=manual_inventory_manage, user=request.user
        )
    # Send success message and redirect to the draft details
    messages.success( request, msg )
    return redirect( "manual-inventory-manage-details",
                     manual_inventory_manage_pk=manual_inventory_manage.pk
                     )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_add_to_shops(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )

    form = forms.StoreToStoreManageToShopForm( request.POST or None,
                                               store_to_store_manage=store_to_store_manage
                                               )
    status = 200

    if form.is_valid():
        if form.cleaned_data["name"]:
            store_to_store_manage.to_shop = form.cleaned_data["name"]
            store_to_store_manage.save()
        else:
            msg = (
                pgettext_lazy( "Dashboard message", "エラー：移動先を選択ください" )
            )
            messages.error( request, msg )
            return redirect( "store-to-store-manage-details",
                             store_to_store_manage_pk=store_to_store_manage_pk
                             )
        msg = (
            pgettext_lazy( "Dashboard message", "店舗間移動へ移動先を選択" )
        )
        messages.success( request, msg )

        events.store_to_store_manage_to_shop_added_event(
            store_to_store_manage=store_to_store_manage,
            user=request.user
            )
        #
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "store_to_store_manage": store_to_store_manage, "form": form }
    return TemplateResponse(
        request,
        "product_stock/store_to_store_manage/modal/edit_to_shop.html", ctx,
        status=status
        )

# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_add_suppliers(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    form = forms.OrderManageSuppliersAddressForm( request.POST or None,
                                                  order_manage=order_manage
                                                  )
    status = 200
    if form.is_valid():
        email_search = request.POST["email"]
        try:
            supplier = Suppliers.objects.get( email=email_search )
        except Suppliers.DoesNotExist:
            new_supplier = Suppliers.objects.create(
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone=form.cleaned_data["phone"],
                first_name_kannji=form.cleaned_data["first_name_kannji"],
                last_name_kannji=form.cleaned_data["last_name_kannji"],
                age=form.cleaned_data["age"],
                gender=form.cleaned_data["gender"],
                birth=form.cleaned_data["birth"],
                work=form.cleaned_data["work"],
                note=form.cleaned_data["note"],
                )
            new_address = Address.objects.create(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone=form.cleaned_data["phone"],
                postal_code=form.cleaned_data["postal_code"],
                city_area=form.cleaned_data["city_area"],
                city=form.cleaned_data["city"],
                street_address_1=form.cleaned_data["street_address_1"],
                street_address_2=form.cleaned_data["street_address_2"],
                )
            new_address.save()
            new_supplier.save()
            supplier = get_object_or_404(
                Suppliers.objects.filter( id=new_supplier.id )
                )
            supplier.address.add( new_address )
        order_manage.suppliers = supplier
        order_manage.save()
        msg = (
            pgettext_lazy( "Dashboard message", "注文出入庫へ取引先(個人)を追加" )
        )
        messages.success( request, msg )

        events.order_manage_supplier_added_event(
            order_manage=order_manage,
            user=request.user
            )

        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form }
    return TemplateResponse(
        request, "product_stock/order_manage/edit_suppliers.html", ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_add_suppliers(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.BarterManageSuppliersAddressForm( request.POST or None,
                                                   barter_manage=barter_manage
                                                   )
    status = 200

    if form.is_valid():
        email_search = request.POST["email"]
        try:
            supplier = Suppliers.objects.get( email=email_search )
        except Suppliers.DoesNotExist:
            new_supplier = Suppliers.objects.create(
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone=form.cleaned_data["phone"],
                first_name_kannji=form.cleaned_data["first_name_kannji"],
                last_name_kannji=form.cleaned_data["last_name_kannji"],
                age=form.cleaned_data["age"],
                gender=form.cleaned_data["gender"],
                birth=form.cleaned_data["birth"],
                work=form.cleaned_data["work"],
                note=form.cleaned_data["note"],
                )
            new_address = Address.objects.create(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone=form.cleaned_data["phone"],
                postal_code=form.cleaned_data["postal_code"],
                city_area=form.cleaned_data["city_area"],
                city=form.cleaned_data["city"],
                street_address_1=form.cleaned_data["street_address_1"],
                street_address_2=form.cleaned_data["street_address_2"],
                )
            new_address.save()
            new_supplier.save()
            supplier = get_object_or_404(
                Suppliers.objects.filter( id=new_supplier.id )
                )
            supplier.address.add( new_address )
        barter_manage.suppliers = supplier
        barter_manage.save()
        msg = (
            pgettext_lazy( "Dashboard message", "物々交換へ取引先(個人)を追加" )
        )
        messages.success( request, msg )

        events.barter_manage_supplier_added_event(
            barter_manage=barter_manage,
            user=request.user
            )

        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form }
    return TemplateResponse(
        request, "product_stock/barter_manage/edit_suppliers.html", ctx,
        status=status
        )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_add_legal_person(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    form = forms.OrderManageLegalPersonAddressForm( request.POST or None,
                                                    order_manage=order_manage
                                                    )
    status = 200

    if form.is_valid():
        email_search = request.POST["email"]
        try:
            legal_person = LegalPerson.objects.get( email=email_search )
        except LegalPerson.DoesNotExist:
            new_legalperson = LegalPerson.objects.create(
                email=form.cleaned_data["email"],
                company_name=form.cleaned_data["company_name"],
                phone=form.cleaned_data["phone"],
                fax=form.cleaned_data["fax"],
                homepage=form.cleaned_data["homepage"],
                note=form.cleaned_data["note"],
                )
            new_address = Address.objects.create(
                first_name=form.cleaned_data["company_name"],
                phone=form.cleaned_data["phone"],
                postal_code=form.cleaned_data["postal_code"],
                city_area=form.cleaned_data["city_area"],
                city=form.cleaned_data["city"],
                street_address_1=form.cleaned_data["street_address_1"],
                street_address_2=form.cleaned_data["street_address_2"],
                )
            new_address.save()
            new_legalperson.save()
            legal_person = get_object_or_404(
                LegalPerson.objects.filter( id=new_legalperson.id )
                )
            legal_person.address.add( new_address )
        order_manage.legal_person = legal_person
        order_manage.save()
        msg = (
            pgettext_lazy( "Dashboard message", "注文出入庫へ取引先(法人)を追加" )
        )
        messages.success( request, msg )

        events.order_manage_legal_person_added_event(
            order_manage=order_manage,
            user=request.user
            )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form }
    return TemplateResponse(
        request, "product_stock/order_manage/edit_legal_person.html",
        ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_add_legal_person(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    form = forms.BarterManageLegalPersonAddressForm( request.POST or None,
                                                     barter_manage=barter_manage
                                                     )
    status = 200

    if form.is_valid():
        email_search = request.POST["email"]
        try:
            legal_person = LegalPerson.objects.get( email=email_search )
        except LegalPerson.DoesNotExist:
            new_legalperson = LegalPerson.objects.create(
                email=form.cleaned_data["email"],
                company_name=form.cleaned_data["company_name"],
                phone=form.cleaned_data["phone"],
                fax=form.cleaned_data["fax"],
                homepage=form.cleaned_data["homepage"],
                note=form.cleaned_data["note"],
                )
            new_address = Address.objects.create(
                first_name=form.cleaned_data["company_name"],
                phone=form.cleaned_data["phone"],
                postal_code=form.cleaned_data["postal_code"],
                city_area=form.cleaned_data["city_area"],
                city=form.cleaned_data["city"],
                street_address_1=form.cleaned_data["street_address_1"],
                street_address_2=form.cleaned_data["street_address_2"],
                )
            new_address.save()
            new_legalperson.save()
            legal_person = get_object_or_404(
                LegalPerson.objects.filter( id=new_legalperson.id )
                )
            legal_person.address.add( new_address )
        barter_manage.legal_person = legal_person
        barter_manage.save()

        msg = (
            pgettext_lazy( "Dashboard message", "物々交換へ取引先(法人)を追加" )
        )
        messages.success( request, msg )

        events.barter_manage_legal_person_added_event(
            barter_manage=barter_manage,
            user=request.user
            )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form }
    return TemplateResponse(
        request, "product_stock/barter_manage/edit_legal_person.html",
        ctx,
        status=status
        )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_edit_legal_person(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    legal_person = order_manage.legal_person
    address = legal_person.address.all().last()
    legal_person_dict = model_to_dict( legal_person )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **legal_person_dict }
    form = forms.OrderManageLegalPersonAddressEditForm( request.POST or None,
                                                        initial=initial_dict
                                                        )
    status = 200
    if form.is_valid():
        legal_person.email = form.cleaned_data["email"]
        legal_person.company_name = form.cleaned_data["company_name"]
        legal_person.phone = form.cleaned_data["phone"]
        legal_person.fax = form.cleaned_data["fax"]
        legal_person.homepage = form.cleaned_data["homepage"]
        legal_person.note = form.cleaned_data["note"]
        legal_person.save()

        address.first_name = form.cleaned_data["company_name"]
        address.phone = form.cleaned_data["phone"]
        address.postal_code = form.cleaned_data["postal_code"]
        address.city_area = form.cleaned_data["city_area"]
        address.city = form.cleaned_data["city"]
        address.street_address_1 = form.cleaned_data["street_address_1"]
        address.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()

        msg = (
            pgettext_lazy( "Dashboard message", "注文出入庫へ取引先(法人)を編集" )
        )
        messages.success( request, msg )

        events.order_manage_legal_person_changed_event(
            order_manage=order_manage,
            user=request.user
            )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form, "edit": True }
    return TemplateResponse(
        request, "product_stock/order_manage/edit_legal_person.html",
        ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_edit_legal_person(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    legal_person = barter_manage.legal_person
    address = legal_person.address.all().last()
    legal_person_dict = model_to_dict( legal_person )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **legal_person_dict }
    form = forms.BarterManageLegalPersonAddressEditForm( request.POST or None,
                                                         initial=initial_dict
                                                         )
    status = 200
    if form.is_valid():
        legal_person.email = form.cleaned_data["email"]
        legal_person.company_name = form.cleaned_data["company_name"]
        legal_person.phone = form.cleaned_data["phone"]
        legal_person.fax = form.cleaned_data["fax"]
        legal_person.homepage = form.cleaned_data["homepage"]
        legal_person.note = form.cleaned_data["note"]
        legal_person.save()

        address.first_name = form.cleaned_data["company_name"]
        address.phone = form.cleaned_data["phone"]
        address.postal_code = form.cleaned_data["postal_code"]
        address.city_area = form.cleaned_data["city_area"]
        address.city = form.cleaned_data["city"]
        address.street_address_1 = form.cleaned_data["street_address_1"]
        address.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()

        msg = (
            pgettext_lazy( "Dashboard message", "物々交換へ取引先(法人)を編集" )
        )
        messages.success( request, msg )

        events.barter_manage_legal_person_changed_event(
            barter_manage=barter_manage,
            user=request.user
            )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form, "edit": True }
    return TemplateResponse(
        request, "product_stock/barter_manage/edit_legal_person.html",
        ctx,
        status=status
        )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_edit_suppliers(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    suppliers = order_manage.suppliers

    address = suppliers.address.all().last()

    suppliers_dict = model_to_dict( suppliers )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **suppliers_dict }
    form = forms.OrderManageSuppliersAddressEditForm( request.POST or None,
                                                      initial=initial_dict
                                                      )
    status = 200
    if form.is_valid():
        suppliers.email = form.cleaned_data["email"]
        suppliers.first_name = form.cleaned_data["first_name"]
        suppliers.last_name = form.cleaned_data["last_name"]
        suppliers.phone = form.cleaned_data["phone"]
        suppliers.first_name_kannji = form.cleaned_data["first_name_kannji"]
        suppliers.last_name_kannji = form.cleaned_data["last_name_kannji"]
        suppliers.age = form.cleaned_data["age"]
        suppliers.gender = form.cleaned_data["gender"]
        suppliers.birth = form.cleaned_data["birth"]
        suppliers.work = form.cleaned_data["work"]
        suppliers.note = form.cleaned_data["note"]
        suppliers.save()
        suppliers.first_name = form.cleaned_data["first_name"]
        suppliers.last_name = form.cleaned_data["last_name"]
        suppliers.phone = form.cleaned_data["phone"]
        suppliers.postal_code = form.cleaned_data["postal_code"]
        suppliers.city_area = form.cleaned_data["city_area"]
        suppliers.city = form.cleaned_data["city"]
        suppliers.street_address_1 = form.cleaned_data["street_address_1"]
        suppliers.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()
        msg = (
            pgettext_lazy( "Dashboard message", "注文出入庫へ取引先(個人)を編集" )
        )
        messages.success( request, msg )

        events.order_manage_supplier_changed_event(
            order_manage=order_manage,
            user=request.user
            )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form, "edit": True }
    return TemplateResponse(
        request, "product_stock/order_manage/edit_suppliers.html",
        ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_edit_suppliers(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    suppliers = barter_manage.suppliers

    address = suppliers.address.all().last()

    suppliers_dict = model_to_dict( suppliers )
    address_dict = model_to_dict( address )
    initial_dict = { **address_dict, **suppliers_dict }
    form = forms.BarterManageSuppliersAddressEditForm( request.POST or None,
                                                       initial=initial_dict
                                                       )
    status = 200
    if form.is_valid():
        suppliers.email = form.cleaned_data["email"]
        suppliers.first_name = form.cleaned_data["first_name"]
        suppliers.last_name = form.cleaned_data["last_name"]
        suppliers.phone = form.cleaned_data["phone"]
        suppliers.first_name_kannji = form.cleaned_data["first_name_kannji"]
        suppliers.last_name_kannji = form.cleaned_data["last_name_kannji"]
        suppliers.age = form.cleaned_data["age"]
        suppliers.gender = form.cleaned_data["gender"]
        suppliers.birth = form.cleaned_data["birth"]
        suppliers.work = form.cleaned_data["work"]
        suppliers.note = form.cleaned_data["note"]
        suppliers.save()
        suppliers.first_name = form.cleaned_data["first_name"]
        suppliers.last_name = form.cleaned_data["last_name"]
        suppliers.phone = form.cleaned_data["phone"]
        suppliers.postal_code = form.cleaned_data["postal_code"]
        suppliers.city_area = form.cleaned_data["city_area"]
        suppliers.city = form.cleaned_data["city"]
        suppliers.street_address_1 = form.cleaned_data["street_address_1"]
        suppliers.street_address_2 = form.cleaned_data["street_address_2"]
        address.save()
        msg = (
            pgettext_lazy( "Dashboard message", "注文出入庫へ取引先(個人)を編集" )
        )
        messages.success( request, msg )

        events.barter_manage_suppliers_changed_event(
            barter_manage=barter_manage,
            user=request.user
            )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )

    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form, "edit": True }
    return TemplateResponse(
        request, "product_stock/barter_manage/edit_suppliers.html",
        ctx,
        status=status
        )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------伝票番号----------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_add_slip_number(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage, pk=order_manage_pk )
    form = forms.OrderManageSlipNumberForm(request.POST or None, instance=order_manage)
    status = 200
    if form.is_valid():
        form.save()
        events.order_manage_add_slip_event(
            order_manage=order_manage, user=request.user
            )
        msg = pgettext_lazy( "Dashboard message related to an order", "伝票番号を追加した" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/order_manage/model/add_slip.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_add_slip_number(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage, pk=barter_manage_pk )
    form = forms.BarterManageSlipNumberForm(request.POST or None, instance=barter_manage)
    status = 200
    if form.is_valid():
        form.save()
        events.barter_manage_add_slip_event(
            barter_manage=barter_manage, user=request.user
            )
        msg = pgettext_lazy( "Dashboard message related to an barter", "伝票番号を追加した" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/barter_manage/modal/add_slip.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_add_slip_number(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage, pk=store_to_store_manage_pk )
    form = forms.StoreToStoreManageSlipNumberForm(request.POST or None, instance=store_to_store_manage)
    status = 200
    if form.is_valid():
        form.save()
        events.store_to_store_manage_add_slip_event(
            store_to_store_manage=store_to_store_manage, user=request.user
            )
        msg = pgettext_lazy( "Dashboard message related to an barter", "伝票番号を追加した" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "store_to_store_manage": store_to_store_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/store_to_store_manage/modal/add_slip.html"
    return TemplateResponse( request, template, ctx, status=status )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_add_note(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage, pk=order_manage_pk )
    form = forms.OrderManageNoteForm( request.POST or None )
    status = 200
    if form.is_valid():
        events.order_manage_note_added_event(
            order_manage=order_manage, user=request.user,
            message=form.cleaned_data["message"]
            )
        msg = pgettext_lazy( "Dashboard message related to an order", "ノートを追加" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/order_manage/model/add_note.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_add_note(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage, pk=barter_manage_pk )
    form = forms.BarterManageNoteForm( request.POST or None )
    status = 200
    if form.is_valid():
        events.barter_manage_note_added_event(
            barter_manage=barter_manage, user=request.user,
            message=form.cleaned_data["message"]
            )
        msg = pgettext_lazy( "Dashboard message related to an order", "ノートを追加" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/barter_manage/modal/add_note.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_add_note(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage,
                                               pk=store_to_store_manage_pk
                                               )
    form = forms.StoreToStoreManageNoteForm( request.POST or None )
    status = 200
    if form.is_valid():
        events.store_to_store_manage_note_added_event(
            store_to_store_manage=store_to_store_manage, user=request.user,
            message=form.cleaned_data["message"]
            )
        msg = pgettext_lazy( "Dashboard message related to an order", "ノートを追加" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "store_to_store_manage": store_to_store_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/store_to_store_manage/modal/add_note.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def manual_inventory_manage_add_note(request, manual_inventory_manage_pk):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage,
                                                 pk=manual_inventory_manage_pk
                                                 )
    form = forms.ManualInventoryManageNoteForm( request.POST or None )
    status = 200
    if form.is_valid():
        events.manual_inventory_manage_note_added_event(
            manual_inventory_manage=manual_inventory_manage, user=request.user,
            message=form.cleaned_data["message"]
            )
        msg = pgettext_lazy( "Dashboard message related to an order", "ノートを追加" )
        messages.success( request, msg )
    elif form.errors:
        status = 400
    ctx = { "manual_inventory_manage": manual_inventory_manage, "form": form }
    ctx.update( csrf( request ) )
    template = "product_stock/manual_inventory_manage/modal/add_note.html"
    return TemplateResponse( request, template, ctx, status=status )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def order_manage_details(request, order_manage_pk):
    qs = OrderManage.objects.select_related(
        "suppliers", "legal_person"
        ).prefetch_related(
        "events__responsible_person",
        "order_manage_lines__product_object_stock__product_stock",
        "fulfillments__lines__order_manage_line",
        )
    order_manage = get_object_or_404( qs, pk=order_manage_pk )
    if order_manage.type_No == 0:
        is_delivery = False
        is_coordination = False
    elif order_manage.type_No == 1:
        is_delivery = True
        is_coordination = False
    else:
        is_delivery = True
        is_coordination = True

    ctx = {
        "order_manage": order_manage,
        "order_manage_get_total_quantity": order_manage.get_total_quantity(),
        "events": order_manage.events.order_by( "-date" ).all(),
        "order_manage_fulfillments": order_manage.fulfillments.all(),
        "notes": order_manage.events.filter( type=events.ManageEvents.NOTE_ADDED ),
        "is_delivery": is_delivery,
        "is_coordination": is_coordination
        }
    return TemplateResponse( request,
                             "product_stock/order_manage/detail.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def barter_manage_details(request, barter_manage_pk):
    qs = BarterManage.objects.select_related().prefetch_related(
        "events__responsible_person",
        "barter_manage_lines__product_object_stock__product_stock",
        "fulfillments__lines__barter_manage_line",
        )
    barter_manage = get_object_or_404( qs, pk=barter_manage_pk )
    ctx = {
        "barter_manage": barter_manage,
        "barter_manage_get_total_quantity": barter_manage.get_total_quantity(),
        "events": barter_manage.events.order_by( "-date" ).all(),
        "barter_manage_fulfillments": barter_manage.fulfillments.all(),
        "notes": barter_manage.events.filter( type=events.ManageEvents.NOTE_ADDED ),
        }
    return TemplateResponse( request,
                             "product_stock/barter_manage/detail.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def store_to_store_manage_details(request, store_to_store_manage_pk):
    qs = StoreToStoreManage.objects.select_related().prefetch_related(
        "events__responsible_person",
        "store_to_store_manage_lines__product_object_stock__product_stock",
        "fulfillments_out__lines__store_to_store_manage_line",
        "fulfillments_in__lines__store_to_store_manage_line",
        )
    store_to_store_manage = get_object_or_404( qs, pk=store_to_store_manage_pk )
    ctx = {
        "store_to_store_manage": store_to_store_manage,
        "events": store_to_store_manage.events.order_by( "-date" ).all(),
        "store_to_store_manage_fulfillments_moveout": store_to_store_manage.fulfillments_out.all(),
        "store_to_store_manage_fulfillments_movein": store_to_store_manage.fulfillments_in.all(),
        "notes": store_to_store_manage.events.filter(
            type=events.ManageEvents.NOTE_ADDED
            ),
        }
    return TemplateResponse( request,
                             "product_stock/store_to_store_manage/detail.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def manual_inventory_manage_details(request, manual_inventory_manage_pk):
    qs = ManualInventoryManage.objects.select_related().prefetch_related(
        "events__responsible_person",
        "manual_inventory_manage_lines__product_object_stock__product_stock",
        "fulfillments_LOCK__lines__manual_inventory_manage_line",
        "fulfillments_UNLOCK__lines__manual_inventory_manage_line",
        )
    manual_inventory_manage = get_object_or_404( qs, pk=manual_inventory_manage_pk )
    ctx = {
        "manual_inventory_manage": manual_inventory_manage,
        "events": manual_inventory_manage.events.order_by( "-date" ).all(),
        "manual_inventory_manage_fulfillments_LOCK": manual_inventory_manage.fulfillments_LOCK.all(),
        "manual_inventory_manage_fulfillments_UNLOCK": manual_inventory_manage.fulfillments_UNLOCK.all(),
        "notes": manual_inventory_manage.events.filter(
            type=events.ManageEvents.NOTE_ADDED
            ),
        }
    return TemplateResponse( request,
                             "product_stock/manual_inventory_manage/detail.html",
                             ctx
                             )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def remove_draft_order_manage(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    order_manage_line_s = OrderManageLine.objects.filter(order_manage=order_manage)
    if request.method == "POST":
        if order_manage_line_s:
            for order_manage_line in order_manage_line_s:
                delete_manage_line(
                    order_manage_line,
                    ProductStockManageStatus.OTHER
                    )
        order_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表下書きを削除"
                             )
        messages.success( request, msg )
        return redirect( "order-manage-list" )
    template = "product_stock/order_manage/model/remove_order_manage.html"
    ctx = { "order_manage": order_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def remove_draft_barter_manage(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    barter_manage_line_s = BarterManageLine.objects.filter( barter_manage=barter_manage )
    if request.method == "POST":
        if barter_manage_line_s:
            for barter_manage_line in barter_manage_line_s:
                delete_barter_manage_line( barter_manage_line, ProductStockManageStatus.OTHER )
        barter_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表下書きを削除"
                             )
        messages.success( request, msg )
        return redirect( "barter-manage-list" )
    template = "product_stock/barter_manage/modal/remove_barter_manage.html"
    ctx = { "barter_manage": barter_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def remove_draft_store_to_store_manage(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    store_to_store_manage_line_s = StoreToStoreManageLine.objects.filter(store_to_store_manage=store_to_store_manage)
    if request.method == "POST":
        if store_to_store_manage_line_s:
            for store_to_store_manage_line in store_to_store_manage_line_s:
                delete_store_manage_line( store_to_store_manage_line,
                                          ProductStockManageStatus.OTHER
                                          )
        store_to_store_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表下書きを削除"
                             )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-list" )
    template = "product_stock/store_to_store_manage/modal/remove_store_to_store_manage.html"
    ctx = { "store_to_store_manage": store_to_store_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def remove_draft_manual_inventory_manage(request, manual_inventory_manage_pk):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    manual_inventory_manage_line_s = ManualInventoryManageLine.objects.filter(
        manual_inventory_manage=manual_inventory_manage
        )
    if request.method == "POST":
        if manual_inventory_manage_line_s:
            for manual_inventory_manage_line in manual_inventory_manage_line_s:
                delete_manual_manage_line( manual_inventory_manage_line,
                                           ProductStockManageStatus.OTHER
                                           )
        manual_inventory_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表下書きを削除"
                             )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-list" )
    template = "product_stock/manual_inventory_manage/modal/remove_manual_inventory_manage.html"
    ctx = { "manual_inventory_manage": manual_inventory_manage }
    return TemplateResponse( request, template, ctx )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def remove_order_manage_line(request, order_manage_pk, order_manage_line_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    order_manage_line = get_object_or_404( order_manage.order_manage_lines,
                                           pk=order_manage_line_pk
                                           )
    form = forms.CancelOrderManageLineForm( data=request.POST or None,
                                            line=order_manage_line
                                            )
    status = 200
    if form.is_valid():
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order line", "執行表の行%sを削除した"
                    )
                % order_manage_line
        )
        delete_manage_line(
            order_manage_line,
            ProductStockManageStatus.OTHER
            )
        events.draft_order_manage_removed_product_object_stock_event(
            order_manage=order_manage, user=request.user,
            order_manage_lines=[(order_manage_line.quantity, order_manage_line)]
            )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "order_manage": order_manage, "item": order_manage_line, "form": form }
    return TemplateResponse(
        request, "product_stock/order_manage/model/cancel_line.html", ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def remove_barter_manage_line(request, barter_manage_pk, barter_manage_line_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    barter_manage_line = get_object_or_404( barter_manage.barter_manage_lines,
                                            pk=barter_manage_line_pk
                                            )
    form = forms.CancelBarterManageLineForm( data=request.POST or None,
                                             line=barter_manage_line
                                             )
    status = 200
    if form.is_valid():
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order line", "執行表の行%sを削除した"
                    )
                % barter_manage_line
        )
        delete_barter_manage_line( barter_manage_line, ProductStockManageStatus.OTHER )
        events.draft_barter_manage_removed_product_object_stock_event(
            barter_manage=barter_manage, user=request.user,
            barter_manage_lines=[(1, barter_manage_line)]
            )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "barter_manage": barter_manage, "item": barter_manage_line, "form": form }
    return TemplateResponse(
        request, "product_stock/barter_manage/modal/cancel_line.html", ctx,
        status=status
        )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def remove_store_to_store_manage_line(
        request, store_to_store_manage_pk, store_to_store_manage_line_pk
        ):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    store_to_store_manage_line = get_object_or_404(
        store_to_store_manage.store_to_store_manage_lines,
        pk=store_to_store_manage_line_pk
        )
    form = forms.CancelStoreToStoreManageLineForm( data=request.POST or None,
                                                   line=store_to_store_manage_line
                                                   )
    status = 200
    if form.is_valid():
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order line", "執行表の行%sを削除した"
                    )
                % store_to_store_manage_line
        )

        delete_store_manage_line( store_to_store_manage_line,
                                  ProductStockManageStatus.OTHER
                                  )

        events.draft_store_to_store_manage_removed_product_object_stock_event(
            store_to_store_manage=store_to_store_manage, user=request.user,
            store_to_store_manage_lines=[(1, store_to_store_manage_line)]
            )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "store_to_store_manage": store_to_store_manage,
            "item": store_to_store_manage_line, "form": form }
    return TemplateResponse(
        request, "product_stock/store_to_store_manage/modal/cancel_line.html",
        ctx, status=status
        )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def remove_manual_inventory_manage_line(
        request, manual_inventory_manage_pk, manual_inventory_manage_line_pk
        ):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    manual_inventory_manage_line = get_object_or_404(
        manual_inventory_manage.manual_inventory_manage_lines,
        pk=manual_inventory_manage_line_pk
        )
    form = forms.CancelManualInventoryManageLineForm( data=request.POST or None,
                                                      line=manual_inventory_manage_line
                                                      )
    status = 200
    if form.is_valid():
        msg = (
                pgettext_lazy(
                    "Dashboard message related to an order line", "執行表の行%sを削除した"
                    )
                % manual_inventory_manage_line
        )
        delete_manual_manage_line( manual_inventory_manage_line,
                                   ProductStockManageStatus.OTHER
                                   )

        events.draft_manual_inventory_manage_removed_product_object_stock_event(
            manual_inventory_manage=manual_inventory_manage, user=request.user,
            manual_inventory_manage_lines=[(1, manual_inventory_manage_line)]
            )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = { "manual_inventory_manage": manual_inventory_manage,
            "item": manual_inventory_manage_line, "form": form }
    return TemplateResponse(
        request,
        "product_stock/manual_inventory_manage/modal/cancel_line.html", ctx,
        status=status
        )



# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
@permission_required( "product_stock.order_cancel_permissions" )
def remove_order_manage(request, order_manage_pk):
    order_manage = get_object_or_404( OrderManage.objects.drafts(), pk=order_manage_pk )
    order_manage_line_s = OrderManageLine.objects.filter(order_manage=order_manage)
    if request.method == "POST":
        if order_manage_line_s:
            for order_manage_line in order_manage_line_s:
                delete_manage_line(
                    order_manage_line,
                    ProductStockManageStatus.OTHER
                    )
        order_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表を取消"
                             )
        messages.success( request, msg )
        return redirect( "order-manage-list" )
    template = "product_stock/order_manage/model/remove_order_manage.html"
    ctx = { "order_manage": order_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.barter_cancel_permissions" )
def remove_barter_manage(request, barter_manage_pk):
    barter_manage = get_object_or_404( BarterManage.objects.drafts(),
                                       pk=barter_manage_pk
                                       )
    barter_manage_line_s = BarterManageLine.objects.filter( barter_manage=barter_manage )
    if request.method == "POST":
        if barter_manage_line_s:
            for barter_manage_line in barter_manage_line_s:
                delete_barter_manage_line( barter_manage_line, ProductStockManageStatus.OTHER )
        barter_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表を取消"
                             )
        messages.success( request, msg )
        return redirect( "barter-manage-list" )
    template = "product_stock/barter_manage/modal/remove_barter_manage.html"
    ctx = { "barter_manage": barter_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.store_to_store_cancel_permissions" )
def remove_store_to_store_manage(request, store_to_store_manage_pk):
    store_to_store_manage = get_object_or_404( StoreToStoreManage.objects.drafts(),
                                               pk=store_to_store_manage_pk
                                               )
    store_to_store_manage_line_s = StoreToStoreManageLine.objects.filter(store_to_store_manage=store_to_store_manage)
    if request.method == "POST":
        if store_to_store_manage_line_s:
            for store_to_store_manage_line in store_to_store_manage_line_s:
                delete_store_manage_line( store_to_store_manage_line,
                                          ProductStockManageStatus.OTHER
                                          )
        store_to_store_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表を取消"
                             )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-list" )
    template = "product_stock/store_to_store_manage/modal/remove_store_to_store_manage.html"
    ctx = { "store_to_store_manage": store_to_store_manage }
    return TemplateResponse( request, template, ctx )


@staff_member_required
@permission_required( "product_stock.manual_inventory_cancel_permissions" )
def remove_manual_inventory_manage(request, manual_inventory_manage_pk):
    manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
                                                 pk=manual_inventory_manage_pk
                                                 )
    manual_inventory_manage_line_s = ManualInventoryManageLine.objects.filter(
        manual_inventory_manage=manual_inventory_manage
        )
    if request.method == "POST":
        if manual_inventory_manage_line_s:
            for manual_inventory_manage_line in manual_inventory_manage_line_s:
                delete_manual_manage_line( manual_inventory_manage_line,
                                           ProductStockManageStatus.OTHER
                                           )
        manual_inventory_manage.delete()
        msg = pgettext_lazy( "Dashboard message",
                             "執行表を取消"
                             )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-list" )
    template = "product_stock/manual_inventory_manage/modal/remove_manual_inventory_manage.html"
    ctx = { "manual_inventory_manage": manual_inventory_manage }
    return TemplateResponse( request, template, ctx )

# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ----------------------棚卸-----------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class stock_taking( generic.FormView ):
    template_name = 'product_stock/Stock_taking/stock_taking_upload.html'
    success_url = reverse_lazy( 'index' )
    form_class = forms.StockTakingUploadForm
    permission_required = "site.manage_settings"

    def form_valid(self, form):
        ENFORCEMENT=[
            InventoryStatus.UNFULFILLED,
            InventoryStatus.PARTIALLY_FULFILLED,
            ]
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csvfile = io.TextIOWrapper( form.cleaned_data['file'], encoding='shift_jis' )
        reader = csv.reader( csvfile )
        fields = ['IMEI', '商品名', 'JAN', 'メモ', '金額', '追加情報',
                  '在庫状態','商品状態', '店舗別', '分配', 'ロック', '利用可能', '入庫予定','在庫切れ',
                  '執行中の買取・注文出入庫執行表','買取・注文出入庫執行表の伝票番号',
                  '執行中の物々交換執行表','物々交換執行表の伝票番号',
                  '執行中の店舗間移動執行表','店舗間移動執行表の伝票番号',
                  '執行中の商品ロック執行表','商品ロック執行表の取引先(サイト)']
        results = []
        for row in reader:
            try:
                product_object_stock_temp = ProductObjectStock.objects.get(
                    imei_code=row[0]
                    )
                order_manage_s = OrderManage.objects.filter(
                    Q( order_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
                    ).distinct().filter(order_status__in=ENFORCEMENT).order_by( "id" )
                barter_manage_s = BarterManage.objects.filter(
                    Q( barter_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
                    ).distinct().filter(barter_status__in=ENFORCEMENT).order_by( "id" )
                store_to_store_manage_s = StoreToStoreManage.objects.filter(
                    Q( store_to_store_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
                    ).distinct().filter(store_to_store_status__in=ENFORCEMENT).order_by( "id" )
                manual_inventory_manage_s = ManualInventoryManage.objects.filter(
                    Q( manual_inventory_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
                    ).distinct().filter(manual_inventory_status__in=ENFORCEMENT).order_by( "id" )
                order_manage_slip=[]
                barter_manage_slip = []
                store_to_store_manage_slip = []
                manual_inventory_manage_e_market = []
                order_manage_id=[]
                barter_manage_id = []
                store_to_store_manage_id = []
                manual_inventory_manage_id = []
                for order_manage in order_manage_s:
                    order_manage_id.append("#"+str(order_manage.id))
                    order_manage_slip.append(str(order_manage.slip_number))
                for barter_manage in barter_manage_s:
                    barter_manage_id.append("#"+str(barter_manage.id))
                    barter_manage_slip.append(str(barter_manage.slip_number))
                for store_to_store_manage in store_to_store_manage_s:
                    store_to_store_manage_id.append("#"+str(store_to_store_manage.id))
                    store_to_store_manage_slip.append(str(store_to_store_manage.slip_number))
                for manual_inventory_manage in manual_inventory_manage_s:
                    manual_inventory_manage_id.append("#"+str(manual_inventory_manage.id))
                    manual_inventory_manage_e_market.append(str(manual_inventory_manage.e_market))



                results.append( [
                    product_object_stock_temp.imei_code,
                    product_object_stock_temp.product_stock.name,
                    product_object_stock_temp.product_stock.jan_code,
                    product_object_stock_temp.notion,
                    product_object_stock_temp.price_override_amount,
                    product_object_stock_temp.extra_informations,

                    product_object_stock_temp.manage_status,
                    product_object_stock_temp.status,
                    product_object_stock_temp.shops,
                    product_object_stock_temp.is_allocate,
                    product_object_stock_temp.is_lock,
                    product_object_stock_temp.is_available_M,
                    product_object_stock_temp.is_temp,
                    product_object_stock_temp.is_out_of_stock,

                    "　　".join( order_manage_id ),
                    "　　".join( order_manage_slip ),

                    "　　".join( barter_manage_id ),
                    "　　".join( barter_manage_slip ),

                    "　　".join( store_to_store_manage_id ),
                    "　　".join( store_to_store_manage_slip ),

                    "　　".join( manual_inventory_manage_id ),
                    "　　".join( manual_inventory_manage_e_market )
                    ]
                    )
            except ProductObjectStock.DoesNotExist:
                results.append(
                    [row[0], "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",
                     "-","-","-","-","-","-","-","-","-"]
                    )

        file_name = str( now() )[:10] + "stocktaking.csv"
        response = HttpResponse( content_type='text/csv' )
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        writer = csv.writer( response )
        writer.writerow( fields )
        writer.writerows( results )
        return response


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ----------------------ajax-----------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


@staff_member_required
def ajax_product_object_stock_list(request):
    product_stock_s = ProductStock.objects.all()
    product_object_stock_queryset = ProductObjectStock.objects.filter(
        product_stock__in=product_stock_s
        )
    search_query = request.GET.get( "q", "" )
    if search_query:
        product_object_stock_queryset = product_object_stock_queryset.filter(
            Q( sku__icontains=search_query )
            | Q( imei_code__icontains=search_query )
            | Q( product_stock__name__icontains=search_query )
            )
    product_object_stock = [{
        "id": product_object_stock.id,
        "text": product_object_stock.get_ajax_label( request.discounts )
        }
        for product_object_stock in product_object_stock_queryset
        ]
    return JsonResponse( { "results": product_object_stock } )


@staff_member_required
def ajax_product_stock_list(request):
    product_stock_s_queryset = ProductStock.objects.all()
    search_query = request.GET.get( "q", "" )
    if search_query:
        product_stock_s_queryset = product_stock_s_queryset.filter(
            Q( name__icontains=search_query )
            | Q( jan_code__icontains=search_query )
            )
    product_stock = [{
        "id": product_stock.id,
        "text": product_stock.get_ajax_label( request.discounts )
        }
        for product_stock in product_stock_s_queryset
        ]
    return JsonResponse( {
        "results": product_stock
        }
        )


@staff_member_required
def ajax_suppliers_list(request):
    queryset = Suppliers.objects.all()
    search_query = request.GET.get( "q", "" )
    if search_query:
        queryset = queryset.filter(
            Q( first_name__icontains=search_query )
            | Q( last_name__icontains=search_query )
            | Q( first_name_kannji__icontains=search_query )
            | Q( last_name_kannji__icontains=search_query )
            | Q( phone__icontains=search_query )
            | Q( address__postal_code__icontains=search_query )
            | Q( address__city__icontains=search_query )
            | Q( address__phone__icontains=search_query )
            | Q( email__icontains=search_query )
            )
    queryset = queryset.order_by( "email" )
    suppliers = [{ "id": supplier.pk, "text": supplier.get_ajax_label() } for supplier
                 in queryset]
    return JsonResponse( { "results": suppliers } )


@staff_member_required
def ajax_legal_person_list(request):
    queryset = LegalPerson.objects.all()
    search_query = request.GET.get( "q", "" )
    if search_query:
        queryset = queryset.filter(
            Q( company_name__icontains=search_query )
            | Q( email__icontains=search_query )
            | Q( phone__icontains=search_query )
            | Q( fax__icontains=search_query )
            | Q( deputy__first_name__icontains=search_query )
            | Q( deputy__last_name__icontains=search_query )
            | Q( deputy__first_name_kannji__icontains=search_query )
            | Q( deputy__last_name_kannji__icontains=search_query )
            )
    queryset = queryset.order_by( "email" )
    legal_person_s = [{ "id": legal_person.pk, "text": legal_person.get_ajax_label() }
                      for legal_person in queryset]
    return JsonResponse( { "results": legal_person_s } )


@staff_member_required
def ajax_product_stock(request):
    product_stock_s_queryset = ProductStock.objects.all()
    search_query = request.POST.get( 'product_stock_jan_search' )
    if search_query:
        product_stock_s_queryset = product_stock_s_queryset.filter(
            Q( jan_code__icontains=search_query )
            )
    if product_stock_s_queryset:
        product_stock = {
            "id": product_stock_s_queryset[0].id,
            "jan": product_stock_s_queryset[0].jan_code,
            "name": product_stock_s_queryset[0].name,
            "description": product_stock_s_queryset[0].description
            }
    else:
        product_stock = {
            "id": "",
            "jan": "",
            "name": "",
            "description": ""
            }

    return JsonResponse( { "results": product_stock } )


@staff_member_required
def ajax_suppliers(request):
    suppliers_s_queryset = Suppliers.objects.all()
    search_query = request.POST.get( 'email' )
    if search_query:
        suppliers_s_queryset = suppliers_s_queryset.filter(
            Q( email__icontains=search_query )
            | Q( phone__icontains=search_query )
            )
    if suppliers_s_queryset:
        address = suppliers_s_queryset[0].address.all()[0]
        suppliers = {
            "email": suppliers_s_queryset[0].email,
            "phone": suppliers_s_queryset[0].phone,
            "first_name": suppliers_s_queryset[0].first_name,
            "last_name": suppliers_s_queryset[0].last_name,
            "first_name_kannji": suppliers_s_queryset[0].first_name_kannji,
            "last_name_kannji": suppliers_s_queryset[0].last_name_kannji,
            "age": suppliers_s_queryset[0].age,
            "gender": suppliers_s_queryset[0].gender,
            "birth": suppliers_s_queryset[0].birth,
            "work": suppliers_s_queryset[0].work,
            "note": suppliers_s_queryset[0].note,
            "postal_code": address.postal_code,
            "city_area": address.city_area,
            "city": address.city,
            "street_address_1": address.street_address_1,
            "street_address_2": address.street_address_2
            }
    else:
        suppliers = {
            "email": "",
            "phone": "",
            "first_name": "",
            "last_name": "",
            "first_name_kannji": "",
            "last_name_kannji": "",
            "age": "",
            "gender": "",
            "birth": "",
            "work": "",
            "note": "",
            "postal_code": "",
            "city_area": "",
            "city": "",
            "street_address_1": "",
            "street_address_2": ""
            }

    return JsonResponse( { "results": suppliers } )


@staff_member_required
def ajax_legal_person(request):
    legal_person_s_queryset = LegalPerson.objects.all()
    search_query = request.POST.get( 'email' )
    if search_query:
        legal_person_s_queryset = legal_person_s_queryset.filter(
            Q( email__exact=search_query )
            | Q( phone__exact=search_query )
            )
    if legal_person_s_queryset:
        address = legal_person_s_queryset[0].address.all()[0]
        legal_person = {
            "email": legal_person_s_queryset[0].email,
            "company_name": legal_person_s_queryset[0].company_name,
            "phone": legal_person_s_queryset[0].phone,
            "fax": legal_person_s_queryset[0].fax,
            "homepage": legal_person_s_queryset[0].homepage,
            "note": legal_person_s_queryset[0].note,
            "postal_code": address.postal_code,
            "city_area": address.city_area,
            "city": address.city,
            "street_address_1": address.street_address_1,
            "street_address_2": address.street_address_2
            }
    else:
        legal_person = {
            "email": "",
            "company_name": "",
            "phone": "",
            "fax": "",
            "homepage": "",
            "note": "",
            "postal_code": "",
            "city_area": "",
            "city": "",
            "street_address_1": "",
            "street_address_2": ""
            }
    return JsonResponse( { "results": legal_person } )


@staff_member_required
def ajax_product_object_stock(request):
    product_object_stock_queryset = ProductObjectStock.objects.all()
    search_query = request.POST.get( 'product_object_stock_imei_search' )
    if search_query:
        product_object_stock_queryset = product_object_stock_queryset.filter(
            Q( imei_code__exact=search_query )
            )
    if product_object_stock_queryset:
        product_object_stock_temp = get_object_or_404( ProductObjectStock.objects.all(),
                                                       pk=product_object_stock_queryset[0].pk
                                                       )
        product_object_stock = {
            "status_":True,
            "manage_status": product_object_stock_temp.manage_status,
            "is_allocate":product_object_stock_temp.is_allocate,
            "is_lock": product_object_stock_temp.is_lock,
            "is_available": product_object_stock_temp.is_available_M,
            "is_out_of_stock": product_object_stock_temp.is_out_of_stock
            }
    else:
        product_object_stock = {
            "status_":False,
            "manage_status": "",
            "is_allocate":"",
            "is_lock": "",
            "is_available": "",
            "is_out_of_stock": ""
            }
    return JsonResponse( { "results": product_object_stock } )



# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# 实现了不用输入IEMI的商品的出入库
@staff_member_required
@permission_required( "product_stock.order_manage_permissions" )
def fulfill_order_manage_lines(request, order_manage_pk):
    order_manage_s = OrderManage.objects.confirmed().prefetch_related(
        "order_manage_lines"
        )
    order_manage = get_object_or_404( order_manage_s, pk=order_manage_pk )
    unfulfilled_lines = order_manage.order_manage_lines.filter(
        quantity_fulfilled__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentForm( request.POST or None, order_manage=order_manage,
                                  instance=OrderManageFulfillment()
                                  )
    # 无论出库入，用同一个表
    FulfillmentLineFormSet = modelformset_factory(
        OrderManageFulfillmentLine,
        form=forms.FulfillmentLineForm,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )

    initial = [
        { "order_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None, queryset=OrderManageFulfillmentLine.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )

    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():

        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            order_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = order_manage_fulfillment
                # 只更新执行数量，不管执行种类
                fulfillment_line.save()

                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity

                # 区分执行类型-入库或者出库

                if fulfillment_line.order_manage_line.product_stock:

                    if fulfillment_line.order_manage_line.order_manage_type == OrderManageType.STORAGE:
                        change_avarage_price(
                            fulfillment_line,
                            is_cancel=False,
                            is_no_imei=True
                            )
                        change_product_stock_ststus(
                            fulfillment_line.order_manage_line.product_stock
                            )
                        change_product_stock_quantity_s(
                            fulfillment_line.order_manage_line.product_stock,
                            is_cancel=False,
                            is_Fulfillment=True,
                            is_no_imei=True,
                            quantity_predestinate_dif=fulfillment_line.quantity,
                            )


                    elif fulfillment_line.order_manage_line.order_manage_type == OrderManageType.DELIVERY:
                        change_product_stock_quantity_s(
                            fulfillment_line.order_manage_line.product_stock,
                            is_cancel=False,
                            is_Fulfillment=True,
                            is_no_imei=True,
                            quantity_allocated_dif=fulfillment_line.quantity,
                            )

                elif fulfillment_line.order_manage_line.product_object_stock:

                    if fulfillment_line.order_manage_line.order_manage_type == OrderManageType.STORAGE:
                        change_avarage_price(
                            fulfillment_line,
                            is_cancel=False,
                            is_no_imei=False
                            )
                        change_product_stock_quantity_s(
                            fulfillment_line.order_manage_line.product_object_stock.product_stock,
                            is_cancel=False,
                            is_Fulfillment=True,
                            is_no_imei=False,
                            quantity_predestinate_dif=fulfillment_line.quantity,
                            )
                        change_product_object_stock_manage_status(
                            fulfillment_line.order_manage_line.product_object_stock,
                            ProductStockManageStatus.ORDER_STORAGE
                            )


                    elif fulfillment_line.order_manage_line.order_manage_type == OrderManageType.DELIVERY:
                        change_product_stock_quantity_s(
                            fulfillment_line.order_manage_line.product_object_stock.product_stock,
                            is_cancel=False,
                            is_Fulfillment=True,
                            is_no_imei=False,
                            quantity_allocated_dif=fulfillment_line.quantity,
                            )
                        change_product_object_stock_manage_status(
                            fulfillment_line.order_manage_line.product_object_stock,
                            ProductStockManageStatus.ORDER_DELIVERY
                            )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            order_manage_fulfillment.refresh_from_db()
            order_manage.refresh_from_db()

            update_order_manage_status( order_manage )

            events.order_manage_fulfillment( order_manage=order_manage,
                                             user=request.user
                                             )
        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません。"
                )
        messages.success( request, msg )
        return redirect( "order-manage-details",
                         order_manage_pk=order_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "order_manage": order_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/order_manage/model/fulfillment_form.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.barter_manage_permissions" )
def fulfill_barter_manage_lines(request, barter_manage_pk):
    barter_manage_s = BarterManage.objects.confirmed().prefetch_related(
        "barter_manage_lines"
        )
    barter_manage = get_object_or_404( barter_manage_s, pk=barter_manage_pk )
    unfulfilled_lines = barter_manage.barter_manage_lines.filter(
        quantity_fulfilled__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentBarterManageForm( request.POST or None,
                                              barter_manage=barter_manage,
                                              instance=BarterManageFulfillment()
                                              )
    # 无论出库入，用同一个表
    FulfillmentLineFormSet = modelformset_factory(
        BarterManageFulfillmentLine,
        form=forms.FulfillmentLineBarterManageForm,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )
    initial = [
        { "barter_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None, queryset=BarterManageFulfillmentLine.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )

    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():
        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            barter_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = barter_manage_fulfillment
                fulfillment_line.save()
                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity
                if fulfillment_line.barter_manage_line.barter_manage_type == BarterManageType.MOVEIN:
                    change_avarage_price(
                        fulfillment_line,
                        is_cancel=False,
                        is_no_imei=False,
                        is_barter=True
                        )
                    change_product_object_stock_manage_status(
                        fulfillment_line.barter_manage_line.product_object_stock,
                        BarterManageStatus.BARTER_MOVE_IN
                        )
                    change_product_stock_quantity_s(
                        fulfillment_line.barter_manage_line.product_object_stock.product_stock,
                        is_cancel=False,
                        is_Fulfillment=True,
                        is_no_imei=False,
                        quantity_predestinate_dif=fulfillment_line.quantity,
                        )

                elif fulfillment_line.barter_manage_line.barter_manage_type == BarterManageType.MOVEOUT:
                    change_product_object_stock_manage_status(
                        fulfillment_line.barter_manage_line.product_object_stock,
                        BarterManageStatus.BARTER_MOVE_OUT
                        )
                    change_product_stock_quantity_s(
                        fulfillment_line.barter_manage_line.product_object_stock.product_stock,
                        is_cancel=False,
                        is_Fulfillment=True,
                        is_no_imei=False,
                        quantity_allocated_dif=fulfillment_line.quantity,
                        )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            barter_manage_fulfillment.refresh_from_db()
            barter_manage.refresh_from_db()

            update_barter_manage_status( barter_manage )

            events.barter_manage_fulfillment( barter_manage=barter_manage,
                                              user=request.user
                                              )
        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません"
                )
        messages.success( request, msg )
        return redirect( "barter-manage-details",
                         barter_manage_pk=barter_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "barter_manage": barter_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/barter_manage/modal/fulfillment_form.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def fulfill_store_manage_lines_MOVEOUT(request, store_to_store_manage_pk):
    store_to_store_manage_s = StoreToStoreManage.objects.confirmed().prefetch_related(
        "store_to_store_manage_lines"
        )
    store_to_store_manage = get_object_or_404( store_to_store_manage_s,
                                               pk=store_to_store_manage_pk
                                               )
    unfulfilled_lines = store_to_store_manage.store_to_store_manage_lines.filter(
        quantity_fulfilled_MOVEOUT__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentStoreManageForm_MOVEOUT( request.POST or None,
                                                     store_to_store_manage=store_to_store_manage,
                                                     instance=StoreToStoreManageFulfillment_MOVEOUT()
                                                     )
    FulfillmentLineFormSet = modelformset_factory(
        StoreToStoreManageFulfillmentLine_MOVEOUT,
        form=forms.FulfillmentLineStoreManageForm_MOVEOUT,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )
    initial = [
        { "store_to_store_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled_MOVEOUT) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None,
        queryset=StoreToStoreManageFulfillmentLine_MOVEOUT.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )
    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():
        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            store_to_store_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = store_to_store_manage_fulfillment
                fulfillment_line.save()
                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity

                change_product_object_stock_manage_status(
                    fulfillment_line.store_to_store_manage_line.product_object_stock,
                    StoreToStoreStatus.STORE_TO_STORE_MOVE_OUT
                    )

                # change_product_stock_quantity_s(
                #     fulfillment_line.store_to_store_manage_line.product_object_stock.product_stock,
                #     is_cancel=False,
                #     is_Fulfillment=False,
                #     is_no_imei=False,
                #     quantity_allocated_dif=fulfillment_line.quantity,
                #     )

                # change_product_object_stock_store(
                #     fulfillment_line.store_to_store_manage_line.product_object_stock,
                #     fulfillment_line.store_to_store_manage_line.store_to_store_manage.to_shop
                #     )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            store_to_store_manage_fulfillment.refresh_from_db()
            store_to_store_manage.refresh_from_db()

            update_store_to_store_manage_status( store_to_store_manage )

            events.store_to_store_manage_fulfillment_MOVEOUT(
                store_to_store_manage=store_to_store_manage,
                user=request.user
                )
        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません"
                )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "store_to_store_manage": store_to_store_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/store_to_store_manage/modal/fulfillment_form.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.store_to_store_manage_permissions" )
def fulfill_store_manage_lines_MOVEIN(request, store_to_store_manage_pk):
    store_to_store_manage_s = StoreToStoreManage.objects.confirmed().prefetch_related(
        "store_to_store_manage_lines"
        )
    store_to_store_manage = get_object_or_404( store_to_store_manage_s,
                                               pk=store_to_store_manage_pk
                                               )
    unfulfilled_lines = store_to_store_manage.store_to_store_manage_lines.filter(
        quantity_fulfilled_MOVEIN__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentStoreManageForm_MOVEIN( request.POST or None,
                                                    store_to_store_manage=store_to_store_manage,
                                                    instance=StoreToStoreManageFulfillment_MOVEIN()
                                                    )
    FulfillmentLineFormSet = modelformset_factory(
        StoreToStoreManageFulfillmentLine_MOVEIN,
        form=forms.FulfillmentLineStoreManageForm_MOVEIN,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )
    initial = [
        { "store_to_store_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled_MOVEIN) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None,
        queryset=StoreToStoreManageFulfillmentLine_MOVEIN.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )
    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():
        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            store_to_store_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = store_to_store_manage_fulfillment
                fulfillment_line.save()
                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity

                change_product_object_stock_manage_status(
                    fulfillment_line.store_to_store_manage_line.product_object_stock,
                    StoreToStoreStatus.STORE_TO_STORE_MOVE_IN
                    )

                change_product_stock_quantity_s(
                    fulfillment_line.store_to_store_manage_line.product_object_stock.product_stock,
                    is_cancel=False,
                    is_Fulfillment=True,
                    is_no_imei=False,
                    quantity_allocated_dif=fulfillment_line.quantity,
                    )

                change_product_object_stock_store(
                    fulfillment_line.store_to_store_manage_line.product_object_stock,
                    fulfillment_line.store_to_store_manage_line.store_to_store_manage.to_shop
                    )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            store_to_store_manage_fulfillment.refresh_from_db()
            store_to_store_manage.refresh_from_db()

            update_store_to_store_manage_status( store_to_store_manage )

            events.store_to_store_manage_fulfillment_MOVEIN(
                store_to_store_manage=store_to_store_manage,
                user=request.user
                )

        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません"
                )
        messages.success( request, msg )
        return redirect( "store-to-store-manage-details",
                         store_to_store_manage_pk=store_to_store_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "store_to_store_manage": store_to_store_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/store_to_store_manage/modal/fulfillment_form_movein.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def fulfill_manual_manage_lines_LOCK(request, manual_inventory_manage_pk):
    manual_inventory_manage_s = ManualInventoryManage.objects.confirmed().prefetch_related(
        "manual_inventory_manage_lines"
        )
    manual_inventory_manage = get_object_or_404( manual_inventory_manage_s,
                                                 pk=manual_inventory_manage_pk
                                                 )
    unfulfilled_lines = manual_inventory_manage.manual_inventory_manage_lines.filter(
        quantity_fulfilled_LOCK__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentManualInventoryManageForm_LOCK( request.POST or None,
                                                            manual_inventory_manage=manual_inventory_manage,
                                                            instance=ManualInventoryManageFulfillment_LOCK()
                                                            )

    FulfillmentLineFormSet = modelformset_factory(
        ManualInventoryManageFulfillmentLine_LOCK,
        form=forms.FulfillmentLineManualInventoryManageForm_LOCK,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )
    initial = [
        { "manual_inventory_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled_LOCK) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None,
        queryset=ManualInventoryManageFulfillmentLine_LOCK.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )
    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():
        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            manual_inventory_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = manual_inventory_manage_fulfillment
                fulfillment_line.save()
                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity

                if fulfillment_line.manual_inventory_manage_line.product_object_stock:
                    change_product_object_stock_manage_status(
                        fulfillment_line.manual_inventory_manage_line.product_object_stock,
                        ManualInventoryStatus.MANUAL_LOCK
                        )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            manual_inventory_manage_fulfillment.refresh_from_db()
            manual_inventory_manage.refresh_from_db()

            update_manual_inventory_manage_status( manual_inventory_manage )

            events.manual_inventory_manage_fulfillment_LOCK(
                manual_inventory_manage=manual_inventory_manage,
                user=request.user
                )
        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません"
                )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "manual_inventory_manage": manual_inventory_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/manual_inventory_manage/modal/fulfillment_form_LOCK.html"
    return TemplateResponse( request, template, ctx, status=status )


@staff_member_required
@permission_required( "product_stock.manual_inventory_manage_permissions" )
def fulfill_manual_manage_lines_UNLOCK(request, manual_inventory_manage_pk):
    manual_inventory_manage_s = ManualInventoryManage.objects.confirmed().prefetch_related(
        "manual_inventory_manage_lines"
        )
    manual_inventory_manage = get_object_or_404( manual_inventory_manage_s,
                                                 pk=manual_inventory_manage_pk
                                                 )
    unfulfilled_lines = manual_inventory_manage.manual_inventory_manage_lines.filter(
        quantity_fulfilled_UNLOCK__lt=F( "quantity" )
        )
    status = 200
    form = forms.FulfillmentManualInventoryManageForm_UNLOCK( request.POST or None,
                                                              manual_inventory_manage=manual_inventory_manage,
                                                              instance=ManualInventoryManageFulfillment_UNLOCK()
                                                              )
    FulfillmentLineFormSet = modelformset_factory(
        ManualInventoryManageFulfillmentLine_UNLOCK,
        form=forms.FulfillmentLineManualInventoryManageForm_UNLOCK,
        extra=len( unfulfilled_lines ),
        formset=forms.BaseFulfillmentLineFormSet,
        )
    initial = [
        { "manual_inventory_manage_line": line,
          "quantity": (line.quantity - line.quantity_fulfilled_UNLOCK) }
        for line in unfulfilled_lines
        ]
    fulfillment_line_formset = FulfillmentLineFormSet(
        request.POST or None,
        queryset=ManualInventoryManageFulfillmentLine_UNLOCK.objects.none(),
        initial=initial
        )
    all_fulfillment_line_forms_valid = all(
        [line_form.is_valid() for line_form in fulfillment_line_formset]
        )
    if all_fulfillment_line_forms_valid and fulfillment_line_formset.is_valid() and form.is_valid():
        forms_to_save = [
            line_form
            for line_form in fulfillment_line_formset
            if line_form.cleaned_data.get( "quantity" ) > 0
            ]
        if forms_to_save:
            manual_inventory_manage_fulfillment = form.save()
            quantity_fulfilled = 0
            for fulfillment_line_form in forms_to_save:
                fulfillment_line = fulfillment_line_form.save( commit=False )
                fulfillment_line.fulfillment = manual_inventory_manage_fulfillment
                fulfillment_line.save()
                quantity = fulfillment_line_form.cleaned_data.get( "quantity" )
                quantity_fulfilled += quantity
                if fulfillment_line.manual_inventory_manage_line.product_object_stock:
                    change_product_object_stock_manage_status(
                        fulfillment_line.manual_inventory_manage_line.product_object_stock,
                        ManualInventoryStatus.MANUAL_UNLOCK
                        )
                    change_product_stock_quantity_s(
                        fulfillment_line.manual_inventory_manage_line.product_object_stock.product_stock,
                        is_cancel=True,
                        is_Fulfillment=False,
                        is_no_imei=False,
                        quantity_locking_dif=fulfillment_line.quantity,
                        )
                elif fulfillment_line.manual_inventory_manage_line.product_stock:
                    change_product_stock_quantity_s(
                        fulfillment_line.manual_inventory_manage_line.product_stock,
                        is_cancel=True,
                        is_Fulfillment=False,
                        is_no_imei=True,
                        quantity_locking_dif=fulfillment_line.quantity,
                        )

            msg = npgettext_lazy(
                "Dashboard message related to an order",
                "%(quantity_fulfilled)d個項目を執行した",
                "%(quantity_fulfilled)d個項目を執行した",
                number="quantity_fulfilled",
                ) % { "quantity_fulfilled": quantity_fulfilled }
            manual_inventory_manage_fulfillment.refresh_from_db()
            manual_inventory_manage.refresh_from_db()

            update_manual_inventory_manage_status( manual_inventory_manage )

            events.manual_inventory_manage_fulfillment_UNLOCK(
                manual_inventory_manage=manual_inventory_manage,
                user=request.user
                )
        else:
            msg = pgettext_lazy(
                "Dashboard message related to an order", "執行項目はありません"
                )
        messages.success( request, msg )
        return redirect( "manual-inventory-manage-details",
                         manual_inventory_manage_pk=manual_inventory_manage_pk
                         )
    elif form.errors:
        status = 400
    ctx = {
        "form": form,
        "fulfillment_line_formset": fulfillment_line_formset,
        "manual_inventory_manage": manual_inventory_manage,
        "unfulfilled_lines": unfulfilled_lines,
        }
    template = "product_stock/manual_inventory_manage/modal/fulfillment_form_UNLOCK.html"
    return TemplateResponse( request, template, ctx, status=status )


# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.change_product_stock" )
def product_change_history(request):
    product_stock_change_history = ProductStockChangeEvent.objects.all().order_by("change_date")
    product_object_stock_change_history = ProductObjectStockChangeEvent.objects.all().order_by("change_date")
    ctx = {
        "product_stock_change_history":product_stock_change_history,
        "product_object_stock_change_history":product_object_stock_change_history
        }
    return TemplateResponse( request,
                             "product_stock/history/product_change_history.html", ctx
                             )

# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
@staff_member_required
@permission_required( "product_stock.manage_product_stock" )
def product_stock_temp_list(request):
    product_stock_temps = ProductStock.objects.prefetch_related()
    product_stock_temps = product_stock_temps.order_by( "name" )
    product_stock_temps_filter = ProductStockFilter( request.GET,
                                                     queryset=product_stock_temps
                                                     )
    product_stock_temps = get_paginator_items(
        product_stock_temps_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )
    ctx = {
        "product_stock_temps": product_stock_temps,
        "product_stock_temps_filter": product_stock_temps_filter,
        "is_empty": not product_stock_temps_filter.queryset.exists(),
        }
    return TemplateResponse( request,
                             "product_stock/product_stock_temp/list.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_stock" )
def product_stock_temp_create(request):
    product_stock_temp = ProductStock()
    form = forms.ProductStockForm( request.POST or None, instance=product_stock_temp )
    if form.is_valid():
        product_stock_temp = form.save(request.user,commit=True,is_logs=True)
        msg = pgettext_lazy( "Dashboard message", "在庫商品類追加" )
        messages.success( request, msg )
        return redirect( "product-stock-temp-list" )
    ctx = { "product_stock_temp": product_stock_temp, "form": form }
    return TemplateResponse( request,
                             "product_stock/product_stock_temp/form.html", ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_stock" )
def product_stock_temp_edit(request, product_stock_temp_pk):
    product_stock_temp = get_object_or_404( ProductStock, pk=product_stock_temp_pk )
    form = forms.ProductStockForm( request.POST or None, instance=product_stock_temp )
    if form.is_valid():

        product_stock_temp = form.save(user=request.user,commit=True)


        msg = pgettext_lazy( "Dashboard message", "在庫商品類編集済" )
        messages.success( request, msg )
        return redirect( "product-stock-temp-list" )
    ctx = { "product_stock_temp": product_stock_temp, "form": form }
    return TemplateResponse( request,
                             "product_stock/product_stock_temp/form.html", ctx
                             )


# ---------------------------------------------------------
# ---------------------------------------------------------

@staff_member_required
@permission_required( "product_stock.manage_product_object_stock" )
def product_object_stock_temp_list(request, product_stock_temp_pk):
    product_stock_temps = ProductStock.objects.prefetch_related(
        "product_object_stock"
        ).all()
    product_stock_temp = get_object_or_404( product_stock_temps,
                                            pk=product_stock_temp_pk
                                            )

    change_history = product_stock_temp.product_stock_change.all()
    order_manage_s = OrderManage.objects.filter(
        Q( order_manage_lines__product_object_stock__product_stock__id__icontains=product_stock_temp.id )
        |Q( order_manage_lines__product_stock__id__icontains=product_stock_temp.id )
        ).distinct().order_by( "id" )
    barter_manage_s = BarterManage.objects.filter(
        Q( barter_manage_lines__product_object_stock__product_stock__id__icontains=product_stock_temp.id )
        | Q( barter_manage_lines__product_stock__id__icontains=product_stock_temp.id )
        ).distinct().order_by( "id" )
    store_to_store_manage_s = StoreToStoreManage.objects.filter(
        Q( store_to_store_manage_lines__product_object_stock__product_stock__id__icontains=product_stock_temp.id )
        | Q( store_to_store_manage_lines__product_stock__id__icontains=product_stock_temp.id )
        ).distinct().order_by( "id" )
    manual_inventory_manage_s = ManualInventoryManage.objects.filter(
        Q( manual_inventory_manage_lines__product_object_stock__product_stock__id__icontains=product_stock_temp.id )
        | Q( manual_inventory_manage_lines__product_stock__id__icontains=product_stock_temp.id )
        ).distinct().order_by( "id" )

    product_object_stock_temps = product_stock_temp.product_object_stock.all()
    product_object_stock_temps = product_object_stock_temps.order_by( "imei_code" )
    product_object_stock_temps_filter = ProductObjectStockFilter( request.GET,
                                                                  queryset=product_object_stock_temps
                                                                  )

    product_object_stock_temps = get_paginator_items(
        product_object_stock_temps_filter.qs,
        settings.DASHBOARD_PAGINATE_BY,
        request.GET.get( "page" )
        )

    ctx = {
        "product_stock_temp": product_stock_temp,
        "product_object_stock_temps": product_object_stock_temps,
        "product_object_stock_temps_filter": product_object_stock_temps_filter,
        "is_empty": not product_object_stock_temps_filter.queryset.exists(),
        "order_manage_s": order_manage_s,
        "barter_manage_s": barter_manage_s,
        "store_to_store_manage_s": store_to_store_manage_s,
        "manual_inventory_manage_s": manual_inventory_manage_s,
        "change_history": change_history
        }
    return TemplateResponse( request,
                             "product_stock/product_object_stock_temp/list.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_object_stock" )
def product_object_stock_temp_details(request, product_stock_temp_pk,product_object_stock_temp_pk):
    product_object_stock_temp = get_object_or_404( ProductObjectStock.objects.all(),
                                                    pk=product_object_stock_temp_pk
                                                    )
    change_history = product_object_stock_temp.product_object_stock_change.all()
    order_manage_s = OrderManage.objects.filter(
        Q( order_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
        ).distinct().order_by( "id" )
    barter_manage_s = BarterManage.objects.filter(
        Q( barter_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
        ).distinct().order_by( "id" )
    store_to_store_manage_s = StoreToStoreManage.objects.filter(
        Q( store_to_store_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
        ).distinct().order_by( "id" )
    manual_inventory_manage_s = ManualInventoryManage.objects.filter(
        Q( manual_inventory_manage_lines__product_object_stock__id__icontains=product_object_stock_temp.id )
        ).distinct().order_by( "id" )
    ctx = {
        "product_object_stock_temp": product_object_stock_temp,
        "product_stock_temp": product_object_stock_temp.product_stock,
        "order_manage_s": order_manage_s,
        "barter_manage_s": barter_manage_s,
        "store_to_store_manage_s": store_to_store_manage_s,
        "manual_inventory_manage_s": manual_inventory_manage_s,
        "change_history": change_history
        }
    return TemplateResponse( request,
                             "product_stock/product_object_stock_temp/detail.html",
                             ctx
                             )



@staff_member_required
@permission_required( "product_stock.manage_product_object_stock" )
def product_object_stock_temp_create(request, product_stock_temp_pk):
    product_stock_temp = get_object_or_404( ProductStock.objects.prefetch_related(
        "product_object_stock"
        ).all(), pk=product_stock_temp_pk
                                            )
    product_object_stock_temp = ProductObjectStock( product_stock=product_stock_temp )
    form = forms.ProductObjectStockForm( request.POST or None,
                                         instance=product_object_stock_temp
                                         )
    if form.is_valid():
        form.save()
        # update_stock_temp( product_stock_temp )
        msg = pgettext_lazy( "Dashboard message", " %sの在庫を追加" ) % (
            product_stock_temp.name,)
        messages.success( request, msg )
        return redirect( "product-object-stock-temp-list",
                         product_stock_temp_pk=product_stock_temp_pk
                         )
    ctx = {
        "product_stock_temp": product_stock_temp,
        "product_object_stock_temp": product_object_stock_temp,
        "form": form
        }
    return TemplateResponse( request,
                             "product_stock/product_object_stock_temp/form.html",
                             ctx
                             )


@staff_member_required
@permission_required( "product_stock.manage_product_object_stock" )
def product_object_stock_temp_edit(
        request, product_stock_temp_pk, product_object_stock_temp_pk
        ):
    product_stock_temp = get_object_or_404( ProductStock.objects.prefetch_related(
        "product_object_stock"
        ).all(), pk=product_stock_temp_pk
                                            )
    product_object_stock_temp = get_object_or_404(
        product_stock_temp.product_object_stock.all(),
        pk=product_object_stock_temp_pk
        )
    form = forms.ProductObjectStockForm( request.POST or None,
                                         instance=product_object_stock_temp
                                         )
    if form.is_valid():
        product_object_stock_temp = form.save(user=request.user,commit=True)
        msg = pgettext_lazy( "Dashboard message", "在庫を編集済" )
        messages.success( request, msg )
        return redirect( "product-object-stock-temp-list",
                         product_stock_temp_pk=product_stock_temp_pk
                         )
    ctx = {
        "product_stock_temp": product_stock_temp,
        "product_object_stock_temp": product_object_stock_temp,
        "form": form
        }
    return TemplateResponse( request,
                             "product_stock/product_object_stock_temp/form.html",
                             ctx
                             )


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------








# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------





# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_list_for_stock(request):
#     products = Product.objects.prefetch_related("images")
#     products = products.order_by("name")
#     product_types = ProductType.objects.all()
#     product_filter = ProductFilter( request.GET, queryset=products )
#     products = get_paginator_items(
#         product_filter.qs, settings.DASHBOARD_PAGINATE_BY, request.GET.get("page")
#     )
#
#     ctx = {
#         "bulk_action_form": product_forms.ProductBulkUpdate(),
#         "products": products,
#         "product_types": product_types,
#         "filter_set": product_filter,
#         "is_empty": not product_filter.queryset.exists(),
#     }
#     return TemplateResponse(request, "product_stock/list.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_details_for_stock(request, pk):
#     products = Product.objects.prefetch_related("variants", "images").all()
#     product = get_object_or_404(products, pk=pk)
#     variants = product.variants.all()
#     images = product.images.all()
#     availability = get_product_availability(
#         product,
#         discounts=request.discounts,
#         country=request.country,
#         extensions=request.extensions,
#     )
#     sale_price = availability.price_range_undiscounted
#     discounted_price = availability.price_range
#     purchase_cost, margin = get_product_costs_data(product)
#     no_variants = not product.product_type.has_variants
#     only_variant = variants.first() if no_variants else None
#     product_stock = product.products_class.all()
#     stock_empty = not product_stock.exists()
#
#     ctx = {
#         "product": product,
#         "tax_rate_code": get_product_tax_rate( product ),
#         "sale_price": sale_price,
#         "discounted_price": discounted_price,
#         "product_stock": product_stock,
#         "stock_empty": stock_empty,
#         "variants": variants,
#         "images": images,
#         "no_variants": no_variants,
#         "only_variant": only_variant,
#         "purchase_cost": purchase_cost,
#         "margin": margin,
#         "is_empty": not variants.exists(),
#     }
#     return TemplateResponse(request, "product_stock/detail.html", ctx)
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_details(request, product_pk, stock_pk):
#     product = get_object_or_404(Product, pk=product_pk)
#     stock = get_object_or_404(product.products_class.all(), pk=stock_pk)
#
#     ctx = {
#         "product": product,
#         "stock": stock,
#     }
#     return TemplateResponse(
#         request, "product_stock/stock/detail.html", ctx
#     )
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_create(request, product_stock_pk):
#     product_stock = get_object_or_404( ProductStock.objects.all(), pk=product_stock_pk )
#     stock = ProductObjectStock( product_stock=product_stock )
#
#
#     form = product_stock_forms.ProductStockForm( request.POST or None, instance=stock )
#     if form.is_valid():
#         form.save()
#         msg = pgettext_lazy("Dashboard message", "Saved stock %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect(
#             "stock-details", product_pk=product.pk, stock_pk=stock.pk
#         )
#
#     ctx = {
#         "form": form,
#         "product": product,
#         "stock": stock,
#     }
#     return TemplateResponse(request, "product_stock/form.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_edit(request, product_pk, stock_pk):
#     product = get_object_or_404(Product.objects.all(), pk=product_pk)
#     stock = get_object_or_404(
#         product.products_class.all(),
#         pk=stock_pk,
#     )
#     form = product_stock_forms.ProductStockForm(request.POST or None, instance=stock)
#     if form.is_valid():
#         form.save()
#         msg = pgettext_lazy("Dashboard message", "Saved variant %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect(
#             "stock-details", product_pk=product.pk, stock_pk=stock.pk
#         )
#     ctx = {"form": form, "product": product, "stock": stock}
#     return TemplateResponse(request, "product_stock/form.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_delete(request, product_pk, stock_pk):
#     product = get_object_or_404(Product.objects.all(), pk=product_pk)
#     stock = get_object_or_404(
#         product.products_class.all(),
#         pk=stock_pk,
#     )
#     if request.method == "POST":
#         stock.delete()
#         msg = pgettext_lazy("Dashboard message", "Removed stock %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect("product-details-for-stock", pk=product.pk)
#     ctx = {
#         "product": product,
#         "stock": stock,
#         }
#
#     return TemplateResponse(request, "product_stock/modal/confirm_delete.html", ctx)
#
#


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


# ---------------------------------------------------------
# ---------------------------------------------------------

# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_list_for_stock(request):
#     products = Product.objects.prefetch_related("images")
#     products = products.order_by("name")
#     product_types = ProductType.objects.all()
#     product_filter = ProductFilter( request.GET, queryset=products )
#     products = get_paginator_items(
#         product_filter.qs, settings.DASHBOARD_PAGINATE_BY, request.GET.get("page")
#     )
#
#     ctx = {
#         "bulk_action_form": product_forms.ProductBulkUpdate(),
#         "products": products,
#         "product_types": product_types,
#         "filter_set": product_filter,
#         "is_empty": not product_filter.queryset.exists(),
#     }
#     return TemplateResponse(request, "product_stock/list.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_details_for_stock(request, pk):
#     products = Product.objects.prefetch_related("variants", "images").all()
#     product = get_object_or_404(products, pk=pk)
#     variants = product.variants.all()
#     images = product.images.all()
#     availability = get_product_availability(
#         product,
#         discounts=request.discounts,
#         country=request.country,
#         extensions=request.extensions,
#     )
#     sale_price = availability.price_range_undiscounted
#     discounted_price = availability.price_range
#     purchase_cost, margin = get_product_costs_data(product)
#     no_variants = not product.product_type.has_variants
#     only_variant = variants.first() if no_variants else None
#     product_stock = product.products_class.all()
#     stock_empty = not product_stock.exists()
#
#     ctx = {
#         "product": product,
#         "tax_rate_code": get_product_tax_rate( product ),
#         "sale_price": sale_price,
#         "discounted_price": discounted_price,
#         "product_stock": product_stock,
#         "stock_empty": stock_empty,
#         "variants": variants,
#         "images": images,
#         "no_variants": no_variants,
#         "only_variant": only_variant,
#         "purchase_cost": purchase_cost,
#         "margin": margin,
#         "is_empty": not variants.exists(),
#     }
#     return TemplateResponse(request, "product_stock/detail.html", ctx)
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_details(request, product_pk, stock_pk):
#     product = get_object_or_404(Product, pk=product_pk)
#     stock = get_object_or_404(product.products_class.all(), pk=stock_pk)
#
#     ctx = {
#         "product": product,
#         "stock": stock,
#     }
#     return TemplateResponse(
#         request, "product_stock/stock/detail.html", ctx
#     )
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_create(request, product_stock_pk):
#     product_stock = get_object_or_404( ProductStock.objects.all(), pk=product_stock_pk )
#     stock = ProductObjectStock( product_stock=product_stock )
#
#
#     form = product_stock_forms.ProductStockForm( request.POST or None, instance=stock )
#     if form.is_valid():
#         form.save()
#         msg = pgettext_lazy("Dashboard message", "Saved stock %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect(
#             "stock-details", product_pk=product.pk, stock_pk=stock.pk
#         )
#
#     ctx = {
#         "form": form,
#         "product": product,
#         "stock": stock,
#     }
#     return TemplateResponse(request, "product_stock/form.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_edit(request, product_pk, stock_pk):
#     product = get_object_or_404(Product.objects.all(), pk=product_pk)
#     stock = get_object_or_404(
#         product.products_class.all(),
#         pk=stock_pk,
#     )
#     form = product_stock_forms.ProductStockForm(request.POST or None, instance=stock)
#     if form.is_valid():
#         form.save()
#         msg = pgettext_lazy("Dashboard message", "Saved variant %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect(
#             "stock-details", product_pk=product.pk, stock_pk=stock.pk
#         )
#     ctx = {"form": form, "product": product, "stock": stock}
#     return TemplateResponse(request, "product_stock/form.html", ctx)
#
#
#
# @staff_member_required
# @permission_required("product_stock.manage_products_stock_permissions")
# def product_stock_delete(request, product_pk, stock_pk):
#     product = get_object_or_404(Product.objects.all(), pk=product_pk)
#     stock = get_object_or_404(
#         product.products_class.all(),
#         pk=stock_pk,
#     )
#     if request.method == "POST":
#         stock.delete()
#         msg = pgettext_lazy("Dashboard message", "Removed stock %s") % (stock.imei,)
#         messages.success(request, msg)
#         return redirect("product-details-for-stock", pk=product.pk)
#     ctx = {
#         "product": product,
#         "stock": stock,
#         }
#
#     return TemplateResponse(request, "product_stock/modal/confirm_delete.html", ctx)
#
#


# ---------------------------------------------------------
# ---------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


# @staff_member_required
# def add_new_product_to_manual_inventory_manage(request, manual_inventory_manage_pk):
#     manual_inventory_manage = get_object_or_404( ManualInventoryManage.objects.drafts(),
#                                                  pk=manual_inventory_manage_pk
#                                                  )
#     form = forms.ManualInventoryManageAddProductForm(
#         request.POST or None, manual_inventory_manage=manual_inventory_manage
#         )
#     status = 200
#     if form.is_valid():
#         if form.cleaned_data['product_stock']:
#             product_stock_temp = form.cleaned_data['product_stock']
#         else:
#             product_stock_temp = ProductStock(
#                 name=form.cleaned_data['name'],
#                 jan_code=form.cleaned_data['jan_code'],
#                 description=form.cleaned_data['description'],
#                 is_temp=True
#                 )
#             product_stock_temp.save()
#         product_object_stock_temp = ProductObjectStock(
#             imei_code=form.cleaned_data['imei_code'],
#             product_stock=product_stock_temp,
#             notion=form.cleaned_data['notion'],
#             price_override_amount=form.cleaned_data['price_override_amount'],
#             shops=form.cleaned_data['shops'],
#             extra_informations=form.cleaned_data['extra_informations'],
#             status=form.cleaned_data['status'],
#             manage_status=ProductStockManageStatus.MANUAL_STORAGE_PREDESTINATE
#             )
#         product_object_stock_temp.save()
#
#         line = add_product_object_stock_s_to_manual_inventory_manage(
#             manual_inventory_manage,
#             product_object_stock_temp,
#             ManualInventoryType.STORAGE,
#             ManualInventoryStatus.MANUAL_STORAGE_PREDESTINATE
#             )
#         events.draft_manual_inventory_manage_added_product_object_stock_s_event(
#             manual_inventory_manage=manual_inventory_manage, user=request.user,
#             manual_inventory_manage_lines=[(line.quantity, line)]
#             )
#
#         msg_dict = {
#             "manual_inventory_manage": form.cleaned_data.get(
#                 "manual_inventory_manage"
#                 ),
#             "quantity": 1,
#             }
#         msg = (
#                 pgettext_lazy(
#                     "Dashboard message related to an order",
#                     "%(manual_inventory_manage)sへ %(quantity)d 個商品を追加",
#                     )
#                 % msg_dict
#         )
#         messages.success( request, msg )
#         return redirect( "manual-inventory-manage-details",
#                          manual_inventory_manage_pk=manual_inventory_manage_pk
#                          )
#
#     ctx = {
#         "manual_inventory_manage": manual_inventory_manage,
#         "form": form,
#         }
#     template = "product_stock/manual_inventory_manage/modal/add_new_product.html"
#     return TemplateResponse( request, template, ctx, status=status )


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


