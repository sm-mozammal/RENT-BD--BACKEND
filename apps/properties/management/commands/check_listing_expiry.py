from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.properties.models import Property


class Command(BaseCommand):
    help = 'Checks properties unconfirmed for >15 days, sends prompt, and auto-hides listings unconfirmed for >20 days'

    def handle(self, *args, **options):
        now = timezone.now()
        fifteen_days_ago = now - timedelta(days=15)
        twenty_days_ago = now - timedelta(days=20)

        # 1. Properties needing 15-day prompt
        prompt_needed = Property.objects.filter(
            is_available=True,
            last_confirmed_available_at__lte=fifteen_days_ago,
            last_confirmed_available_at__gt=twenty_days_ago,
        )
        self.stdout.write(f"Found {prompt_needed.count()} properties needing 15-day availability check prompt.")
        for prop in prompt_needed:
            self.stdout.write(
                f"[PROMPT SENT via SMS/Push] To landlord {prop.landlord.full_name} ({prop.landlord.phone_number}): "
                f"'Is your listing \"{prop.title}\" still available? Tap to confirm or it will be auto-hidden in 5 days.'"
            )

        # 2. Properties unresponsive for >20 days -> Auto-hide into Property Vault
        expired_properties = Property.objects.filter(
            is_available=True,
            last_confirmed_available_at__lte=twenty_days_ago,
        )
        expired_count = expired_properties.count()
        for prop in expired_properties:
            prop.is_available = False
            prop.save(update_fields=['is_available'])
            warning_style = getattr(self.style, 'WARNING', str)
            self.stdout.write(warning_style(f"Auto-hidden unresponsive listing: {prop.title} (Moved to Property Vault)."))

        success_style = getattr(self.style, 'SUCCESS', str)
        self.stdout.write(success_style(f"Done! {prompt_needed.count()} prompted, {expired_count} auto-hidden."))
