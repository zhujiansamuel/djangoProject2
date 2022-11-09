from django.utils.translation import pgettext_lazy
from enum import Enum


class AccountErrorCode(Enum):
    ACTIVATE_OWN_ACCOUNT = "activate_own_account"
    ACTIVATE_SUPERUSER_ACCOUNT = "activate_superuser_account"
    DEACTIVATE_OWN_ACCOUNT = "deactivate_own_account"
    DEACTIVATE_SUPERUSER_ACCOUNT = "deactivate_superuser_account"
    DELETE_NON_STAFF_USER = "delete_non_staff_user"
    DELETE_OWN_ACCOUNT = "delete_own_account"
    DELETE_STAFF_ACCOUNT = "delete_staff_account"
    DELETE_SUPERUSER_ACCOUNT = "delete_superuser_account"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    INVALID_PASSWORD = "invalid_password"
    NOT_FOUND = "not_found"
    PASSWORD_ENTIRELY_NUMERIC = "password_entirely_numeric"
    PASSWORD_TOO_COMMON = "password_too_common"
    PASSWORD_TOO_SHORT = "password_too_short"
    PASSWORD_TOO_SIMILAR = "password_too_similar"
    REQUIRED = "required"
    UNIQUE = "unique"

class ManageEvents:
    DRAFT_CREATED = "draft_created"
    DRAFT_ADDED_PRODUCTS = "draft_added_products_stock"
    DRAFT_REMOVED_PRODUCTS = "draft_removed_products_stock"



    PLACED_FROM_DRAFT = "placed_from_draft"

    SLIP_NUMBER_ADDED = "slip_number_added"
    SLIP_NUMBER_CHANGED = "slip_number_changed"

    CASH_RECEIPTED = "cash_receipted"
    CASH_RECEIPTING = "cash_receipting"
    CASH_RECEIPTING_CANCELED = "cash_receipt_canceled"
    CASH_RECEIPT_REFUNDED = "cash_receipt_refunded"

    CASH_DISBURSED = "cash_disbursed"
    CASH_DISBURSING = "cash_disbursing"
    CASH_DISBURSING_CANCELED = "cash_disburse_canceled"
    CASH_DISBURSE_REFUNDED = "cash_disburse_refunded"

    FULFILLMENT_CANCELED = "fulfillment_canceled"
    FULFILLMENT_FULFILLED_ITEMS = "fulfillment_fulfilled_items"
    FULFILLMENT_RESTOCKED_ITEMS = "fulfillment_restocked_items"

    FULFILLMENT_MOVEIN = "fulfillment_movein"
    FULFILLMENT_MOVEOUT = "fulfillment_moveout"

    FULFILLMENT_LOCK = "fulfillment_lock"
    FULFILLMENT_UNLOCK = "fulfillment_unlock"

    SUPPLIER_ADDED = "supplier_added"
    SUPPLIER_CHANGED = "supplier_changed"
    LEGALPERSON_ADDED = "legalperson_added"
    LEGALPERSON_CHANGED = "legalperson_changed"

    TO_SHOP_ADDED = "to_shop_added"
    TO_SHOP_CHANGED = "to_shop_changed"

    EMAIL_SENT = "email_sent"
    NOTE_ADDED = "note_added"
    CANCELED = "canceled"
    OTHER = "other"

    CHOICES = [
        (
            DRAFT_CREATED,
            pgettext_lazy(
                "Event from a staff user that created a draft order",
                "The draft manage was created",
                ),
            ),
        (
            DRAFT_ADDED_PRODUCTS,
            pgettext_lazy(
                "Event from a staff user that added products to a draft order",
                "Some products were added to the draft manage",
                ),
            ),
        (
            DRAFT_REMOVED_PRODUCTS,
            pgettext_lazy(
                "Event from a staff user that removed products from a draft order",
                "Some products were removed from the draft manage",
                ),
            ),

        (
            PLACED_FROM_DRAFT,
            pgettext_lazy(
                "Event from a staff user that placed a draft order",
                "The draft manage was placed",
                ),
            ),
        (
            SLIP_NUMBER_ADDED,
            pgettext_lazy(
                "Event that added a slip_number to an order",
                "A slip_number was added to an manage",
                ),
            ),
        (
            SLIP_NUMBER_CHANGED,
            pgettext_lazy(
                "Event that added a slip_number to an order",
                "A slip_number was changed to an manage",
                ),
            ),

        (CASH_RECEIPTED,pgettext_lazy("cash_receipted","cash_receipted", ),),
        (CASH_RECEIPTING, pgettext_lazy( "CASH_RECEIPTING", "CASH_RECEIPTING", ),),
        (CASH_RECEIPTING_CANCELED, pgettext_lazy( "CASH_RECEIPTING_CANCELED", "CASH_RECEIPTING_CANCELED", ),),
        (CASH_RECEIPT_REFUNDED, pgettext_lazy( "CASH_RECEIPT_REFUNDED", "CASH_RECEIPT_REFUNDED", ),),
        (CASH_DISBURSED, pgettext_lazy( "CASH_DISBURSED", "CASH_DISBURSED", ),),
        (CASH_DISBURSING, pgettext_lazy( "CASH_DISBURSING", "CASH_DISBURSING", ),),
        (CASH_DISBURSING_CANCELED, pgettext_lazy( "CASH_DISBURSING_CANCELED", "CASH_DISBURSING_CANCELED", ),),
        (CASH_DISBURSE_REFUNDED, pgettext_lazy( "CASH_DISBURSE_REFUNDED", "CASH_DISBURSE_REFUNDED", ),),
        (
            FULFILLMENT_CANCELED,
            pgettext_lazy(
                "Event from a staff user that canceled a fulfillment",
                "A fulfillment was canceled",
                ),
            ),
        (
            FULFILLMENT_RESTOCKED_ITEMS,
            pgettext_lazy(
                "Event from a staff user that restocked the items that were used "
                "for a fulfillment",
                "The items of the fulfillment were restocked",
                ),
            ),
        (
            FULFILLMENT_FULFILLED_ITEMS,
            pgettext_lazy(
                "Event from a staff user that fulfilled some items",
                "Some items were fulfilled",
                ),
            ),
        (
            EMAIL_SENT,
            pgettext_lazy(
                "Event generated from a user action that led to a " "email being sent",
                "The email was sent",
                ),
            ),
        (
            NOTE_ADDED,
            pgettext_lazy(
                "Event from an user that added a note to an order",
                "A note was added to the order",
                ),
            ),

        (
            CANCELED,
            pgettext_lazy(
                "Event from a staff user that canceled an order",
                "The order was canceled",
                ),
            ),
        (
            OTHER,
            pgettext_lazy(
                "An other type of order event containing a message",
                "An unknown order event containing a message",
                ),
            ),
        (
            SUPPLIER_ADDED, "supplier_added"

            ),
        (
            LEGALPERSON_ADDED, "legalperson_added"

            ),
        (
            TO_SHOP_ADDED, "to_shop_added"
            ),
        ]


