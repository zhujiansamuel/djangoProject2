from typing import List, Tuple
from django.utils.translation import pgettext_lazy
from kingbuy.account.models import User
from ..product_stock.models import (
    ManualInventoryManage,
    ManualInventoryManageLine,
    ManualInventoryManageEvent,
    StoreToStoreManage,
    StoreToStoreManageLine,
    StoreToStoreManageEvent,
    BarterManage,
    BarterManageLine,
    BarterManageEvent,
    OrderManage,
    OrderManageLine,
    OrderManageEvent,
    )

from ..product_stock import (
    ManageEvents,
    )

UserType = User

class OrderManageEventsEmails:
    """The different order emails event types."""

    PAYMENT = "payment_confirmation"
    SHIPPING = "shipping_confirmation"
    TRACKING_UPDATED = "tracking_updated"
    ORDER = "order_confirmation"
    FULFILLMENT = "fulfillment_confirmation"
    DIGITAL_LINKS = "digital_links"

    CHOICES = [
        (
            PAYMENT,
            pgettext_lazy(
                "A payment confirmation email was sent",
                "The payment confirmation email was sent",
            ),
        ),
        (
            SHIPPING,
            pgettext_lazy(
                "A shipping confirmation email was sent",
                "The shipping confirmation email was sent",
            ),
        ),
        (
            TRACKING_UPDATED,
            pgettext_lazy(
                "A tracking code update confirmation email was sent",
                "The fulfillment tracking code email was sent",
            ),
        ),
        (
            ORDER,
            pgettext_lazy(
                "A order confirmation email was sent",
                "The order placement confirmation email was sent",
            ),
        ),
        (
            FULFILLMENT,
            pgettext_lazy(
                "A fulfillment confirmation email was sent",
                "The fulfillment confirmation email was sent",
            ),
        ),
        (
            DIGITAL_LINKS,
            pgettext_lazy(
                "An email containing a or some digital link was sent",
                "The email containing the digital links was sent",
            ),
        ),
    ]


# ---------------------------------------------------------
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# ---------------------------------------------------------

# templatetages-有
def order_manage_fulfillment(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.FULFILLMENT_FULFILLED_ITEMS,
        responsible_person=user
        )

# templatetages-有
def draft_order_manage_created_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.DRAFT_CREATED,
        responsible_person=user
        )

# templatetages-有
def draft_order_manage_added_product_object_stock_s_with_IEMI_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_order_manage_added_product_stock_s_event(
        *, order_manage: OrderManage, user: UserType,
        order_manage_lines: List[Tuple[int, OrderManageLine]]
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_order_manage_added_product_object_stock_s_event(
        *, order_manage: OrderManage, user: UserType,
        order_manage_lines: List[Tuple[int, OrderManageLine]]
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_order_manage_removed_product_object_stock_event(
        *, order_manage: OrderManage, user: UserType,
        order_manage_lines: List[Tuple[int, OrderManageLine]]
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.DRAFT_REMOVED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def order_manage_note_added_event(
        *, order_manage: OrderManage, user: UserType, message: str
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.NOTE_ADDED,
        parameters={ "message": message },
        responsible_person=user
    )

# templatetages-有
def order_manage_supplier_added_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.SUPPLIER_ADDED,
        responsible_person=user
    )

# templatetages-有
def order_manage_legal_person_added_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.LEGALPERSON_ADDED,
        responsible_person=user
    )

# templatetages-有
def order_manage_supplier_changed_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.SUPPLIER_CHANGED,
        responsible_person=user
        )

# templatetages-有
def order_manage_legal_person_changed_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage,
        type=ManageEvents.LEGALPERSON_CHANGED,
        responsible_person=user
        )

# templatetages-有
def order_manage_created_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage, type=ManageEvents.PLACED_FROM_DRAFT,
        responsible_person=user
        )

# templatetages-有
def order_manage_add_slip_event(
        *, order_manage: OrderManage, user: UserType
        ) -> OrderManageEvent:
    return OrderManageEvent.objects.create(
        order_manage=order_manage, type=ManageEvents.SLIP_NUMBER_ADDED,
        responsible_person=user
        )



# ---------------------------------------------------------
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# ---------------------------------------------------------

# templatetages-有
def draft_barter_manage_created_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.DRAFT_CREATED,
        responsible_person=user
        )

# templatetages-有
def draft_barter_manage_added_product_object_stock_s_event(
        *, barter_manage: BarterManage, user: UserType,
        barter_manage_lines: List[Tuple[int, BarterManageLine]]
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_barter_manage_added_product_object_stock_s_with_IEMI_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def barter_manage_supplier_added_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.SUPPLIER_ADDED,
        responsible_person=user
    )

# templatetages-有
def barter_manage_legal_person_added_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.LEGALPERSON_ADDED,
        responsible_person=user
    )

