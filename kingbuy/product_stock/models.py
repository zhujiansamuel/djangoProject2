from model_utils import FieldTracker
from uuid import uuid1, uuid4
from decimal import Decimal
from django.db.models import JSONField
from django_prices.templatetags import prices
from django.core.validators import MinValueValidator
from django.conf import settings
from django_prices.models import MoneyField
from django.utils.timezone import now
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.db import models
from django.db.models import Max

from kingbuy.core.utils.json_serializer import CustomJsonEncoder
from kingbuy.core.models import (
    ModelWithMetadata,
    )

from . import (
    ProductStockEventStatus,
    ProductStockManageStatus,
    FulfillmentStatus,
    InventoryStatus,
    InventoryFundsStatus,
    ManualInventoryType,
    ManualInventoryStatus,
    StoreToStoreType,
    StoreToStoreStatus,
    BarterManageType,
    BarterManageStatus,
    OrderManageType,
    OrderManageStatus,
    ManageEvents,
    AccountErrorCode,
    )

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number


def validate_possible_number(phone, country=None):
    phone_number = to_python( phone, country )
    if (
            phone_number
            and not is_possible_number( phone_number )
            or not phone_number.is_valid()
    ):
        raise ValidationError(
            _( "The phone number entered is not valid." ), code=AccountErrorCode.INVALID
            )
    return phone_number

class PossiblePhoneNumberField( PhoneNumberField ):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------





# permissions+
class E_mark( models.Model ):
    name = models.CharField( max_length=128 )
    slug = models.SlugField( max_length=128 )
    description = models.TextField( blank=True, null=True )

    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_E_mark",
                pgettext_lazy( "Permission description", "取引先(サイト)管理" ),
                ),
            )

    def __str__(self):
        return self.name

    def get_ajax_label(self):
        return self.name


class Address( models.Model ):
    legal_person_name = models.CharField( max_length=256, blank=True, null=True )
    first_name = models.CharField( max_length=256, blank=True, null=True )
    last_name = models.CharField( max_length=256, blank=True, null=True )
    company_name = models.CharField( max_length=256, blank=True, null=True )
    street_address_1 = models.CharField( max_length=256, blank=True, null=True )
    street_address_2 = models.CharField( max_length=256, blank=True, null=True )
    city = models.CharField( max_length=256, blank=True, null=True )
    city_area = models.CharField( max_length=128, blank=True, null=True )
    postal_code = models.CharField( max_length=20, blank=True, null=True )
    country = CountryField( default="JP" )
    country_area = models.CharField( max_length=128, blank=True, null=True )

    # phone = PossiblePhoneNumberField(blank=True, default="")
    phone = models.CharField( max_length=128, blank=True, null=True )
    tracker = FieldTracker()
    class Meta:
        ordering = ("pk",)
        app_label = "product_stock"

    @property
    def full_name(self):
        if self.legal_person_name:
            return self.legal_person_name
        return "%s %s" % (self.last_name, self.first_name)

    def __str__(self):
        if self.legal_person_name:
            return self.legal_person_name
        return self.full_name


# permissions+
class Suppliers( ModelWithMetadata ):
    email = models.EmailField( unique=True )
    first_name = models.CharField( max_length=256, blank=True )
    last_name = models.CharField( max_length=256, blank=True )
    address = models.ManyToManyField(
        Address, blank=True, related_name="suppliers_addresses"
        )
    # phone = PossiblePhoneNumberField( blank=True, default="" )
    phone = models.CharField( max_length=128, blank=True, null=True )
    first_name_kannji = models.CharField( max_length=256, blank=True, null=True )
    last_name_kannji = models.CharField( max_length=256, blank=True, null=True )
    age = models.CharField( max_length=6, blank=True, null=True )
    gender = models.CharField( max_length=256, blank=True, null=True )
    birth = models.DateField( blank=True, null=True )
    work = models.CharField( max_length=256, blank=True, null=True )
    note = models.TextField( null=True, blank=True )
    date_joined = models.DateTimeField( default=now, editable=False )
    tracker = FieldTracker()
    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_suppliers",
                pgettext_lazy( "Permission description", "取引先(個人)管理" ),
                ),
            )

    def get_full_name(self):
        if self.first_name or self.last_name:
            return ("%s %s(%s)" % (self.last_name, self.first_name, self.email)).strip()
        return self.email

    def __str__(self):
        return self.get_full_name()

    def get_ajax_label(self):
        if self.first_name or self.last_name:
            return "%s %s (%s)" % (self.last_name, self.first_name, self.email)
        return self.email


# permissions+
class LegalPerson( ModelWithMetadata ):
    company_name = models.CharField( max_length=256, blank=True )
    deputy = models.ManyToManyField(
        Suppliers, blank=True, related_name="legalperson_deputy"
        )
    address = models.ManyToManyField(
        Address, blank=True, related_name="legalpersons_addresses"
        )
    email = models.EmailField( unique=True )
    phone = models.CharField( max_length=128, blank=True, null=True )
    # phone = PossiblePhoneNumberField( blank=True, default="" )
    note = models.TextField( null=True, blank=True )
    fax = models.CharField( max_length=256, blank=True )
    homepage = models.CharField( max_length=256, blank=True )
    tracker = FieldTracker()
    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_legalperson",
                pgettext_lazy( "Permission description", "取引先(法人)管理" ),
                ),
            )

    def __str__(self):
        return "%s (%s)" % (self.company_name, self.email)

    def get_ajax_label(self):
        return "%s (%s)" % (self.company_name, self.email)


