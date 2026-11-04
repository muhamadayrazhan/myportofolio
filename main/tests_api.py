import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience, Project

PASSWORD = "test-password"


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password=PASSWORD, email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password=PASSWORD
        )
        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            tech_stack="Django, SQLite",
            year=2026,
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project",
            "description": "A useful app",
            "category": "web",
            "tech_stack": "Python",
            "project_url": "https://example.com/",
            "project_image_url": "",
            "year": 2025,
            "is_featured": False,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(response.data[0]["category_display"], "Web Development")
        self.assertEqual(response.data[0]["tech_stack_list"], ["Django", "SQLite"])
        self.assertEqual(
            self.client.get(self.detail_url).status_code, status.HTTP_200_OK
        )

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(
            self.client.get(url).status_code, status.HTTP_404_NOT_FOUND
        )

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"title": "Changed"}, format="json"
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
            ({"year": "bukan-angka"}, "year"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url, {"title": "Changed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN
        )

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")

        # Akun lain tetap melihat is_starred False.
        self.client.force_authenticate(user=self.owner)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.get(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(
            self.detail_url, {"title": "Changed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password=PASSWORD))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password=PASSWORD)
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password=PASSWORD, email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password=PASSWORD
        )
        self.editor = User.objects.create_user(username="editor", password=PASSWORD)
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="bachelor",
            major="Ilmu Komputer",
            description="Mahasiswa.",
            start_year=2025,
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "SMA Negeri 1",
            "level": "senior-high",
            "major": "IPA",
            "description": "Murid.",
            "start_year": 2021,
            "end_year": 2024,
        }

    def test_public_list_search_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["level_display"], "Sarjana")
        self.assertEqual(response.data[0]["period"], "2025 - Sekarang")

        self.assertEqual(
            len(self.client.get(self.list_url, {"institution": "indonesia"}).data), 1
        )
        self.assertEqual(self.client.get(self.list_url, {"institution": "zzz"}).data, [])
        self.assertEqual(
            self.client.get(self.detail_url).status_code, status.HTTP_200_OK
        )

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"major": "Diubah"}, format="json"
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Education.objects.count(), 1)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.patch(
            self.detail_url, {"major": "Sistem Informasi"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.major, "Sistem Informasi")

        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(
            self.client.patch(
                self.detail_url, {"major": "Diubah"}, format="json"
            ).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Education.objects.count(), 1)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "institution": '<img src="x" onerror="alert(1)">'},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("institution", response.data)

        response = self.client.post(
            self.list_url,
            {**self.payload, "institution_url": "javascript:alert(1)"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Education.objects.count(), 1)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.client.force_authenticate(user=self.visitor)
        self.assertTrue(self.client.post(self.star_url).data["is_starred"])
        self.assertFalse(self.client.post(self.star_url).data["is_starred"])


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password=PASSWORD, email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password=PASSWORD
        )
        self.editor = User.objects.create_user(username="editor", password=PASSWORD)
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.experience = Experience.objects.create(
            title="Staf COMPFEST",
            description="Divisi Event.",
            category="volunteer",
            started_at="2026-09-09",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Software Engineer Intern",
            "description": "Membangun fitur baru.",
            "category": "internship",
            "started_at": "2025-02-01",
            "ended_at": "2025-10-01",
        }

    def test_public_list_search_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["category_display"], "Volunteer")
        self.assertTrue(response.data[0]["is_ongoing"])

        self.assertEqual(
            len(self.client.get(self.list_url, {"title": "compfest"}).data), 1
        )
        self.assertEqual(self.client.get(self.list_url, {"title": "zzz"}).data, [])
        self.assertEqual(
            self.client.get(self.detail_url).status_code, status.HTTP_200_OK
        )

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"title": "Diubah"}, format="json"
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["is_ongoing"])

        response = self.client.patch(
            self.detail_url, {"title": "Staf COMPFEST 18"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Staf COMPFEST 18")
        self.assertEqual(self.experience.description, "Divisi Event.")

        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(
            self.client.patch(
                self.detail_url, {"title": "Diubah"}, format="json"
            ).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Experience.objects.count(), 1)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "title": '<img src="x" onerror="alert(1)">'},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

        response = self.client.post(
            self.list_url, {**self.payload, "started_at": "bukan-tanggal"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Experience.objects.count(), 1)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.client.force_authenticate(user=self.visitor)
        self.assertTrue(self.client.post(self.star_url).data["is_starred"])
        self.assertFalse(self.client.post(self.star_url).data["is_starred"])
