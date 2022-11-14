import bleach
import uuid
import os
from django import forms

from django.core.validators import MinValueValidator
from django.urls import reverse_lazy
from django.conf import settings
from django.db import transaction
from django_prices.forms import MoneyField
from django.utils.translation import npgettext_lazy
from kingbuy.core.forms import (
    MoneyModelForm,
    AjaxSelect2ChoiceField,
    )

from django.utils.translation import pgettext_lazy
from django.utils.text import slugify


from kingbuy.core.taxes import zero_money


from kingbuy.core.widgets import RichTextEditorWidget
from ..product_stock.models import (
    E_mark,
    Suppliers,
    LegalPerson,
    Shops,
    OrderManage,
    ManualInventoryManage,
    StoreToStoreManage,
    BarterManage,
    ProductStockStatus,
    ExtraInformation,
    ProductStock,
    ProductObjectStock,
    OrderManageFulfillment,
    OrderManageFulfillmentLine,
    BarterManageFulfillment,
    BarterManageFulfillmentLine,
    StoreToStoreManageFulfillment_MOVEOUT,
    StoreToStoreManageFulfillmentLine_MOVEOUT,
    StoreToStoreManageFulfillment_MOVEIN,
    StoreToStoreManageFulfillmentLine_MOVEIN,
    ManualInventoryManageFulfillment_LOCK,
    ManualInventoryManageFulfillment_UNLOCK,
    ManualInventoryManageFulfillmentLine_LOCK,
    ManualInventoryManageFulfillmentLine_UNLOCK,

    # ProductStockImage,
    # ProductObjectStockImage,
    )

from ..product_stock import (
    # emails,
    InventoryStatus,
    )
from ..product_stock.utils import (
    fulfill_order_line,
    fulfill_store_MOVEOUT,
    fulfill_store_MOVEIN,
    fulfill_manual_inventory_LOCK,
    fulfill_manual_inventory_UNLOCK,
    log_product_stock_changed,
    log_product_object_stock_changed,
    )


# ----------------------------------------------------------------------------------------
class QuantityField( forms.IntegerField ):
    """A specialized integer field with initial quantity and min/max values."""

    def __init__(self, **kwargs):
        super().__init__(
            min_value=0,
            max_value=settings.MAX_CHECKOUT_LINE_QUANTITY,
            initial=1,
            **kwargs,
            )


def make_money_field():
    return MoneyField(
        available_currencies=settings.AVAILABLE_CURRENCIES,
        min_values=[zero_money()],
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        required=False,
        )


