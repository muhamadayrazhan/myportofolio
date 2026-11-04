from django.core.exceptions import ValidationError
from django.forms import (
    CheckboxInput,
    DateInput,
    ModelForm,
    NumberInput,
    Select,
    TextInput,
    Textarea,
    URLInput,
)

from django.utils.html import strip_tags

from main.models import Education, Experience, Project


# Lapisan pertahanan kedua terhadap XSS, dipakai oleh method clean_<field> di
# ketiga form. Tag HTML dibuang sejak data masuk, sehingga berlaku untuk view
# biasa maupun view AJAX yang sama-sama memakai form ini. Pertahanan utamanya
# tetap escaping saat data ditampilkan, karena hasil strip_tags tidak dijamin
# aman sebagai HTML dan pembersihan ini hanya berlaku untuk data baru.
def _clean_text(value, required_message=None):
    cleaned = strip_tags(value or "").strip()

    # Field wajib yang isinya hanya tag HTML akan kosong setelah dibersihkan,
    # dan itu harus ditolak, bukan disimpan sebagai string kosong.
    if required_message and not cleaned:
        raise ValidationError(required_message)

    return cleaned


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

    def clean_institution(self):
        return _clean_text(
            self.cleaned_data["institution"],
            "Nama institusi tidak boleh hanya berisi tag HTML.",
        )

    def clean_major(self):
        return _clean_text(self.cleaned_data["major"])

    def clean_description(self):
        return _clean_text(self.cleaned_data["description"])


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Nama Posisi / Kegiatan",
            "description": "Deskripsi Pengalaman",
            "category": "Kategori Pengalaman",
            "thumbnail": "URL Gambar / Logo",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "IT Force / Staff",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalamanmu di sini",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def clean_title(self):
        return _clean_text(
            self.cleaned_data["title"],
            "Nama posisi atau kegiatan tidak boleh hanya berisi tag HTML.",
        )

    def clean_description(self):
        return _clean_text(
            self.cleaned_data["description"],
            "Deskripsi tidak boleh hanya berisi tag HTML.",
        )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "category",
            "tech_stack",
            "project_url",
            "project_image_url",
            "year",
            "is_featured",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "category": "Kategori Proyek",
            "tech_stack": "Tech Stack",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
            "year": "Tahun Pengerjaan",
            "is_featured": "Tampilkan sebagai proyek unggulan",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portofolio Pribadi",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan proyekmu di sini",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, SQLite, HTML, CSS",
                    "maxlength": 255,
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/muhamadayrazhan/myportofolio",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "year": NumberInput(
                attrs={
                    "placeholder": "2026",
                    "min": 1990,
                    "max": 2100,
                }
            ),
            "is_featured": CheckboxInput(),
        }

    def clean_title(self):
        return _clean_text(
            self.cleaned_data["title"],
            "Nama proyek tidak boleh hanya berisi tag HTML.",
        )

    def clean_tech_stack(self):
        return _clean_text(self.cleaned_data["tech_stack"])

    def clean_description(self):
        return _clean_text(self.cleaned_data["description"])

