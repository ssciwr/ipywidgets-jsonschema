from IPython.display import display

import collections
import ipywidgets
import jsonschema
import json
import os
import pyrsistent
import re
import traitlets


class FormError(Exception):
    pass


FormElement = collections.namedtuple(
    "FormElement", ["getter", "setter", "widgets", "subelements", "register_observer"]
)


def as_tuple(obj):
    if isinstance(obj, collections.abc.Iterable) and not isinstance(obj, str):
        return obj
    else:
        return (obj,)


class Form:
    def __init__(self, schema, vertically_place_labels=False, use_sliders=False):
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
        """
        # Make sure that the given schema is valid
        filename = os.path.join(
            os.path.split(jsonschema.__file__)[0], "schemas", "draft7.json"
        )
        with open(filename, "r") as f:
            meta_schema = json.load(f)
        meta_schema["additionalProperties"] = False
        jsonschema.validate(instance=pyrsistent.thaw(schema), schema=meta_schema)

        # Store the given data members
        self.schema = schema
        self.vertically_place_labels = vertically_place_labels
        self.use_sliders = use_sliders

        # Store a list of registered observers to add them to runtime-generated widgets
        self._observers = []

        # Construct the widgets
        self._form_element = self._construct(schema, root=True, label=None)

    def construct_element(
        self,
        getter=lambda: None,
        setter=lambda _: None,
        widgets=[],
        subelements=[],
        register_observer=lambda h, n, t: None,
    ):
        return FormElement(
            getter=getter,
            setter=setter,
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
        jsonschema.validate(
            instance=pyrsistent.thaw(data), schema=pyrsistent.thaw(self.schema)
        )

        return data

    @data.setter
    def data(self, _data):
        # Ensure that the given data even validates against the schema
        jsonschema.validate(
            instance=pyrsistent.thaw(_data), schema=pyrsistent.thaw(self.schema)
        )

        # Update all widgets according to the given data
        self._form_element.setter(_data)

    def _construct(self, schema, label=None, root=False):
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
            raise FormError("Expecting type information for non-enum properties")
        if not isinstance(type_, str):
            raise FormError("Not accepting arrays of types currently")
        return getattr(self, f"_construct_{type_}")(schema, label=label, root=root)

    def _wrap_accordion(self, widget_list, schema, label=None):
        titles = []
        if label is not None or "title" in schema:
            titles = [schema.get("title", label)]
        accordion = ipywidgets.Accordion(
            children=[ipywidgets.VBox(widget_list)], titles=titles
        )

        # This folds the accordion
        accordion.selected_index = None
        return [accordion]

    def _construct_object(self, schema, label=None, root=False):
        # Construct form elements for all the fields
        elements = {}
        for prop, subschema in schema["properties"].items():
            elements[prop] = self._construct(subschema, label=prop)

        # If this is not the root document, we wrap this in an Accordion widget
        widget_list = sum((e.widgets for e in elements.values()), [])
        if not root:
            widget_list = self._wrap_accordion(widget_list, schema, label=label)

        def _setter(_d):
            for k, v in _d.items():
                elements[k].setter(v)

        def _register_observer(h, n, t):
            for e in elements.values():
                e.register_observer(h, n, t)

        return self.construct_element(
            getter=lambda: pyrsistent.m(**{p: e.getter() for p, e in elements.items()}),
            setter=_setter,
            widgets=widget_list,
            subelements=elements,
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
                    label=ipywidgets.Layout(width="100%"),
                    tooltip=tooltip,
                ),
            )

        # Make sure that the widget shows the tooltip
        if tooltip is not None:
            widget.tooltip = tooltip

        # Apply a potential default
        if "default" in schema:
            widget.value = schema["default"]

        # Apply potential constant values without generating a widget
        if "const" in schema:
            return self.construct_element(getter=lambda: schema["const"])

        # Apply regex pattern matching
        def pattern_checker(val):
            # This only makes sense for strings
            if schema["type"] != "string":
                return True

            # Try matching the given data against the pattern
            pattern = schema.get("pattern", ".*")
            return re.fullmatch(pattern, val)

        # Describe how change handlers are registered
        def _register_observer(h, n, t):
            widget.observe(h, names=n, type=t)

        def _setter(_d):
            if pattern_checker(_d):
                widget.value = _d
            else:
                # We will have to see whether or not throwing is a good idea here
                raise FormError(
                    f"Value '{_d}' does not match the specified pattern '{schema['pattern']}'"
                )

        def _getter():
            if not pattern_checker(widget.value):
                # We will have to see whether or not throwing is a good idea here
                raise FormError(
                    f"Value '{widget.value}' does not match the specified pattern '{schema['pattern']}'"
                )

            return widget.value

        # Make sure the widget adapts to the outer layout
        widget.layout = ipywidgets.Layout(width="100%")

        # Make the placing of labels optional
        box_type = ipywidgets.HBox
        if self.vertically_place_labels:
            box_type = ipywidgets.VBox

        return self.construct_element(
            getter=_getter,
            setter=_setter,
            widgets=[box_type(box)],
            register_observer=_register_observer,
        )

    def _construct_string(self, schema, label=None, root=False):
        return self._construct_simple(schema, ipywidgets.Text(), label=label)

    def _construct_number(self, schema, label=None, root=False):
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
                _class(min=schema["minimum"], max=schema["maximum"]),
                label=label,
            )
        else:
            return self._construct_simple(schema, ipywidgets.FloatText(), label=label)

    def _construct_integer(self, schema, label=None, root=False):
        # Inputs bounded only from below or above are currently not supported
        # in ipywidgets - rather strange
        if "minimum" in schema and "maximum" in schema:
            _class = (
                ipywidgets.IntSlider if self.use_sliders else ipywidgets.BoundedIntText
            )
            return self._construct_simple(
                schema,
                _class(min=schema["minimum"], max=schema["maximum"]),
                label=label,
            )
        else:
            return self._construct_simple(schema, ipywidgets.IntText(), label=label)

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

        # Construct a widget that allows to add an array entry
        button = ipywidgets.Button(
            description="Add entry", icon="plus", layout=ipywidgets.Layout(width="100%")
        )
        vbox = ipywidgets.VBox([button])
        elements = []

        def add_entry(_):
            # if we are at the specified maximum, add should be ignored
            if "maxItems" in schema:
                if len(vbox.children) == schema["maxItems"] + 1:
                    return

            newelem = self._construct(schema["items"], label=None)
            elements.insert(0, newelem)
            item = elements[0].widgets[0]

            # Register existing observers
            for h, n, t in self._observers:
                newelem.register_observer(h, n, t)

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

            # We trigger observers upon adding
            trigger_observers()

            def remove_entry(b):
                # If we are at the specified minimum, remove should be ignored
                if "minItems" in schema:
                    if len(vbox.children) is schema["minItems"]:
                        return

                # Identify the current list index of the entry
                for index, child in enumerate(vbox.children[:-1]):
                    if b in child.children[1].children:
                        break

                # Remove it from the widget list and the handler list
                vbox.children = vbox.children[:index] + vbox.children[index + 1 :]
                elements.pop(index)

                # We trigger observers upon removing
                trigger_observers()

            trash.on_click(remove_entry)

            def move(dir):
                def _move(b):
                    items = list(vbox.children[:-1])
                    for i, it in enumerate(items):
                        if b in it.children[1].children:
                            newi = min(max(i + dir, 0), len(items) - 1)
                            items[i], items[newi] = items[newi], items[i]
                            elements[i], elements[newi] = (
                                elements[newi],
                                elements[i],
                            )
                            break

                    vbox.children = tuple(items) + (vbox.children[-1],)

                return _move

            # Register the handler for moving up and down
            up.on_click(move(-1))
            down.on_click(move(1))

            vbox.children = (
                ipywidgets.VBox(
                    [
                        item,
                        ipywidgets.HBox(
                            [trash, up, down], layout=ipywidgets.Layout(width="100%")
                        ),
                    ]
                ),
            ) + vbox.children

        button.on_click(add_entry)

        # Initialize the widget with the minimal number of subwidgets
        for _ in range(schema.get("minItems", 0)):
            add_entry(_)

        # If this is not the root document, we wrap this in an Accordion widget
        wrapped_vbox = [vbox]
        if not root:
            wrapped_vbox = self._wrap_accordion(wrapped_vbox, schema, label=label)

        def _setter(_d):
            elements.clear()
            vbox.children = (vbox.children[-1],)
            for item in reversed(_d):
                add_entry(None)
                elements[0].setter(item)

        def _register_observer(h, n, t):
            for e in elements:
                e.register_observer(h, n, t)

        # If a default was specified, we now set it
        if "default" in schema:
            _setter(schema["default"])

        return self.construct_element(
            getter=lambda: pyrsistent.pvector(h.getter() for h in elements),
            setter=_setter,
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
        names = []
        elements = []

        # Iterate over the given subschema
        for s in schema[key]:
            if "title" in s:
                names.append(s["title"])
                elements.append(self._construct(s))
            else:
                raise FormError(
                    "Schemas within anyOf/oneOf/allOf need to set the title field"
                )

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
                    jsonschema.validate(
                        instance=pyrsistent.thaw(_d), schema=pyrsistent.thaw(s)
                    )
                    selector.value = names[i]
                    _select(None)
                    elements[i].setter(_d)
                except jsonschema.ValidationError:
                    pass

        def _register_observer(h, n, t):
            for e in elements:
                e.register_observer(h, n, t)

        return self.construct_element(
            getter=lambda: elements[names.index(selector.value)].getter(),
            setter=_setter,
            widgets=[widget],
            subelements=elements,
            register_observer=_register_observer,
        )
