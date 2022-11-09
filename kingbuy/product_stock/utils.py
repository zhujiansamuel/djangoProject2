from django.db.models import F
from decimal import Decimal
from django_prices.forms import Money
from django.shortcuts import get_object_or_404

from . import (
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
    ProductStock,
    ProductObjectStock,
    OrderManageLine,
    BarterManageLine,
    StoreToStoreManageLine,
    ManualInventoryManageLine,
    ProductStockChangeEvent,
    ProductObjectStockChangeEvent,
    )

from . import (
    events,
    FulfillmentStatus,
    InventoryStatus,
    InventoryFundsStatus,
    ProductStockManageStatus,
    )

def log_product_stock_changed(user,product_stock_pk,field,new_value,old_value):
    try:
        product_stock_temp = ProductStock.objects.get(pk=product_stock_pk)
        logs = ProductStockChangeEvent.objects.create(
            product_stock=product_stock_temp,
            change_field=field,
            changed_value=new_value,
            old_value=old_value,
            responsible_person=user
            )
        logs.save()
    except ProductStock.DoesNotExist:
        pass

def log_product_object_stock_changed(user,product_object_stock_pk,field,new_value,old_value):
    try:
        product_object_stock_temp = ProductObjectStock.objects.get(pk=product_object_stock_pk)
        logs = ProductObjectStockChangeEvent.objects.create(
            product_object_stock=product_object_stock_temp,
            change_field=field,
            changed_value=new_value,
            old_value=old_value,
            responsible_person=user
            )
        logs.save()
    except ProductStock.DoesNotExist:
        pass




def change_avarage_price(line, is_cancel=False, is_no_imei=True, is_barter=False):
    def _difference(a, b, _type, _is_cancel=False):
        if _type == "+-":
            if not _is_cancel:
                return a + b
            else:
                return a - b
        elif _type == "-+":
            if not _is_cancel:
                return a - b
            else:
                return a + b
    if is_barter:
        unit_price_amount = line.barter_manage_line.unit_price_amount
        if is_no_imei:
            product_stock_temp = ProductStock.objects.get(
                pk=line.barter_manage_line.product_stock.pk
                )
        else:
            product_stock_temp = ProductStock.objects.get(
                pk=line.barter_manage_line.product_object_stock.product_stock.pk
                )
    else:
        unit_price_amount = line.order_manage_line.unit_price_amount
        if is_no_imei:
            product_stock_temp = ProductStock.objects.get(
                pk=line.order_manage_line.product_stock.pk
                )
        else:
            product_stock_temp = ProductStock.objects.get(
                pk=line.order_manage_line.product_object_stock.product_stock.pk
                )
    product_stock_temp.price_average_amount =int( (_difference(
        (
                product_stock_temp.get_quantity_for_avarage() * product_stock_temp.price_average_amount),
        (unit_price_amount * line.quantity),
        "+-",
        _is_cancel=is_cancel
        )
                                       ) / (
                                           _difference(
                                               product_stock_temp.get_quantity_for_avarage(),
                                               line.quantity,
                                               "+-",
                                               _is_cancel=is_cancel
                                               )
                                       ))


    product_stock_temp.save( update_fields=["price_average_amount"] )
    for product_object_stock in product_stock_temp:
        product_object_stock.price_average_amount=product_stock_temp.price_average_amount
        product_object_stock.save( update_fields=["price_average_amount"] )


def fulfill_manual_inventory_LOCK(line, quantity):
    line.quantity_fulfilled_LOCK += quantity
    line.save( update_fields=["quantity_fulfilled_LOCK"] )


def fulfill_manual_inventory_UNLOCK(line, quantity):
    line.quantity_fulfilled_UNLOCK += quantity
    line.save( update_fields=["quantity_fulfilled_UNLOCK"] )


def fulfill_store_MOVEOUT(line, quantity):
    line.quantity_fulfilled_MOVEOUT += quantity
    line.save( update_fields=["quantity_fulfilled_MOVEOUT"] )


def fulfill_store_MOVEIN(line, quantity):
    line.quantity_fulfilled_MOVEIN += quantity
    line.save( update_fields=["quantity_fulfilled_MOVEIN"] )


def fulfill_order_line(order_line, quantity):
    """Fulfill order line with given quantity."""
    order_line.quantity_fulfilled += quantity
    order_line.save( update_fields=["quantity_fulfilled"] )