class FulfillmentType:
    PRODUCTOBJECT = "product-object"
    PRODUCT = "product"
    PRODUCTOBJECTNOIEMI = "product-object-no-iemi"
    OTHER = "OTHER"
    CHOICES = [
        (
            PRODUCTOBJECT,
            pgettext_lazy(
                "product-object",
                "product-object",
            ),
        ),
        (
            PRODUCT,
            pgettext_lazy(
                "product",
                "product",
            ),
        ),
        (
            PRODUCTOBJECTNOIEMI,
            pgettext_lazy(
                "product-object-no-iemi",
                "product-object-no-iemi",
                ),
            ),
        (
            OTHER,
            pgettext_lazy(
                "other",
                "other",
                ),
            ),
    ]


class FulfillmentStatus:
    FULFILLED = "執行"
    CANCELED = "取消"
    CHOICES = [
        (
            FULFILLED,
            pgettext_lazy(
                "fulfilled",
                "執行",
            ),
        ),
        (
            CANCELED,
            pgettext_lazy(
                "canceled",
                "取消",
            ),
        ),
    ]


class InventoryFundsStatus:
    NOT_CASH_RECEIPT = "未入金"
    CASH_RECEIPTED = "入金済"
    CASH_RECEIPTING = "入金予定"
    NOT_CASH_DISBURSE = "未出金"
    CASH_DISBURSED = "出金済"
    CASH_DISBURSING = "出金予定"
    CANCELED = "取消"
    UNDECIDED = "未定"
    OTHER = "その他"

    CHOICES = [
        (
            NOT_CASH_RECEIPT,
            pgettext_lazy(
                "NOT_CASH_RECEIPT",
                "未入金",
                ),
            ),
        (
            CASH_RECEIPTED,
            pgettext_lazy(
                "CASH_RECEIPTED", "入金済"
                ),
            ),
        (
            CASH_RECEIPTING,
            pgettext_lazy(
                "CASH_RECEIPTING",
                "入金予定",
                ),
            ),
        (
            NOT_CASH_DISBURSE,
            pgettext_lazy(
                "NOT_CASH_DISBURSE", "未出金"
                ),
            ),
        (
            CASH_DISBURSED,
            pgettext_lazy( "CASH_DISBURSED", "出金済" ),
            ),
        (
            CASH_DISBURSING,
            pgettext_lazy( "CASH_DISBURSING", "出金予定" ),
            ),
        (
            CANCELED,
            pgettext_lazy( "Canceled", "取消" ),
            ),
        (
            OTHER,
            pgettext_lazy( "OTHER", "その他" ),
            ),
        (
            UNDECIDED,
            pgettext_lazy( "UNDECIDED", "未定" ),
            ),

        ]


