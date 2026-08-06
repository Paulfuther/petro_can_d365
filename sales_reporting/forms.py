from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {
            "accept": (
                ".xlsx,"
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]

        return [single_file_clean(data, initial)]


class SalesReportUploadForm(forms.Form):
    files = MultipleFileField(
        label="D365 category sales reports",
        help_text="Select up to 10 XLSX files from the same reporting month.",
    )

    def clean_files(self):
        files = self.cleaned_data["files"]

        if not files:
            raise ValidationError("Select at least one CSV file.")

        if len(files) > 10:
            raise ValidationError("You can upload a maximum of 10 files at once.")

        for uploaded_file in files:
            extension = Path(uploaded_file.name).suffix.lower()

            if extension != ".xlsx":
                raise ValidationError(
                    f"{uploaded_file.name} is not a Excel file."
                )

            if uploaded_file.size > 10 * 1024 * 1024:
                raise ValidationError(
                    f"{uploaded_file.name} exceeds the 10 MB file limit."
                )

        return files


class WorkbookInspectorForm(forms.Form):
    workbook = forms.FileField(
        label="D365 workbook",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": (
                    ".xlsx,"
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            }
        ),
        help_text="Select one D365 XLSX workbook to inspect.",
    )

    def clean_workbook(self):
        uploaded_file = self.cleaned_data["workbook"]
        extension = Path(uploaded_file.name).suffix.lower()

        if extension != ".xlsx":
            raise ValidationError("Select an XLSX workbook.")

        if uploaded_file.size > 10 * 1024 * 1024:
            raise ValidationError(
                "The workbook exceeds the 10 MB limit."
            )

        return uploaded_file