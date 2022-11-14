from django.conf import settings
from django.template import Library
from django.utils.translation import npgettext_lazy, pgettext_lazy
from django_prices.templatetags import prices
from prices import Money

from kingbuy.product_stock.models import (
    OrderManageEvent,
    ManualInventoryManageEvent,
    StoreToStoreManageEvent,
    BarterManageEvent,
    )

from kingbuy.product_stock import (
    events,
    ManageEvents
    )


register = Library()


EMAIL_CHOICES = {
    events.OrderManageEventsEmails.PAYMENT: pgettext_lazy(
        "Email type", "Payment confirmation"
    ),
    events.OrderManageEventsEmails.SHIPPING: pgettext_lazy(
        "Email type", "Shipping confirmation"
    ),
    events.OrderManageEventsEmails.FULFILLMENT: pgettext_lazy(
        "Email type", "Fulfillment confirmation"
    ),
    events.OrderManageEventsEmails.ORDER: pgettext_lazy("Email type", "Order confirmation"),
}


def get_money_from_params(amount):
    """Retrieve the correct money amount from the given object.

    Money serialization changed at one point, as for now it's serialized
    as a dict. But we keep those settings for the legacy data.

    Can be safely removed after migrating to product_stock 2.0
    """
    if isinstance(amount, Money):
        return amount
    if isinstance(amount, dict):
        return Money(amount=amount["amount"], currency=amount["currency"])
    return Money(amount, settings.DEFAULT_CURRENCY)


# events----有
# events----無し
@register.simple_tag
def display_order_manage_event(order_manage_event: OrderManageEvent):
    event_type = order_manage_event.type
    params = order_manage_event.parameters
    #
    if event_type == ManageEvents.NOTE_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sによりノートを追加した: %(note)s"
            % { "note": params["message"], "user_name": order_manage_event.responsible_person },
            )
    #
    if event_type == ManageEvents.FULFILLMENT_FULFILLED_ITEMS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより項目を執行した"
            ) % {"user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.DRAFT_CREATED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより執行表の下書きを作成した",
        ) % {"user_name": order_manage_event.responsible_person}
    #
    if event_type == ManageEvents.DRAFT_ADDED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を追加した"
        ) % {"user_name": order_manage_event.responsible_person}
    #
    if event_type == ManageEvents.DRAFT_REMOVED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を削除した",
        ) % {"user_name": order_manage_event.responsible_person}
    #
    if event_type == ManageEvents.SUPPLIER_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(個人)を追加した",
            ) % { "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.LEGALPERSON_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(法人)を追加した",
            ) % { "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.LEGALPERSON_CHANGED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(法人)を編集した",
            ) % { "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.SUPPLIER_CHANGED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(個人)を編集した",
            ) % { "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.PLACED_FROM_DRAFT:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより執行表を作成した",
            ) % { "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.SLIP_NUMBER_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより伝票番号を追加した"
        ) % {"user_name": order_manage_event.responsible_person}
    # ----------------------------------------------------------------------------------------
    #
    if event_type == ManageEvents.OTHER:
        # events----無し
        return order_manage_event.parameters["message"]
    #
    if event_type == ManageEvents.CANCELED:
        # events----無し
        return pgettext_lazy(
            "product_stock message related to an order", "Order was canceled"
            )
    #
    if event_type == ManageEvents.FULFILLMENT_RESTOCKED_ITEMS:
        # events----無し
        return npgettext_lazy(
            "product_stock message related to an order",
            "We restocked %(quantity)d item",
            "We restocked %(quantity)d items",
            number="quantity",
            ) % { "quantity": params["quantity"] }
    #
    if event_type == ManageEvents.FULFILLMENT_CANCELED:
        # events----無し
        return pgettext_lazy(
            "product_stock message",
            "Fulfillment #%(fulfillment)s canceled by %(user_name)s",
            ) % { "fulfillment": params["composed_id"], "user_name": order_manage_event.responsible_person }
    #
    if event_type == ManageEvents.EMAIL_SENT:
        # events----無し
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(email_type)s email was sent to the customer " "(%(email)s)",
        ) % {
            "email_type": EMAIL_CHOICES[params["email_type"]],
            "email": params["email"],
        }

    raise ValueError("Not supported event type: %s" % (event_type))


