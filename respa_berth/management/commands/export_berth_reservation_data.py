import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from respa_berth.models.berth import Berth
from respa_berth.models.berth_reservation import BerthReservation
from respa_berth.models.purchase import Purchase


class Command(BaseCommand):
    help = 'Export reservations, their details, and purchasers to a CSV file'

    def handle(self, *args, **options):
        output_file = 'reservation_data.csv'

        reservations = BerthReservation.objects.all().select_related('berth__resource', 'purchase__purchase_code')

        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # CSV header row
            csv_writer.writerow(['Timestamp','Reservation ID', 'Resource ID', 'Price', 'Purchase Code', 'Reserver Name', 'Email'])

            timestamp = timezone.now()
            # Iterate over the reservations and write data to the CSV file
            for reservation in reservations:
                csv_writer.writerow([
                    timestamp,
                    reservation.is_paid,
                    reservation.berth.resource.id,
                    reservation.berth.price,
                    reservation.purchase.purchase_code if reservation.purchase else '',
                    reservation.purchase.reserver_name if reservation.purchase else '',
                    reservation.purchase.reserver_email_address,
                ])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported data to {output_file}'))