# permissions+
class Shops( models.Model ):
    name = models.CharField( max_length=128 )
    slug = models.SlugField( max_length=128 )
    addresses = models.ManyToManyField(
        Address, blank=True, related_name="shops_addresses"
        )
    description = models.TextField( blank=True, null=True )

    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_shopss",
                pgettext_lazy( "Permission description", "店舗別管理" ),
                ),
            )

    def __str__(self):
        return self.name

    def get_ajax_label(self):
        return self.name


# permissions+
class ProductStockStatus( models.Model ):
    name = models.CharField( max_length=128 )
    slug = models.SlugField( max_length=128 )
    description = models.TextField( blank=True, null=True )

    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_product_stock_status",
                pgettext_lazy( "Permission description", "商品状態管理" ),
                ),
            )

    def __str__(self):
        return self.name


class ExtraInformation( models.Model ):
    name = models.CharField( max_length=128 )
    slug = models.SlugField( max_length=128 )
    description = models.TextField( blank=True, null=True )

    class Meta:
        app_label = "product_stock"
        permissions = (
            (
                "manage_extrainformation",
                pgettext_lazy( "Permission description", "商品追加情報管理" ),
                ),
            )

    def __str__(self):
        return self.name


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------


# permissions+
class ProductStock( models.Model ):
    # 名称
    name = models.CharField( max_length=128, blank=True, null=True )
    # JAN
    jan_code = models.CharField( max_length=128, blank=True, null=True )

    last_change = models.DateTimeField( auto_now=True, null=True )

    description = models.CharField( max_length=128, blank=True, null=True )

    # images = models.ManyToManyField( "ProductStockImage",
    #                                  through="ProductObjectStockImage"
    #                                  )

    price_average_amount = models.DecimalField(
        default=0,
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
        )
    price_average = MoneyField( amount_field="price_average_amount",
                                currency_field="currency",
                                )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    quantity_temp = models.IntegerField( validators=[MinValueValidator( 0 )],
                                         default=Decimal( 0 )
                                         )
    quantity_all = models.IntegerField( validators=[MinValueValidator( 0 )],
                                        default=Decimal( 0 )
                                        )

    quantity = models.IntegerField( validators=[MinValueValidator( 0 )],
                                    default=Decimal( 0 )
                                    )
    quantity_no_imei = models.IntegerField( validators=[MinValueValidator( 0 )],
                                            default=Decimal( 0 )
                                            )

    quantity_available = models.IntegerField( validators=[MinValueValidator( 0 )],
                                              default=Decimal( 0 )
                                              )
    quantity_available_no_imei = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=Decimal( 0 )
        )

    quantity_locking = models.IntegerField( validators=[MinValueValidator( 0 )],
                                            default=Decimal( 0 )
                                            )
    quantity_locking_no_imei = models.IntegerField( validators=[MinValueValidator( 0 )],
                                                    default=Decimal( 0 )
                                                    )

    quantity_allocated = models.IntegerField( validators=[MinValueValidator( 0 )],
                                              default=Decimal( 0 )
                                              )
    quantity_allocated_no_imei = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=Decimal( 0 )
        )

    quantity_predestinate = models.IntegerField( validators=[MinValueValidator( 0 )],
                                                 default=Decimal( 0 )
                                                 )
    quantity_predestinate_no_imei = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=Decimal( 0 )
        )

    quantity_out_of_stock = models.IntegerField( validators=[MinValueValidator( 0 )],
                                                 default=Decimal( 0 )
                                                 )
    quantity_out_of_stock_no_imei = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=Decimal( 0 )
        )

    is_temp = models.BooleanField( default=True )

    tracker = FieldTracker()

    class Meta:
        app_label = "product_stock"
        ordering = ("name",)
        permissions = (
            (
                "manage_product_stock",
                pgettext_lazy( "Permission description", "商品類管理" ),
                ),
            (
                "change_product_stock",
                pgettext_lazy( "Permission description", "商品類編集" ),
                ),
            )

    def __repr__(self):
        class_ = type( self )
        return "<%s.%s(pk=%r, name=%r)>" % (
            class_.__module__,
            class_.__name__,
            self.pk,
            self.name,
            )

    def __str__(self):
        return self.name

    def __iter__(self):
        if not hasattr(self, "__product_object_stock"):
            setattr(self, "__product_object_stock", self.product_object_stock.all())
        return iter(getattr(self, "__product_object_stock"))

    def get_ajax_label(self, discounts=None):
        price = self.price_average
        if price is not None:
            return "%s, %s, %s" % (self.name, self.jan_code, prices.amount( price ))
        else:
            return "%s, %s" % (self.name, self.jan_code)

    def get_quantity_for_avarage(self):
        return int(self.quantity_available)+int(self.quantity_locking)+int(self.quantity_allocated)+\
               int( self.quantity_available_no_imei ) + int( self.quantity_locking_no_imei ) + int(self.quantity_allocated_no_imei)


