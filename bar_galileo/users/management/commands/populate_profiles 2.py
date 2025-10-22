from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import PerfilUsuario
from allauth.socialaccount.models import SocialAccount
import requests
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Populates empty fields in PerfilUsuario for existing users.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting profile population...'))
        
        updated_count = 0
        for user in User.objects.all():
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            updated = False

            # Populate name
            if not perfil.nombre:
                social_account = SocialAccount.objects.filter(user=user, provider='google').first()
                if social_account:
                    perfil.nombre = social_account.extra_data.get('name', user.get_full_name())
                else:
                    perfil.nombre = user.get_full_name() or user.username
                updated = True

            # Populate avatar
            if not perfil.avatar:
                social_account = SocialAccount.objects.filter(user=user, provider='google').first()
                if social_account:
                    picture_url = social_account.extra_data.get('picture')
                    if picture_url:
                        try:
                            response = requests.get(picture_url, stream=True)
                            response.raise_for_status()
                            
                            img = Image.open(response.raw)
                            buffer = BytesIO()
                            img.save(buffer, format='WEBP', quality=85)
                            buffer.seek(0)

                            file_name = f"{user.id}_avatar.webp"
                            perfil.avatar.save(file_name, ContentFile(buffer.read()), save=False)
                            updated = True
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Failed to fetch avatar for {user.username}: {e}'))
            
            if updated:
                perfil.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated profile for {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Finished. Total profiles updated: {updated_count}'))
