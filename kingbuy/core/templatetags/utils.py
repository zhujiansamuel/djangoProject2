from json import dumps
from draftjs_sanitizer import SafeJSONEncoder
from django.template import Library
from urllib.parse import urlencode
from django.template.defaultfilters import yesno
from django.utils.translation import pgettext_lazy
from django import forms
from django_filters.fields import RangeField
from django.templatetags.static import static

register = Library()


@register.simple_tag(takes_context=True)
def serialize_messages(context):
    """Serialize django.contrib.messages to JSON."""
    messages = context.get("messages", [])
    data = {}
    for i, message in enumerate(messages):
        data[i] = str(message)
    return dumps(data, cls=SafeJSONEncoder)




CHIPS_PATTERN = "%s: %s"


def handle_default(field, request_get):
    """Build a list of chips using raw field's value."""
    return [
        {
            "content": CHIPS_PATTERN % (field.label, field.value()),
            "link": get_cancel_url(request_get, field.name),
        }
    ]


def handle_single_choice(field, request_get):
    """Build a list of chips for ChoiceField field."""
    for choice_value, choice_label in field.field.choices:
        if choice_value == field.value():
            item = {
                "content": CHIPS_PATTERN % (field.label, choice_label),
                "link": get_cancel_url(request_get, field.name),
            }
            return [item]
    return []


def handle_multiple_choice(field, request_get):
    """Build a list of chips for MultipleChoiceField field."""
    items = []
    for value in field.value():
        for choice_value, choice_label in field.field.choices:
            if choice_value == value:
                items.append(
                    {
                        "content": CHIPS_PATTERN % (field.label, choice_label),
                        "link": get_cancel_url(request_get, field.name, value),
                    }
                )
    return items


def handle_single_model_choice(field, request_get):
    """Build a list of chips for ModelChoiceField field."""
    for obj in field.field.queryset:
        if str(obj.pk) == str(field.value()):
            return [
                {
                    "content": CHIPS_PATTERN % (field.label, str(obj)),
                    "link": get_cancel_url(request_get, field.name),
                }
            ]
    return []


def handle_multiple_model_choice(field, request_get):
    """Build a list of chips for ModelMultipleChoiceField field."""
    items = []
    for pk in field.value():
        # iterate over field's queryset to match the selected object
        for obj in field.field.queryset:
            if str(obj.pk) == str(pk):
                items.append(
                    {
                        "content": CHIPS_PATTERN % (field.label, str(obj)),
                        "link": get_cancel_url(request_get, field.name, pk),
                    }
                )
    return items


def handle_nullboolean(field, request_get):
    """Build a list of chips for NullBooleanField field."""
    value = yesno(
        field.value(), pgettext_lazy("Possible values of boolean filter", "yes,no,all")
    )
    return [
        {
            "content": CHIPS_PATTERN % (field.label, value),
            "link": get_cancel_url(request_get, field.name),
        }
    ]


def handle_range(field, request_get):
    """Build a list of chips for RangeField field."""
    items = []
    values = [f if f else None for f in field.value()]
    range_edges = ["min", "max"]
    range_labels = [
        pgettext_lazy("Label of first value in range filter", "From %(value)s"),
        pgettext_lazy("Label of second value in range filter", "To %(value)s"),
    ]
    for value, edge, label in zip(values, range_edges, range_labels):
        if value:
            param_name = "%s_%s" % (field.name, edge)
            items.append(
                {
                    "content": CHIPS_PATTERN % (field.label, label % {"value": value}),
                    "link": get_cancel_url(request_get, param_name),
                }
            )
    return items


def get_cancel_url(request_get, param_name, param_value=None):
    """Build a new URL from a query dict excluding given parameter.

    `request_get` - dictionary of query parameters
    `param_name` - name of a parameter to exclude
    `param_value` - value of a parameter value to exclude (in case a parameter
    has multiple values)
    """
    new_request_get = {
        k: request_get.getlist(k) for k in request_get if k != param_name
    }
    param_values_list = request_get.getlist(param_name)
    if len(param_values_list) > 1 and param_value is not None:
        new_param_values = [v for v in param_values_list if v != param_value]
        new_request_get[param_name] = new_param_values
    cancel_url = "?" + urlencode(new_request_get, True)
    return cancel_url





@register.inclusion_tag("core_templates/_filters.html", takes_context=True)
def filters(context, filter_set, sort_by_filter_name="sort_by"):
    """Render the filtering template based on the filter set."""
    chips = []
    request_get = context["request"].GET.copy()
    for filter_name in filter_set.form.cleaned_data.keys():
        if filter_name == sort_by_filter_name:
            # Skip processing of sort_by filter, as it's rendered differently
            continue

        field = filter_set.form[filter_name]
        if field.value() not in ["", None]:
            if isinstance(field.field, forms.NullBooleanField):
                items = handle_nullboolean(field, request_get)
            elif isinstance(field.field, forms.ModelMultipleChoiceField):
                items = handle_multiple_model_choice(field, request_get)
            elif isinstance(field.field, forms.MultipleChoiceField):
                items = handle_multiple_choice(field, request_get)
            elif isinstance(field.field, forms.ModelChoiceField):
                items = handle_single_model_choice(field, request_get)
            elif isinstance(field.field, forms.ChoiceField):
                items = handle_single_choice(field, request_get)
            elif isinstance(field.field, RangeField):
                items = handle_range(field, request_get)
            else:
                items = handle_default(field, request_get)
            chips.extend(items)
    return {
        "chips": chips,
        "filter": filter_set,
        "sort_by": request_get.get(sort_by_filter_name, None),
    }


@register.inclusion_tag("core_templates/_sorting_header.html", takes_context=True)
def sorting_header(context, field, label, is_wide=False):
    """Render a table sorting header."""
    request = context["request"]
    request_get = request.GET.copy()
    sort_by = request_get.get("sort_by")

    # path to icon indicating applied sorting
    sorting_icon = ""

    # flag which determines if active sorting is on field
    is_active = False

    if sort_by:
        if field == sort_by:
            is_active = True
            # enable ascending sort
            # new_sort_by is used to construct a link with already toggled
            # sort_by value
            new_sort_by = "-%s" % field
            # sorting_icon = static("images/arrow-up-icon.svg")
        else:
            # enable descending sort
            new_sort_by = field
            if field == sort_by.strip("-"):
                is_active = True
                # sorting_icon = static("images/arrow-down-icon.svg")
    else:
        new_sort_by = field

    request_get["sort_by"] = new_sort_by
    return {
        "url": "%s?%s" % (request.path, request_get.urlencode()),
        "is_active": is_active,
        "sorting_icon": sorting_icon,
        "label": label,
        "is_wide": is_wide,
    }
