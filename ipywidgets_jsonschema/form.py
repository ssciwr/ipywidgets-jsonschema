import copy
import datetime

from IPython.display import display
from packaging import version

import collections
import ipywidgets
import jsonschema
from jsonschema.validators import Draft7Validator
import json
import os
import re
import traitlets
import collections.abc
from pydantic import BaseModel

# We are providing some compatibility for ipywidgets v7 and v8
IS_VERSION_8 = version.parse(ipywidgets.__version__).major == 8

# We currently do not support all the format options that the
# JSONSchema standard supports:
# https://json-schema.org/understanding-json-schema/reference/string#built-in-formats
SUPPORTED_FORMATS_VERSION_7 = []
SUPPORTED_FORMATS_VERSION_8 = ["date-time", "time", "date"]
STRING_FORMATS = ["email", "hostname", "ipv4", "ipv6", "uri", "uuid"]
REGEX_DICT = {
    "email": r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$",
    "hostname": r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$",
    "ipv4": r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$",
    "ipv6": r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))",
    "uri": r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*):(?://(?:[a-zA-Z0-9\-._~%!$&\'()*+,;=]+@)?(?:\[[^\]]+\]|[a-zA-Z0-9\-._~%]+)(?::\d+)?)?(?:/[a-zA-Z0-9\-._~%!$&\'()*+,;=:@]*)*(?:\?[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/?]*)?(?:#[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/?]*)?$",
    "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$",
}


class FormError(Exception):
    pass


FormElement = collections.namedtuple(
    "FormElement",
    ["getter", "setter", "resetter", "widgets", "subelements", "register_observer"],
)


def as_tuple(obj):
    if isinstance(obj, collections.abc.Iterable) and not isinstance(obj, str):
        return obj
    else:
        return (obj,)


def convert_pydantic_to_schema(model) -> dict:
    """
    Converts a Pydantic model class to its corresponding JSON schema.
    """
    if isinstance(model, type) and issubclass(model, BaseModel):
        return model.model_json_schema()
    return model


def minmax_schema_rule(widget, schema):
    """This implements the minimum/maximum rules

    Only used for inputs bounded from one side, as ipywidgets
    has dedicated widgets for inputs bound from both sides. Defined
    in a separate function, because it used twice for number and
    integer widgets.
    """

    mapping = {
        "minimum": lambda x, y: x < y,
        "maximum": lambda x, y: x > y,
        "exclusiveMinimum": lambda x, y: x <= y,
        "exclusiveMaximum": lambda x, y: x >= y,
    }

    for rule, operator in mapping.items():
        if rule in schema:

            def _create_handler(r, op, minmax):
                def _handler(change):
                    if op(widget.value, minmax):
                        if r.startswith("exclusive"):
                            widget.value = change["old"]
                        else:
                            widget.value = minmax

                return _handler

            widget.observe(_create_handler(rule, operator, schema[rule]), names="value")

    return widget


