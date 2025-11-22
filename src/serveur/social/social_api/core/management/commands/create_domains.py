"""
Management command to create the 9 predefined domains.
As per specifications.md section 3.2: Domains
"""
from django.core.management.base import BaseCommand
from core.models import Forum


class Command(BaseCommand):
    help = 'Create the 9 predefined political domains'

    def handle(self, *args, **options):
        domains_data = [
            {
                'name': 'Culture',
                'description': 'Discussions sur la culture locale, événements culturels, patrimoine',
            },
            {
                'name': 'Sport',
                'description': 'Infrastructures sportives, événements sportifs, associations',
            },
            {
                'name': 'Environnement',
                'description': 'Écologie, développement durable, espaces verts',
            },
            {
                'name': 'Transports',
                'description': 'Transports en commun, mobilité, infrastructures routières',
            },
            {
                'name': 'Sécurité',
                'description': 'Sécurité publique, prévention, police municipale',
            },
            {
                'name': 'Santé',
                'description': 'Santé publique, établissements de santé, prévention',
            },
            {
                'name': 'Emploi',
                'description': 'Emploi local, formation professionnelle, économie',
            },
            {
                'name': 'Éducation',
                'description': 'Écoles, établissements scolaires, programmes éducatifs',
            },
            {
                'name': 'Numérique',
                'description': 'Transformation numérique, connectivité, services en ligne',
            },
        ]

        created_count = 0
        for domain_data in domains_data:
            forum, created = Forum.objects.get_or_create(
                name=domain_data['name'],
                defaults={
                    'description': domain_data['description'],
                    'visibility': 'public',
                    'created_by': None,  # System-created
                    'parent_forum': None,  # Top-level domains
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created domain: {forum.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Domain already exists: {forum.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} domains created successfully!')
        )
