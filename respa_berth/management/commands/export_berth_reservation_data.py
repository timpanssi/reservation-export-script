import csv
import os
import datetime
from pathlib import Path
from django.db.models import IntegerField, Case, When, Value, Subquery
from django.db.models.functions import Cast
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from respa_berth.models.berth_reservation import BerthReservation


class Command(BaseCommand):
    help = 'Export reservations and their details to a CSV file'

    def handle(self, *args, **options):

        home_directory = os.path.expanduser('~')
        current_date_for_filename = datetime.datetime.now().strftime("%Y-%m-%d")
        file_name = '{}_reservation_data.csv'.format(current_date_for_filename)

        #Create a new dir if it doesn't already exist
        csv_file_path = os.path.join(home_directory, 'exports', file_name)
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

        #To set correct time for timestamps when the csv was created.
        timezone_adjustment = 2
        #Remove duplicates
        reservations = BerthReservation.objects.annotate(
            charfield_as_int=Case(
                When(berth__resource__name__regex=r'^\d+$', then=Cast('berth__resource__name', IntegerField())),
                default=Value(9999),  # Those with non-integer value should go to the bottom of the list
                output_field=IntegerField()
            )
        ).order_by('berth__resource__unit__name', 'berth__resource__pk', 'charfield_as_int')


        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # CSV header row
            csv_writer.writerow([
                                'Timestamp',

                                'Resource ID', 'Resource external ID', 'Resource name', 'Resource description',
                                'Resource location', 'Resource reservation info', 'Resource is reservable',

                                'Unit name', 'Unit ID', 'Unit description',

                                'Purchase code', 'Purchase reserver identity code', 'Purchase reserver company', 'Purchase reserver name', 'Purchase reserver email',
                                'Purchase reserver phone', 'Purchase reserver address street', 'Purchase reserver address zip',
                                'Purchase reserver address city', 'Purchase price vat', 'Purchase price vat percent',
                                'Purchase product name','Purchase payment service order no.', 'Purchase payment service paid',
                                'Purchase payment service method', 'Purchase finished',

                                'Reservation begins', 'Reservation ends', 'Reservation is active',
                                'Reservation state updated at', 'Reservation reserver ssn',
                                'Reservation is paid', 'Reservation is paid at', 'Reservation key returned',
                                'Reservation key returned at', 'Reservation key return notification sent at',

                                'Berth width cm', 'Berth depth cm', 'Berth length cm', 'Berth price',
                                'Berth type','Berth is disabled', 'Berth reserving staff member', 'Berth is deleted',
                                     ])

            timestamp = timezone.now()
            adjusted_timestamp = timestamp + timedelta(hours=timezone_adjustment)
            formatted_timestamp = adjusted_timestamp.strftime('%Y-%m-%d %H:%M:%S')

            def safe_getattr(obj, attr, default=''):
                try:
                    for part in attr.split('.'):
                        if part.endswith("()"):
                            method_name = part[:-2]  # Remove '()' to get the method name
                            obj = getattr(obj, method_name)()
                        else:
                            obj = getattr(obj, part)
                    return obj if obj is not None else default
                except:
                    return default



            # Iterate over the reservations and write data to the CSV file
            for reservation in reservations:

                resource_id = safe_getattr(reservation, 'berth.resource.pk')
                reservation_external_id = safe_getattr(reservation, 'reservation.origin_id')

                resource_name = safe_getattr(reservation, 'berth.resource.name')
                resource_description = safe_getattr(reservation, 'berth.resource.description')
                resource_location = safe_getattr(reservation, 'berth.resource.location')
                resource_reservation_info = safe_getattr(reservation, 'berth.resource.reservation_info')
                resource_is_reservable = safe_getattr(reservation, 'berth.resource.is_reservable')

                resource_unit_name = safe_getattr(reservation, 'berth.resource.unit.name')
                resource_unit_id = safe_getattr(reservation, 'berth.resource.unit.id')
                resource_unit_description = safe_getattr(reservation, 'berth.resource.unit.description')

                purchase_code = safe_getattr(reservation, 'purchase.purchase_code')
                reservation_reserver_id = safe_getattr(reservation, 'reservation.reserver_id')
                reservation_reserver_company = safe_getattr(reservation, 'reservation.company')
                reservation_reserver_name = safe_getattr(reservation, 'reservation.reserver_name')
                reservation_reserver_email_address = safe_getattr(reservation, 'reservation.reserver_email_address')
                reservation_reserver_phone_number = safe_getattr(reservation, 'reservation.reserver_phone_number')
                reservation_reserver_address_street = safe_getattr(reservation, 'reservation.reserver_address_street')
                reservation_reserver_address_zip = safe_getattr(reservation, 'reservation.reserver_address_zip')
                reservation_reserver_address_city = safe_getattr(reservation, 'reservation.reserver_address_city')
                purchase_price_vat = safe_getattr(reservation, 'purchase.price_vat')
                purchase_vat_percent = safe_getattr(reservation,'purchase.vat_percent')
                purchase_product_name = safe_getattr(reservation, 'purchase.product_name')
                purchase_payment_service_order_number = safe_getattr(reservation, 'purchase.payment_service_order_number')
                purchase_payment_service_paid = safe_getattr(reservation, 'purchase.payment_service_paid')
                purchase_payment_service_method = safe_getattr(reservation, 'purchase.payment_service_method')
                purchase_finished = safe_getattr(reservation, 'purchase.finished')

                resource_begin = safe_getattr(reservation, 'reservation.begin')
                resource_end = safe_getattr(reservation, 'reservation.end')
                resource_is_active = safe_getattr(reservation, 'reservation.is_active()')
                reservation_state_updated_at = safe_getattr(reservation,'state_updated_at')
                reservation_reserver_ssn = safe_getattr(reservation, 'reserver_ssn')
                reservation_is_paid = safe_getattr(reservation, 'is_paid')
                reservation_is_paid_at = safe_getattr(reservation, 'is_paid_at')
                reservation_key_returned = safe_getattr(reservation, 'key_returned')
                reservation_key_returned_at = safe_getattr(reservation, 'key_returned_at')
                reservation_key_return_notification_sent_at = safe_getattr(reservation, 'key_return_notification_sent_at')

                berth_width_cm = safe_getattr(reservation, 'berth.width_cm')
                berth_depth_cm = safe_getattr(reservation, 'berth.depth_cm')
                berth_length_cm = safe_getattr(reservation, 'berth.length_cm')
                berth_price = safe_getattr(reservation, 'berth.price')
                berth_type = safe_getattr(reservation, 'berth.type')
                berth_is_disabled = safe_getattr(reservation, 'berth.is_disabled')
                berth_reserving_staff_member = safe_getattr(reservation, 'berth.reserving_staff_member')
                berth_is_deleted = safe_getattr(reservation, 'berth.is_deleted')

                csv_writer.writerow([
                    formatted_timestamp,

                    resource_id,
                    reservation_external_id,

                    resource_name,
                    resource_description,
                    resource_location,
                    resource_reservation_info,
                    resource_is_reservable,

                    resource_unit_name,
                    resource_unit_id,
                    resource_unit_description,

                    purchase_code,
                    reservation_reserver_id,
                    reservation_reserver_company,
                    reservation_reserver_name,
                    reservation_reserver_email_address,
                    reservation_reserver_phone_number,
                    reservation_reserver_address_street,
                    reservation_reserver_address_zip,
                    reservation_reserver_address_city,
                    purchase_price_vat,
                    purchase_vat_percent,
                    purchase_product_name,
                    purchase_payment_service_order_number,
                    purchase_payment_service_paid,
                    purchase_payment_service_method,
                    purchase_finished,

                    resource_begin,
                    resource_end,
                    resource_is_active,
                    reservation_state_updated_at,
                    reservation_reserver_ssn,
                    reservation_is_paid,
                    reservation_is_paid_at,
                    reservation_key_returned,
                    reservation_key_returned_at,
                    reservation_key_return_notification_sent_at,

                    berth_width_cm,
                    berth_depth_cm,
                    berth_length_cm,
                    berth_price,
                    berth_type,
                    berth_is_disabled,
                    berth_reserving_staff_member,
                    berth_is_deleted,
                ])

