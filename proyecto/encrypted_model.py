from django.db import models
from pgcrypto.fields import EncryptedCharField, EncryptedTextField
from django.db.models import CharField, TextField

class EncryptedModel(models.Model):
    class Meta:
        abstract = True

    def __init_subclass__(cls):
        super().__init_subclass__()
        for field in list(cls._meta.fields):
            if isinstance(field, CharField) and not isinstance(field, EncryptedCharField):
                cls._replace_field(field, EncryptedCharField)
            elif isinstance(field, TextField) and not isinstance(field, EncryptedTextField):
                cls._replace_field(field, EncryptedTextField)

    @classmethod
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