# permissions+
class ProductObjectStock( models.Model ):
    # 唯一标识
    slug = models.SlugField( max_length=128, blank=True, null=True )
    sku = models.CharField( primary_key=False, max_length=255,
                            default=str( uuid4() ) + "-" + str( uuid1() )
                            )
    # sku =models.UUIDField( primary_key=False, auto_created=True, default=uuid4(), editable=False)
    imei_code = models.CharField( max_length=128, blank=True )
    product_stock = models.ForeignKey(
        ProductStock, related_name="product_object_stock", on_delete=models.CASCADE
        )

    create = models.DateTimeField( default=now, null=True )
    last_change = models.DateTimeField( auto_now=True, null=True )
    notion = models.CharField( max_length=128, blank=True, null=True, )

    price_average_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
        )
    price_average = MoneyField( amount_field="price_average_amount",
                                currency_field="currency"
                                )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    price_override_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
        )
    price_override = MoneyField(
        amount_field="price_override_amount", currency_field="currency"
        )

    extra_informations = models.ForeignKey( ExtraInformation,
                                            related_name="extra_information",
                                            on_delete=models.CASCADE, blank=True,
                                            null=True
                                            )

    manage_status = models.CharField( max_length=32,
                                      default=ProductStockManageStatus.OTHER,
                                      choices=ProductStockManageStatus.CHOICES,
                                      blank=True, null=True
                                      )
    status = models.ForeignKey( ProductStockStatus, related_name="productstockstatus",
                                on_delete=models.CASCADE, blank=True, null=True
                                )
    shops = models.ForeignKey( Shops, related_name="shops", on_delete=models.CASCADE,
                               blank=True, null=True
                               )
    is_select = models.BooleanField( default=False )
    is_allocate = models.BooleanField( default=False )
    is_lock = models.BooleanField( default=False )
    is_available_M = models.BooleanField( default=True )
    is_temp = models.BooleanField( default=True )
    is_out_of_stock = models.BooleanField( default=False )

    tracker = FieldTracker()

    def __repr__(self):
        class_ = type( self )
        return "<%s.%s(pk=%r, imei=%r)>" % (
            class_.__module__,
            class_.__name__,
            self.pk,
            self.imei_code,
            )

    def __str__(self):
        price = self.price_average
        if price is not None:
            return "%s, %s, %s (%s)" % (
                self.product_stock.name, self.imei_code, prices.amount( price ),
                self.shops)
        else:
            return "%s, %s (%s)" % (self.product_stock.name, self.imei_code, self.shops)

    class Meta:
        app_label = "product_stock"
        ordering = ("id",)
        permissions = (
            (
                "manage_product_object_stock",
                pgettext_lazy( "Permission description", "商品在庫管理" ),
                ),
            (
                "change_product_object_stock",
                pgettext_lazy( "Permission description", "商品在庫編集" ),
                ),
            )

    def save(self, *args, **kwargs):
        # do_something()
        super().save( *args, **kwargs )

    def get_ajax_label(self, discounts=None):
        price = self.price_average
        if price is not None:
            return "%s, %s, %s (%s)" % (
            self.product_stock.name, self.imei_code, prices.amount( price ), self.shops)
        else:
            return "%s, %s (%s)" % (self.product_stock.name, self.imei_code, self.shops)


# ---------------------------------------------------------
# ---------------------------------------------------------

class ProductStockChangeEvent( models.Model ):
    product_stock = models.ForeignKey(
        ProductStock, related_name="product_stock_change", on_delete=models.CASCADE
        )
    change_field = models.CharField(max_length=128, blank=True, null=True)
    changed_value = models.CharField( max_length=128, blank=True, null=True )
    old_value = models.CharField( max_length=128, blank=True, null=True )
    change_date = models.DateTimeField( default=now, null=True )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="ProductStockChangeEvent_responsible_person",
        on_delete=models.SET_NULL,
        )
    class Meta:
        app_label = "product_stock"
        ordering = ("change_date",)
        permissions = (
            (
                "manage_product_stock_change",
                pgettext_lazy( "Permission description", "商品類編集歴史を訪問" ),
                ),
            )

    def __str__(self):
        return "<JAN：%s, 項目：%s)>(%s->%s)" % (self.product_stock.jan_code,self.change_field,self.old_value,self.changed_value)

class ProductObjectStockChangeEvent( models.Model ):
    product_object_stock = models.ForeignKey(
        ProductObjectStock, related_name="product_object_stock_change", on_delete=models.CASCADE
        )
    change_field = models.CharField( max_length=128, blank=True, null=True )
    changed_value = models.CharField( max_length=128, blank=True, null=True )
    old_value = models.CharField( max_length=128, blank=True, null=True )
    current_value = models.CharField( max_length=128, blank=True, null=True )
    change_date = models.DateTimeField( default=now, null=True )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="ProductObjectStockChangeEvent_responsible_person",
        on_delete=models.SET_NULL,
        )
    class Meta:
        app_label = "product_stock"
        ordering = ("change_date",)
        permissions = (
            (
                "manage_product_object_stock_change",
                pgettext_lazy( "Permission description", "商品情報編集歴史を訪問" ),
                ),
            )
    def __str__(self):
        return "<JAN：%s,IMEI：%s, 項目：%s)>(%s->%s)" % (self.product_object_stock.product_stock.jan_code,self.product_object_stock.imei_code,self.change_field,self.old_value,self.changed_value)



# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------


class ManualInventoryManageQueryset( models.QuerySet ):
    def confirmed(self):
        """Return non-draft orders."""
        return self.exclude( manual_inventory_status=InventoryStatus.DRAFT )

    def drafts(self):
        """Return draft orders."""
        return self.filter( manual_inventory_status=InventoryStatus.DRAFT )


# permissions+
class ManualInventoryManage( models.Model ):
    token = models.CharField( max_length=36, unique=True, blank=True )
    management_numbers = models.CharField( max_length=255, unique=True,
                                           default=str( uuid1() )
                                           )
    confirm_file_id = models.CharField( max_length=16, blank=True )
    slip_number = models.CharField( max_length=16, blank=True )
    created = models.DateTimeField( default=now, editable=False )
    last_change = models.DateTimeField( default=now, editable=False )

    suppliers = models.ForeignKey(
        Suppliers,
        blank=True,
        null=True,
        related_name="manual_inventory_manage_suppliers",
        on_delete=models.SET_NULL,
        )
    legal_person = models.ForeignKey(
        LegalPerson,
        blank=True,
        null=True,
        related_name="manual_inventory_manage_suppliers",
        on_delete=models.SET_NULL,
        )

    e_market = models.ForeignKey(
        E_mark,
        blank=True,
        null=True,
        related_name="manual_inventory_manage_e_market",
        on_delete=models.SET_NULL,
        )


    manual_inventory_status = models.CharField(
        max_length=32, default=InventoryStatus.DRAFT,
        choices=InventoryStatus.CHOICES
        )
    funds_status = models.CharField(
        max_length=32, default=InventoryFundsStatus.UNDECIDED,
        choices=InventoryFundsStatus.CHOICES
        )

    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="ManualInventoryManage_responsible_person",
        on_delete=models.SET_NULL,
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    note = models.TextField( blank=True, default="" )
    total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        )
    total = MoneyField( amount_field="total_amount", currency_field="currency" )

    objects = ManualInventoryManageQueryset.as_manager()

    class Meta:
        ordering = ("-pk",)
        permissions = (
            (
                "manual_inventory_manage_permissions",
                pgettext_lazy( "Permission description", "マニュアル入庫出庫管理" ),
                ),
            (
                "manual_inventory_cancel_permissions",
                pgettext_lazy( "Permission description", "マニュアル入庫出庫取り消し" ),
                ),
            )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str( uuid1() )
        return super().save( *args, **kwargs )

    def __repr__(self):
        return "<ManualInventoryManage #%r>" % (self.id,)

    def __str__(self):
        return "#%d" % (self.id,)

    def __iter__(self):
        return iter( self.manual_inventory_manage_lines.all() )

    def get_absolute_url(self):
        return reverse( "ManualInventoryManage:details",
                        kwargs={ "token": self.token }
                        )

    def can_cancel(self):
        return self.manual_inventory_status not in { InventoryStatus.CANCELED,
                                                     InventoryStatus.DRAFT,
                                                     InventoryStatus.FULFILLED,
                                                     InventoryStatus.PARTIALLY_FULFILLED
                                                     }

    def is_draft(self):
        return self.manual_inventory_status == InventoryStatus.DRAFT

    def is_open(self):
        statuses = { InventoryStatus.UNFULFILLED, InventoryStatus.PARTIALLY_FULFILLED }
        return self.manual_inventory_status in statuses

    def get_total_quantity(self):
        return sum( [line.quantity for line in self] )

    #
    @property
    def quantity_fulfilled_LOCK(self):
        return sum( [line.quantity_fulfilled_LOCK for line in self] )

    @property
    def quantity_fulfilled_UNLOCK(self):
        return sum( [line.quantity_fulfilled_UNLOCK for line in self] )

    def is_locked(self):
        return self.quantity_fulfilled_LOCK == self.get_total_quantity()


class ManualInventoryManageLine( models.Model ):
    manual_inventory_type = models.CharField(
        max_length=32, default=ManualInventoryType.OTHER,
        choices=ManualInventoryType.CHOICES
        )
    manual_inventory_status = models.CharField(
        max_length=32, default=ManualInventoryStatus.OTHER,
        choices=ManualInventoryStatus.CHOICES
        )
    manual_inventory_manage = models.ForeignKey(
        ManualInventoryManage, related_name="manual_inventory_manage_lines",
        editable=False, on_delete=models.CASCADE
        )
    product_stock = models.ForeignKey(
        ProductStock,
        related_name="manual_inventory_manage_lines_product_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_object_stock = models.ForeignKey(
        ProductObjectStock,
        related_name="manual_inventory_manage_lines_product_object_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_stock_name = models.CharField( max_length=386 )
    product_stock_jan_code = models.CharField( max_length=386 )

    product_object_stock_name = models.CharField( max_length=255, default="",
                                                  blank=True
                                                  )
    product_object_stock_sku = models.CharField( max_length=255, default="",
                                                 blank=True
                                                 )

    quantity = models.IntegerField( validators=[MinValueValidator( 1 )] )
    quantity_fulfilled_LOCK = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    quantity_fulfilled_UNLOCK = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    unit_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        )
    unit_price = MoneyField(
        amount_field="unit_price_amount", currency_field="currency"
        )
    line_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
        )
    line_price = MoneyField(
        amount_field="line_price_amount", currency_field="currency"
        )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return (
            f"{self.product_stock_name} ({self.product_object_stock_name})"
            if self.product_object_stock_name
            else self.product_stock_name
        )

    def get_total(self):
        return self.unit_price * self.quantity

    @property
    def quantity_unfulfilled_LOCK(self):
        return self.quantity - self.quantity_fulfilled_LOCK

    @property
    def quantity_unfulfilled_UNLOCK(self):
        return self.quantity - self.quantity_fulfilled_UNLOCK


