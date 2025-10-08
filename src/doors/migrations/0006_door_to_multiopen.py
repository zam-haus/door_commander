from django.db import migrations

def door_to_multiopen(apps, schema_editor):
    Door = apps.get_model('doors', 'Door')
    MultiOpen = apps.get_model('doors', 'MultiOpen')
    # For each Door, create a MultiOpen and link the Door, then delete the Door
    for door in Door.objects.all():
        multiopen = MultiOpen.objects.create(
            display_name=door.display_name,
            order=door.order,
            text_color=door.text_color,
            button_color=door.button_color,
        )
        multiopen.doors.add(door)
        multiopen.save()
        door.hidden = True
        door.save()

class Migration(migrations.Migration):
    dependencies = [
        ('doors', '0005_door_hidden_multiopen'),
    ]
    operations = [
        migrations.RunPython(door_to_multiopen),
    ]