# events----有
# events----無し
@register.simple_tag
def display_barter_manage_event(barter_manage_event: BarterManageEvent):
    event_type = barter_manage_event.type
    params = barter_manage_event.parameters

    if event_type == ManageEvents.NOTE_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sによりノートを追加した: %(note)s"
            % { "note": params["message"], "user_name": barter_manage_event.responsible_person },
            )

    if event_type == ManageEvents.DRAFT_CREATED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより項目を執行した",
        ) % {"user_name": barter_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_ADDED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を追加した"
        ) % {"user_name": barter_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_REMOVED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を削除した",
        ) % {"user_name": barter_manage_event.responsible_person}

    if event_type == ManageEvents.LEGALPERSON_CHANGED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(法人)を編集した",
            ) % { "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.SUPPLIER_CHANGED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(個人)を編集した",
            ) % { "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.PLACED_FROM_DRAFT:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより執行表を作成した",
            ) % { "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.SUPPLIER_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)s により取引先(個人)を追加した",
            ) % { "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.LEGALPERSON_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより取引先(法人)を追加した",
            ) % { "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.FULFILLMENT_FULFILLED_ITEMS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより項目を執行",
            ) % { "user_name": barter_manage_event.responsible_person }
    #
    if event_type == ManageEvents.SLIP_NUMBER_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより伝票番号を追加した"
        ) % {"user_name": barter_manage_event.responsible_person}

    # -------------------------------------------------------------------------------------------
    #
    if event_type == ManageEvents.FULFILLMENT_CANCELED:
        # events----無し
        return pgettext_lazy(
            "product_stock message",
            "Fulfillment #%(fulfillment)s canceled by %(user_name)s",
            ) % { "fulfillment": params["composed_id"],
                  "user_name": barter_manage_event.responsible_person }

    if event_type == ManageEvents.CANCELED:
        # events----無し
        return pgettext_lazy(
            "product_stock message related to an order", "Order was canceled"
            )

    if event_type == ManageEvents.OTHER:
        # events----無し
        return barter_manage_event.parameters["message"]

    if event_type == ManageEvents.FULFILLMENT_RESTOCKED_ITEMS:
        # events----無し
        return npgettext_lazy(
            "product_stock message related to an order",
            "We restocked %(quantity)d item",
            "We restocked %(quantity)d items",
            number="quantity",
            ) % { "quantity": params["quantity"] }

    if event_type == ManageEvents.EMAIL_SENT:
        # events----無し
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(email_type)s email was sent to the customer " "(%(email)s)",
            ) % {
                   "email_type": EMAIL_CHOICES[params["email_type"]],
                   "email": params["email"],
                   }

    raise ValueError("Not supported event type: %s" % (event_type))


# events----有
# events----無し
@register.simple_tag
def display_manual_inventory_manage_event(manual_inventory_manage_event: ManualInventoryManageEvent):
    event_type = manual_inventory_manage_event.type
    params = manual_inventory_manage_event.parameters

    if event_type == ManageEvents.NOTE_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sによりノートを追加した: %(note)s"
            % { "note": params["message"], "user_name": manual_inventory_manage_event.responsible_person },
            )

    if event_type == ManageEvents.DRAFT_CREATED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより執行表の下書きを作成した",
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_ADDED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を追加した"
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_REMOVED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品を削除した",
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.PLACED_FROM_DRAFT:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより下書きから商品ロック執行表を作成",
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.FULFILLMENT_LOCK:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品ロックを執行",
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.FULFILLMENT_UNLOCK:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより商品ロックの解除を執行",
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    if event_type == ManageEvents.SLIP_NUMBER_ADDED:
        # events----有
        return pgettext_lazy(
            "product_stock message related to an order",
            "%(user_name)sにより伝票番号を追加した"
        ) % {"user_name": manual_inventory_manage_event.responsible_person}

    #
    #
    # --------------------------------------------------------------------------------------------
    #
    if event_type == ManageEvents.OTHER:
        # events----無し
        return manual_inventory_manage_event.parameters["message"]

    if event_type == ManageEvents.FULFILLMENT_CANCELED:
        # events----無し
        return pgettext_lazy(
            "product_stock message",
            "Fulfillment #%(fulfillment)s canceled by %(user_name)s",
            ) % { "fulfillment": params["composed_id"], "user_name": manual_inventory_manage_event.responsible_person }

    if event_type == ManageEvents.EMAIL_SENT:
        # events----無し
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(email_type)s email was sent to the customer " "(%(email)s)",
        ) % {
            "email_type": EMAIL_CHOICES[params["email_type"]],
            "email": params["email"],
        }

    if event_type == ManageEvents.CANCELED:
        # events----無し
        return pgettext_lazy(
            "Dashboard message related to an order", "Order was canceled"
            )

    if event_type == ManageEvents.FULFILLMENT_RESTOCKED_ITEMS:
        # events----無し
        return npgettext_lazy(
            "Dashboard message related to an order",
            "We restocked %(quantity)d item",
            "We restocked %(quantity)d items",
            number="quantity",
            ) % { "quantity": params["quantity"] }

    raise ValueError("Not supported event type: %s" % (event_type))




