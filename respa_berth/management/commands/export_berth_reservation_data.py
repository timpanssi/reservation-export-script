import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from respa_berth.models.berth import Berth
from respa_berth.models.berth_reservation import BerthReservation
from respa_berth.models.purchase import Purchase

class Command(BaseCommand):
    help = 'Export reservations and their details to a CSV file'

    def handle(self, *args, **options):

        timezone_adjustment = 2
        output_file = 'reservation_data.csv'
        reservations = BerthReservation.objects.all()

        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # CSV header row
            csv_writer.writerow(['Timestamp', 'Reserver name', 'Reserver email address', 'Reserver phone number',
                                  'Reserver address street','Reserver address zip', 'Reserver address city',
                                    'Product name', 'Is paid', 'Time of payment', 'Key returned', 'Time of key returned',
                                    'Resource', 'Price', 'Berth type', 'Reserving staff member', 'Is deleted' ])

            timestamp = timezone.now()
            adjusted_timestamp = timestamp + timedelta(hours=timezone_adjustment)
            formatted_timestamp = adjusted_timestamp.strftime('%Y-%m-%d %H:%M:%S')

            def safe_getattr(obj, attr, default='Empty'):
                try:
                    for part in attr.split('.'):
                        obj = getattr(obj, part)
                    return obj or default
                except:
                    return default

            # Iterate over the reservations and write data to the CSV file
            for reservation in reservations:
                reserver_name = safe_getattr(reservation, 'purchase.reserver_name')
                reserver_email_address = safe_getattr(reservation, 'purchase.reserver_email_address')
                reserver_phone_number = safe_getattr(reservation, 'purchase.reserver_phone_number')
                reserver_address_street = safe_getattr(reservation, 'purchase.reserver_address_street')
                reserver_address_zip = safe_getattr(reservation, 'purchase.reserver_address_zip')
                reserver_address_city = safe_getattr(reservation, 'purchase.reserver_address_city')
                product_name = safe_getattr(reservation, 'purchase.product_name')

                is_paid = safe_getattr(reservation, 'is_paid')
                is_paid_at = safe_getattr(reservation, 'is_paid_at')
                key_returned = safe_getattr(reservation, 'key_returned')
                key_returned_at = safe_getattr(reservation, 'key_returned_at')

                resource = safe_getattr(reservation, 'berth.resource')
                price = safe_getattr(reservation, 'berth.price')
                berth_type = safe_getattr(reservation, 'berth.type')
                reserving_staff_member = safe_getattr(reservation, 'berth.reserving_staff_member')
                is_deleted = safe_getattr(reservation, 'berth.is_deleted')

                csv_writer.writerow([
                    formatted_timestamp,

                    reserver_name,
                    reserver_email_address,
                    reserver_phone_number,
                    reserver_address_street,
                    reserver_address_zip,
                    reserver_address_city,
                    product_name,

                    is_paid,
                    is_paid_at,
                    key_returned,
                    key_returned_at,

                    resource,
                    price,
                    berth_type,
                    reserving_staff_member,
                    is_deleted
                ])

