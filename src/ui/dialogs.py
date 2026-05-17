from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from tkinter import StringVar, messagebox, ttk, simpledialog


@dataclass(frozen=True)
class FieldSpec:
    name: str
    label: str
    kind: str = "str"
    required: bool = True
    choices: tuple[str, ...] | None = None
    default: object | None = None


class FormDialog(simpledialog.Dialog):
    def __init__(
        self,
        parent,
        title: str,
        field_specs: list[FieldSpec],
        initial_values: dict[str, object] | None = None,
    ) -> None:
        self._field_specs = field_specs
        self._initial_values = initial_values or {}
        self.result: dict[str, object] | None = None
        super().__init__(parent, title)

    def body(self, master):
        self._variables: dict[str, StringVar] = {}

        for row, field in enumerate(self._field_specs):
            ttk.Label(master, text=field.label).grid(row=row, column=0, sticky="w", padx=6, pady=4)
            variable = StringVar(value=self._get_initial_value(field))
            self._variables[field.name] = variable

            if field.choices:
                widget = ttk.Combobox(master, textvariable=variable, values=list(field.choices), state="readonly")
            else:
                widget = ttk.Entry(master, textvariable=variable, show="*" if field.kind == "password" else "")

            widget.grid(row=row, column=1, sticky="ew", padx=6, pady=4)

        master.columnconfigure(1, weight=1)
        return master

    def validate(self) -> bool:
        try:
            self.result = self._parse_values()
            return True
        except ValueError as error:
            messagebox.showerror("Validation error", str(error))
            return False

    def _parse_values(self) -> dict[str, object]:
        parsed_values: dict[str, object] = {}
        for field in self._field_specs:
            raw_value = self._variables[field.name].get().strip()
            if not raw_value:
                if field.required:
                    raise ValueError(f"{field.label} is required.")
                parsed_values[field.name] = None
                continue

            if field.kind == "int":
                parsed_values[field.name] = int(raw_value)
            elif field.kind == "float":
                parsed_values[field.name] = float(raw_value)
            elif field.kind == "date":
                parsed_values[field.name] = date.fromisoformat(raw_value)
            elif field.kind == "datetime":
                parsed_values[field.name] = datetime.fromisoformat(raw_value)
            else:
                parsed_values[field.name] = raw_value

        return parsed_values

    def _get_initial_value(self, field: FieldSpec) -> str:
        value = self._initial_values.get(field.name, field.default)
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.isoformat(timespec="minutes")
        if isinstance(value, date):
            return value.isoformat()
        return str(value)


def prompt_for_values(
    parent,
    title: str,
    field_specs: list[FieldSpec],
    initial_values: dict[str, object] | None = None,
) -> dict[str, object] | None:
    dialog = FormDialog(parent, title, field_specs, initial_values)
    return dialog.result