@register.simple_tag
def display_store_to_store_manage_event(store_to_store_manage_event: StoreToStoreManageEvent):
    event_type = store_to_store_manage_event.type
    params = store_to_store_manage_event.parameters

    if event_type == ManageEvents.NOTE_ADDED:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)s によりノートを追加した: %(note)s"
            % { "note": params["message"], "user_name": store_to_store_manage_event.responsible_person },
            )

    if event_type == ManageEvents.DRAFT_CREATED:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより執行表の下書きを作成した",
        ) % {"user_name": store_to_store_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_ADDED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより商品を追加した"
        ) % {"user_name": store_to_store_manage_event.responsible_person}

    if event_type == ManageEvents.DRAFT_REMOVED_PRODUCTS:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより商品を削除した",
        ) % {"user_name": store_to_store_manage_event.responsible_person}

    if event_type == ManageEvents.TO_SHOP_ADDED:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより移動先の店舗を追加",
            ) % { "user_name": store_to_store_manage_event.responsible_person }

    if event_type == ManageEvents.PLACED_FROM_DRAFT:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより店舗間移動執行表の下書きを作成",
            ) % { "user_name": store_to_store_manage_event.responsible_person }

    if event_type == ManageEvents.FULFILLMENT_MOVEOUT:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより元店舗から転移迁出を執行",
            ) % { "user_name": store_to_store_manage_event.responsible_person }

    if event_type == ManageEvents.FULFILLMENT_MOVEIN:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(user_name)sにより新店舗へ転移迁入を執行",
            ) % { "user_name": store_to_store_manage_event.responsible_person }

    if event_type == ManageEvents.SLIP_NUMBER_ADDED:
        # events----有
        return pgettext_lazy(
            "Dashboard message related to an order", "%(user_name)s SLIP_NUMBER"
        ) % {"user_name": store_to_store_manage_event.responsible_person}
    #
    # ---------------------------------------------------------------------------------------------
    #
    if event_type == ManageEvents.OTHER:
        # events----無し
        return store_to_store_manage_event.parameters["message"]

    if event_type == ManageEvents.EMAIL_SENT:
        # events----無し
        return pgettext_lazy(
            "Dashboard message related to an order",
            "%(email_type)s email was sent to the customer " "(%(email)s)",
        ) % {
            "email_type": EMAIL_CHOICES[params["email_type"]],
            "email": params["email"],
        }

    if event_type == ManageEvents.FULFILLMENT_CANCELED:
        # events----無し
        return pgettext_lazy(
            "Dashboard message",
            "Fulfillment #%(fulfillment)s canceled by %(user_name)s",
            ) % { "fulfillment": params["composed_id"], "user_name": store_to_store_manage_event.responsible_person }

    if event_type == ManageEvents.CANCELED:
        # events----無し
        return pgettext_lazy(
            "Dashboard message related to an order", "Order was canceled"
            )

    if event_type == ManageEvents.FULFILLMENT_RESTOCKED_ITEMS:
        # events----無し
        return npgettext_lazy(
            "Dashboard message related to an order",
            "We restocked %(quantity)d item",
            "We restocked %(quantity)d items",
            number="quantity",
            ) % { "quantity": params["quantity"] }

    if event_type == ManageEvents.FULFILLMENT_FULFILLED_ITEMS:
        # events----無し
        return pgettext_lazy(
            "Dashboard message related to an order", "Fulfilled some items"
            )

    raise ValueError("Not supported event type: %s" % (event_type))
