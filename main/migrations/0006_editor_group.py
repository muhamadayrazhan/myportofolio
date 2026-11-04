from django.db import migrations

EDITOR_GROUP = "Editor"

# Editor hanya diberi permission "change_*". Permission "add_*" dan "delete_*"
# sengaja tidak diberikan, sehingga editor bisa memperbarui data yang ada tetapi
# tidak bisa membuat entri baru atau menghapusnya. Superuser tidak perlu masuk
# group ini karena has_perm() selalu mengembalikan True untuknya.
EDITOR_PERMISSIONS = [
    ("education", "change_education", "Can change education"),
    ("experience", "change_experience", "Can change experience"),
    ("project", "change_project", "Can change project"),
]


def create_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    permissions = []
    for model, codename, name in EDITOR_PERMISSIONS:
        # Pada database baru, sinyal post_migrate yang biasanya membuat baris
        # Permission belum berjalan saat migrasi ini dieksekusi.
        content_type, _ = ContentType.objects.get_or_create(
            app_label="main", model=model
        )
        permission, _ = Permission.objects.get_or_create(
            codename=codename, content_type=content_type, defaults={"name": name}
        )
        permissions.append(permission)

    group, _ = Group.objects.get_or_create(name=EDITOR_GROUP)
    group.permissions.set(permissions)


def delete_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=EDITOR_GROUP).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_project_starred_by"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(create_editor_group, delete_editor_group),
    ]