class ManualInventoryManageFulfillment_LOCK( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    manual_inventory_manage = models.ForeignKey(
        ManualInventoryManage, related_name="fulfillments_LOCK", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """
        Assign an auto incremented value as a fulfillment order.
        """
        if not self.pk:
            groups = self.manual_inventory_manage.fulfillments_LOCK.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.manual_inventory_manage.id, self.fulfillment_order)


class ManualInventoryManageFulfillmentLine_LOCK( models.Model ):
    manual_inventory_manage_line = models.ForeignKey(
        ManualInventoryManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        ManualInventoryManageFulfillment_LOCK, related_name="lines",
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class ManualInventoryManageFulfillment_UNLOCK( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    manual_inventory_manage = models.ForeignKey(
        ManualInventoryManage, related_name="fulfillments_UNLOCK", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.manual_inventory_manage.fulfillments_UNLOCK.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.manual_inventory_manage.id, self.fulfillment_order)


class ManualInventoryManageFulfillmentLine_UNLOCK( models.Model ):
    manual_inventory_manage_line = models.ForeignKey(
        ManualInventoryManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        ManualInventoryManageFulfillment_UNLOCK, related_name="lines",
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class ManualInventoryManageEvent( models.Model ):
    date = models.DateTimeField( default=now, editable=False )
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in ManageEvents.CHOICES
            ],
        )
    manual_inventory_manage = models.ForeignKey( ManualInventoryManage,
                                                 related_name="events",
                                                 on_delete=models.CASCADE
                                                 )
    parameters = JSONField( blank=True, default=dict, encoder=CustomJsonEncoder )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        )

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.responsible_person!r})"


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------


class StoreToStoreManageQueryset( models.QuerySet ):
    def confirmed(self):
        """Return non-draft orders."""
        return self.exclude( store_to_store_status=InventoryStatus.DRAFT )

    def drafts(self):
        """Return draft orders."""
        return self.filter( store_to_store_status=InventoryStatus.DRAFT )


# permissions+
class StoreToStoreManage( models.Model ):
    token = models.CharField( max_length=36, unique=True, blank=True )
    management_numbers = models.CharField( max_length=255, unique=True,
                                           default=str( uuid1() )
                                           )
    confirm_file_id = models.CharField( max_length=16, blank=True )
    slip_number = models.CharField( max_length=16, blank=True )
    created = models.DateTimeField( default=now, editable=False )
    last_change = models.DateTimeField( editable=False, auto_now=True )

    from_shop = models.ForeignKey(
        Shops,
        related_name="from_shop",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    to_shop = models.ForeignKey(
        Shops,
        related_name="to_shop",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )

    store_to_store_status = models.CharField(
        max_length=32, default=InventoryStatus.DRAFT,
        choices=InventoryStatus.CHOICES
        )
    funds_status = models.CharField(
        max_length=32, default=InventoryFundsStatus.UNDECIDED,
        choices=InventoryFundsStatus.CHOICES
        )

    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="StoreToStoreManage_responsible_person",
        on_delete=models.SET_NULL,
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    note = models.TextField( blank=True, default="" )
    objects = StoreToStoreManageQueryset.as_manager()

    class Meta:
        ordering = ("-pk",)
        permissions = (
            (
                "store_to_store_manage_permissions",
                pgettext_lazy( "Permission description", "店間転移迁入迁出管理" ),
                ),
            (
                "store_to_store_cancel_permissions",
                pgettext_lazy( "Permission description", "店間転移迁入迁出取り消し" ),
                ),
            )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str( uuid1() )
        return super().save( *args, **kwargs )

    def __repr__(self):
        return "<StoreToStoreManage #%r>" % (self.id,)

    def __str__(self):
        return "#%d" % (self.id,)

    def __iter__(self):
        return iter( self.store_to_store_manage_lines.all() )

    def get_absolute_url(self):
        return reverse( "ManualInventoryManage:details",
                        kwargs={ "token": self.token }
                        )

    def can_cancel(self):
        return self.store_to_store_status not in { InventoryStatus.CANCELED,
                                                   InventoryStatus.DRAFT,
                                                   InventoryStatus.FULFILLED,
                                                   InventoryStatus.PARTIALLY_FULFILLED }

    def is_draft(self):
        return self.store_to_store_status == InventoryStatus.DRAFT

    def is_open(self):
        statuses = { InventoryStatus.UNFULFILLED, InventoryStatus.PARTIALLY_FULFILLED }
        return self.store_to_store_status in statuses

    def get_total_quantity(self):
        return sum( [line.quantity for line in self] )

    #
    @property
    def quantity_fulfilled_MOVEOUT(self):
        return sum( [line.quantity_fulfilled_MOVEOUT for line in self] )

    @property
    def quantity_fulfilled_MOVEIN(self):
        return sum( [line.quantity_fulfilled_MOVEIN for line in self] )

    def is_moved_out(self):
        return self.quantity_fulfilled_MOVEOUT == self.get_total_quantity()


class StoreToStoreManageLine( models.Model ):
    store_to_store_type = models.CharField(
        max_length=32, default=StoreToStoreType.OTHER,
        choices=StoreToStoreType.CHOICES
        )
    store_to_store_status = models.CharField(
        max_length=32, default=StoreToStoreStatus.OTHER,
        choices=StoreToStoreStatus.CHOICES
        )
    store_to_store_manage = models.ForeignKey(
        StoreToStoreManage, related_name="store_to_store_manage_lines",
        editable=False, on_delete=models.CASCADE
        )
    product_stock = models.ForeignKey(
        ProductStock,
        related_name="store_to_store_manage_lines_product_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_object_stock = models.ForeignKey(
        ProductObjectStock,
        related_name="store_to_store_manage_lines_product_object_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_stock_name = models.CharField( max_length=386 )
    product_stock_jan_code = models.CharField( max_length=386 )

    product_object_stock_name = models.CharField( max_length=255, default="",
                                                  blank=True
                                                  )
    product_object_stock_sku = models.CharField( max_length=255, default="",
                                                 blank=True
                                                 )

    quantity = models.IntegerField( validators=[MinValueValidator( 1 )] )
    quantity_fulfilled_MOVEOUT = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    quantity_fulfilled_MOVEIN = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    unit_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        )
    unit_price = MoneyField(
        amount_field="unit_price_amount", currency_field="currency"
        )
    line_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
        )
    line_price = MoneyField(
        amount_field="line_price_amount", currency_field="currency"
        )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return (
            f"{self.product_stock_name} ({self.product_object_stock_name})"
            if self.product_object_stock_name
            else self.product_stock_name
        )

    def get_total(self):
        return self.unit_price * self.quantity

    @property
    def quantity_unfulfilled_MOVEOUT(self):
        return self.quantity - self.quantity_fulfilled_MOVEOUT

    @property
    def quantity_unfulfilled_MOVEIN(self):
        return self.quantity - self.quantity_fulfilled_MOVEIN