class Form:
    def __init__(
        self,
        schema,
        vertically_place_labels=False,
        use_sliders=False,
        preconstruct_array_items=0,
        sorter=sorted,
        date_time_fmt_func=lambda dt: dt.isoformat(),
        date_time_parse_func=datetime.datetime.fromisoformat,
        date_fmt_func=lambda dt: dt.isoformat(),
        date_parse_func=datetime.date.fromisoformat,
        time_fmt_func=lambda dt: dt.isoformat(),
        time_parse_func=datetime.time.fromisoformat,
        show_descriptions=False,
    ):
        """Create a form with Jupyter widgets from a JSON schema

        :param schema:
            The JSON schema for the data object that the form should generate.
            The schema is expected to conform to the Draft 07 JSON schema standard.
            We do *not* implement the full standard, but incrementally add the
            functionality that we need.
        :type schema: dict
        :param vertically_place_labels:
            Whether labels for input fields should be placed next to the input widget
            horizontally or vertically.
        :type vertically_place_labels: bool
        :param use_sliders:
            Whether bounded input fields should use sliders or regular input widgets
        :type use_sliders: bool
        :param preconstruct_array_items:
            How many array item widgets should be pre-generated. For very complex
            subschemas for each array item, this can be a performance optimization
            trading construction time vs. usage delay.
        :type preconstruct_array_items: int
        :param sorter:
            A function that is used to sort the keys in a dictionary. Defaults to
            the built-in sorted, but is no-op if sorted raises a TypeError.
        """
        schema = convert_pydantic_to_schema(schema)
        # Make sure that the given schema is valid
        Draft7Validator.check_schema(schema)

        # Store the given data members
        self.schema = schema
        self.vertically_place_labels = vertically_place_labels
        self.use_sliders = use_sliders
        self.preconstruct_array_items = preconstruct_array_items
        self.sorter = sorter
        self.date_time_fmt_func = date_time_fmt_func
        self.date_time_parse_func = date_time_parse_func
        self.date_fmt_func = date_fmt_func
        self.date_parse_func = date_parse_func
        self.time_fmt_func = time_fmt_func
        self.time_parse_func = time_parse_func
        self.show_descriptions = show_descriptions

        self._construction_stack = []
        # Store a list of registered observers to add them to runtime-generated widgets
        self._observers = []

        # Construct the widgets
        self._form_element = self._construct(schema, root=True, label=None)

    def construct_element(
        self,
        getter=lambda: None,
        setter=lambda _: None,
        resetter=lambda: None,
        widgets=[],
        subelements=[],
        register_observer=lambda h, n, t: None,
    ):
        return FormElement(
            getter=getter,
            setter=setter,
            resetter=resetter,
            widgets=widgets,
            subelements=subelements,
            register_observer=register_observer,
        )

    def observe(self, handler, names=traitlets.All, type="change"):
        """Register a change handler with all the widgets that support it"""
        self._observers.append((handler, names, type))
        self._form_element.register_observer(handler, names, type)

    @property
    def widget(self):
        """Return the resulting widget for further use"""
        return ipywidgets.VBox(self._form_element.widgets)

    def show(self, width="100%"):
        """Show the resulting combined widget in the Jupyter notebook"""
        w = ipywidgets.VBox(
            self._form_element.widgets, layout=ipywidgets.Layout(width=width)
        )
        display(w)

    @property
    def data(self):
        """Get a (non-updating) snapshot of the current form data

        :returns:
            A dictionary that reflects the current state of the widget and
            conforms to the given schema.
        """
        # Construct the data by calling all the data handlers on an empty dictionary
        data = self._form_element.getter()

        # Validate the resulting document just to be sure
        jsonschema.validate(instance=data, schema=self.schema)

        return data

    @data.setter
    def data(self, _data):
        # Ensure that the given data even validates against the schema
        jsonschema.validate(instance=_data, schema=self.schema)

        # Update all widgets according to the given data
        self._form_element.setter(_data)

    def _construct(self, schema, label=None, root=False):
        if schema in self._construction_stack and not (
            "$ref" in schema or "enum" in schema
        ):
            return self.construct_element()
        self._construction_stack.append(schema)

        # Enumerations are handled a dropdowns
        if "enum" in schema:
            return self._construct_enum(schema, label=label)

        # anyOf rules are handled with dropdown selections
        if "anyOf" in schema:
            return self._construct_anyof(schema, label=label)

        # We use the same code for oneOf and allOf - if the data cannot be validated,
        # a validation error will be thrown when accessing the data. There is no
        # upfront checking in the form.
        if "oneOf" in schema:
            return self._construct_anyof(schema, label=label, key="oneOf")
        if "allOf" in schema:
            return self._construct_anyof(schema, label=label, key="allOf")

        # Handle other input based on the input type
        type_ = schema.get("type", None)
        if type_ is None:
            if "$ref" in schema:
                return self._construct_ref(schema, label=label)
            raise FormError(
                f"Expecting type information for non-enum properties, schema: {schema}"
            )
        if not isinstance(type_, str):
            raise FormError("Not accepting arrays of types currently")

        # Maybe this is using a built-in format
        format_ = schema.get("format", None)
        if format_ is not None:
            if (
                (IS_VERSION_8 and format_ in SUPPORTED_FORMATS_VERSION_8)
                or (not IS_VERSION_8 and format_ in SUPPORTED_FORMATS_VERSION_7)
                or (format_ in STRING_FORMATS)
            ):
                if format_ in REGEX_DICT:
                    return self._construct_format(
                        schema, REGEX_DICT[format_], label, root=root
                    )
                type_ = format_.replace("-", "_")

        result = getattr(self, f"_construct_{type_}")(schema, label=label, root=root)
        self._construction_stack.pop()
        return result

    def _wrap_accordion(self, widget_list, schema, label=None):
        titles = []
        if label is not None or "title" in schema:
            titles = [schema.get("title", label)]

        if IS_VERSION_8:
            accordion = ipywidgets.Accordion(
                children=[ipywidgets.VBox(widget_list)], titles=titles
            )
        else:
            accordion = ipywidgets.Accordion(children=[ipywidgets.VBox(widget_list)])
            for i, title in enumerate(titles):
                accordion.set_title(i, title)

        # This folds the accordion
        accordion.selected_index = None
        return [accordion]

    def _wrap_description(self, widget, tooltip):
        if self.show_descriptions and tooltip:
            layout = ipywidgets.Layout(display="flex", justify_content="flex-end")
            style = dict(font_size="0.8em", font_weight="lighter")
            widget = ipywidgets.VBox(
                [
                    widget,
                    ipywidgets.Label(tooltip, layout=layout, style=style),
                ]
            )

        return widget

    def _construct_object(self, schema, label=None, root=False):
        # Construct form elements for all the fields, including some that are
        # added through 'if'-'then' rules. This maps key -> FormElement
        elements = {}

        # Store the conditional information from the schema in the following form:
        # [(schema, cprop, element), ..]
        # with the following meaning:
        #   schema: The schema that the data needs to match
        #   cprop: The property that is maybe added
        #   element: The subelement for the property
        conditionals = []

        if "properties" in schema:
            for prop, subschema in schema["properties"].items():
                elements[prop] = self._construct(subschema, label=prop)
        elif "additionalProperties" in schema:
            # Handle dictionaries with dynamically defined keys and values
            elements["dict_container"] = self._construct_dict(
                schema, label=label
            )  # call the new function for dict

            widget_list = elements[
                "dict_container"
            ].widgets  # get dict_container widgets
            # Maybe wrap this in an Accordion widget
            wrapped_widget_list = widget_list
            if not root and label is not None:
                wrapped_widget_list = self._wrap_accordion(
                    widget_list, schema, label=label
                )

            def _getter():
                return elements["dict_container"].getter()

            def _setter(_d):
                elements["dict_container"].setter(_d)

            def _register_observer(h, n, t):
                elements["dict_container"].register_observer(h, n, t)

            def _resetter():
                elements["dict_container"].resetter()

            return self.construct_element(
                getter=_getter,
                setter=_setter,
                resetter=_resetter,
                widgets=wrapped_widget_list,
                subelements=elements,
                register_observer=_register_observer,
            )

        else:
            widget_list = []

        # Handle the conditionals
        def add_conditional_elements(s):
            # Check whether we have an if statement
            cond = s.get("if", None)
            if cond is None:
                return

            for cprop, csubschema in s.get("then", {}).get("properties", {}).items():
                celem = self._construct(csubschema, label=cprop)
                conditionals.append((cond, cprop, celem))
                elements[cprop] = celem

            if "else" in s:
                add_conditional_elements(s["else"])

        add_conditional_elements(schema)

        # Apply sorting to the keys
        if "properties" in schema:
            keys = schema["properties"].keys()
            try:
                keys = self.sorter(keys)
            except TypeError:
                # If the keys cannot be compared, we stick to the original order
                pass

            # Collect the list of widgets: First the regular ones, then conditional ones
            widget_list = sum((elements[k].widgets for k in keys), [])
            widget_list.extend(
                [
                    ipywidgets.HBox(layout=ipywidgets.Layout(width="100%"))
                    for _ in range(len(conditionals))
                ]
            )
        else:
            widget_list = []

        # Maybe wrap this in an Accordion widget
        wrapped_widget_list = widget_list
        if (
            not root
            and len(schema.get("properties", {})) > 1
            and not "additionalProperties" in schema
        ):
            wrapped_widget_list = self._wrap_accordion(widget_list, schema, label=label)

        def _getter():
            # Get all regular properties
            result = {}
            if "properties" in schema:
                for k in schema["properties"].keys():
                    result[k] = elements[k].getter()

                # Add conditional properties
                for cschema, cprop, celem in conditionals:
                    try:
                        jsonschema.validate(instance=result, schema=cschema)
                        result[cprop] = celem.getter()
                    except jsonschema.ValidationError:
                        pass
            elif "additionalProperties" in schema:
                result = {}

            return result

        def _setter(_d):
            if "properties" in schema:
                for k in elements.keys():
                    if k in _d:
                        elements[k].setter(_d[k])
                    else:
                        elements[k].resetter()

        def _register_observer(h, n, t):
            if "properties" in schema:
                for e in elements.values():
                    e.register_observer(h, n, t)
            elif "additionalProperties" in schema:
                elements["dict_container"].register_observer(h, n, t)

        def _resetter():
            if "properties" in schema:
                for e in elements.values():
                    e.resetter()
            elif "additionalProperties" in schema:
                elements["dict_container"].resetter()

        # Add the conditional information
        if "properties" in schema:
            for i, (cschema, cprop, celem) in enumerate(conditionals):

                def create_observer(j, s, prop, e):
                    def _cond_observer(_):
                        # Check whether our data matches the given schema
                        try:
                            jsonschema.validate(instance=_getter(), schema=s)
                            elements[prop] = e
                            widget_list[len(keys) + j].children = e.widgets
                        except jsonschema.ValidationError:
                            widget_list[len(keys) + j].children = []

                    # We need to call the observer once so that we get a correctly
                    # initialized widget, because otherwise it triggers only if it
                    # differs from the default.
                    _cond_observer({})

                    return _cond_observer

                for k in cschema.get("properties", {}).keys():
                    elements[k].register_observer(
                        create_observer(i, cschema, cprop, celem), "value", "change"
                    )
        # Ensure that defaults are initialized
        _resetter()

        if self.show_descriptions:
            wrapped_widget_list = [
                self._wrap_description(
                    ipywidgets.VBox(
                        wrapped_widget_list, layout=ipywidgets.Layout(width="100%")
                    ),
                    schema.get("description", None),
                )
            ]

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=wrapped_widget_list,
            subelements=elements,
            register_observer=_register_observer,
        )

    def _construct_dict(self, schema, label=None):
        if "additionalProperties" not in schema:
            raise FormError(
                f"Expecting 'additionalProperties' key in schema for type dict: {schema}"
            )

        additional_props_schema = schema["additionalProperties"]

        # container for the input widgets

        widget = ipywidgets.VBox([])

        elements = []  # list of widgets corresponding to each key

        def _update_widget():
            widget.children = [ipywidgets.VBox(e.widgets) for e in elements]

        def add_dict_entry(key=None, value=None):
            if key is None or key == "":
                key = "key" + str(len(elements))

            key_widget = ipywidgets.Text(value=key, description="key")

            elem_dict = self._construct(additional_props_schema)

            trash = ipywidgets.Button(icon="trash")

            def remove_entry(_):
                # Identify the current list index of the entry
                for index, child in enumerate(widget.children):
                    if trash in child.children:
                        break

                elements.pop(index)

                # Remove it from the widget list and the handler list
                _update_widget()

            trash.on_click(remove_entry)

            def _dict_getter():
                return {key_widget.value: elem_dict.getter()}

            def _dict_setter(_dict):

                if key_widget.value in _dict:
                    elem_dict.setter(_dict[key_widget.value])
                else:
                    elem_dict.resetter()

            elements.append(
                self.construct_element(
                    getter=_dict_getter,
                    setter=_dict_setter,
                    resetter=elem_dict.resetter,
                    widgets=[
                        ipywidgets.HBox(
                            [key_widget, ipywidgets.VBox(elem_dict.widgets), trash]
                        )
                    ],
                )
            )
            _update_widget()

        add_btn = ipywidgets.Button(
            description="Add key value",
            icon="plus",
            layout=ipywidgets.Layout(width="100%"),
        )
        add_btn.on_click(lambda x: add_dict_entry())

        widget_list = [widget, add_btn]

        def _getter():

            data = {}
            for e in elements:
                data.update(e.getter())

            return data

        def _setter(_d):

            for e in elements:
                key = list(e.getter().keys())[0]
                if key in _d:
                    e.setter(_d)
                else:
                    e.resetter()

            # check for keys that need to added
            keys = [list(e.getter().keys())[0] for e in elements]
            for key, value in _d.items():

                if key not in keys:
                    add_dict_entry(key=key, value=value)

        def _register_observer(h, n, t):
            for e in elements:
                e.register_observer(h, n, t)

        def _resetter():
            if "default" in schema:
                _setter(schema["default"])

        _resetter()

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=widget_list,
            register_observer=_register_observer,
        )

    def _construct_simple(self, schema, widget, label=None, root=False):
        # Extract the best description that we have
        tooltip = schema.get("description", None)

        # Construct the label widget that describes the input
        box = [widget]
        if label is not None or "title" in schema:
            # Extract the best guess for a title that we have
            title = schema.get("title", label)

            # Use the label as the backup tooltip
            if tooltip is None:
                tooltip = title

            # Prepend a label to the widget
            box.insert(
                0,
                ipywidgets.Label(
                    title,
                    layout=ipywidgets.Layout(width="100%"),
                ),
            )

        # Make sure that the widget shows the tooltip
        if tooltip is not None:
            widget.tooltip = tooltip

        # Apply potential constant values without generating a widget
        if "const" in schema:
            return self.construct_element(getter=lambda: schema["const"])

        # Apply regex pattern matching
        def pattern_checker(val):
            # This only makes sense for strings
            if schema["type"] != "string" or val is None:
                return True

            # Try matching the given data against the pattern
            pattern = schema.get("pattern", ".*")
            return re.fullmatch(pattern, val)

        # Describe how change handlers are registered
        def _register_observer(h, n, t):
            widget.observe(h, names=n, type=t)

        warning_label = ipywidgets.Label(
            "", layout=ipywidgets.Layout(color="red", display="none")
        )

        def _observer(change):
            if not pattern_checker(widget.value):
                pattern = schema.get("pattern", ".*")
                warning_label.value = (
                    f"Warning: Input does not match the specified pattern"
                )
                warning_label.layout.display = "block"
                change.owner.layout.border = "2px solid red"
            else:
                change.owner.layout.border = "none"
                warning_label.value = ""
                warning_label.layout.display = "none"

        widget.observe(_observer, names="value", type="change")

        def _setter(_d):
            if pattern_checker(_d):
                widget.value = _d
            else:
                # Check if its a valid format
                format_ = schema.get("format", None)
                if format_ is not None:
                    if format_ in REGEX_DICT:
                        raise FormError(
                            f"Value '{widget.value}' does not match the specified format '{schema['format']}'"
                        )
                    else:
                        raise FormError(
                            f"'{schema['format']}' is not a supported format."
                        )
                else:
                    # We will have to see whether or not throwing is a good idea here
                    raise FormError(
                        f"Value '{_d}' does not match the specified pattern '{schema['pattern']}'"
                    )

        def _resetter():
            # Apply a potential default
            if "default" in schema:
                widget.value = schema["default"]
            else:
                widget.value = widget.trait_defaults()["value"]
                if "minimum" in schema:
                    widget.value = schema["minimum"]
                if "maximum" in schema:
                    widget.value = schema["maximum"]

        def _getter():
            if not pattern_checker(widget.value):
                format_ = schema.get("format", None)
                if format_ is not None:
                    if format_ in REGEX_DICT:
                        raise FormError(
                            f"Value '{widget.value}' does not match the specified format'{schema['format']}'"
                        )
                    else:
                        raise FormError(
                            f"'{schema['format']}' is not a supported format."
                        )
                else:
                    # We will have to see whether or not throwing is a good idea here
                    raise FormError(
                        f"Value '{widget.value}' does not match the specified pattern '{schema['pattern']}'"
                    )

            return widget.value

        # Trigger generation of defaults in construction
        _resetter()

        # Make sure the widget adapts to the outer layout
        widget.layout = ipywidgets.Layout(width="100%")

        # Make the placing of labels optional
        box_type = ipywidgets.HBox
        if self.vertically_place_labels:
            box_type = ipywidgets.VBox

        box = box_type(box, layout=ipywidgets.Layout(width="100%"))
        box = self._wrap_description(box, tooltip)

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=[box, warning_label],
            register_observer=_register_observer,
        )

    def _construct_string(self, schema, label=None, root=False):
        return self._construct_simple(schema, ipywidgets.Text(), label=label)

    def _construct_date_time(self, schema, label=None, root=False):
        widget = ipywidgets.DatetimePicker()

        # Extract the best description that we have
        tooltip = schema.get("description", None)

        # Construct the label widget that describes the input
        box = [widget]
        if label is not None or "title" in schema:
            # Extract the best guess for a title that we have
            title = schema.get("title", label)

            # Use the label as the backup tooltip
            if tooltip is None:
                tooltip = title

            widget.description = title

        # Make sure that the widget shows the tooltip
        if tooltip is not None:
            widget.tooltip = tooltip

        def _register_observer(h, n, t):
            widget.observe(h, names=n, type=t)

        def _setter(_d):
            widget.value = self.date_time_parse_func(_d)

        def _resetter():
            # Apply a potential default
            if "default" in schema:
                widget.value = self.date_time_parse_func(schema["default"])
            else:
                widget.value = datetime.datetime.now()

        def _getter():
            if widget.value:
                return self.date_time_fmt_func(widget.value)
            return ""

        # Trigger generation of defaults in construction
        _resetter()

        # Make sure the widget adapts to the outer layout
        widget.layout = ipywidgets.Layout(width="100%")

        # Make the placing of labels optional
        box_type = ipywidgets.HBox
        if self.vertically_place_labels:
            box_type = ipywidgets.VBox

        box = box_type(box, layout=ipywidgets.Layout(width="100%"))
        box = self._wrap_description(box, tooltip)

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=[box],
            register_observer=_register_observer,
        )

    def _construct_date(self, schema, label=None, root=False):
        widget = ipywidgets.DatePicker()

        # Extract the best description that we have
        tooltip = schema.get("description", None)

        # Construct the label widget that describes the input
        box = [widget]
        if label is not None or "title" in schema:
            # Extract the best guess for a title that we have
            title = schema.get("title", label)

            # Use the label as the backup tooltip
            if tooltip is None:
                tooltip = title

            widget.description = title

        # Make sure that the widget shows the tooltip
        if tooltip is not None:
            widget.tooltip = tooltip

        def _register_observer(h, n, t):
            widget.observe(h, names=n, type=t)

        def _setter(_d):
            widget.value = self.date_parse_func(_d)

        def _resetter():
            # Apply a potential default
            if "default" in schema:
                widget.value = self.date_parse_func(schema["default"])
            else:
                widget.value = datetime.datetime.now()

        def _getter():
            if widget.value:
                return self.date_fmt_func(widget.value)
            return ""

        # Trigger generation of defaults in construction
        _resetter()

        # Make sure the widget adapts to the outer layout
        widget.layout = ipywidgets.Layout(width="100%")

        # Make the placing of labels optional
        box_type = ipywidgets.HBox
        if self.vertically_place_labels:
            box_type = ipywidgets.VBox

        box = box_type(box, layout=ipywidgets.Layout(width="100%"))
        box = self._wrap_description(box, tooltip)

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=[box],
            register_observer=_register_observer,
        )

    def _construct_time(self, schema, label=None, root=False):
        widget = ipywidgets.TimePicker()

        # Extract the best description that we have
        tooltip = schema.get("description", None)

        # Construct the label widget that describes the input
        box = [widget]
        if label is not None or "title" in schema:
            # Extract the best guess for a title that we have
            title = schema.get("title", label)

            # Use the label as the backup tooltip
            if tooltip is None:
                tooltip = title

            widget.description = title

        # Make sure that the widget shows the tooltip
        if tooltip is not None:
            widget.tooltip = tooltip

        def _register_observer(h, n, t):
            widget.observe(h, names=n, type=t)

        def _setter(_d):
            widget.value = self.time_parse_func(_d)

        def _resetter():
            # Apply a potential default
            if "default" in schema:
                widget.value = self.time_parse_func(schema["default"])
            else:
                widget.value = datetime.datetime.now()

        def _getter():
            if widget.value:
                return self.time_fmt_func(widget.value)
            return ""

        # Trigger generation of defaults in construction
        _resetter()

        # Make sure the widget adapts to the outer layout
        widget.layout = ipywidgets.Layout(width="100%")

        # Make the placing of labels optional
        box_type = ipywidgets.HBox
        if self.vertically_place_labels:
            box_type = ipywidgets.VBox

        box = box_type(box, layout=ipywidgets.Layout(width="100%"))
        box = self._wrap_description(box, tooltip)

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=[box],
            register_observer=_register_observer,
        )

    def _construct_format(self, schema, regex=None, label=None, root=False):
        schema["pattern"] = regex
        return self._construct_simple(schema, ipywidgets.Text(), label=label, root=root)

    def _construct_number(self, schema, label=None, root=False):
        kwargs = dict()
        if "multipleOf" in schema:
            kwargs["step"] = schema["multipleOf"]
        # Inputs bounded only from below or above are currently not supported
        # in ipywidgets - rather strange
        if "minimum" in schema and "maximum" in schema:
            _class = (
                ipywidgets.FloatSlider
                if self.use_sliders
                else ipywidgets.BoundedFloatText
            )
            return self._construct_simple(
                schema,
                _class(min=schema["minimum"], max=schema["maximum"], **kwargs),
                label=label,
            )
        else:
            widget = minmax_schema_rule(ipywidgets.FloatText(**kwargs), schema)
            return self._construct_simple(schema, widget, label=label)

    def _construct_integer(self, schema, label=None, root=False):
        kwargs = dict()
        if "multipleOf" in schema:
            kwargs["step"] = schema["multipleOf"]
        # Inputs bounded only from below or above are currently not supported
        # in ipywidgets - rather strange
        if "minimum" in schema and "maximum" in schema:
            _class = (
                ipywidgets.IntSlider if self.use_sliders else ipywidgets.BoundedIntText
            )
            return self._construct_simple(
                schema,
                _class(min=schema["minimum"], max=schema["maximum"], **kwargs),
                label=label,
            )
        else:
            widget = minmax_schema_rule(ipywidgets.IntText(**kwargs), schema)
            return self._construct_simple(schema, widget, label=label)

    def _construct_boolean(self, schema, label=None, root=False):
        # Extract the labelling for the checkbox
        title = schema.get("title", label)

        if title is None:
            raise FormError(
                "Fields of boolean type need to specify title or be part of a mapping"
            )

        return self._construct_simple(
            {k: v for k, v in schema.items() if k != "title"},
            ipywidgets.Checkbox(indent=False, description=title),
            label=None,
        )

    def _construct_null(self, schema, label=None, root=False):
        return self.construct_element()

    def _construct_array(self, schema, label=None, root=False):
        if "items" not in schema:
            raise FormError("Expecting 'items' key for 'array' type")

        # Determine whether this is a fixed length list
        fixed_length = schema.get("minItems", -1) == schema.get("maxItems", -2)

        # Construct a widget that allows to add an array entry
        button = ipywidgets.Button(
            description="Add entry", icon="plus", layout=ipywidgets.Layout(width="100%")
        )

        # Construct the final widget that will be updated by handlers
        vbox = ipywidgets.VBox([])

        # The subelements of this widget that are referenced in the
        # recursive implementation of this array element
        elements = []

        # We separately to store the size of the elements array. The reason
        # for this is that we do want to minimize the amount of element creations
        # as these are very costly for complex schemas
        element_size = 0

        # Trigger whenever the resulting widget needs update
        def update_widget():
            subwidgets = []
            for e in elements[:element_size]:
                if e.widgets:
                    subwidgets.extend(e.widgets)
            if not fixed_length:
                subwidgets.append(button)
            vbox.children = subwidgets

        def add_entry(_):
            nonlocal element_size

            # if we are at the specified maximum, add should be ignored
            if "maxItems" in schema:
                if element_size == schema["maxItems"]:
                    return

            def trigger_observers():
                # Adding or removing an entry to this widget should trigger all value change handlers.
                # As we do not have a proper widget to register the handler, we trigger it
                # ourselves. This should make proper use of traitlets.
                for h, n, t in self._observers:
                    if t == "change" and (n is traitlets.All or "value" in as_tuple(n)):
                        h(
                            {
                                "name": "value",
                                "old": {},
                                "new": {},
                                "owner": None,
                                "type": "change",
                            }
                        )

            # A new element should only be generated if we do not have an excess
            # one stored in the elements list
            if element_size == len(elements):
                # Create a new element by going into recursion
                recelem = self._construct(schema["items"], label=None)

                # Register existing observers
                for h, n, t in self._observers:
                    recelem.register_observer(h, n, t)

                # Add array controls to our new element
                trash = ipywidgets.Button(
                    icon="trash", layout=ipywidgets.Layout(width="33%")
                )
                up = ipywidgets.Button(
                    icon="arrow-up", layout=ipywidgets.Layout(width="33%")
                )
                down = ipywidgets.Button(
                    icon="arrow-down", layout=ipywidgets.Layout(width="33%")
                )

                def remove_entry(b):
                    nonlocal element_size

                    # If we are at the specified minimum, remove should be ignored
                    if "minItems" in schema:
                        if element_size == schema["minItems"]:
                            return

                    # Identify the current list index of the entry
                    for index, child in enumerate(vbox.children):
                        if child.children and b in child.children[1].children:
                            break

                    # Move the corresponding element to the back of the list
                    # and reduce the actual size
                    elements.append(elements.pop(index))
                    element_size = element_size - 1

                    # Remove it from the widget list and the handler list
                    update_widget()

                    # We trigger observers upon removing
                    trigger_observers()

                trash.on_click(remove_entry)

                def move(dir):
                    def _move(b):
                        items = list(vbox.children)
                        for i, it in enumerate(items):
                            if it.children and b in it.children[1].children:
                                newi = min(max(i + dir, 0), len(items) - 1)
                                items[i], items[newi] = items[newi], items[i]
                                elements[i], elements[newi] = (
                                    elements[newi],
                                    elements[i],
                                )
                                break

                        update_widget()

                    return _move

                # Register the handler for moving up and down
                up.on_click(move(-1))
                down.on_click(move(1))

                array_entry_widget = ipywidgets.VBox()
                children = []
                if recelem.widgets:
                    children.append(ipywidgets.VBox(recelem.widgets))
                if not fixed_length:
                    children.append(
                        ipywidgets.HBox(
                            [trash, up, down], layout=ipywidgets.Layout(width="100%")
                        )
                    )

                array_entry_widget.children = children

                # Modify recelem to our needs
                elemdict = recelem._asdict()
                elemdict["widgets"] = [array_entry_widget]

                # Insert this into the elements list
                elements.append(self.construct_element(**elemdict))

            # Maybe reset it to the default
            elements[element_size].resetter()

            # Regardless of whether we actually constructed an element or whether
            # we are reusing an existing one - we need to increase the size now
            element_size = element_size + 1

            # Trigger observes when item is added regardless whether it was preconstructed
            trigger_observers()

            update_widget()

        button.on_click(add_entry)

        # Initialize the widget with the minimal number of subwidgets
        for _ in range(max(schema.get("minItems", 0), self.preconstruct_array_items)):
            add_entry(_)
        element_size = schema.get("minItems", 0)
        update_widget()

        # If this is not the root document, we wrap this in an Accordion widget
        wrapped_vbox = [vbox]
        if not root:
            wrapped_vbox = self._wrap_accordion(wrapped_vbox, schema, label=label)

        def _setter(_d):
            nonlocal element_size

            # We reset element_size so that we can offload all handling of it
            # to add_entry which already does that.
            element_size = 0

            # Update the widget potentially constructing new ones.
            for i, item in enumerate(_d):
                add_entry(None)
                elements[i].setter(item)

            update_widget()

        def _register_observer(h, n, t):
            for e in elements:
                e.register_observer(h, n, t)

        def _resetter():
            # If a default was specified, we now set it
            if "default" in schema:
                _setter(schema["default"])

        # Initially call the resetter
        _resetter()

        def _getter():
            result = [h.getter() for h in elements[:element_size]]
            if schema.get("uniqueItems", False):
                result = list(set(result))
            return result

        wrapped_vbox[0] = self._wrap_description(
            wrapped_vbox[0], schema.get("description", None)
        )

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            resetter=_resetter,
            widgets=wrapped_vbox,
            subelements=elements,
            register_observer=_register_observer,
        )

    def _construct_enum(self, schema, label=None, root=False):
        # We omit trivial enums, but make sure that they end up in the result
        if len(schema["enum"]) == 1:
            return self.construct_element(getter=lambda: schema["enum"][0])

        # Otherwise, we use a dropdown menu
        return self._construct_simple(
            schema, ipywidgets.Dropdown(options=schema["enum"]), label=label
        )

    def _construct_anyof(self, schema, label=None, key="anyOf"):
        # If this is a trivial anyOf rule, we omit it:
        if len(schema[key]) == 1:
            if key == "allOf":
                sub_schema = deep_update_missing(
                    {k: v for k, v in schema.items() if k != key}, schema[key][0]
                )
            else:
                sub_schema = schema[key][0]
            return self._construct(sub_schema, label=label, root=False)

        # The list of subelements and their descriptive names
        names = []
        elements = []

        # Iterate over the given subschema
        for i, s in enumerate(schema[key]):

            if "title" in s:
                names.append(s["title"])
            elif "$ref" in s:
                names.append(s["$ref"].split("/")[-1])
            elif "type" in s:
                if (
                    s["type"] == "object"
                    and "properties" in s
                    and "title" in s["properties"]
                ):
                    names.append(s["properties"]["title"]["const"])
                else:
                    names.append(s["type"])
            elif "additionalProperties" in s and "title" in schema:
                names.append(f"Option {len(names) + 1}")

            else:
                names.append(f"Option {len(names) + 1}")

            elements.append(self._construct(s))

        # Create the selector and subschema widget
        selector = ipywidgets.Dropdown(options=names, value=names[0])
        widget = ipywidgets.VBox([selector] + elements[0].widgets)

        # Whenever there is a change, we switch the subschema widget
        def _select(_):
            widget.children = [selector] + elements[names.index(selector.value)].widgets

        selector.observe(_select)

        def _setter(_d):
            for i, s in enumerate(schema[key]):
                try:
                    jsonschema.validate(instance=_d, schema=s)
                    selector.value = names[i]
                    _select(None)
                    elements[i].setter(_d)
                    return  # Exit if one schema matches

                except jsonschema.ValidationError:
                    pass

        def _resetter():
            for e in elements:
                e.resetter()
            if "default" in schema and schema["default"] is not None:
                _setter(schema["default"])

        def _register_observer(h, n, t):
            selector.observe(h, names=n, type=t)
            for e in elements:
                e.register_observer(h, n, t)

        return self.construct_element(
            getter=lambda: elements[names.index(selector.value)].getter(),
            setter=_setter,
            resetter=_resetter,
            widgets=[ipywidgets.VBox(children=[widget])],
            subelements=elements,
            register_observer=_register_observer,
        )

    def _construct_ref(self, schema, label=None):
        ref = schema["$ref"].split("/")[-1]
        return self._construct(self.schema["$defs"][ref], label=label)


def deep_update_missing(target, source):
    target = target.copy()
    for k, v in source.items():
        if k in target:
            if isinstance(v, collections.abc.Mapping) and isinstance(
                target[k], collections.abc.Mapping
            ):
                target[k] = deep_update_missing(target[k], v)
        else:
            target[k] = v
    return target