class RichTextField( forms.CharField ):
    """A field for rich text editor, providing backend sanitization."""

    widget = RichTextEditorWidget

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )
        self.help_text = pgettext_lazy(
            "Help text in rich-text editor field",
            "Select text to enable text-formatting tools.",
            )

    def to_python(self, value):
        tags = settings.ALLOWED_TAGS or bleach.ALLOWED_TAGS
        attributes = settings.ALLOWED_ATTRIBUTES or bleach.ALLOWED_ATTRIBUTES
        styles = settings.ALLOWED_STYLES or bleach.ALLOWED_STYLES
        value = super().to_python( value )
        value = bleach.clean( value, tags=tags, attributes=attributes, styles=styles )
        return value

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class OrderManageSlipNumberForm(forms.ModelForm):
    slip_number = forms.CharField(
        label=pgettext_lazy("Order_slip_number", "伝票番号"), widget=forms.Textarea()
    )
    class Meta:
        model = OrderManage
        fields = ["slip_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return self.cleaned_data

    def save(self):
        super().save()
        if self.cleaned_data.get( "slip_number" ):
            self.instance.slip_number=self.cleaned_data.get("slip_number")
        self.instance.save( update_fields=["slip_number"] )
        return self.instance


class BarterManageSlipNumberForm(forms.ModelForm):
    slip_number = forms.CharField(
        label=pgettext_lazy("Barter_slip_number", "伝票番号"), widget=forms.Textarea()
    )
    class Meta:
        model = BarterManage
        fields = ["slip_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return self.cleaned_data

    def save(self):
        super().save()
        if self.cleaned_data.get( "slip_number" ):
            self.instance.slip_number=self.cleaned_data.get("slip_number")
        self.instance.save( update_fields=["slip_number"] )
        return self.instance


class StoreToStoreManageSlipNumberForm(forms.ModelForm):
    slip_number = forms.CharField(
        label=pgettext_lazy("Barter_slip_number", "伝票番号"), widget=forms.Textarea()
    )
    class Meta:
        model = StoreToStoreManage
        fields = ["slip_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return self.cleaned_data

    def save(self):
        super().save()
        if self.cleaned_data.get( "slip_number" ):
            self.instance.slip_number=self.cleaned_data.get("slip_number")
        self.instance.save( update_fields=["slip_number"] )
        return self.instance



class BulkChangeForm(forms.Form):
    shops = forms.ModelChoiceField(
        queryset=Shops.objects.all(),
        label=pgettext_lazy( "Shops", "店舗別" ),
        required=True
        )
    extra_informations = forms.ModelChoiceField(
        queryset=ExtraInformation.objects.all(),
        label=pgettext_lazy( "ExtraInformation", "追加情報" ),
        required=True
        )
    status = forms.ModelChoiceField(
        queryset=ProductStockStatus.objects.all(),
        label=pgettext_lazy( "ProductStockStatus", "商品状態" ),
        required=True
        )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
class ExtFileField(forms.FileField):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in self.ext_whitelist:
            raise forms.ValidationError("※拡張子csvのファイルをアップロードしてください。")

class StockTakingUploadForm(forms.Form):
    file = ExtFileField(
        ext_whitelist=(".csv"),
        required = True,
        label='CSVファイル')


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class BaseFulfillmentLineFormSet( forms.BaseModelFormSet ):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )
        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        total_quantity = sum(
            form.cleaned_data.get( "quantity", 0 ) for form in self.forms
            )
        if total_quantity <= 0:
            raise forms.ValidationError( "Total quantity must be larger than 0." )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

#
# class NoIemiFulfillmentLineForm( forms.ModelForm ):
#     class Meta:
#         model = OrderManageFulfillmentLine
#         fields = ["order_manage_line", "quantity"]
#
#     def clean_quantity(self):
#         quantity = self.cleaned_data.get( "quantity" )
#         order_manage_line = self.cleaned_data.get( "order_manage_line" )
#         if quantity > order_manage_line.quantity_unfulfilled:
#             raise forms.ValidationError(
#                 npgettext_lazy(
#                     "Fulfill order line form error",
#                     "%(quantity)d item remaining to fulfill.",
#                     "%(quantity)d items remaining to fulfill.",
#                     number="quantity",
#                     )
#                 % {
#                     "quantity": order_manage_line.quantity_unfulfilled,
#                     "order_manage_line": order_manage_line,
#                     }
#                 )
#         return quantity
#
#     def save(self, commit=True):
#         fulfill_order_line( self.instance.order_manage_line, self.instance.quantity )
#         return super().save( commit )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class STORAGEFulfillmentLineForm():
    pass


class DELIVERYFulfillmentLineForm():
    pass


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class FulfillmentLineForm( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = OrderManageFulfillmentLine
        fields = ["order_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        order_manage_line = self.cleaned_data.get( "order_manage_line" )
        if quantity > order_manage_line.quantity_unfulfilled:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": order_manage_line.quantity_unfulfilled,
                    "order_manage_line": order_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_order_line( self.instance.order_manage_line, self.instance.quantity )
        return super().save( commit )


class FulfillmentLineBarterManageForm( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = BarterManageFulfillmentLine
        fields = ["barter_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        barter_manage_line = self.cleaned_data.get( "barter_manage_line" )
        if quantity > barter_manage_line.quantity_unfulfilled:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": barter_manage_line.quantity_unfulfilled,
                    "barter_manage_line": barter_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_order_line( self.instance.barter_manage_line, self.instance.quantity )
        return super().save( commit )


class FulfillmentLineStoreManageForm_MOVEOUT( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = StoreToStoreManageFulfillmentLine_MOVEOUT
        fields = ["store_to_store_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        store_to_store_manage_line = self.cleaned_data.get(
            "store_to_store_manage_line"
            )
        if quantity > store_to_store_manage_line.quantity_unfulfilled_MOVEOUT:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": store_to_store_manage_line.quantity_unfulfilled_MOVEOUT,
                    "store_to_store_manage_line": store_to_store_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_store_MOVEOUT( self.instance.store_to_store_manage_line,
                               self.instance.quantity
                               )
        return super().save( commit )


class FulfillmentLineStoreManageForm_MOVEIN( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = StoreToStoreManageFulfillmentLine_MOVEIN
        fields = ["store_to_store_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        store_to_store_manage_line = self.cleaned_data.get(
            "store_to_store_manage_line"
            )
        if quantity > store_to_store_manage_line.quantity_unfulfilled_MOVEIN:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": store_to_store_manage_line.quantity_unfulfilled_MOVEIN,
                    "store_to_store_manage_line": store_to_store_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_store_MOVEIN( self.instance.store_to_store_manage_line,
                              self.instance.quantity
                              )
        return super().save( commit )


class FulfillmentLineManualInventoryManageForm_LOCK( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = ManualInventoryManageFulfillmentLine_LOCK
        fields = ["manual_inventory_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        manual_inventory_manage_line = self.cleaned_data.get(
            "manual_inventory_manage_line"
            )
        if quantity > manual_inventory_manage_line.quantity_unfulfilled_LOCK:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": manual_inventory_manage_line.quantity_unfulfilled_LOCK,
                    "manual_inventory_manage_line": manual_inventory_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_manual_inventory_LOCK( self.instance.manual_inventory_manage_line,
                                       self.instance.quantity
                                       )
        return super().save( commit )


class FulfillmentLineManualInventoryManageForm_UNLOCK( forms.ModelForm ):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = ManualInventoryManageFulfillmentLine_UNLOCK
        fields = ["manual_inventory_manage_line", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get( "quantity" )
        manual_inventory_manage_line = self.cleaned_data.get(
            "manual_inventory_manage_line"
            )
        if quantity > manual_inventory_manage_line.quantity_unfulfilled_UNLOCK:
            raise forms.ValidationError(
                npgettext_lazy(
                    "Fulfill order line form error",
                    "未執行の項目は%(quantity)d個",
                    "未執行の項目は%(quantity)d個",
                    number="quantity",
                    )
                % {
                    "quantity": manual_inventory_manage_line.quantity_unfulfilled_UNLOCK,
                    "manual_inventory_manage_line": manual_inventory_manage_line,
                    }
                )
        return quantity

    def save(self, commit=True):
        fulfill_manual_inventory_UNLOCK( self.instance.manual_inventory_manage_line,
                                         self.instance.quantity
                                         )
        return super().save( commit )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class FulfillmentForm( forms.ModelForm ):
    class Meta:
        model = OrderManageFulfillment
        fields = []

    def __init__(self, *args, **kwargs):
        order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )
        self.instance.order_manage = order_manage


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class FulfillmentStoreManageForm_MOVEOUT( forms.ModelForm ):
    class Meta:
        model = StoreToStoreManageFulfillment_MOVEOUT
        fields = []

    def __init__(self, *args, **kwargs):
        store_to_store_manage = kwargs.pop( "store_to_store_manage" )
        super().__init__( *args, **kwargs )
        self.instance.store_to_store_manage = store_to_store_manage


class FulfillmentStoreManageForm_MOVEIN( forms.ModelForm ):
    class Meta:
        model = StoreToStoreManageFulfillment_MOVEIN
        fields = []

    def __init__(self, *args, **kwargs):
        store_to_store_manage = kwargs.pop( "store_to_store_manage" )
        super().__init__( *args, **kwargs )
        self.instance.store_to_store_manage = store_to_store_manage


class FulfillmentBarterManageForm( forms.ModelForm ):
    class Meta:
        model = BarterManageFulfillment
        fields = []

    def __init__(self, *args, **kwargs):
        barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )
        self.instance.barter_manage = barter_manage


class FulfillmentManualInventoryManageForm_LOCK( forms.ModelForm ):
    class Meta:
        model = ManualInventoryManageFulfillment_LOCK
        fields = []

    def __init__(self, *args, **kwargs):
        manual_inventory_manage = kwargs.pop( "manual_inventory_manage" )
        super().__init__( *args, **kwargs )
        self.instance.manual_inventory_manage = manual_inventory_manage


class FulfillmentManualInventoryManageForm_UNLOCK( forms.ModelForm ):
    class Meta:
        model = ManualInventoryManageFulfillment_UNLOCK
        fields = []

    def __init__(self, *args, **kwargs):
        manual_inventory_manage = kwargs.pop( "manual_inventory_manage" )
        super().__init__( *args, **kwargs )
        self.instance.manual_inventory_manage = manual_inventory_manage


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class ExtraInformationForm( forms.ModelForm ):
    class Meta:
        model = ExtraInformation
        fields = ["name", "description"]
        labels = {
            "name": pgettext_lazy( "extra_information", "追加情報" ),
            "description": pgettext_lazy( "extra_information_description", "説明" ),
            }

    def save(self, commit=True):
        self.instance.slug = slugify( str( uuid.uuid4() ) )
        return super().save( commit=commit )


class ShopsForm( forms.ModelForm ):
    class Meta:
        model = ExtraInformation
        fields = ["name", "description"]
        labels = {
            "name": pgettext_lazy( "extra_information", "店舗名" ),
            "description": pgettext_lazy( "extra_information_description", "説明" ),
            }

    def save(self, commit=True):
        self.instance.slug = slugify( str( uuid.uuid4() ) )
        return super().save( commit=commit )


class EmarketForm( forms.ModelForm ):
    class Meta:
        model = E_mark
        fields = ["name", "description"]
        labels = {
            "name": pgettext_lazy( "extra_information", "Eマーケット名" ),
            "slug": pgettext_lazy( "extra_information_slug", "Slug" ),
            "description": pgettext_lazy( "extra_information_description", "説明" ),
            }

    def save(self, commit=True):
        self.instance.slug = slugify( str( uuid.uuid4() ) )
        return super().save( commit=commit )


class ProductStockStatusForm( forms.ModelForm ):
    class Meta:
        model = ProductStockStatus
        fields = ["name", "description"]
        labels = {
            "name": pgettext_lazy( "extra_information", "追加情報" ),
            "description": pgettext_lazy( "extra_information_description", "説明" ),
            }

    def save(self, commit=True):
        self.instance.slug = slugify( str( uuid.uuid4() ) )
        return super().save( commit=commit )


class SuppliersForm( forms.Form ):
    GENDER = [
        ("男性", "男性"),
        ("女性", "女性"),
        ]
    WORKS = [
        ("事務職","事務職"),
        ("販売職","販売職"),
        ("専門的･技術的職","専門的･技術的職"),
        ("生産工程職","生産工程職"),
        ("サービス職","サービス職"),
        ("保安職","保安職"),
        ("建設･採掘職","建設･採掘職"),
        ("輸送･機械運転職","輸送･機械運転職"),
        ("運搬･清掃･包装等職","運搬･清掃･包装等職"),
        ("農林漁業職","農林漁業職"),
        ("管理職","管理職"),
        ("分類不能","分類不能"),
        ]
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    last_name = forms.CharField( required=True, label='姓（アルファベット）' )
    first_name = forms.CharField( required=False, label='名（アルファベット）' )
    last_name_kannji = forms.CharField( required=False, label='姓（漢字）' )
    first_name_kannji = forms.CharField( required=False, label='名（漢字）' )
    age = forms.CharField( required=False, label='年齢' )
    work = forms.CharField( required=False,
                            label='職業',
                            widget=forms.Select( choices=WORKS ),
                            )
    phone = forms.CharField( required=False, label='電話' )
    gender = forms.CharField(
        required=False,
        label="性別",
        widget=forms.Select( choices=GENDER ),
        )
    birth = forms.DateField(
        required=False,
        label=pgettext_lazy( "Address form field label", "生年月日" ),
        widget=forms.DateInput( attrs={ "type": "date" } ),
        )
    note = forms.CharField( required=False, label='ノート' )

    # ------------------------------------------------
    postal_code = forms.IntegerField(
        required=False,
        label="郵便番号",
        widget=forms.TextInput(
            attrs={ 'class': 'p-postal-code', 'placeholder': '記入例：8900053', }
            )
        )
    city_area = forms.CharField(
        required=False,
        label="都道府県",
        widget=forms.TextInput(
            attrs={ 'class': 'p-region', 'placeholder': '記入例：鹿児島県' }
            )
        )
    city = forms.CharField(
        required=False,
        label="市区町村・番地",
        widget=forms.TextInput(
            attrs={ 'class': 'p-locality p-street-address p-extended-address','placeholder': '記入例：鹿児島市中央町１０' }
            )
        )
    street_address_1 = forms.CharField( required=False, label="建物名・部屋番号" )
    street_address_2 = forms.CharField( required=False, label="そのた" )

    def __init__(self, *args, **kwargs):

        super().__init__( *args, **kwargs )


class LegalPersonForm( forms.Form ):
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    company_name = forms.CharField( required=False, label='会社名' )
    phone = forms.CharField( required=False, label='電話番号' )
    fax = forms.CharField( required=False, label='FAX' )
    homepage = forms.CharField( required=False, label='ホームページ' )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField(
        required=False,
        label="郵便番号",
        widget=forms.TextInput(
            attrs={ 'class': 'p-postal-code', 'placeholder': '記入例：8900053', }
            )
        )
    city_area = forms.CharField(
        required=False,
        label="都道府県",
        widget=forms.TextInput(
            attrs={ 'class': 'p-region', 'placeholder': '記入例：鹿児島県' }
            )
        )
    city = forms.CharField(
        required=False,
        label="市区町村・番地",
        widget=forms.TextInput(
            attrs={ 'class': 'p-locality p-street-address p-extended-address','placeholder': '記入例：鹿児島市中央町１０' }
            )
        )
    street_address_1 = forms.CharField( required=False, label="建物名・部屋番号" )
    street_address_2 = forms.CharField( required=False, label="そのた" )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class ProductStockForm( forms.ModelForm ):
    class Meta:
        model = ProductStock
        fields = [
            "name",
            "jan_code",
            "description",
            ]
        labels = {
            "name": pgettext_lazy( "name", "商品名" ),
            "jan_code": pgettext_lazy(
                "jan_code", "JAN"
                ),
            "description": pgettext_lazy( "Description", "説明" )
            }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, user, commit=True, is_logs=True):
        # assert commit is True, "Commit is required to build the M2M structure"
        changed=self.instance.tracker.changed()
        super().save()
        if is_logs:
            for key in changed:
                log_product_stock_changed( user, self.instance.pk,self._meta.labels[key], getattr(self.instance,key,""),
                                           changed[key]
                                           )
        return self.instance


class ProductObjectStockForm( MoneyModelForm ):
    shops = forms.ModelChoiceField(
        queryset=Shops.objects.all()
        )
    extra_informations = forms.ModelChoiceField(
        queryset=ExtraInformation.objects.all()
        )
    price_override = make_money_field()
    status = forms.ModelChoiceField(
        queryset=ProductStockStatus.objects.all()
        )

    class Meta:
        model = ProductObjectStock
        exclude = [
            "slug",
            "sku",
            "create",
            "last_change",
            "price_average_amount",
            "price_average",
            "currency",
            "price_override_amount",
            "product_stock",
            "is_lock",
            "is_select",
            "is_allocate",
            "manage_status",
            "is_available_M",

            ]
        labels = {
            "shops": pgettext_lazy( "shops",
                                    "店舗別"
                                    ),
            "extra_informations": pgettext_lazy( "extra_informations",
                                                 "追加情報"
                                                 ),
            "status": pgettext_lazy( "status",
                                     "商品状態"
                                     ),
            "imei_code": pgettext_lazy( "IMEI",
                                        "IMEI"
                                        ),
            "notion": pgettext_lazy( "notion",
                                     "メモ"
                                     ),
            "price_override": pgettext_lazy( "price_override",
                                             "買取価格"
                                             ),

            }

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )
        self.fields["price_override"].required = True
        self.fields["shops"].required = False
        self.fields["extra_informations"].required = False
        self.fields["status"].required = False

    @transaction.atomic
    def save(self, user,commit=True, is_logs=True):
        # assert commit is True, "Commit is required to build the M2M structure"
        changed=self.instance.tracker.changed()
        super().save()
        if is_logs:
            for key in changed:
                log_product_object_stock_changed( user, self.instance.pk, self._meta.labels[key], getattr(self.instance,key,""),
                                           changed[key]
                                           )
        return self.instance



# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class ProductObjectStockBulkSelectForm( forms.Form ):
    product_object_stock_s = forms.ModelMultipleChoiceField(
        queryset=ProductObjectStock.objects.filter( is_lock=False, is_available_M=True,
                                                    is_temp=False
                                                    ).exclude( is_allocate=True )
        )

    def __init__(self, *args, **kwargs):
        self.order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )

    class Meta:
        model = ProductObjectStock
        fields = ("product_object_stock_s",)


class ManualInventoryManageProductObjectStockSelectForm( forms.Form ):
    product_object_stock_s = forms.ModelMultipleChoiceField(
        queryset=ProductObjectStock.objects.filter( is_lock=False, is_available_M=True,
                                                    is_temp=False
                                                    ).exclude( is_allocate=True )
        )

    def __init__(self, *args, **kwargs):
        self.manual_inventory_manage = kwargs.pop( "manual_inventory_manage" )
        super().__init__( *args, **kwargs )

    class Meta:
        model = ProductObjectStock
        fields = ("product_object_stock_s",)


class StoreToStoreManageProductObjectStockSelectForm( forms.Form ):
    product_object_stock_s = forms.ModelMultipleChoiceField(
        queryset=ProductObjectStock.objects.filter( is_lock=False, is_available_M=True,
                                                    is_temp=False
                                                    ).exclude( is_allocate=True )
        )

    def __init__(self, *args, **kwargs):
        self.store_to_store_manage = kwargs.pop( "store_to_store_manage" )
        super().__init__( *args, **kwargs )

    class Meta:
        model = ProductObjectStock
        fields = ("product_object_stock_s",)


class BarterManageProductObjectStockSelectForm( forms.Form ):
    product_object_stock_s = forms.ModelMultipleChoiceField(
        queryset=ProductObjectStock.objects.filter( is_lock=False, is_available_M=True,
                                                    is_temp=False
                                                    ).exclude( is_allocate=True )
        )

    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )

    class Meta:
        model = ProductObjectStock
        fields = ("product_object_stock_s",)


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


# class OrderManageAddProductFormModel( forms.ModelForm ):
#
#     class Mate:
#         model = ProductObjectStock
#         fields = [
#             "imei_code",
#             "notion",
#             "price_override_amount",
#             "extra_informations",
#             "status",
#             "shops",
#             ]
#
#
#     def __init__(self, *args, **kwargs):
#         product_stock = kwargs.pop( "product_stock" )
#         super().__init__( *args, **kwargs )
#         self.instance.product_stock = product_stock


class StoreToStoreManageToShopForm( forms.ModelForm ):
    name = forms.ModelChoiceField(
        queryset=Shops.objects.all(),
        label=pgettext_lazy( "Shops", "店舗別" ),
        required=True
        )

    class Meta:
        model = Shops
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        self.store_to_store_manage = kwargs.pop( "store_to_store_manage" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class OrderManageAddProductForm_with_iemi( forms.Form ):
    name = forms.CharField( required=True, label='商品類名前' )
    jan_code = forms.CharField( required=True, label='商品類JANコード',
                                widget=forms.TextInput(
                                    attrs={ 'id': 'product_stock_jan_search_id' }
                                    )
                                )
    description = forms.CharField( required=False, label='商品類説明' )

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to order_manage form: variant field",
            "既存商品類"
            ),
        required=False
        )
    quantity = forms.IntegerField( required=True, label='数量', initial=int( 1 ) )

    price_to_cal = forms.IntegerField( label='買取価格',required=False )

    def __init__(self, *args, **kwargs):
        self.no_imei = kwargs.pop( "no_imei" )
        self.order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )

    def fields_required(self, fields):
        """Used for conditionally marking fields as required."""
        for field in fields:
            if not self.cleaned_data.get( field, '' ):
                msg = forms.ValidationError( "このフィールドは必須です。" )
                self.add_error( field, msg )

    def clean(self):
        if self.no_imei:
            self.fields_required( ['name','jan_code','quantity','price_to_cal'] )
        else:
            self.cleaned_data['price_to_cal'] = ''
        return self.cleaned_data


class BarterManageAddProductForm_with_iemi( forms.Form ):
    name = forms.CharField( required=True, label='商品類名前' )
    jan_code = forms.CharField( required=True, label='商品類JANコード',
                                widget=forms.TextInput(attrs={'id': 'product_stock_jan_search_id'}) )
    description = forms.CharField( required=False, label='商品類説明' )

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "barter_manage: subform to add variant to order_manage form: variant field",
            "既存商品類"
            ),
        required=False
        )
    quantity = forms.IntegerField( required=True, label='数量', initial=int( 1 ) )

    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )


class ManualInventoryManageAddProductForm( forms.Form ):
    name = forms.CharField( required=False, label='商品類名前' )
    jan_code = forms.CharField( required=False, label='商品類JANコード' )
    description = forms.CharField( required=False, label='商品類説明' )

    slug = forms.CharField( required=False, label='SLUG' )
    imei_code = forms.CharField( required=False, label='IMEI' )
    notion = forms.CharField( required=False, label='メモ' )
    price_override_amount = forms.IntegerField( required=False, label='買取価格' )

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock-s" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to order_manage form: variant field",
            "既存商品類"
            ),
        required=False
        )
    shops = forms.ModelChoiceField(
        queryset=Shops.objects.all(),
        label=pgettext_lazy( "Shops", "店舗別" ),
        required=True
        )
    extra_informations = forms.ModelChoiceField(
        queryset=ExtraInformation.objects.all(),
        label=pgettext_lazy( "ExtraInformation", "追加情報" ),
        required=True
        )
    status = forms.ModelChoiceField(
        queryset=ProductStockStatus.objects.all(),
        label=pgettext_lazy( "ProductStockStatus", "商品状態" ),
        required=True
        )

    def __init__(self, *args, **kwargs):
        self.manual_inventory_manage = kwargs.pop( "manual_inventory_manage" )
        super().__init__( *args, **kwargs )