def update_barter_manage_status(barter_manage):
    quantity_fulfilled = barter_manage.quantity_fulfilled
    total_quantity = barter_manage.get_total_quantity()
    if quantity_fulfilled <= 0:
        status = InventoryStatus.UNFULFILLED
    elif quantity_fulfilled < total_quantity:
        status = InventoryStatus.PARTIALLY_FULFILLED
    else:
        status = InventoryStatus.FULFILLED
    if status != barter_manage.barter_status:
        barter_manage.barter_status = status
        barter_manage.save( update_fields=["barter_status"] )


def change_product_object_stock_store(product_object_stock, store):
    product_object_stock.shops = store
    product_object_stock.save( update_fields=["shops"] )


def update_manual_inventory_manage_status(manual_inventory_manage):
    quantity_fulfilled_LOCK = manual_inventory_manage.quantity_fulfilled_LOCK
    quantity_fulfilled_UNLOCK = manual_inventory_manage.quantity_fulfilled_UNLOCK
    quantity_fulfilled = quantity_fulfilled_LOCK + quantity_fulfilled_UNLOCK
    total_quantity = manual_inventory_manage.get_total_quantity() * 2
    if quantity_fulfilled <= 0:
        status = InventoryStatus.UNFULFILLED
    elif quantity_fulfilled < total_quantity:
        status = InventoryStatus.PARTIALLY_FULFILLED
    else:
        status = InventoryStatus.FULFILLED
    if status != manual_inventory_manage.manual_inventory_status:
        manual_inventory_manage.manual_inventory_status = status
        manual_inventory_manage.save( update_fields=["manual_inventory_status"] )


def update_store_to_store_manage_status(store_to_store_manage):
    quantity_fulfilled_MOVEOUT = store_to_store_manage.quantity_fulfilled_MOVEOUT
    quantity_fulfilled_MOVEIN = store_to_store_manage.quantity_fulfilled_MOVEIN
    quantity_fulfilled = quantity_fulfilled_MOVEOUT + quantity_fulfilled_MOVEIN
    total_quantity = store_to_store_manage.get_total_quantity() * 2
    if quantity_fulfilled <= 0:
        status = InventoryStatus.UNFULFILLED
    elif quantity_fulfilled < total_quantity:
        status = InventoryStatus.PARTIALLY_FULFILLED
    else:
        status = InventoryStatus.FULFILLED
    if status != store_to_store_manage.store_to_store_status:
        store_to_store_manage.store_to_store_status = status
        store_to_store_manage.save( update_fields=["store_to_store_status"] )


def update_order_manage_status(order_manage):
    quantity_fulfilled = order_manage.quantity_fulfilled
    total_quantity = order_manage.get_total_quantity()
    if quantity_fulfilled <= 0:
        status = InventoryStatus.UNFULFILLED
    elif quantity_fulfilled < total_quantity:
        status = InventoryStatus.PARTIALLY_FULFILLED
    else:
        status = InventoryStatus.FULFILLED
    if status != order_manage.order_status:
        order_manage.order_status = status
        order_manage.save( update_fields=["order_status"] )


