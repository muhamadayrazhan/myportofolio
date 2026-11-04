import datetime

from django.test import TestCase
from django.urls import reverse

from main.models import Education, Experience


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at=datetime.date(2026, 1, 15),
        )
        self.api_url = reverse("api:experience-list")

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        # Halaman ini hanya mengirim kerangkanya; isinya diambil dari API.
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, 'id="search-input"')
        self.assertContains(response, self.api_url)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_experience_data_is_served_by_the_api(self):
        response = self.client.get(self.api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        experience = response.data[0]
        self.assertEqual(experience["title"], self.experience.title)
        self.assertEqual(experience["description"], self.experience.description)
        self.assertEqual(experience["category_display"], "Part-Time")
        self.assertTrue(experience["is_ongoing"])

    def test_empty_experience_page(self):
        Experience.objects.all().delete()

        # Empty state selalu ada di DOM, ditampilkan JavaScript saat kosong.
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan")

        self.assertEqual(self.client.get(self.api_url).data, [])

    def test_completed_experience(self):
        self.experience.ended_at = datetime.date(2026, 6, 30)
        self.experience.save()

        self.assertFalse(self.experience.is_ongoing)

        experience = self.client.get(self.api_url).data[0]
        self.assertFalse(experience["is_ongoing"])
        self.assertEqual(experience["period"], "Jan 2026 - Jun 2026")


class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="bachelor",
            major="Ilmu Komputer",
            description="Fokus pada rekayasa perangkat lunak dan basis data.",
            start_year=2025,
        )
        self.api_url = reverse("api:education-list")

    def test_education_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_data_is_served_by_the_api(self):
        response = self.client.get(self.api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        education = response.data[0]
        self.assertEqual(education["institution"], self.education.institution)
        self.assertEqual(education["major"], self.education.major)
        self.assertEqual(education["description"], self.education.description)
        self.assertEqual(education["level_display"], "Sarjana")
        self.assertEqual(education["period"], "2025 - Sekarang")

    def test_empty_education_page_shows_empty_state(self):
        Education.objects.all().delete()

        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan")
        self.assertNotContains(response, self.education.description)

        self.assertEqual(self.client.get(self.api_url).data, [])

    def test_education_model(self):
        self.assertEqual(str(self.education), "Universitas Indonesia (2025)")
        self.assertTrue(self.education.is_ongoing)

        self.education.end_year = 2029
        self.education.save()

        self.assertFalse(self.education.is_ongoing)
        self.assertEqual(self.education.period, "2025 - 2029")

    def test_navbar_links_to_education_page(self):
        education_url = reverse("main:show_education")

        for url_name in ["main:show_main", "main:show_experience", "main:show_education"]:
            response = self.client.get(reverse(url_name))

            self.assertContains(response, f'href="{education_url}"')