class InventoryStatus:
    DRAFT = "下書き"
    ON_HOLD = "保留"
    UNFULFILLED = "未執行"
    PARTIALLY_FULFILLED = "一部執行済"
    FULFILLED = "執行済"
    CANCELED = "取消"
    CHOICES = [
        (
            DRAFT,
            pgettext_lazy(
                "draft",
                "下書き",
                ),
            ),
        (
            ON_HOLD,
            pgettext_lazy(
                "ON_HOLD",
                "保留",
                ),
            ),
        (
            UNFULFILLED,
            pgettext_lazy(
                "Unfulfilled", "未執行"
                ),
            ),
        (
            PARTIALLY_FULFILLED,
            pgettext_lazy(
                "Partially fulfilled",
                "一部執行済",
                ),
            ),
        (
            FULFILLED,
            pgettext_lazy(
                "Fulfilled", "執行済"
                ),
            ),
        (
            CANCELED,
            pgettext_lazy( "Canceled", "取消" ),
            ),
        ]


class ManualInventoryType:
    LOCK = "ロック"
    UNLOCK = "ロック解除"
    OTHER = "その他"
    CHOICES = [
        (LOCK, pgettext_lazy( "STORAGE", "ロック", ),),
        (UNLOCK, pgettext_lazy( "DELIVERY", "ロック解除", ),),
        (OTHER, pgettext_lazy( "OTHER", "その他", ),),
        ]

class ManualInventoryStatus:
    MANUAL_LOCK_PREDESTINATE = "ロック予定"
    MANUAL_LOCK = "ロック済"
    MANUAL_UNLOCK = "ロック解除済"
    OTHER = "その他"
    CHOICES = [
        (MANUAL_LOCK_PREDESTINATE, pgettext_lazy( "ロック予定", "ロック予定", ),),
        (MANUAL_LOCK, pgettext_lazy( "ロック済", "ロック済", ),),
        (MANUAL_UNLOCK, pgettext_lazy( "ロック解除済", "ロック解除済", ),),
        (OTHER, pgettext_lazy( "other", "その他", ),),
        ]


class StoreToStoreType:
    MOVEIN = "転移迁入"
    MOVEOUT = "転移迁出"
    OTHER = "その他"
    CHOICES = [
        (MOVEIN, pgettext_lazy( "MOVEIN", "転移迁入", ),),
        (MOVEOUT, pgettext_lazy( "MOVEOUT", "転移迁出", ),),
        (OTHER, pgettext_lazy( "OTHER", "その他", ),),
        ]