class StoreToStoreManageAddProductForm( forms.Form ):
    pass


class BarterManageAddProductForm( forms.Form ):
    name = forms.CharField( required=False, label='商品類名前' )
    jan_code = forms.CharField( required=False, label='商品類JANコード' )
    description = forms.CharField( required=False, label='商品類説明' )

    slug = forms.CharField( required=False, label='SLUG' )
    imei_code = forms.CharField( required=False, label='IMEI' )
    notion = forms.CharField( required=False, label='メモ' )
    price_override_amount = forms.IntegerField( required=False, label='買取価格' )

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock-s" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to order_manage form: variant field",
            "既存商品類"
            ),
        required=False
        )
    shops = forms.ModelChoiceField(
        queryset=Shops.objects.all(),
        label=pgettext_lazy( "Shops", "店舗別" ),
        required=True
        )
    extra_informations = forms.ModelChoiceField(
        queryset=ExtraInformation.objects.all(),
        label=pgettext_lazy( "ExtraInformation", "追加情報" ),
        required=True
        )
    status = forms.ModelChoiceField(
        queryset=ProductStockStatus.objects.all(),
        label=pgettext_lazy( "ProductStockStatus", "商品状態" ),
        required=True
        )

    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class CancelOrderManageLineForm( forms.Form ):
    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop( "line" )
        super().__init__( *args, **kwargs )