class StoreToStoreManageFulfillment_MOVEOUT( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    store_to_store_manage = models.ForeignKey(
        StoreToStoreManage, related_name="fulfillments_out", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment MOVEOUT #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.store_to_store_manage.fulfillments_out.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.store_to_store_manage.id, self.fulfillment_order)


class StoreToStoreManageFulfillmentLine_MOVEOUT( models.Model ):
    store_to_store_manage_line = models.ForeignKey(
        StoreToStoreManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        StoreToStoreManageFulfillment_MOVEOUT, related_name="lines",
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class StoreToStoreManageFulfillment_MOVEIN( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    store_to_store_manage = models.ForeignKey(
        StoreToStoreManage, related_name="fulfillments_in", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment MOVEIN #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.store_to_store_manage.fulfillments_in.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.store_to_store_manage.id, self.fulfillment_order)


class StoreToStoreManageFulfillmentLine_MOVEIN( models.Model ):
    store_to_store_manage_line = models.ForeignKey(
        StoreToStoreManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        StoreToStoreManageFulfillment_MOVEIN, related_name="lines",
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class StoreToStoreManageEvent( models.Model ):
    date = models.DateTimeField( default=now, editable=False )
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in ManageEvents.CHOICES
            ],
        )
    store_to_store_manage = models.ForeignKey( StoreToStoreManage,
                                               related_name="events",
                                               on_delete=models.CASCADE
                                               )
    parameters = JSONField( blank=True, default=dict, encoder=CustomJsonEncoder )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        )

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.responsible_person!r})"


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------


class BarterManageQueryset( models.QuerySet ):
    def confirmed(self):
        """Return non-draft orders."""
        return self.exclude( barter_status=InventoryStatus.DRAFT )

    def drafts(self):
        """Return draft orders."""
        return self.filter( barter_status=InventoryStatus.DRAFT )


# permissions
class BarterManage( models.Model ):
    token = models.CharField( max_length=36, unique=True, blank=True )
    management_numbers = models.CharField( max_length=255, unique=True,
                                           default=str( uuid1() )
                                           )
    confirm_file_id = models.CharField( max_length=16, blank=True )
    slip_number = models.CharField( max_length=16, blank=True )
    created = models.DateTimeField( default=now, editable=False )
    last_change = models.DateTimeField( editable=False, auto_now=True )

    suppliers = models.ForeignKey(
        Suppliers,
        blank=True,
        null=True,
        related_name="barter_manage_suppliers",
        on_delete=models.SET_NULL,
        )
    legal_person = models.ForeignKey(
        LegalPerson,
        blank=True,
        null=True,
        related_name="barter_manage_suppliers",
        on_delete=models.SET_NULL,
        )

    barter_status = models.CharField(
        max_length=32, default=InventoryStatus.DRAFT,
        choices=InventoryStatus.CHOICES
        )

    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="barter_manage_responsible_person",
        on_delete=models.SET_NULL,
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    note = models.TextField( blank=True, default="" )

    total_MOVEIN_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        )
    total_MOVEIN = MoneyField( amount_field="total_amount", currency_field="currency" )

    total_MOVEOUT_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        )
    total_MOVEOUT = MoneyField( amount_field="total_amount", currency_field="currency" )

    total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        )
    total = MoneyField( amount_field="total_amount", currency_field="currency" )

    objects = BarterManageQueryset.as_manager()

    class Meta:
        ordering = ("-pk",)
        permissions = (
            (
                "barter_manage_permissions",
                pgettext_lazy( "Permission description", "物々交換迁入迁出管理" ),
                ),
            (
                "barter_cancel_permissions",
                pgettext_lazy( "Permission description", "物々交換迁入迁出取り消し" ),
                ),

            )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str( uuid1() )
        return super().save( *args, **kwargs )

    def __repr__(self):
        return "<BarterManage #%r>" % (self.id,)

    def __str__(self):
        return "#%d" % (self.id,)

    def __iter__(self):
        return iter( self.barter_manage_lines.all() )

    def get_absolute_url(self):
        return reverse( "BarterManage:details",
                        kwargs={ "token": self.token }
                        )

    def can_cancel(self):
        return self.barter_status not in { InventoryStatus.CANCELED,
                                           InventoryStatus.DRAFT,
                                           InventoryStatus.FULFILLED,
                                           InventoryStatus.PARTIALLY_FULFILLED }

    def is_draft(self):
        return self.barter_status == InventoryStatus.DRAFT

    def is_open(self):
        statuses = { InventoryStatus.UNFULFILLED, InventoryStatus.PARTIALLY_FULFILLED }
        return self.barter_status in statuses

    def get_total_quantity(self):
        return sum( [line.quantity for line in self] )

    #
    @property
    def quantity_fulfilled(self):
        return sum( [line.quantity_fulfilled for line in self] )


