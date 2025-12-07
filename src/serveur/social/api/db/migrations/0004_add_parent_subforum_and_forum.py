from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_merge_20251202_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='subforum',
            name='parent_subforum',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subforums', to='db.subforum'),
        ),
        migrations.AddField(
            model_name='subforum',
            name='forum',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='all_subforums', to='db.forum'),
        ),
        migrations.RemoveConstraint(
            model_name='subforum',
            name='subforum_one_parent',
        ),
        migrations.AddConstraint(
            model_name='subforum',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(parent_domain__isnull=False, parent_forum__isnull=True, parent_subforum__isnull=True) |
                    models.Q(parent_domain__isnull=True, parent_forum__isnull=False, parent_subforum__isnull=True) |
                    models.Q(parent_domain__isnull=True, parent_forum__isnull=True, parent_subforum__isnull=False)
                ),
                name='subforum_one_parent',
            ),
        ),
        migrations.AddIndex(
            model_name='subforum',
            index=models.Index(fields=['parent_subforum'], name='subforum_parent_subf_idx'),
        ),
        migrations.AddIndex(
            model_name='subforum',
            index=models.Index(fields=['forum'], name='subforum_forum_idx'),
        ),
    ]