def change_product_object_stock_manage_status(product_object_stock, manage_status):
    product_object_stock = get_object_or_404( ProductObjectStock.objects.all(),
                                              pk=product_object_stock.pk
                                              )

    if product_object_stock.manage_status in [
        ProductStockManageStatus.ORDER_STORAGE_PREDESTINATE,
        ProductStockManageStatus.BARTER_MOVE_IN_PREDESTINATE
        ] and manage_status in [
        ProductStockManageStatus.DELETE
        ]:
        product_object_stock.delete()
    else:
        product_object_stock.manage_status = manage_status
        if manage_status in [
            ProductStockManageStatus.OTHER
            ]:
            product_object_stock.is_allocate = False
            product_object_stock.is_available_M = True
            product_object_stock.is_temp = False
            product_object_stock.is_lock = False
        elif manage_status in [
            ProductStockManageStatus.ORDER_DELIVERY_PREDESTINATE,
            ProductStockManageStatus.STORE_MOVE_OUT_PREDESTINATE,
            ProductStockManageStatus.BARTER_MOVE_OUT_PREDESTINATE
            ]:
            product_object_stock.is_allocate = True
            product_object_stock.is_available_M = False

        elif manage_status in [
            ProductStockManageStatus.ORDER_DELIVERY,
            ProductStockManageStatus.BARTER_MOVE_OUT,
            ]:
            product_object_stock.is_allocate = True
            product_object_stock.is_available_M = False
            product_object_stock.is_out_of_stock = True
        elif manage_status in [
            ProductStockManageStatus.ORDER_STORAGE_PREDESTINATE,
            ProductStockManageStatus.BARTER_MOVE_IN_PREDESTINATE
            ]:
            product_object_stock.is_allocate = False
            product_object_stock.is_available_M = True
            product_object_stock.is_out_of_stock = False
            product_object_stock.is_temp = True
        elif manage_status in [
            ProductStockManageStatus.ORDER_STORAGE,
            ProductStockManageStatus.BARTER_MOVE_IN
            ]:
            product_object_stock.is_allocate = False
            product_object_stock.is_available_M = True
            product_object_stock.is_out_of_stock = False
            product_object_stock.is_temp = False
        elif manage_status in [
            ProductStockManageStatus.STORE_TO_STORE_MOVE_OUT
            ]:
            product_object_stock.is_allocate = True
            product_object_stock.is_available_M = False
        elif manage_status in [
            ProductStockManageStatus.STORE_TO_STORE_MOVE_IN
            ]:
            product_object_stock.is_allocate = False
            product_object_stock.is_available_M = True
        elif manage_status in [
            ProductStockManageStatus.STORE_MOVE_IN_PREDESTINATE
            ]:
            product_object_stock.is_allocate = False
            product_object_stock.is_available_M = False
        elif manage_status in [
            ProductStockManageStatus.MANUAL_LOCK_PREDESTINATE,
            ProductStockManageStatus.MANUAL_LOCK
            ]:
            product_object_stock.is_lock = True
            product_object_stock.is_available_M = False
        elif manage_status in [
            ProductStockManageStatus.MANUAL_UNLOCK
            ]:
            product_object_stock.is_lock = False
            product_object_stock.is_available_M = True
        product_object_stock.save()


