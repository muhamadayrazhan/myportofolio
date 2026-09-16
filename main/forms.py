from django.forms import ModelForm, NumberInput, Select, TextInput, Textarea, URLInput

from main.models import Education


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "level",
            "major",
            "description",
            "start_year",
            "end_year",
            "institution_url",
            "institution_image_url",
        ]

        labels = {
            "institution": "Nama Institusi",
            "level": "Jenjang Pendidikan",
            "major": "Jurusan / Program Studi",
            "description": "Deskripsi Pendidikan",
            "start_year": "Tahun Mulai",
            "end_year": "Tahun Selesai",
            "institution_url": "URL Institusi",
            "institution_image_url": "URL Gambar Institusi",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "level": Select(),
            "major": TextInput(
                attrs={
                    "placeholder": "Ilmu Komputer",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pendidikanmu di sini",
                    "rows": 3,
                }
            ),
            "start_year": NumberInput(
                attrs={
                    "placeholder": "2025",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "end_year": NumberInput(
                attrs={
                    "placeholder": "Kosongkan jika masih berjalan",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "institution_url": URLInput(
                attrs={
                    "placeholder": "https://www.ui.ac.id/",
                }
            ),
            "institution_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }
