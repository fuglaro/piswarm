
import os
from django.db import migrations
from django.conf import settings


def update_site_name(apps, schema_editor):
    """ Set the site domain and name from the env vars:
     * DOMAIN
     * SITE_NAME
    Note that subsequent changes must be done from the admin page.
    """
    SiteModel = apps.get_model('sites', 'Site')

    SiteModel.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={'domain': os.environ['DOMAIN'],
                  'name': os.environ['SITE_NAME']}
    )


class Migration(migrations.Migration):
    """ Automatically set the site name and domain in the
    database from the environment.
    """

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site_name),
    ]