class StoreToStoreStatus:
    # 店间移动移出预定
    STORE_MOVE_OUT_PREDESTINATE = "転移迁出予定"
    # 店间移动移出
    STORE_TO_STORE_MOVE_OUT = "転移迁出済"
    # 店间移动移入预定
    STORE_MOVE_IN_PREDESTINATE = "転移迁入予定"
    # 店间移动移入
    STORE_TO_STORE_MOVE_IN = "転移迁入済"
    # other
    OTHER = "その他"
    CHOICES = [
        (STORE_MOVE_OUT_PREDESTINATE, pgettext_lazy( "店间移动移出预定", "転移迁出予定", ),),
        (STORE_TO_STORE_MOVE_OUT, pgettext_lazy( "店间移动移出", "転移迁出済", ),),
        (STORE_MOVE_IN_PREDESTINATE, pgettext_lazy( "店间移动移入预定", "転移迁入予定", ),),
        (STORE_TO_STORE_MOVE_IN, pgettext_lazy( "店间移动移入", "転移迁入済", ),),
        (OTHER, pgettext_lazy( "other", "その他", ),),
        ]


class BarterManageType:
    MOVEIN = "物々交換迁入"
    MOVEOUT = "物々交換迁出"
    OTHER = "その他"
    CHOICES = [
        (MOVEIN, pgettext_lazy( "MOVEIN", "物々交換迁入", ),),
        (MOVEOUT, pgettext_lazy( "MOVEOUT", "物々交換迁出", ),),
        (OTHER, pgettext_lazy( "OTHER", "その他", ),),
        ]
class BarterManageStatus:
    BARTER_MOVE_OUT_PREDESTINATE = "物々交換迁出予定"
    BARTER_MOVE_OUT = "物々交換迁出済"
    BARTER_MOVE_IN_PREDESTINATE = "物々交換迁入予定"
    BARTER_MOVE_IN = "物々交換迁入済"
    OTHER = "その他r"
    CHOICES = [
        (BARTER_MOVE_OUT_PREDESTINATE, pgettext_lazy( "物换物移出预定", "物々交換迁出予定", ),),
        (BARTER_MOVE_OUT, pgettext_lazy( "物换物移出", "物々交換迁出済", ),),
        (BARTER_MOVE_IN_PREDESTINATE, pgettext_lazy( "物换物移入预定", "物々交換迁入予定", ),),
        (BARTER_MOVE_IN, pgettext_lazy( "物换物移入", "物々交換迁入済", ),),
        (OTHER, pgettext_lazy( "other", "その他", ),),
        ]


class OrderManageType:
    STORAGE = "注文入庫"
    DELIVERY = "注文出庫"
    OTHER = "その他"
    CHOICES = [
        (STORAGE, pgettext_lazy( "STORAGE", "注文入庫", ),),
        (DELIVERY, pgettext_lazy( "DELIVERY", "注文出庫", ),),
        (OTHER, pgettext_lazy( "OTHER", "その他", ),),
        ]
class OrderManageStatus:
    # 订单入库预定
    ORDER_STORAGE_PREDESTINATE = "注文入庫予定"
    # 订单入库
    ORDER_STORAGE = "注文入庫済"
    # 订单出库预定
    ORDER_DELIVERY_PREDESTINATE = "注文出庫予定"
    # 订单出库
    ORDER_DELIVERY = "注文出庫済"
    # other
    OTHER = "その他"
    CHOICES = [
        (ORDER_STORAGE_PREDESTINATE, pgettext_lazy( "订单入库预定", "注文入庫予定", ),),
        (ORDER_STORAGE, pgettext_lazy( "订单入库", "注文入庫済", ),),

        (ORDER_DELIVERY_PREDESTINATE, pgettext_lazy( "订单出库预定", "注文出庫予定", ),),
        (ORDER_DELIVERY, pgettext_lazy( "订单出库", "注文出庫済", ),),

        (OTHER, pgettext_lazy( "other", "その他", ),),
        ]