class BarterManageLine( models.Model ):
    barter_manage_type = models.CharField(
        max_length=32, default=BarterManageType.OTHER,
        choices=BarterManageType.CHOICES
        )
    barter_manage_status = models.CharField(
        max_length=32, default=BarterManageStatus.OTHER,
        choices=BarterManageStatus.CHOICES
        )
    barter_manage = models.ForeignKey(
        BarterManage, related_name="barter_manage_lines",
        editable=False, on_delete=models.CASCADE
        )
    product_stock = models.ForeignKey(
        ProductStock,
        related_name="barter_manage_lines_product_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_object_stock = models.ForeignKey(
        ProductObjectStock,
        related_name="barter_manage_lines_product_object_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_stock_name = models.CharField( max_length=386 )
    product_stock_jan_code = models.CharField( max_length=386 )

    product_object_stock_name = models.CharField( max_length=255, default="",
                                                  blank=True
                                                  )
    product_object_stock_sku = models.CharField( max_length=255, default="",
                                                 blank=True
                                                 )

    quantity = models.IntegerField( validators=[MinValueValidator( 1 )] )
    quantity_fulfilled = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    unit_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        )
    unit_price = MoneyField(
        amount_field="unit_price_amount", currency_field="currency"
        )
    line_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
        )
    line_price = MoneyField(
        amount_field="line_price_amount", currency_field="currency"
        )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return (
            f"{self.product_stock_name} ({self.product_object_stock_name})"
            if self.product_object_stock_name
            else self.product_stock_name
        )

    def get_total(self):
        return self.unit_price * self.quantity

    @property
    def quantity_unfulfilled(self):
        return self.quantity - self.quantity_fulfilled


class BarterManageFulfillment( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    barter_manage = models.ForeignKey(
        BarterManage, related_name="fulfillments", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.barter_manage.fulfillments.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.barter_manage.id, self.fulfillment_order)


class BarterManageFulfillmentLine( models.Model ):
    barter_manage_line = models.ForeignKey(
        BarterManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        BarterManageFulfillment, related_name="lines", on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class BarterManageEvent( models.Model ):
    date = models.DateTimeField( default=now, editable=False )
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in ManageEvents.CHOICES
            ],
        )
    barter_manage = models.ForeignKey( BarterManage, related_name="events",
                                       on_delete=models.CASCADE
                                       )
    parameters = JSONField( blank=True, default=dict, encoder=CustomJsonEncoder )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        )

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.responsible_person!r})"


# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------


class OrderManageQueryset( models.QuerySet ):
    def confirmed(self):
        """Return non-draft orders."""
        return self.exclude( order_status=InventoryStatus.DRAFT )

    def drafts(self):
        """Return draft orders."""
        return self.filter( order_status=InventoryStatus.DRAFT )


# permissions+
class OrderManage( models.Model ):
    type_No = models.PositiveSmallIntegerField( default=2, null=True, blank=True )
    token = models.CharField( max_length=36, unique=True, blank=True )
    management_numbers = models.CharField( max_length=255, unique=False,
                                           primary_key=False,
                                           default=str( uuid1() )
                                           )
    confirm_file_id = models.CharField( max_length=16, blank=True )
    slip_number = models.CharField( max_length=16, blank=True )
    created = models.DateTimeField( default=now, editable=False )
    last_change = models.DateTimeField( editable=False, auto_now=True )

    suppliers = models.ForeignKey(
        Suppliers,
        blank=True,
        null=True,
        related_name="order_manage_suppliers",
        on_delete=models.SET_NULL,
        )
    legal_person = models.ForeignKey(
        LegalPerson,
        blank=True,
        null=True,
        related_name="order_manage_legal_person",
        on_delete=models.SET_NULL,
        )

    order_status = models.CharField(
        max_length=32, default=InventoryStatus.DRAFT,
        choices=InventoryStatus.CHOICES
        )
    funds_status = models.CharField(
        max_length=32, default=InventoryFundsStatus.UNDECIDED,
        choices=InventoryFundsStatus.CHOICES
        )

    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="order_manage_responsible_person",
        on_delete=models.SET_NULL,
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    note = models.TextField( blank=True, default="" )
    total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        )
    total = MoneyField( amount_field="total_amount", currency_field="currency" )

    total_gross_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    total_gross = MoneyField(
        amount_field="total_gross_amount", currency_field="currency"
    )

    objects = OrderManageQueryset.as_manager()

    class Meta:
        ordering = ("-pk",)
        permissions = (
            (
                "order_manage_permissions",
                pgettext_lazy( "Permission description", "注文入庫出庫管理" ),
                ),
            (
                "order_cancel_permissions",
                pgettext_lazy( "Permission description", "注文入庫出庫取り消し" ),
                ),

            )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str( uuid1() )
        return super().save( *args, **kwargs )

    def __repr__(self):
        return "<OrderManage #%r>" % (self.id,)

    def __str__(self):
        return "#%d" % (self.id,)

    def __iter__(self):
        return iter( self.order_manage_lines.all() )

    def get_absolute_url(self):
        return reverse( "OrderManage:details",
                        kwargs={ "token": self.token }
                        )

    def can_cancel(self):
        return self.order_status not in { InventoryStatus.CANCELED,
                                          InventoryStatus.DRAFT,
                                          InventoryStatus.FULFILLED,
                                          InventoryStatus.PARTIALLY_FULFILLED }

    def is_draft(self):
        return self.order_status == InventoryStatus.DRAFT

    def is_open(self):
        statuses = { InventoryStatus.UNFULFILLED, InventoryStatus.PARTIALLY_FULFILLED }
        return self.order_status in statuses

    def get_total_quantity(self):
        return sum( [line.quantity for line in self] )

    #
    @property
    def quantity_fulfilled(self):
        return sum( [line.quantity_fulfilled for line in self] )