def change_product_stock_quantity_s(
        product_stock,
        is_cancel=False,
        is_Fulfillment=False,
        is_no_imei=False,
        quantity_locking_dif=0,
        quantity_allocated_dif=0,
        quantity_predestinate_dif=0,
        ):
    product_stock = get_object_or_404(
        ProductStock.objects.all().filter( pk=product_stock.pk )
        )

    def _difference(a, b, _type, _is_cancel=False):
        if _type == "+-":
            # / move-in / not-fulfillment
            if not _is_cancel:
                return a + b
            else:
                return a - b
        elif _type == "-+":
            # / locking / not-fulfillment
            if not _is_cancel:
                return a - b
            else:
                return a + b

    if quantity_predestinate_dif:
        if not is_Fulfillment:
            if not is_no_imei:
                # / move-in / not-fulfillment / iemi / ------------------------OK
                product_stock.quantity_predestinate = _difference(
                    product_stock.quantity_predestinate, quantity_predestinate_dif,
                    "+-", is_cancel
                    )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_predestinate_dif,
                                                          "+-", is_cancel
                                                          )
            elif is_no_imei:
                # / move-in / not-fulfillment / no-iemi / ------------------------OK
                product_stock.quantity_predestinate_no_imei = _difference(
                    product_stock.quantity_predestinate_no_imei,
                    quantity_predestinate_dif, "+-", is_cancel
                    )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_predestinate_dif,
                                                          "+-", is_cancel
                                                          )
        else:
            if not is_no_imei:
                # / move-in / fulfillment / iemi / ------------------------OK
                product_stock.quantity_predestinate = _difference(
                    product_stock.quantity_predestinate, quantity_predestinate_dif,
                    "-+", is_cancel
                    )
                product_stock.quantity_available = _difference(
                    product_stock.quantity_available, quantity_predestinate_dif, "+-",
                    is_cancel
                    )
                product_stock.quantity = _difference( product_stock.quantity,
                                                      quantity_predestinate_dif, "+-",
                                                      is_cancel
                                                      )
            elif is_no_imei:
                # / move-in / fulfillment / no-iemi / ------------------------OK
                product_stock.quantity_predestinate_no_imei = _difference(
                    product_stock.quantity_predestinate_no_imei,
                    quantity_predestinate_dif, "-+", is_cancel
                    )
                product_stock.quantity_available_no_imei = _difference(
                    product_stock.quantity_available_no_imei, quantity_predestinate_dif,
                    "+-", is_cancel
                    )
                product_stock.quantity_no_imei = _difference(
                    product_stock.quantity_no_imei, quantity_predestinate_dif, "+-",
                    is_cancel
                    )

    elif quantity_locking_dif:
        if not is_Fulfillment:
            if not is_no_imei:
                # / locking / not-fulfillment / iemi / ------------------------OK
                product_stock.quantity_locking = _difference(
                    product_stock.quantity_locking, quantity_locking_dif, "+-",
                    is_cancel
                    )
                product_stock.quantity_available = _difference(
                    product_stock.quantity_available, quantity_locking_dif, "-+",
                    not is_cancel
                    )
            elif is_no_imei:
                # / locking / not-fulfillment / no-iemi / ------------------------OK
                product_stock.quantity_locking_no_imei = _difference(
                    product_stock.quantity_locking_no_imei, quantity_locking_dif, "+-",
                    is_cancel
                    )
                product_stock.quantity_available_no_imei = _difference(
                    product_stock.quantity_available_no_imei, quantity_locking_dif,
                    "-+", is_cancel
                    )
        else:
            # fulfillment意味着出库
            if not is_no_imei:
                # / locking / fulfillment / iemi / ------------------------OK
                product_stock.quantity_locking = _difference(
                    product_stock.quantity_locking, quantity_locking_dif, "-+",
                    is_cancel
                    )
                product_stock.quantity = _difference( product_stock.quantity,
                                                      quantity_locking_dif, "-+",
                                                      is_cancel
                                                      )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_locking_dif, "-+",
                                                          is_cancel
                                                          )
                product_stock.quantity_out_of_stock = _difference(
                    product_stock.quantity_out_of_stock, quantity_locking_dif, "+-",
                    is_cancel
                    )
            elif is_no_imei:
                # / locking / fulfillment / no-iemi / ------------------------OK
                product_stock.quantity_locking_no_imei = _difference(
                    product_stock.quantity_locking_no_imei, quantity_locking_dif, "-+",
                    is_cancel
                    )
                product_stock.quantity_no_imei = _difference(
                    product_stock.quantity_no_imei, quantity_locking_dif, "-+",
                    is_cancel
                    )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_locking_dif, "-+",
                                                          is_cancel
                                                          )
                product_stock.quantity_out_of_stock_no_imei = _difference(
                    product_stock.quantity_out_of_stock_no_imei, quantity_locking_dif,
                    "+-", is_cancel
                    )

    elif quantity_allocated_dif:
        if not is_Fulfillment:
            if not is_no_imei:
                # / move-out / no-fulfillment / iemi / ------------------------OK
                product_stock.quantity_allocated = _difference(
                    product_stock.quantity_allocated, quantity_allocated_dif, "+-",
                    is_cancel
                    )
                product_stock.quantity_available = _difference(
                    product_stock.quantity_available, quantity_allocated_dif, "-+",
                    is_cancel
                    )
            elif is_no_imei:
                # / move-out / no-fulfillment / no-iemi / ------------------------OK
                product_stock.quantity_allocated_no_imei = _difference(
                    product_stock.quantity_allocated_no_imei, quantity_allocated_dif,
                    "+-", is_cancel
                    )
                product_stock.quantity_available_no_imei = _difference(
                    product_stock.quantity_available_no_imei, quantity_allocated_dif,
                    "-+", is_cancel
                    )
        else:
            if not is_no_imei:
                # / move-out / fulfillment / no-iemi /
                product_stock.quantity_allocated = _difference(
                    product_stock.quantity_allocated, quantity_allocated_dif, "-+",
                    is_cancel
                    )
                product_stock.quantity = _difference( product_stock.quantity,
                                                      quantity_allocated_dif, "-+",
                                                      is_cancel
                                                      )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_allocated_dif, "-+",
                                                          is_cancel
                                                          )
                product_stock.quantity_out_of_stock = _difference(
                    product_stock.quantity_out_of_stock, quantity_allocated_dif, "+-",
                    is_cancel
                    )
            elif is_no_imei:
                # / move-out / fulfillment / iemi /
                product_stock.quantity_allocated_no_imei = _difference(
                    product_stock.quantity_allocated_no_imei, quantity_allocated_dif,
                    "-+", is_cancel
                    )
                product_stock.quantity_no_imei = _difference(
                    product_stock.quantity_no_imei, quantity_allocated_dif, "-+",
                    is_cancel
                    )
                product_stock.quantity_all = _difference( product_stock.quantity_all,
                                                          quantity_allocated_dif, "-+",
                                                          is_cancel
                                                          )
                product_stock.quantity_out_of_stock_no_imei = _difference(
                    product_stock.quantity_out_of_stock_no_imei, quantity_allocated_dif,
                    "+-", is_cancel
                    )

    product_stock.save()


