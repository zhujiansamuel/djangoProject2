#  dashboard   ----------------------------------  dashboard #
from django import forms
from django.utils.translation import npgettext, pgettext_lazy
from django_filters import (
    NumberFilter,
    CharFilter,
    ChoiceFilter,
    MultipleChoiceFilter,
    ModelMultipleChoiceFilter,
    DateFromToRangeFilter,
    RangeFilter,
)
from kingbuy.account.models import User
from kingbuy.core.filters import SortedFilterSet
from kingbuy.core.widgets import (
    MoneyRangeWidget,
    DateRangeWidget,
    )


from ..product_stock import (
    ProductStockManageStatus,
    InventoryStatus,
    )


from ..product_stock.models import (
    Suppliers,
    LegalPerson,
    Shops,
    ProductStockStatus,
    ExtraInformation,
    ProductStock,
    ProductObjectStock,
    ManualInventoryManage,
    StoreToStoreManage,
    BarterManage,
    OrderManage,
    )
#  dashboard   ----------------------------------  dashboard #
PRODUCT_OBJECT_STOCK_IS_ALLOCATE = {
    ("1",pgettext_lazy("IS_ALLOCATE","分配済")),
    ("0",pgettext_lazy("IS_ALLOCATE","分配無")),
    }
PRODUCT_OBJECT_STOCK_IS_LOCK = {
    ("1",pgettext_lazy("IS_ALLOCATE","ロック")),
    ("0",pgettext_lazy("IS_ALLOCATE","ロック解除")),
    }
PRODUCT_OBJECT_STOCK_IS_AVAILABLE = {
    ("1",pgettext_lazy("IS_ALLOCATE","利用可能")),
    ("0",pgettext_lazy("IS_ALLOCATE","利用不可")),
    }
PRODUCT_OBJECT_STOCK_IS_TEMP = {
    ("1",pgettext_lazy("IS_ALLOCATE","入庫予定中")),
    ("0",pgettext_lazy("IS_ALLOCATE","入庫済または入庫取消")),
    }
PRODUCT_OBJECT_STOCK_IS_OUT_OF_STOCK = {
    ("1",pgettext_lazy("IS_ALLOCATE","在庫切れ")),
    ("0",pgettext_lazy("IS_ALLOCATE","在庫または入庫予定")),
    }
SUPPLIERS_GENDER = {
    ("男性",pgettext_lazy("IS_ALLOCATE","男性")),
    ("女性",pgettext_lazy("IS_ALLOCATE","女性")),
    }

#  dashboard   ----------------------------------  dashboard #





class ProductStockFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy("Product_stock list filter label", "商品類名前"),
        lookup_expr="icontains",
    )
    jan_code = CharFilter(
        label=pgettext_lazy("Product_stock list filter label", "JAN"),
        lookup_expr="icontains",
    )

    price_average = RangeFilter(
        label=pgettext_lazy("Product list filter label", "Price"),
        field_name="price_average_amount",
        widget=MoneyRangeWidget,
    )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = ProductStock
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個商品類を発見",
            " %(counter)d 個商品類を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class ProductObjectStockFilter(SortedFilterSet):
    imei_code = CharFilter(
        label=pgettext_lazy("Product_stock list filter label", "IMEI"),
        lookup_expr="icontains",
    )

    price_average = RangeFilter(
        label=pgettext_lazy("Product list filter label", "平均価格"),
        field_name="price_average_amount",
        widget=MoneyRangeWidget,
    )
    extra_informations = ModelMultipleChoiceFilter(
        label=pgettext_lazy("Product list filter label", "追加情報"),
        field_name="extra_informations",
        queryset=ExtraInformation.objects.all(),
    )
    manage_status = MultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "在庫管理状態" ),
        field_name="manage_status",
        choices=ProductStockManageStatus.CHOICES,
        )
    status = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "商品状態" ),
        field_name="extra_informations",
        queryset=ProductStockStatus.objects.all(),
        )
    shops = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "店舗別" ),
        field_name="extra_informations",
        queryset=Shops.objects.all(),
        )
    is_allocate = ChoiceFilter(
        label=pgettext_lazy("Product list filter label", "分配"),
        choices=PRODUCT_OBJECT_STOCK_IS_ALLOCATE,
        empty_label=pgettext_lazy("Filter empty choice label", "全て"),
        widget=forms.Select,
    )
    is_lock = ChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "ロック" ),
        choices=PRODUCT_OBJECT_STOCK_IS_LOCK,
        empty_label=pgettext_lazy( "Filter empty choice label", "全て" ),
        widget=forms.Select,
        )
    is_available_M = ChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "利用可能" ),
        choices=PRODUCT_OBJECT_STOCK_IS_AVAILABLE,
        empty_label=pgettext_lazy( "Filter empty choice label", "全て" ),
        widget=forms.Select,
        )
    is_temp = ChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "入庫予定" ),
        choices=PRODUCT_OBJECT_STOCK_IS_TEMP,
        empty_label=pgettext_lazy( "Filter empty choice label", "全て" ),
        widget=forms.Select,
        )
    is_out_of_stock = ChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "在庫切れ" ),
        choices=PRODUCT_OBJECT_STOCK_IS_OUT_OF_STOCK,
        empty_label=pgettext_lazy( "Filter empty choice label", "全て" ),
        widget=forms.Select,
        )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = ProductObjectStock
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個商品を発見",
            " %(counter)d 個商品を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class OrderManageFilter(SortedFilterSet):
    id = NumberFilter(
        label=pgettext_lazy( "OrderManage list filter label", "注文出入庫執行表ID" ),
        )

    slip_number = CharFilter(
        label=pgettext_lazy("OrderManage list filter label", "伝票番号"),
        lookup_expr="icontains",
    )

    created = DateFromToRangeFilter(
        label=pgettext_lazy("OrderManage list filter label", "作成日付"),
        field_name="created",
        widget=DateRangeWidget,
        )
    suppliers = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "取引先(個人)" ),
        field_name="suppliers",
        queryset=Suppliers.objects.all(),
        )
    legal_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "取引先(法人)" ),
        field_name="legal_person",
        queryset=LegalPerson.objects.all(),
        )
    order_status = MultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "注文出入庫執行表状態" ),
        field_name="order_status",
        choices=InventoryStatus.CHOICES,
        )
    total = RangeFilter(
        label=pgettext_lazy("Product list filter label", "金額"),
        field_name="total_amount",
        widget=MoneyRangeWidget,
    )
    responsible_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "Product list filter label", "責任者" ),
        field_name="responsible_person",
        queryset=User.objects.filter(is_staff=True),
        )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = OrderManage
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個注文出入庫執行表を発見",
            " %(counter)d 個注文出入庫執行表を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class BarterManageFilter(SortedFilterSet):
    id = NumberFilter(
        label=pgettext_lazy( "BarterManage list filter label", "物々交換執行表ID" ),
        )

    slip_number = CharFilter(
        label=pgettext_lazy("BarterManage list filter label", "伝票番号"),
        lookup_expr="icontains",
    )

    created = DateFromToRangeFilter(
        label=pgettext_lazy("BarterManage list filter label", "作成日付"),
        field_name="created",
        widget=DateRangeWidget,
        )
    suppliers = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "BarterManage list filter label", "取引先(個人)" ),
        field_name="suppliers",
        queryset=Suppliers.objects.all(),
        )
    legal_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "BarterManage list filter label", "取引先(法人)" ),
        field_name="legal_person",
        queryset=LegalPerson.objects.all(),
        )
    barter_status = MultipleChoiceFilter(
        label=pgettext_lazy( "BarterManage list filter label", "物々交換執行表状態" ),
        field_name="barter_status",
        choices=InventoryStatus.CHOICES,
        )
    total = RangeFilter(
        label=pgettext_lazy("BarterManage list filter label", "金額"),
        field_name="total_amount",
        widget=MoneyRangeWidget,
    )
    responsible_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "BarterManage list filter label", "責任者" ),
        field_name="responsible_person",
        queryset=User.objects.filter(is_staff=True),
        )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = BarterManage
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個物々交換執行表を発見",
            " %(counter)d 個物々交換執行表を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class StoreToStoreManageFilter(SortedFilterSet):
    id = NumberFilter(
        label=pgettext_lazy( "StoreToStoreManage list filter label", "店舗間転移執行表ID" ),
        )

    slip_number = CharFilter(
        label=pgettext_lazy("StoreToStoreManage list filter label", "伝票番号"),
        lookup_expr="icontains",
    )

    created = DateFromToRangeFilter(
        label=pgettext_lazy("StoreToStoreManage list filter label", "作成日付"),
        field_name="created",
        widget=DateRangeWidget,
        )
    to_shop = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "StoreToStoreManage list filter label", "移動先" ),
        field_name="to_shop",
        queryset=Shops.objects.all(),
        )
    store_to_store_status = MultipleChoiceFilter(
        label=pgettext_lazy( "StoreToStoreManage list filter label", "店舗間転移執行表状態" ),
        field_name="barter_status",
        choices=InventoryStatus.CHOICES,
        )
    responsible_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "StoreToStoreManage list filter label", "責任者" ),
        field_name="responsible_person",
        queryset=User.objects.filter(is_staff=True),
        )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = StoreToStoreManage
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個店舗間転移執行表を発見",
            " %(counter)d 個店舗間転移執行表を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class ManualInventoryManageFilter(SortedFilterSet):
    id = NumberFilter(
        label=pgettext_lazy( "ManualInventoryManage list filter label", "商品ロック執行表ID" ),
        )

    slip_number = CharFilter(
        label=pgettext_lazy("ManualInventoryManage list filter label", "伝票番号"),
        lookup_expr="icontains",
    )
    created = DateFromToRangeFilter(
        label=pgettext_lazy("ManualInventoryManage list filter label", "作成日付"),
        field_name="created",
        widget=DateRangeWidget,
        )
    manual_inventory_status = MultipleChoiceFilter(
        label=pgettext_lazy( "ManualInventoryManage list filter label", "商品ロック執行表状態" ),
        field_name="barter_status",
        choices=InventoryStatus.CHOICES,
        )
    responsible_person = ModelMultipleChoiceFilter(
        label=pgettext_lazy( "ManualInventoryManage list filter label", "責任者" ),
        field_name="responsible_person",
        queryset=User.objects.filter(is_staff=True),
        )
    total = RangeFilter(
        label=pgettext_lazy("ManualInventoryManage list filter label", "金額"),
        field_name="total_amount",
        widget=MoneyRangeWidget,
    )
    # sort_by = OrderingFilter(
    #     label=pgettext_lazy("Product list filter label", "Sort by"),
    #     fields=PRODUCT_SORT_BY_FIELDS.keys(),
    #     field_labels=PRODUCT_SORT_BY_FIELDS,
    # )

    class Meta:
        model = ManualInventoryManage
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個商品ロック執行表を発見",
            " %(counter)d 個商品ロック執行表を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())