# templatetages-有
def barter_manage_suppliers_changed_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.SUPPLIER_CHANGED,
        responsible_person=user
        )

# templatetages-有
def barter_manage_legal_person_changed_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.LEGALPERSON_CHANGED,
        responsible_person=user
        )

# templatetages-有
def draft_barter_manage_removed_product_object_stock_event(
        *, barter_manage: BarterManage, user: UserType,
        barter_manage_lines: List[Tuple[int, BarterManageLine]]
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage, type=ManageEvents.DRAFT_REMOVED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def barter_manage_note_added_event(
        *, barter_manage: BarterManage, user: UserType, message: str
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage,
        type=ManageEvents.NOTE_ADDED,
        parameters={"message": message},
        responsible_person=user
    )

# templatetages-有
def barter_manage_created_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage, type=ManageEvents.PLACED_FROM_DRAFT,
        responsible_person=user
        )

# templatetages-有
def barter_manage_fulfillment(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage, type=ManageEvents.FULFILLMENT_FULFILLED_ITEMS,
        responsible_person=user
        )

# templatetages-有
def barter_manage_add_slip_event(
        *, barter_manage: BarterManage, user: UserType
        ) -> BarterManageEvent:
    return BarterManageEvent.objects.create(
        barter_manage=barter_manage, type=ManageEvents.SLIP_NUMBER_ADDED,
        responsible_person=user
        )

# ---------------------------------------------------------
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# ---------------------------------------------------------

# templatetages-有
def draft_store_to_store_manage_created_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.DRAFT_CREATED,
        responsible_person=user
        )

# templatetages-有
def draft_store_to_store_manage_added_product_object_stock_s_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType,
        store_to_store_manage_lines: List[Tuple[int, StoreToStoreManageLine]]
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_store_to_store_manage_removed_product_object_stock_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType,
        store_to_store_manage_lines: List[Tuple[int, StoreToStoreManageLine]]
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.DRAFT_REMOVED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def store_to_store_manage_note_added_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType, message: str
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.NOTE_ADDED,
        parameters={"message": message},
        responsible_person=user
    )

# templatetages-有
def store_to_store_manage_to_shop_added_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.TO_SHOP_ADDED,
        responsible_person=user
    )

# templatetages-有
def store_to_store_manage_created_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.PLACED_FROM_DRAFT,
        responsible_person=user
        )

# templatetages-有
def store_to_store_manage_fulfillment_MOVEOUT(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.FULFILLMENT_MOVEOUT,
        responsible_person=user
        )

# templatetages-有
def store_to_store_manage_fulfillment_MOVEIN(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage,
        type=ManageEvents.FULFILLMENT_MOVEIN,
        responsible_person=user
        )

# templatetages-有
def store_to_store_manage_add_slip_event(
        *, store_to_store_manage: StoreToStoreManage, user: UserType
        ) -> StoreToStoreManageEvent:
    return StoreToStoreManageEvent.objects.create(
        store_to_store_manage=store_to_store_manage, type=ManageEvents.SLIP_NUMBER_ADDED,
        responsible_person=user
        )
# ---------------------------------------------------------
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# ---------------------------------------------------------

# templatetages-有
def draft_manual_inventory_manage_created_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.DRAFT_CREATED,
        responsible_person=user
        )

# templatetages-有
def draft_manual_inventory_manage_added_product_object_stock_s_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType,
        manual_inventory_manage_lines: List[Tuple[int, ManualInventoryManageLine]]
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.DRAFT_ADDED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def draft_manual_inventory_manage_removed_product_object_stock_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType,
        manual_inventory_manage_lines: List[Tuple[int, ManualInventoryManageLine]]
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.DRAFT_REMOVED_PRODUCTS,
        responsible_person=user
        )

# templatetages-有
def manual_inventory_manage_note_added_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType, message: str
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.NOTE_ADDED,
        parameters={"message": message},
        responsible_person=user
    )

# templatetages-有
def manual_inventory_manage_created_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.PLACED_FROM_DRAFT,
        responsible_person=user
        )

# templatetages-有
def manual_inventory_manage_fulfillment_LOCK(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.FULFILLMENT_LOCK,
        responsible_person=user
        )

# templatetages-有
def manual_inventory_manage_fulfillment_UNLOCK(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage,
        type=ManageEvents.FULFILLMENT_UNLOCK,
        responsible_person=user
        )

# templatetages-有
def manual_inventory_manage_add_slip_event(
        *, manual_inventory_manage: ManualInventoryManage, user: UserType
        ) -> ManualInventoryManageEvent:
    return ManualInventoryManageEvent.objects.create(
        manual_inventory_manage=manual_inventory_manage, type=ManageEvents.SLIP_NUMBER_ADDED,
        responsible_person=user
        )

# ---------------------------------------------------------
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# ---------------------------------------------------------
