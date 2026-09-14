import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    LEVEL_CHOICES = [
        ('elementary', 'Sekolah Dasar'),
        ('junior-high', 'Sekolah Menengah Pertama'),
        ('senior-high', 'Sekolah Menengah Atas'),
        ('bachelor', 'Sarjana'),
        ('master', 'Magister'),
        ('doctoral', 'Doktor'),
        ('course', 'Kursus & Sertifikasi'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    major = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_year', 'institution']

    def __str__(self):
        return f"{self.institution} ({self.start_year})"

    @property
    def is_ongoing(self):
        return self.end_year is None

    @property
    def period(self):
        if self.is_ongoing:
            return f"{self.start_year} - Sekarang"
        return f"{self.start_year} - {self.end_year}"