class OrderManageLine( models.Model ):
    order_manage_type = models.CharField(
        max_length=32, default=OrderManageType.OTHER,
        choices=OrderManageType.CHOICES
        )
    order_manage_status = models.CharField(
        max_length=32, default=OrderManageStatus.OTHER,
        choices=OrderManageStatus.CHOICES
        )
    order_manage = models.ForeignKey(
        OrderManage, related_name="order_manage_lines",
        editable=False, on_delete=models.CASCADE
        )
    product_object_stock = models.ForeignKey(
        ProductObjectStock,
        related_name="order_manage_lines_product_object_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )
    product_stock = models.ForeignKey(
        ProductStock,
        related_name="order_manage_lines_product_stock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        )

    product_stock_name = models.CharField( max_length=386 )
    product_stock_jan_code = models.CharField( max_length=386 )

    product_object_stock_name = models.CharField( max_length=255, default="",
                                                  blank=True
                                                  )
    product_object_stock_sku = models.CharField( max_length=255, default="",
                                                 blank=True
                                                 )

    quantity = models.IntegerField( validators=[MinValueValidator( 1 )] )
    quantity_fulfilled = models.IntegerField(
        validators=[MinValueValidator( 0 )], default=0
        )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY,
        )
    unit_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        )
    unit_price = MoneyField(
        amount_field="unit_price_amount", currency_field="currency"
        )
    line_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
        )
    line_price = MoneyField(
        amount_field="line_price_amount", currency_field="currency"
        )

    # fulfillment_type = models.CharField(
    #     max_length=32, default=FulfillmentType.OTHER,
    #     choices=FulfillmentType.CHOICES
    #     )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return (
            f"{self.product_stock_name} (JAN:{self.product_stock_jan_code})"
        )

    def get_total(self):
        return self.unit_price * self.quantity

    @property
    def quantity_unfulfilled(self):
        return self.quantity - self.quantity_fulfilled


class OrderManageFulfillment( ModelWithMetadata ):
    fulfillment_order = models.PositiveIntegerField( editable=False )
    order_manage = models.ForeignKey(
        OrderManage, related_name="fulfillments", editable=False,
        on_delete=models.CASCADE
        )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
        )
    date = models.DateTimeField( default=now, editable=False )

    def __str__(self):
        return pgettext_lazy( "Fulfillment str", "Fulfillment #%s" ) % (
            self.composed_id,)

    def __iter__(self):
        return iter( self.lines.all() )

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.order_manage.fulfillments.all()
            existing_max = groups.aggregate( Max( "fulfillment_order" ) )
            existing_max = existing_max.get( "fulfillment_order__max" )
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save( *args, **kwargs )

    @property
    def composed_id(self):
        return "%s-%s" % (self.order_manage.id, self.fulfillment_order)


class OrderManageFulfillmentLine( models.Model ):
    order_manage_line = models.ForeignKey(
        OrderManageLine, related_name="+", on_delete=models.CASCADE
        )
    fulfillment = models.ForeignKey(
        OrderManageFulfillment, related_name="lines", on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()


class OrderManageEvent( models.Model ):
    date = models.DateTimeField( default=now, editable=False )
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in ManageEvents.CHOICES
            ],
        )
    order_manage = models.ForeignKey( OrderManage, related_name="events",
                                      on_delete=models.CASCADE
                                      )
    parameters = JSONField( blank=True, default=dict, encoder=CustomJsonEncoder )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        )

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.responsible_person!r})"

# ---------------------------------------------------------
# ---------------------------------------------------------

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------

# ---------------------------------------------------------
# ---------------------------------------------------------


class ProductStockEvent( models.Model ):
    date = models.DateTimeField( default=now, editable=False )
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in
            ProductStockEventStatus.CHOICES
            ],
        )
    product_object_stock = models.ForeignKey( ProductObjectStock,
                                              related_name="productobjectstockevent",
                                              on_delete=models.CASCADE
                                              )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        )

    class Meta:
        ordering = ("date",)



# ---------------------------------------------------------
# ---------------------------------------------------------
# class ProductStockImage( SortableModel ):
#     product_stock = models.ForeignKey(
#         ProductStock, related_name="images", on_delete=models.CASCADE
#         )
#     image = VersatileImageField( upload_to="product_stock", ppoi_field="ppoi",
#                                  blank=False
#                                  )
#     ppoi = PPOIField()
#     alt = models.CharField( max_length=128, blank=True )
#
#     class Meta:
#         ordering = ("sort_order",)
#         app_label = "product_stock"
#
#     def get_ordering_queryset(self):
#         return self.product_stock.images.all()

# class ProductObjectStockImage( models.Model ):
#     ProductObjectStock = models.ForeignKey(
#         "ProductObjectStock", related_name="product_object_stock_images",
#         on_delete=models.CASCADE
#         )
#     image = models.ForeignKey(
#         ProductStockImage, related_name="product_object_stock_images",
#         on_delete=models.CASCADE
#         )

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
