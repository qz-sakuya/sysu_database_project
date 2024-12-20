from django.db import models



class Image(models.Model):
    image_data = models.BinaryField()
    image_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Image {self.id}"


class Line(models.Model):
    line_no = models.CharField(max_length=10, unique=True)
    line_name = models.CharField(max_length=100, unique=True)
    colour = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.line_name

class Station(models.Model):
    station_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.station_name


class Platform(models.Model):
    platform_no = models.IntegerField()
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('line', 'platform_no'), ('line', 'station'))

    def __str__(self):
        return f"Platform {self.platform_no} on Line {self.line.line_no} at Station {self.station.station_name}"


class Exit(models.Model):
    exit_no = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    exit_name = models.CharField(max_length=100)
    exit_address = models.CharField(max_length=255)
    exit_sub_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('station', 'exit_no'), )

    def __str__(self):
        return f"Exit {self.exit_no} at Station {self.station.station_name}"


class Section(models.Model):
    section_no = models.IntegerField()
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    platform1 = models.ForeignKey(Platform, related_name='section_platform1_set', on_delete=models.CASCADE)
    platform2 = models.ForeignKey(Platform, related_name='section_platform2_set', on_delete=models.CASCADE)
    travel_time = models.IntegerField()
    fare = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('line', 'section_no'), ('line', 'platform1', 'platform2'))

    def __str__(self):
        return f"Section {self.section_no} on Line {self.line.line_no}"


class Transfer(models.Model):
    platform1 = models.ForeignKey(Platform, related_name='transfer_platform1_set', on_delete=models.CASCADE)
    platform2 = models.ForeignKey(Platform, related_name='transfer_platform2_set', on_delete=models.CASCADE)
    transfer_time = models.IntegerField()
    out_station = models.BooleanField()

    class Meta:
        unique_together = (('platform1', 'platform2'),)

    def __str__(self):
        return f"Transfer from Platform {self.platform1.platform_no} to Platform {self.platform2.platform_no}"

class FirstTrain(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10)
    departure_time = models.TimeField()

    class Meta:
        unique_together = (('platform', 'direction'),)

    def __str__(self):
        return f"First Train on Platform {self.platform.platform_no} ({self.direction})"


class LastTrain(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10)
    departure_time = models.TimeField()

    class Meta:
        unique_together = (('platform', 'direction'),)

    def __str__(self):
        return f"Last Train on Platform {self.platform.platform_no} ({self.direction})"


class StationFacility(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    facility_type = models.CharField(max_length=50)
    icon_image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = (('station', 'facility_type'),)

    def __str__(self):
        return f"{self.facility_type} at Station {self.station.station_name}"