class CancelManualInventoryManageLineForm( forms.Form ):
    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop( "line" )
        super().__init__( *args, **kwargs )


class CancelStoreToStoreManageLineForm( forms.Form ):
    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop( "line" )
        super().__init__( *args, **kwargs )


class CancelBarterManageLineForm( forms.Form ):
    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop( "line" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class CreateOrderManageFromDraftForm( forms.ModelForm ):

    notify_customer = forms.BooleanField(
        label=pgettext_lazy(
            "Send email to customer about order created by staff users",
            "執行表の確認メールをお客様に送信",
            ),
        required=False,
        initial=False,
        )

    class Meta:
        model = OrderManage
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

    def clean(self):
        super().clean()
        errors = []
        if self.instance.get_total_quantity() == 0:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "商品がないと注文出入庫執行表が作成できませんでした",
                        )
                    )
                )
        if not self.instance.suppliers and not self.instance.legal_person:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "取引先がないと注文出入庫執行表が作成できませんでした",
                        )
                    )
                )
        # TODO:是不是要再确认一下商品在库情况
        if errors:
            raise forms.ValidationError( errors )
        return self.cleaned_data

    def save(self):
        self.instance.order_status = InventoryStatus.UNFULFILLED
        super().save()
        return self.instance


class CreateManualInventoryManageFromDraftForm( forms.ModelForm ):
    notify_customer = forms.BooleanField(
        label=pgettext_lazy(
            "Send email to customer about order created by staff users",
            "執行表の確認メールをお客様に送信",
            ),
        required=False,
        initial=False,
        )

    class Meta:
        model = ManualInventoryManage
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

    def clean(self):
        super().clean()
        errors = []
        if self.instance.get_total_quantity() == 0:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "商品がないと商品ロック執行表が作成できませんでした",
                        )
                    )
                )

        # TODO:是不是要再确认一下商品在库情况
        if errors:
            raise forms.ValidationError( errors )
        return self.cleaned_data

    def save(self):
        self.instance.manual_inventory_status = InventoryStatus.UNFULFILLED
        super().save()
        return self.instance


class CreateStoreToStoreManageFromDraftForm( forms.ModelForm ):
    notify_customer = forms.BooleanField(
        label=pgettext_lazy(
            "Send email to customer about order created by staff users",
            "執行表の確認メールをお客様に送信",
            ),
        required=False,
        initial=False,
        )

    class Meta:
        model = StoreToStoreManage
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

    def clean(self):
        super().clean()
        errors = []
        if self.instance.get_total_quantity() == 0:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "商品がないと店舗間移動執行表が作成できませんでした",
                        )
                    )
                )
        if not self.instance.to_shop:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "移動先がないと店舗間移動執行表が作成できませんでした",
                        )
                    )
                )
        # TODO:是不是要再确认一下商品在库情况
        if errors:
            raise forms.ValidationError( errors )
        return self.cleaned_data

    def save(self):
        self.instance.store_to_store_status = InventoryStatus.UNFULFILLED
        super().save()
        return self.instance


