from django.db import models

class CustomQuerySet(models.QuerySet):
  @property
  def verbose_name(self):
    return self.model._meta.verbose_name

  @property
  def verbose_name_plural(self):
    return self.model._meta.verbose_name_plural


class BaseModel(models.Model):
  objects = CustomQuerySet.as_manager()

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  # def __str__(self):
  #   return str(self.id)

  class Meta:
    abstract = True
