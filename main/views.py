import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from main.forms import EducationForm, ExperienceForm, ProjectForm
from main.models import Education, Experience, Project

NAME = "Muhamad Ayrazhan"


def _filtered(model, request, field):
    """Return (queryset, query) filtered by a case-insensitive GET lookup."""
    query = request.GET.get(field, "").strip()
    queryset = model.objects.all()

    if query:
        queryset = queryset.filter(**{f"{field}__icontains": query})

    return queryset, query


def _deserialize(json_response):
    """Turn a JSON HttpResponse from one of the API views back into objects."""
    data = serializers.deserialize("json", json_response.content.decode("utf-8"))
    return [item.object for item in data]


def show_main(request):
    # Cookie yang baru dihapus saat logout masih bisa terkirim dengan nilai
    # kosong, jadi nilai kosong diperlakukan sama seperti cookie yang hilang.
    last_login = (
        request.COOKIES.get("last_login")
        or "Belum ada sesi login / Cookie tidak ditemukan"
    )
    context = {
        "name": NAME,
        "last_login": last_login,
        "npm": "2506586236",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


# ---------------------------------------------------------------- education


def get_education_json(request):
    educations, _ = _filtered(Education, request, "institution")
    education_json = serializers.serialize("json", educations)
    return HttpResponse(education_json, content_type="application/json")


def get_education_xml(request):
    educations, _ = _filtered(Education, request, "institution")
    education_xml = serializers.serialize("xml", educations)
    return HttpResponse(education_xml, content_type="application/xml")


def show_education(request):
    context = {
        "name": NAME,
        "education_list": _deserialize(get_education_json(request)),
        "institution_query": request.GET.get("institution", "").strip(),
    }
    return render(request, "education.html", context)


@login_required(login_url="/login/")
def create_education(request):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Tambahkan riwayat pendidikanmu!",
        "page_title": "Add New Education",
        "submit_label": "Tambah Education",
        "cancel_url": reverse("main:show_education"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def edit_education(request, education_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Perbarui riwayat pendidikanmu",
        "page_title": "Edit Education",
        "submit_label": "Simpan Perubahan",
        "cancel_url": reverse("main:show_education"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def delete_education(request, education_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")

    return redirect("main:show_education")


# --------------------------------------------------------------- experience


def get_experience_json(request):
    experiences, _ = _filtered(Experience, request, "title")
    experience_json = serializers.serialize("json", experiences)
    return HttpResponse(experience_json, content_type="application/json")


def get_experience_xml(request):
    experiences, _ = _filtered(Experience, request, "title")
    experience_xml = serializers.serialize("xml", experiences)
    return HttpResponse(experience_xml, content_type="application/xml")


def show_experience(request):
    context = {
        "name": NAME,
        "experience_list": _deserialize(get_experience_json(request)),
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Tambahkan pengalamanmu!",
        "page_title": "Add New Experience",
        "submit_label": "Tambah Experience",
        "cancel_url": reverse("main:show_experience"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Perbarui pengalamanmu",
        "page_title": "Edit Experience",
        "submit_label": "Simpan Perubahan",
        "cancel_url": reverse("main:show_experience"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")

    return redirect("main:show_experience")


# ------------------------------------------------------------------ project


def get_project_json(request):
    projects, _ = _filtered(Project, request, "title")
    project_json = serializers.serialize(
        "json", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(project_json, content_type="application/json")


def get_project_xml(request):
    projects, _ = _filtered(Project, request, "title")
    project_xml = serializers.serialize(
        "xml", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(project_xml, content_type="application/xml")


def show_project(request):
    context = {
        "name": NAME,
        "project_list": _deserialize(get_project_json(request)),
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "project.html", context)


@login_required(login_url="/login/")
def create_project(request):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Tambahkan proyekmu!",
        "page_title": "Add New Project",
        "submit_label": "Tambah Project",
        "cancel_url": reverse("main:show_project"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def edit_project(request, project_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_project")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Perbarui proyekmu",
        "page_title": "Edit Project",
        "submit_label": "Simpan Perubahan",
        "cancel_url": reverse("main:show_project"),
    }
    return render(request, "form_page.html", context)


@login_required(login_url="/login/")
def delete_project(request, project_id):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah data;
    # akun terdaftar lain dihentikan dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")

    return redirect("main:show_project")


# ------------------------------------------------------------------ star


# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star.
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_project")


# ------------------------------------------------------------------- auth


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Bergabung ke portofolio ini",
        "page_title": "Buat Akun",
        "submit_label": "Daftar",
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response

    context = {
        "name": NAME,
        "form": form,
        "kicker": "Masuk ke akunmu",
        "page_title": "Login",
        "submit_label": "Login",
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