class CreateBarterManageFromDraftForm( forms.ModelForm ):
    notify_customer = forms.BooleanField(
        label=pgettext_lazy(
            "Send email to customer about order created by staff users",
            "執行表の確認メールをお客様に送信",
            ),
        required=False,
        initial=False,
        )

    class Meta:
        model = BarterManage
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

    def clean(self):
        super().clean()
        errors = []
        if self.instance.get_total_quantity() == 0:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "商品がないと物々交換執行表が作成できませんでした",
                        )
                    )
                )
        if not self.instance.suppliers and not self.instance.legal_person:
            errors.append(
                forms.ValidationError(
                    pgettext_lazy(
                        "Create draft order form error",
                        "移動先がないと物々交換執行表が作成できませんでした",
                        )
                    )
                )
        # TODO:是不是要再确认一下商品在库情况
        if errors:
            raise forms.ValidationError( errors )
        return self.cleaned_data

    def save(self):
        self.instance.barter_status = InventoryStatus.UNFULFILLED
        super().save()
        return self.instance


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class OrderManageNoteForm( forms.Form ):
    message = forms.CharField(
        label=pgettext_lazy( "OrderManage note", "注文出入庫メモ" ), widget=forms.Textarea()
        )


class BarterManageNoteForm( forms.Form ):
    message = forms.CharField(
        label=pgettext_lazy( "OrderManage note", "物々交換メモ" ), widget=forms.Textarea()
        )


class StoreToStoreManageNoteForm( forms.Form ):
    message = forms.CharField(
        label=pgettext_lazy( "OrderManage note", "店舗間転移メモ" ), widget=forms.Textarea()
        )


class ManualInventoryManageNoteForm( forms.Form ):
    message = forms.CharField(
        label=pgettext_lazy( "OrderManage note", "商品ロックメモ" ), widget=forms.Textarea()
        )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class AddProductStockToOrderManageForm( forms.Form ):
    """Allow adding lines with given quantity to an order_manage."""

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.filter( is_temp=False ),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to order_manage form: variant field",
            "注文出入庫: 商品類を選択s"
            ),
        )
    quantity = QuantityField(
        label=pgettext_lazy(
            "Add variant to order_manage form label",
            "数量"
            ),
        validators=[MinValueValidator( 1 )],
        )

    def __init__(self, *args, **kwargs):
        self.order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )


class AddProductStockToManualInventoryManageForm( forms.Form ):
    """Allow adding lines with given quantity to an manual_inventory_manage."""

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.filter( is_temp=False ),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to manual_inventory_manage form: variant field",
            "商品ロック: 商品類を選択"
            ),
        )
    quantity = QuantityField(
        label=pgettext_lazy(
            "Add variant to manual_inventory_manage form label",
            "数量"
            ),
        validators=[MinValueValidator( 1 )],
        )

    def __init__(self, *args, **kwargs):
        self.manual_inventory_manage = kwargs.pop( "manual_inventory_manage" )
        super().__init__( *args, **kwargs )


class AddProductStockToStoreToStoreManageForm( forms.Form ):
    """Allow adding lines with given quantity to an store_to_store_manage."""

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.filter( is_temp=False ),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to store_to_store_manage form: variant field",
            "店舗間移動: 商品類を選択"
            ),
        )
    quantity = QuantityField(
        label=pgettext_lazy(
            "Add variant to store_to_store_manage form label",
            "数量"
            ),
        validators=[MinValueValidator( 1 )],
        )

    def __init__(self, *args, **kwargs):
        self.store_to_store_manage = kwargs.pop( "store_to_store_manage" )
        super().__init__( *args, **kwargs )


class AddProductStockToBarterManageForm( forms.Form ):
    """Allow adding lines with given quantity to an barter_manage."""

    product_stock = AjaxSelect2ChoiceField(
        queryset=ProductStock.objects.filter( is_temp=False ),
        fetch_data_url=reverse_lazy( "product_stock:ajax-product-stock" ),
        label=pgettext_lazy(
            "Order form: subform to add variant to barter_manage form: variant field",
            "物々交換: 商品類を選択"
            ),
        )
    quantity = QuantityField(
        label=pgettext_lazy(
            "Add variant to barter_manage form label",
            "数量"
            ),
        validators=[MinValueValidator( 1 )],
        )

    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class OrderManageSuppliersAddressForm( forms.Form ):
    GENDER = [
        ("男性", "男性"),
        ("女性", "女性"),
        ]
    WORKS = [
        ("事務職", "事務職"),
        ("販売職", "販売職"),
        ("専門的･技術的職", "専門的･技術的職"),
        ("生産工程職", "生産工程職"),
        ("サービス職", "サービス職"),
        ("保安職", "保安職"),
        ("建設･採掘職", "建設･採掘職"),
        ("輸送･機械運転職", "輸送･機械運転職"),
        ("運搬･清掃･包装等職", "運搬･清掃･包装等職"),
        ("農林漁業職", "農林漁業職"),
        ("管理職", "管理職"),
        ("分類不能", "分類不能"),
        ]
    suppliers = AjaxSelect2ChoiceField(
        queryset=Suppliers.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-suppliers-list" ),
        required=False,
        label=pgettext_lazy(
            "Order form: editing suppliers details - selecting a suppliers",
            "取引先(個人)"
            ),
        )
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    last_name = forms.CharField( required=True, label='姓（アルファベット）' )
    first_name = forms.CharField( required=False, label='名（アルファベット）' )
    last_name_kannji = forms.CharField( required=False, label='姓（漢字）' )
    first_name_kannji = forms.CharField( required=False, label='名（漢字）' )
    age = forms.CharField( required=False, label='年齢' )
    work = forms.CharField( required=False,
                            label='職業',
                            widget=forms.Select( choices=WORKS ),
                            )
    phone = forms.CharField( required=False, label='電話' )
    gender = forms.CharField(
        required=False,
        label="性別",
        widget=forms.Select( choices=GENDER ),
        )
    birth = forms.DateField(
        required=False,
        label=pgettext_lazy( "Address form field label", "生年月日" ),
        widget=forms.DateInput( attrs={ "type": "date" } ),
        )
    note = forms.CharField( required=False, label='ノート' )

    # ------------------------------------------------
    postal_code = forms.IntegerField(
        required=False,
        label="郵便番号",
        widget=forms.TextInput(
            attrs={ 'class': 'p-postal-code', 'placeholder': '記入例：8900053', }
            )
        )
    city_area = forms.CharField(
        required=False,
        label="都道府県",
        widget=forms.TextInput(
            attrs={ 'class': 'p-region', 'placeholder': '記入例：鹿児島県' }
            )
        )
    city = forms.CharField(
        required=False,
        label="市区町村・番地",
        widget=forms.TextInput(
            attrs={ 'class': 'p-locality p-street-address p-extended-address','placeholder': '記入例：鹿児島市中央町１０' }
            )
        )
    street_address_1 = forms.CharField( required=False, label="建物名・部屋番号" )
    street_address_2 = forms.CharField( required=False, label="そのた" )
    def __init__(self, *args, **kwargs):
        self.order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )


class ManualInventoryManageSuppliersAddressForm( forms.Form ):
    pass


class StoreToStoreManageSuppliersAddressForm( forms.Form ):
    pass


class BarterManageSuppliersAddressForm( forms.Form ):
    GENDER = [
        ("男性", "男性"),
        ("女性", "女性"),
        ]
    WORKS = [
        ("事務職", "事務職"),
        ("販売職", "販売職"),
        ("専門的･技術的職", "専門的･技術的職"),
        ("生産工程職", "生産工程職"),
        ("サービス職", "サービス職"),
        ("保安職", "保安職"),
        ("建設･採掘職", "建設･採掘職"),
        ("輸送･機械運転職", "輸送･機械運転職"),
        ("運搬･清掃･包装等職", "運搬･清掃･包装等職"),
        ("農林漁業職", "農林漁業職"),
        ("管理職", "管理職"),
        ("分類不能", "分類不能"),
        ]
    suppliers = AjaxSelect2ChoiceField(
        queryset=Suppliers.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-suppliers-list" ),
        required=False,
        label=pgettext_lazy(
            "Order form: editing suppliers details - selecting a suppliers",
            "取引先(個人)"
            ),
        )
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    last_name = forms.CharField( required=True, label='姓（アルファベット）' )
    first_name = forms.CharField( required=False, label='名（アルファベット）' )
    last_name_kannji = forms.CharField( required=False, label='姓（漢字）' )
    first_name_kannji = forms.CharField( required=False, label='名（漢字）' )
    age = forms.CharField( required=False, label='年齢' )
    work = forms.CharField( required=False,
                            label='職業',
                            widget=forms.Select( choices=WORKS ),
                            )
    phone = forms.CharField( required=False, label='電話' )
    gender = forms.CharField(
        required=False,
        label="性別",
        widget=forms.Select( choices=GENDER ),
        )
    birth = forms.DateField(
        required=False,
        label=pgettext_lazy( "Address form field label", "生年月日" ),
        widget=forms.DateInput( attrs={ "type": "date" } ),
        )
    note = forms.CharField( required=False, label='ノート' )

    # ------------------------------------------------
    postal_code = forms.IntegerField(
        required=False,
        label="郵便番号",
        widget=forms.TextInput(
            attrs={ 'class': 'p-postal-code', 'placeholder': '記入例：8900053', }
            )
        )
    city_area = forms.CharField(
        required=False,
        label="都道府県",
        widget=forms.TextInput(
            attrs={ 'class': 'p-region', 'placeholder': '記入例：鹿児島県' }
            )
        )
    city = forms.CharField(
        required=False,
        label="市区町村・番地",
        widget=forms.TextInput(
            attrs={ 'class': 'p-locality p-street-address p-extended-address','placeholder': '記入例：鹿児島市中央町１０' }
            )
        )
    street_address_1 = forms.CharField( required=False, label="建物名・部屋番号" )
    street_address_2 = forms.CharField( required=False, label="そのた" )
    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class OrderManageLegalPersonAddressForm( forms.Form ):
    legalperson = AjaxSelect2ChoiceField(
        queryset=LegalPerson.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-legal-person-list" ),
        required=False,
        label=pgettext_lazy(
            "Order form: editing suppliers details - selecting a suppliers",
            "取引先(法人)"
            ),
        )
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )

    company_name = forms.CharField( required=False, label='会社名' )
    phone = forms.CharField( required=False, label='電話番号' )
    fax = forms.CharField( required=False, label='FAX' )
    homepage = forms.CharField( required=False, label='ホームページ' )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        self.order_manage = kwargs.pop( "order_manage" )
        super().__init__( *args, **kwargs )


class ManualInventoryManageLegalPersonAddressForm( forms.Form ):
    pass


class StoreToStoreManageLegalPersonAddressForm( forms.Form ):
    pass


class BarterManageLegalPersonAddressForm( forms.Form ):
    legalperson = AjaxSelect2ChoiceField(
        queryset=LegalPerson.objects.all(),
        fetch_data_url=reverse_lazy( "product_stock:ajax-legal-person-list" ),
        required=False,
        label=pgettext_lazy(
            "Order form: editing suppliers details - selecting a suppliers",
            "取引先(法人)"
            ),
        )
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )

    company_name = forms.CharField( required=False, label='会社名' )
    phone = forms.CharField( required=False, label='電話番号' )
    fax = forms.CharField( required=False, label='FAX' )
    homepage = forms.CharField( required=False, label='ホームページ' )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        self.barter_manage = kwargs.pop( "barter_manage" )
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

class OrderManageLegalPersonAddressEditForm( forms.Form ):
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Email" ),
        )
    company_name = forms.CharField( required=False, label='会社名' )
    phone = forms.CharField( required=False, label='電話番号' )
    fax = forms.CharField( required=False, label='FAX' )
    homepage = forms.CharField( required=False, label='ホームページ' )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )


class BarterManageLegalPersonAddressEditForm( forms.Form ):
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Email" ),
        )
    company_name = forms.CharField( required=False, label='会社名' )
    phone = forms.CharField( required=False, label='電話番号' )
    fax = forms.CharField( required=False, label='FAX' )
    homepage = forms.CharField( required=False, label='ホームページ' )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------


