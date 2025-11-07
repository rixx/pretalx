# SPDX-FileCopyrightText: 2025-present Tobias Kunze and contributors
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django_scopes import scopes_disabled

from pretalx.common.models import ActivityLog


class Command(BaseCommand):
    help = "Migrate ActivityLog data from legacy_data (TextField) to data (JSONField)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Show what would be migrated without making changes",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            dest="batch_size",
            help="Number of records to process in each batch (default: 1000)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        with scopes_disabled():
            # Find all ActivityLog entries where legacy_data has content
            # but data is either null or empty dict
            from django.db.models import Q

            queryset = ActivityLog.objects.filter(
                legacy_data__isnull=False
            ).exclude(
                legacy_data=""
            ).filter(
                Q(data__isnull=True) | Q(data={})
            )

            total_count = queryset.count()

            if total_count == 0:
                self.stdout.write(self.style.SUCCESS("No records need migration"))
                return

            self.stdout.write(f"Found {total_count} records to migrate")

            migrated_count = 0
            error_count = 0
            processed = 0

            # Process in batches
            while processed < total_count:
                batch = list(queryset[processed:processed + batch_size])

                if not batch:
                    break

                records_to_update = []

                for log in batch:
                    try:
                        # Parse JSON from legacy_data
                        parsed_data = json.loads(log.legacy_data)
                        log.data = parsed_data
                        records_to_update.append(log)
                    except json.JSONDecodeError as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Error parsing JSON for ActivityLog ID {log.id}: {e}"
                            )
                        )
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"Unexpected error for ActivityLog ID {log.id}: {e}"
                            )
                        )

                # Bulk update if not in dry-run mode
                if not dry_run and records_to_update:
                    with transaction.atomic():
                        ActivityLog.objects.bulk_update(records_to_update, ["data"])

                migrated_count += len(records_to_update)
                processed += len(batch)

                # Progress indicator
                self.stdout.write(
                    f"Processed {processed}/{total_count} records "
                    f"({migrated_count} migrated, {error_count} errors)"
                )

        # Final statistics
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== Migration Summary ==="))
        self.stdout.write(f"Total records found: {total_count}")
        self.stdout.write(f"Successfully migrated: {migrated_count}")
        self.stdout.write(f"Errors encountered: {error_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No actual changes were made"))
        else:
            self.stdout.write(self.style.SUCCESS("Migration completed successfully"))
