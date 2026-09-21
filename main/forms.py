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

from main.models import Education, Experience, Project


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