class OrderManageSuppliersAddressEditForm( forms.Form ):
    GENDER = [
        ("男性", "男性"),
        ("女性", "女性"),
        ]
    WORKS = [
        ("事務職", "事務職"),
        ("販売職", "販売職"),
        ("専門的･技術的職", "専門的･技術的職"),
        ("生産工程職", "生産工程職"),
        ("サービス職", "サービス職"),
        ("保安職", "保安職"),
        ("建設･採掘職", "建設･採掘職"),
        ("輸送･機械運転職", "輸送･機械運転職"),
        ("運搬･清掃･包装等職", "運搬･清掃･包装等職"),
        ("農林漁業職", "農林漁業職"),
        ("管理職", "管理職"),
        ("分類不能", "分類不能"),
        ]
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    last_name = forms.CharField( required=True, label='姓（アルファベット）' )
    first_name = forms.CharField( required=False, label='名（アルファベット）' )
    last_name_kannji = forms.CharField( required=False, label='姓（漢字）' )
    first_name_kannji = forms.CharField( required=False, label='名（漢字）' )
    age = forms.CharField( required=False, label='年齢' )
    work = forms.CharField( required=False,
                            label='職業',
                            widget=forms.Select( choices=WORKS ),
                            )
    phone = forms.CharField( required=False, label='電話' )
    gender = forms.CharField(
        required=False,
        label="性別",
        widget=forms.Select( choices=GENDER ),
        )
    birth = forms.DateField(
        required=False,
        label=pgettext_lazy( "Address form field label", "生年月日" ),
        widget=forms.DateInput( attrs={ "type": "date" } ),
        )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )


class BarterManageSuppliersAddressEditForm( forms.Form ):
    GENDER = [
        ("男性", "男性"),
        ("女性", "女性"),
        ]
    WORKS = [
        ("事務職", "事務職"),
        ("販売職", "販売職"),
        ("専門的･技術的職", "専門的･技術的職"),
        ("生産工程職", "生産工程職"),
        ("サービス職", "サービス職"),
        ("保安職", "保安職"),
        ("建設･採掘職", "建設･採掘職"),
        ("輸送･機械運転職", "輸送･機械運転職"),
        ("運搬･清掃･包装等職", "運搬･清掃･包装等職"),
        ("農林漁業職", "農林漁業職"),
        ("管理職", "管理職"),
        ("分類不能", "分類不能"),
        ]
    email = forms.EmailField(
        required=True,
        label=pgettext_lazy( "Address form field label", "Emailまたは電話番号" ),
        )
    last_name = forms.CharField( required=True, label='姓（アルファベット）' )
    first_name = forms.CharField( required=False, label='名（アルファベット）' )
    last_name_kannji = forms.CharField( required=False, label='姓（漢字）' )
    first_name_kannji = forms.CharField( required=False, label='名（漢字）' )
    age = forms.CharField( required=False, label='年齢' )
    work = forms.CharField( required=False,
                            label='職業',
                            widget=forms.Select( choices=WORKS ),
                            )
    phone = forms.CharField( required=False, label='電話' )
    gender = forms.CharField(
        required=False,
        label="性別",
        widget=forms.Select( choices=GENDER ),
        )
    birth = forms.DateField(
        required=False,
        label=pgettext_lazy( "Address form field label", "生年月日" ),
        widget=forms.DateInput( attrs={ "type": "date" } ),
        )
    note = forms.CharField( required=False, label='ノート' )
    # ------------------------------------------------
    postal_code = forms.IntegerField( required=False, label="郵便番号" )
    city_area = forms.CharField( required=False, label="都道府県" )
    city = forms.CharField( required=False, label="市" )
    street_address_1 = forms.CharField( required=False, label="区町村" )
    street_address_2 = forms.CharField( required=False, label="番地・建物名・部屋番号" )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

# -----------------------暂时不用---------------------------暂时不用---------------------------
# -----------------------暂时不用---------------------------暂时不用---------------------------
# -----------------------暂时不用---------------------------暂时不用---------------------------


# class ProductStockImageForm(forms.ModelForm):
#     use_required_attribute = False
#     class Meta:
#         model = ProductStockImage
#         exclude = ("product", "sort_order")
#         labels = {
#             "image": pgettext_lazy("Product image", "画像"),
#             "alt": pgettext_lazy("Description", "説明"),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance.image:
#             self.fields["image"].widget = ImagePreviewWidget()
#
#     def save(self, commit=True):
#         image = super().save(commit=commit)
#         create_product_thumbnails.delay(image.pk)
#         return image


#
# class ExtraInformationMixin:
#     """Form mixin that dynamically adds attribute fields."""
#
#     available_extra_information = ExtraInformation.objects.none()
#
#     def prepare_fields_for_extra_information(self):
#         initial_extra_information = self.instance.extra_informations
#
#         for extra_information in self.available_extra_information:
#
#             extra_information_rel = initial_extra_information.filter(
#                 assignment__attribute_id=extra_information.pk
#             ).first()
#             initial = None if extra_information_rel is None else extra_information_rel.values.first()
#
#             field_defaults = {
#                 "label": extra_information.name,
#                 "required": False,
#                 "initial": initial,
#             }
#
#             if extra_information.has_values():
#                 field = ModelChoiceOrCreationField(
#                     queryset=extra_information.values.all(), **field_defaults
#                 )
#             else:
#                 field = forms.CharField(**field_defaults)
#
#             self.fields[extra_information.get_formfield_name()] = field
#
#     def iter_extra_information_fields(self):
#         """In use in templates to retrieve the attributes input fields."""
#         for extra_info in self.available_extra_information:
#             yield self[extra_info.get_formfield_name()]
#
#     def save_extra_information(self):
#         assert self.instance.pk is not None, "The instance must be saved first"
#
#         for extra_info in self.available_extra_information:
#             value = self.cleaned_data.pop(extra_info.get_formfield_name())
#
#             # Skip if no value was supplied for that attribute
#             if not value:
#                 continue
#
#             # If the passed attribute value is a string, create the attribute value.
#             if not isinstance(value, ExtraInformation):
#                 value = ExtraInformation.objects.create(
#                     id=extra_info.pk, name=value, slug=slugify(value)
#                 )
#
#             # associate_attribute_values_to_instance(self.instance, extra_info, value)
#
#
