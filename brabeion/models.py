from django.utils import timezone

from django.db import models

from django.conf import settings
from django.utils.importlib import import_module
import warnings


class BadgeAwardAbstractClass(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="badges_earned")
    awarded_at = models.DateTimeField(default=timezone.now)
    slug = models.CharField(max_length=255)
    level = models.IntegerField()
    
    def __getattr__(self, attr):
        return getattr(self._badge, attr)
    
    @property
    def badge(self):
        return self
    
    @property
    def _badge(self):
        from brabeion import badges
        return badges._registry[self.slug]
    
    @property
    def name(self):
        return self._badge.levels[self.level].name
    
    @property
    def description(self):
        return self._badge.levels[self.level].description
    
    @property
    def progress(self):
        return self._badge.progress(self.user, self.level)

    class Meta:
        abstract = True


def get_base_model():
    """
    Determine the base Model to inherit in the
    BadgeAward Model; this allows to overload it.
    """
    BASE_MODEL = getattr(settings, 'ELDARION_BASE_BADGE_AWARD_MODEL', '')
    if not BASE_MODEL:
        return BadgeAwardAbstractClass
    dot = BASE_MODEL.rindex('.')
    module_name = BASE_MODEL[:dot]
    class_name = BASE_MODEL[dot + 1:]
    try:
        _class = getattr(import_module(module_name), class_name)
        return _class
    except (ImportError, AttributeError):
        warnings.warn('%s cannot be imported' % BASE_MODEL,
                      RuntimeWarning)
    return BadgeAwardAbstractClass


class BadgeAward(get_base_model()):
    """
    The final BadgeAward model based on inheritance.
    This pattern was copied after django-blog-zinnia's overloadable Entry model.
    """
