from ipywidgets_jsonschema.form import Form
from IPython.display import display
import ipywidgets as widgets


class PydanticEditorMixin:
    """
    Mixin providing an interactive form for editing pydantic model attributes.

    """

    def edit(self):

        # Setup the form
        form = Form(self.__class__)
        form.data = self.model_dump()

        form_output = widgets.Output()
        with form_output:
            form.show()

        edit_btn = widgets.Button(
            value=False,
            description="Edit",
            disabled=False,
            tooltip="Edit model",
            icon="pencil",
        )

        save_btn = widgets.Button(
            value=False,
            description="Save",
            disabled=False,
            button_style="success",
            tooltip="Save all changes",
            icon="save",
        )

        cancel_btn = widgets.Button(
            value=False,
            description="Cancel",
            disabled=False,
            button_style="warning",
            tooltip="Undo all changes",
            icon="times",
        )

        btn_container = widgets.HBox([cancel_btn, save_btn])
        container = widgets.VBox([edit_btn, form_output, btn_container])

        form_output.layout.display = "none"
        btn_container.layout.display = "none"

        def on_edit_btn_clicked(b):
            form_output.layout.display = "block"
            btn_container.layout.display = "block"
            edit_btn.layout.display = "none"

        def on_save_btn_clicked(b):
            # Update model data
            self.__dict__.update(self.model_construct(**form.data))
            form_output.layout.display = "none"
            btn_container.layout.display = "none"
            edit_btn.layout.display = "block"

        def on_cancel_btn_clicked(b):
            # Reset the form to the current model data
            form.data = self.model_dump()
            form_output.layout.display = "none"
            btn_container.layout.display = "none"
            edit_btn.layout.display = "block"

        edit_btn.on_click(on_edit_btn_clicked)
        save_btn.on_click(on_save_btn_clicked)
        cancel_btn.on_click(on_cancel_btn_clicked)
        display(container)