class ProductStockManageStatus:
    # 手动入库预定
    MANUAL_LOCK_PREDESTINATE = "ロック予定"
    # 手动入库
    MANUAL_LOCK = "ロック済"

    # 订单入库预定
    ORDER_STORAGE_PREDESTINATE = "注文入庫予定"
    # 订单入库
    ORDER_STORAGE = "注文入庫済"

    # 店间移动移出预定
    STORE_MOVE_OUT_PREDESTINATE = "転移迁出予定"
    # 店间移动移出
    STORE_TO_STORE_MOVE_OUT = "転移迁出済"

    # 店间移动移入预定
    STORE_MOVE_IN_PREDESTINATE = "転移迁入予定"
    # 店间移动移入
    STORE_TO_STORE_MOVE_IN = "転移迁入済"


    MANUAL_UNLOCK = "ロック解除済"

    # 订单出库预定
    ORDER_DELIVERY_PREDESTINATE = "注文出庫予定"
    # 订单出库
    ORDER_DELIVERY = "注文出庫済"

    # 物换物移出预定
    BARTER_MOVE_OUT_PREDESTINATE = "物々交換迁出予定"
    # 物换物移出
    BARTER_MOVE_OUT = "物々交換迁出済"

    # 物换物移入预定
    BARTER_MOVE_IN_PREDESTINATE = "物々交換迁入予定"
    # 物换物移入
    BARTER_MOVE_IN = "物々交換迁入済"

    # 商品信息变更
    PRODUCT_STOCK_INFO_CHANGE = "商品情報変更"
    # other
    OTHER = "その他"

    DELETE = "delete"

    CHOICES = [
        (MANUAL_LOCK_PREDESTINATE, pgettext_lazy( "ロック预定", "ロック予定", ),),
        (MANUAL_LOCK, pgettext_lazy( "ロック", "ロック済", ),),

        (ORDER_STORAGE_PREDESTINATE, pgettext_lazy( "订单入库预定", "注文入庫予定", ),),
        (ORDER_STORAGE, pgettext_lazy( "订单入库", "注文入庫済", ),),

        (STORE_MOVE_OUT_PREDESTINATE, pgettext_lazy( "店间移动移出预定", "転移迁出予定", ),),
        (STORE_TO_STORE_MOVE_OUT, pgettext_lazy( "店间移动移出", "転移迁出済", ),),

        (STORE_MOVE_IN_PREDESTINATE, pgettext_lazy( "店间移动移入预定", "転移迁入予定", ),),
        (STORE_TO_STORE_MOVE_IN, pgettext_lazy( "店间移动移入", "転移迁入済", ),),

        (MANUAL_UNLOCK, pgettext_lazy( "ロック解除済", "ロック解除済", ),),

        (ORDER_DELIVERY_PREDESTINATE, pgettext_lazy( "订单出库预定", "注文出庫予定", ),),
        (ORDER_DELIVERY, pgettext_lazy( "订单出库", "注文出庫済", ),),

        (BARTER_MOVE_OUT_PREDESTINATE, pgettext_lazy( "物换物移出预定", "物々交換迁出予定", ),),
        (BARTER_MOVE_OUT, pgettext_lazy( "物换物移出", "物々交換迁出済", ),),

        (BARTER_MOVE_IN_PREDESTINATE, pgettext_lazy( "物换物移入预定", "物々交換迁入予定", ),),
        (BARTER_MOVE_IN, pgettext_lazy( "物换物移入", "物々交換迁入済", ),),

        (OTHER, pgettext_lazy( "other", "その他", ),),
        (PRODUCT_STOCK_INFO_CHANGE, pgettext_lazy( "商品信息变更", "商品情報変更", ),),

        ]