class SuppliersFilter(SortedFilterSet):
    email = CharFilter(
        label=pgettext_lazy("Suppliers list filter label", "メール"),
        lookup_expr="icontains",
        )
    last_name = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "姓()" ),
        lookup_expr="icontains",
        )
    first_name = CharFilter(
        label=pgettext_lazy("Suppliers list filter label", "名()"),
        lookup_expr="icontains",
        )
    last_name_kannji = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "姓(漢字)" ),
        lookup_expr="icontains",
        )
    first_name_kannji = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "名(漢字)" ),
        lookup_expr="icontains",
        )
    phone = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "電話番号" ),
        lookup_expr="icontains",
        )
    age = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "年齢" ),
        lookup_expr="icontains",
        )
    gender = ChoiceFilter(
        label=pgettext_lazy("Product list filter label", "性別"),
        choices=SUPPLIERS_GENDER,
        empty_label=pgettext_lazy("Filter empty choice label", "全て"),
        widget=forms.Select,
    )
    work = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "仕事" ),
        lookup_expr="icontains",
        )
    note = CharFilter(
        label=pgettext_lazy( "Suppliers list filter label", "ノート" ),
        lookup_expr="icontains",
        )
    class Meta:
        model = Suppliers
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個取引先(個人)を発見",
            " %(counter)d 個取引先(個人)を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())




class LegalPersonFilter(SortedFilterSet):
    email = CharFilter(
        label=pgettext_lazy("LegalPerson list filter label", "メール"),
        lookup_expr="icontains",
        )
    phone = CharFilter(
        label=pgettext_lazy( "LegalPerson list filter label", "電話番号" ),
        lookup_expr="icontains",
        )
    fax = CharFilter(
        label=pgettext_lazy( "LegalPerson list filter label", "FAX" ),
        lookup_expr="icontains",
        )
    note = CharFilter(
        label=pgettext_lazy( "LegalPerson list filter label", "ノート" ),
        lookup_expr="icontains",
        )
    homepage = CharFilter(
        label=pgettext_lazy( "LegalPerson list filter label", "ホームページ" ),
        lookup_expr="icontains",
        )
    class Meta:
        model = LegalPerson
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            "Number of matching records in the dashboard products list",
            " %(counter)d 個取引先(法人)を発見",
            " %(counter)d 個取引先(法人)を発見",
            number=counter,
        ) % {"counter": counter}

    def get_total(self):
        return str(self.qs.count())


#  dashboard   ----------------------------------  dashboard #
