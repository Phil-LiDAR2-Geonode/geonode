from django.db import models

class Publication(models.Model):
    title = models.TextField()
    doc_file = models.FileField("Document File", upload_to="doc_publication/")
    date_uploaded = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title

class TechReport(models.Model):
    class Meta:
        verbose_name = "Technical Report and Manual"

    title = models.TextField()
    doc_file = models.FileField("Document File", upload_to="doc_techreports/")

    DOC_TYPE_CHOICES = (
        ('Algorithms/Workflows and Field Validation Manuals', 'Algorithms/Workflows and Field Validation Manuals'),
        ('Vulnerability Assessment', 'Vulnerability Assessment'),
        ('Policy Recommendations', 'Policy Recommendations'),
        ('Training Manuals', 'Training Manuals'),
        ('QA/QC Documentation', 'QA/QC Documentation'),
        ('Operational Web-based GIS Platform', 'Operational Web-based GIS Platform'),
    )

    doc_type = models.CharField(
        "Document Type",
        blank=True,
        max_length=100,
        choices=DOC_TYPE_CHOICES,
    )

    date_uploaded = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return self.title
