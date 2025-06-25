from django.db import models


# Create your models here.
class RegistrationInfo(models.Model):
    school_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pc_count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.school_name} - {self.city}"

# models.py


class School(models.Model):
    dise_code = models.CharField(max_length=20, primary_key=True)
    school_name = models.CharField(max_length=100)
    cluster = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    block = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    principleName = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.school_name

class Asset(models.Model):
    dise = models.ForeignKey(School, to_field='dise_code', on_delete=models.CASCADE)
    lab = models.CharField(max_length=100)
    pc = models.IntegerField()
    serial_number = models.CharField(max_length=100)
    tft = models.CharField(max_length=100)
    headphone = models.CharField(max_length=100)
    webcam = models.CharField(max_length=100)
    switch = models.CharField(max_length=100)
    date = models.DateField()
    status=models.CharField(max_length=20,default='inactive')
    

    def __str__(self):
        return f"{self.dise.dise_code} - {self.serial_number}"