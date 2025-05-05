from django.db import models
from pgcrypto.fields import EncryptedCharField, EncryptedTextField
from django.db.models import CharField, TextField
from django.db.models.signals import class_prepared
from django.dispatch import receiver

class EncryptedModel(models.Model):
    class Meta:
        abstract = True

@receiver(class_prepared)
def encrypt_fields(sender, **kwargs):
    if issubclass(sender, EncryptedModel) and sender != EncryptedModel:
        for field in list(sender._meta.fields):
            if isinstance(field, CharField) and not isinstance(field, EncryptedCharField):
                _replace_field(sender, field, EncryptedCharField)
            elif isinstance(field, TextField) and not isinstance(field, EncryptedTextField):
                _replace_field(sender, field, EncryptedTextField)

def _replace_field(cls, old_field, new_field_class):
    name = old_field.name
    new_field = new_field_class(
        name=name,
        max_length=getattr(old_field, 'max_length', None),
        null=old_field.null,
        blank=old_field.blank,
        default=old_field.default,
        verbose_name=old_field.verbose_name,
        help_text=old_field.help_text,
    )
    cls.add_to_class(name, new_field)
