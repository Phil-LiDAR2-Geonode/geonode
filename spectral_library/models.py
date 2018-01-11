from django.db import models
from geonode.people.models import Profile


class Target(models.Model):
    site_id = models.CharField("Site ID", max_length=200, blank=True)
    date_acquired = models.DateField("Date", blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    observer = models.CharField(max_length=200, blank=True)
    time_acquired = models.TimeField("Time", blank=True)
    waypoint = models.CharField(max_length=200, blank=True)
    latitude = models.CharField(max_length=200, blank=True)
    longitude = models.CharField(max_length=200, blank=True)
    altitude = models.CharField(max_length=50, blank=True)
    gps_unit = models.CharField("GPS Unit", max_length=200, blank=True)
    province = models.CharField(max_length=200, blank=True)
    city_municipality = models.CharField("City/Municipality",max_length=200, blank=True)
    barangay = models.CharField(max_length=200, blank=True)
    land_cover_class = models.CharField(max_length=200, blank=True)
    land_cover_type = models.CharField(max_length=200, blank=True)
    spectrum = models.CharField("Spectrum/Target name",max_length=200, blank=True)
    target_homogeneity = models.CharField(max_length=50, blank=True)
    pictures_file_name = models.CharField(max_length=200, blank=True)
    num_of_spectra = models.IntegerField("# spectra/sample", default=0)
    white_reference = models.CharField(max_length=200, blank=True)
    sensor = models.CharField(max_length=200, blank=True)
    instrument = models.CharField(max_length=200, blank=True)
    fiber_optic_cable_length = models.CharField(max_length=50, blank=True)
    reflectance = models.BooleanField(default=False)
    digital_numbers = models.BooleanField(default=False)
    cloud_cover = models.CharField(max_length=200, blank=True)
    file_format = models.CharField(max_length=50, blank=True)
    target_irradiance_1 = models.CharField(max_length=200, blank=True)
    target_irradiance_2 = models.CharField(max_length=200, blank=True)
    target_irradiance_3 = models.CharField(max_length=200, blank=True)
    white_reference_file_names = models.CharField(max_length=200, blank=True)
    reflectance_1 = models.CharField(max_length=200, blank=True)
    reflectance_2 = models.CharField(max_length=200, blank=True)
    reflectance_3 = models.CharField(max_length=200, blank=True)
    common_name = models.CharField(max_length=200, blank=True)
    scientific_name = models.CharField(max_length=200, blank=True)
    leaf_canopy = models.CharField("Leaf/Canopy", max_length=200, blank=True)
    ground_canopy_distance = models.CharField(max_length=50, blank=True)
    phenologic_stage = models.CharField(max_length=200, blank=True)
    presence_of_irrigation = models.BooleanField(default=False)
    background = models.CharField("Background (soil/other)", max_length=200, blank=True)
    soil_type = models.CharField("Soil type/color", max_length=200, blank=True)

    target_file = models.FileField(upload_to="spectral_target/")
    graph = models.FileField(upload_to="spectral_graph/", blank=True)
    image = models.FileField(upload_to="spectral_image/", blank=True)

    title = models.CharField(max_length=200, editable=False)

    def __unicode__(self):
        return self.title

    def save(self):
        sample_num = self.target_file.name[-8:][:1]
        if self.phenologic_stage == "":
            self.title = "{0} from {1} Spectral Signature Sample {2}".format(self.common_name, self.province, sample_num)
        else:
            self.title = "{0} {1} Stage from {2} Spectral Signature Sample {3}".format(self.common_name, self.phenologic_stage, self.province, sample_num)
        super(Target, self).save()

class Queue(models.Model):
    profile = models.ForeignKey(Profile)
    target = models.ForeignKey(Target)

    STATUS_CHOICES = (
        ('ADDED TO QUEUE', 'Added to queue'),
        ('DOWNLOADED', 'Downloaded'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ADDED TO QUEUE'
    )
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.target.title