def change_product_stock_ststus(product_stock):
    product_stock.is_temp = False
    product_stock.save( update_fields=["is_temp"] )

# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------

def add_product_object_stock_s_to_order_manage(
        order_manage, product_object_stock, type, status
        ):
    try:
        line = order_manage.order_manage_lines.get(
            product_object_stock=product_object_stock
            )
    except OrderManageLine.DoesNotExist:
        if type == OrderManageType.STORAGE:
            line = order_manage.order_manage_lines.create(
                order_manage_type=type,
                order_manage_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.price_override,
                line_price=product_object_stock.price_override
                )
            order_manage.total_amount += product_object_stock.price_override_amount
            order_manage.save( update_fields=["total_amount"] )
        elif type == OrderManageType.DELIVERY:
            line = order_manage.order_manage_lines.create(
                order_manage_type=type,
                order_manage_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
            order_manage.total_amount += product_object_stock.product_stock.price_average_amount if product_object_stock.product_stock.price_average_amount else 0
            order_manage.save( update_fields=["total_amount"] )
    return line


def add_product_object_stock_s_to_barter_manage(
        barter_manage, product_object_stock, type, status
        ):
    try:
        line = barter_manage.barter_manage_lines.get(
            product_object_stock=product_object_stock
            )
    except BarterManageLine.DoesNotExist:
        if type == BarterManageType.MOVEIN:
            line = barter_manage.barter_manage_lines.create(
                barter_manage_type=type,
                barter_manage_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.price_override,
                line_price=product_object_stock.price_override,
                )
            barter_manage.total_MOVEIN_amount += product_object_stock.price_override_amount
            barter_manage.save( update_fields=["total_MOVEIN_amount"] )
        elif type == BarterManageType.MOVEOUT:
            line = barter_manage.barter_manage_lines.create(
                barter_manage_type=type,
                barter_manage_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
            barter_manage.total_MOVEOUT_amount += product_object_stock.product_stock.price_average_amount if product_object_stock.product_stock.price_average_amount else 0
            barter_manage.save( update_fields=["total_MOVEOUT_amount"] )
        barter_manage.total_amount=barter_manage.total_MOVEIN_amount-barter_manage.total_MOVEOUT_amount
        barter_manage.save( update_fields=["total_amount"] )
    return line


def add_product_object_stock_s_to_store_to_store_manage(
        store_to_store_manage, product_object_stock, type, status
        ):
    try:
        line = store_to_store_manage.store_to_store_manage_lines.get(
            product_object_stock=product_object_stock
            )
    except StoreToStoreManageLine.DoesNotExist:
        if type == StoreToStoreType.MOVEIN:
            line = store_to_store_manage.store_to_store_manage_lines.create(
                store_to_store_type=type,
                store_to_store_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.price_override,
                line_price=product_object_stock.price_override
                )
        elif type == StoreToStoreType.MOVEOUT:
            line = store_to_store_manage.store_to_store_manage_lines.create(
                store_to_store_type=type,
                store_to_store_status=status,
                product_object_stock=product_object_stock,
                product_stock_name=product_object_stock.product_stock.name,
                product_stock_jan_code=product_object_stock.product_stock.jan_code,
                product_object_stock_sku=product_object_stock.sku,
                quantity=1,
                unit_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
    return line


def add_product_object_stock_s_to_manual_inventory_manage(
        manual_inventory_manage, product_object_stock, type, status
        ):
    try:
        line = manual_inventory_manage.manual_inventory_manage_lines.get(
            product_object_stock=product_object_stock
            )
    except ManualInventoryManageLine.DoesNotExist:
        line = manual_inventory_manage.manual_inventory_manage_lines.create(
            manual_inventory_type=type,
            manual_inventory_status=status,
            product_object_stock=product_object_stock,
            product_stock_name=product_object_stock.product_stock.name,
            product_stock_jan_code=product_object_stock.product_stock.jan_code,
            product_object_stock_sku=product_object_stock.sku,
            quantity=1,
            unit_price=product_object_stock.price_override,
            line_price=product_object_stock.product_stock.price_average if product_object_stock.product_stock.price_average else Money(
                0, "JPY"
                ),
            )
    return line


# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------


def add_product_stock_s_to_order_manage(
        order_manage, product_stock, quantity, type, status, unit_price_new=0
        ):
    try:
        line = order_manage.order_manage_lines.get(
            product_stock=product_stock, unit_price_amount=unit_price_new
            )
        line.quantity += quantity
        line.line_price_amount += unit_price_new*quantity
        line.save( update_fields=["quantity","line_price_amount"] )
    except OrderManageLine.DoesNotExist:
        if type == OrderManageType.STORAGE:
            line = order_manage.order_manage_lines.create(
                order_manage_type=type,
                order_manage_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=Money( unit_price_new, "JPY" ),
                line_price=Money( unit_price_new * quantity, "JPY" )
                )
        elif type == OrderManageType.DELIVERY:
            line = order_manage.order_manage_lines.create(
                order_manage_type=type,
                order_manage_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=quantity * product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
    order_manage.total_amount += line.line_price_amount
    order_manage.save( update_fields=["total_amount"] )
    return line


def add_product_stock_s_to_barter_manage(
        barter_manage, product_stock, quantity, type, status, unit_price_new=0
        ):
    try:
        line = barter_manage.barter_manage_lines.get(
            product_stock=product_stock
            )
        line.quantity += quantity
        line.line_price_amount += unit_price_new * quantity
        line.save( update_fields=["quantity", "line_price_amount"] )
    except BarterManageLine.DoesNotExist:
        if type == BarterManageType.MOVEIN:
            line = barter_manage.barter_manage_lines.create(
                barter_manage_type=type,
                barter_manage_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=Money( unit_price_new, "JPY" ),
                line_price=Money( unit_price_new * quantity, "JPY" )
                )
        elif type == BarterManageType.MOVEOUT:
            line = barter_manage.barter_manage_lines.create(
                barter_manage_type=type,
                barter_manage_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=quantity * product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
    barter_manage.total_amount += line.line_price_amount
    barter_manage.save( update_fields=["total_amount"] )
    return line


def add_product_stock_s_to_store_to_store_manage(
        store_to_store_manage, product_stock, quantity, type, status, unit_price_new=0
        ):
    try:
        line = store_to_store_manage.store_to_store_manage_lines.get(
            product_stock=product_stock
            )
        line.quantity += quantity
        line.line_price_amount += unit_price_new * quantity
        line.save( update_fields=["quantity", "line_price_amount"] )
    except StoreToStoreManageLine.DoesNotExist:
        if type == StoreToStoreType.MOVEIN:
            line = store_to_store_manage.store_to_store_manage_lines.create(
                store_to_store_type=type,
                store_to_store_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=Money( unit_price_new, "JPY" ),
                line_price=Money( unit_price_new * quantity, "JPY" )
                )
        elif type == StoreToStoreType.MOVEOUT:
            line = store_to_store_manage.store_to_store_manage_lines.create(
                store_to_store_type=type,
                store_to_store_status=status,
                product_stock=product_stock,
                product_stock_name=product_stock.name,
                product_stock_jan_code=product_stock.jan_code,
                quantity=quantity,
                unit_price=product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                line_price=quantity * product_stock.price_average if product_stock.price_average else Money(
                    0, "JPY"
                    ),
                )
    return line


def add_product_stock_s_to_manual_inventory_manage(
        manual_inventory_manage, product_stock, quantity, type, status, unit_price_new=0
        ):
    try:
        line = manual_inventory_manage.manual_inventory_manage_lines.get(
            product_stock=product_stock
            )
        line.quantity += quantity
        line.line_price_amount += unit_price_new * quantity
        line.save( update_fields=["quantity","line_price_amount"] )
    except ManualInventoryManageLine.DoesNotExist:
        line = manual_inventory_manage.manual_inventory_manage_lines.create(
            manual_inventory_type=type,
            manual_inventory_status=status,
            product_stock=product_stock,
            product_stock_name=product_stock.name,
            product_stock_jan_code=product_stock.jan_code,
            quantity=quantity,
            unit_price=Money( unit_price_new, "JPY" ),
            line_price=quantity * product_stock.price_average if product_stock.price_average else Money(
                0, "JPY"
                ),
            )
    return line


# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------
# ,------------------------------------------------------------------------------------------------------


def delete_store_manage_line(line, managestatus):
    if line.product_object_stock:
        change_product_object_stock_manage_status( line.product_object_stock,
                                                   managestatus
                                                   )
        if line.store_to_store_type == StoreToStoreType.MOVEOUT:
            change_product_stock_quantity_s(
                line.product_object_stock.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )

    line.delete()


# -------------------------------------------------------------------------------------------------------

def delete_manage_line(line, managestatus):
    if line.product_object_stock:
        if line.order_manage_type == "注文入庫":
            change_product_stock_quantity_s(
                line.product_object_stock.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=0,
                quantity_predestinate_dif=1,
                )
            line.product_object_stock.delete()
        elif line.order_manage_type == "注文出庫":
            change_product_stock_quantity_s(
                line.product_object_stock.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )
            change_product_object_stock_manage_status( line.product_object_stock,
                                                       managestatus
                                                       )
    elif line.product_stock:
        if line.order_manage_type == "注文入庫":
            change_product_stock_quantity_s(
                line.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=True,
                quantity_locking_dif=0,
                quantity_allocated_dif=0,
                quantity_predestinate_dif=line.quantity,
                )
        elif line.order_manage_type == "注文出庫":
            change_product_stock_quantity_s(
                line.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=True,
                quantity_locking_dif=0,
                quantity_allocated_dif=line.quantity,
                quantity_predestinate_dif=0,
                )
    line.order_manage.total_amount -= line.line_price_amount
    line.order_manage.save( update_fields=["total_amount"] )
    line.delete()


def delete_manual_manage_line(line, managestatus):
    if line.product_object_stock:
        change_product_object_stock_manage_status( line.product_object_stock,
                                                   managestatus
                                                   )
        change_product_stock_quantity_s(
            line.product_object_stock.product_stock,
            is_cancel=True,
            is_Fulfillment=False,
            is_no_imei=False,
            quantity_locking_dif=1,
            quantity_allocated_dif=0,
            quantity_predestinate_dif=0,
            )
    elif line.product_stock:
        change_product_stock_quantity_s(
            line.product_stock,
            is_cancel=True,
            is_Fulfillment=False,
            is_no_imei=True,
            quantity_locking_dif=line.quantity,
            quantity_allocated_dif=0,
            quantity_predestinate_dif=0,
            )
    line.delete()


def delete_barter_manage_line(line, managestatus):
    if line.product_object_stock:

        if line.barter_manage_type == BarterManageType.MOVEIN:
            change_product_stock_quantity_s(
                line.product_object_stock.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=0,
                quantity_predestinate_dif=1,
                )
            line.product_object_stock.delete()
        elif line.barter_manage_type == BarterManageType.MOVEOUT:
            change_product_stock_quantity_s(
                line.product_object_stock.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=False,
                quantity_locking_dif=0,
                quantity_allocated_dif=1,
                quantity_predestinate_dif=0,
                )
            change_product_object_stock_manage_status( line.product_object_stock,
                                                       managestatus
                                                       )
    elif line.product_stock:
        if line.barter_manage_type == BarterManageType.MOVEIN:
            change_product_stock_quantity_s(
                line.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=True,
                quantity_locking_dif=0,
                quantity_allocated_dif=0,
                quantity_predestinate_dif=line.quantity,
                )
        elif line.barter_manage_type == BarterManageType.MOVEOUT:
            change_product_stock_quantity_s(
                line.product_stock,
                is_cancel=True,
                is_Fulfillment=False,
                is_no_imei=True,
                quantity_locking_dif=0,
                quantity_allocated_dif=line.quantity,
                quantity_predestinate_dif=0,
                )
    line.barter_manage.total_amount -= line.line_price_amount
    line.barter_manage.save( update_fields=["total_amount"] )
    line.delete()


# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


def update_stock_temp(product_stock):
    c_num = product_stock.product_object_stock.all().count()
    product_stock.quantity = c_num
    update_fields = ["quantity"]
    product_stock.save( update_fields=update_fields )