class ProductStockEventStatus:
    MANUAL_LOCK_PREDESTINATE = "ロック予定"
    # 手动入库
    MANUAL_LOCK = "ロック済"

    # 订单入库预定
    ORDER_STORAGE_PREDESTINATE = "注文入庫予定"
    # 订单入库
    ORDER_STORAGE = "注文入庫済"

    # 店间移动移出预定
    STORE_MOVE_OUT_PREDESTINATE = "転移迁出予定"
    # 店间移动移出
    STORE_TO_STORE_MOVE_OUT = "転移迁出済"

    # 店间移动移入预定
    STORE_MOVE_IN_PREDESTINATE = "転移迁入予定"
    # 店间移动移入
    STORE_TO_STORE_MOVE_IN = "転移迁入済"


    MANUAL_UNLOCK = "ロック解除済"

    # 订单出库预定
    ORDER_DELIVERY_PREDESTINATE = "注文出庫予定"
    # 订单出库
    ORDER_DELIVERY = "注文出庫済"

    # 物换物移出预定
    BARTER_MOVE_OUT_PREDESTINATE = "物々交換迁出予定"
    # 物换物移出
    BARTER_MOVE_OUT = "物々交換迁出済"

    # 物换物移入预定
    BARTER_MOVE_IN_PREDESTINATE = "物々交換迁入予定"
    # 物换物移入
    BARTER_MOVE_IN = "物々交換迁入済"

    # 商品信息变更
    PRODUCT_STOCK_INFO_CHANGE = "商品情報変更"
    # other
    OTHER = "その他"

    CHOICES = [
        (MANUAL_LOCK_PREDESTINATE, pgettext_lazy( "ロック预定", "ロック予定", ),),
        (MANUAL_LOCK, pgettext_lazy( "ロック", "ロック済", ),),

        (ORDER_STORAGE_PREDESTINATE, pgettext_lazy( "订单入库预定", "注文入庫予定", ),),
        (ORDER_STORAGE, pgettext_lazy( "订单入库", "注文入庫済", ),),

        (STORE_MOVE_OUT_PREDESTINATE, pgettext_lazy( "店间移动移出预定", "転移迁出予定", ),),
        (STORE_TO_STORE_MOVE_OUT, pgettext_lazy( "店间移动移出", "転移迁出済", ),),

        (STORE_MOVE_IN_PREDESTINATE, pgettext_lazy( "店间移动移入预定", "転移迁入予定", ),),
        (STORE_TO_STORE_MOVE_IN, pgettext_lazy( "店间移动移入", "転移迁入済", ),),

        (MANUAL_UNLOCK, pgettext_lazy( "ロック解除済", "ロック解除済", ),),

        (ORDER_DELIVERY_PREDESTINATE, pgettext_lazy( "订单出库预定", "注文出庫予定", ),),
        (ORDER_DELIVERY, pgettext_lazy( "订单出库", "マニュアル出庫済", ),),

        (BARTER_MOVE_OUT_PREDESTINATE, pgettext_lazy( "物换物移出预定", "物々交換迁出予定", ),),
        (BARTER_MOVE_OUT, pgettext_lazy( "物换物移出", "物々交換迁出済", ),),

        (BARTER_MOVE_IN_PREDESTINATE, pgettext_lazy( "物换物移入预定", "物々交換迁入予定", ),),
        (BARTER_MOVE_IN, pgettext_lazy( "物换物移入", "物々交換迁入済", ),),

        (OTHER, pgettext_lazy( "other", "その他", ),),
        (PRODUCT_STOCK_INFO_CHANGE, pgettext_lazy( "商品信息变更", "商品情報変更", ),),

        ]


class ManageErrorCode(Enum):
    CANNOT_CANCEL_FULFILLMENT = "cannot_cancel_fulfillment"
    CANNOT_CANCEL_ORDER = "cannot_cancel_order"
    CANNOT_DELETE = "cannot_delete"
    CANNOT_REFUND = "cannot_refund"
    CAPTURE_INACTIVE_PAYMENT = "capture_inactive_payment"
    NOT_EDITABLE = "not_editable"
    FULFILL_ORDER_LINE = "fulfill_order_line"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    ORDER_NO_SHIPPING_ADDRESS = "order_no_shipping_address"
    PAYMENT_ERROR = "payment_error"
    PAYMENT_MISSING = "payment_missing"
    REQUIRED = "required"
    SHIPPING_METHOD_NOT_APPLICABLE = "shipping_method_not_applicable"
    SHIPPING_METHOD_REQUIRED = "shipping_method_required"
    UNIQUE = "unique"
    VOID_INACTIVE_PAYMENT = "void_inactive_payment"
    ZERO_QUANTITY = "zero_quantity"

