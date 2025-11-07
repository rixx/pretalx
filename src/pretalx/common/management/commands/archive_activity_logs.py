# SPDX-FileCopyrightText: 2025-present Tobias Kunze and contributors
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import gzip
import json
from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import now
from django_scopes import scopes_disabled

from pretalx.common.models import ActivityLog
from pretalx.event.models import Event


class Command(BaseCommand):
    help = (
        "Archive and/or delete old activity log entries to maintain database performance. "
        "Logs can be archived to compressed JSON files before deletion."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-days",
            type=int,
            default=365,
            dest="older_than_days",
            help="Delete logs older than this many days (default: 365, minimum: 90)",
        )
        parser.add_argument(
            "--event",
            type=str,
            dest="event_slug",
            help="Only process logs for the specified event slug",
        )
        parser.add_argument(
            "--archive-to",
            type=str,
            dest="archive_path",
            help="Archive logs to this directory before deletion (creates .jsonl.gz files)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Show what would be deleted/archived without making changes",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            dest="batch_size",
            help="Number of records to process in each batch (default: 1000)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="skip_confirmation",
            help="Skip confirmation prompt (use with caution)",
        )

    def handle(self, *args, **options):
        older_than_days = options["older_than_days"]
        event_slug = options["event_slug"]
        archive_path = options["archive_path"]
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        skip_confirmation = options["skip_confirmation"]

        # Safety checks
        if older_than_days < 90:
            raise CommandError(
                "Cannot delete logs less than 90 days old (safety limit). "
                "Use --older-than-days with a value of at least 90."
            )

        cutoff_date = now() - timedelta(days=older_than_days)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Build queryset
        with scopes_disabled():
            queryset = ActivityLog.objects.filter(timestamp__lt=cutoff_date)

            if event_slug:
                try:
                    event = Event.objects.get(slug=event_slug)
                    queryset = queryset.filter(event=event)
                    self.stdout.write(f"Filtering logs for event: {event.name} ({event.slug})")
                except Event.DoesNotExist:
                    raise CommandError(f"Event with slug '{event_slug}' does not exist")

            total_count = queryset.count()

            if total_count == 0:
                self.stdout.write(self.style.SUCCESS("No logs match the criteria"))
                return

            # Show summary and confirm
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("=== Summary ==="))
            self.stdout.write(f"Logs older than: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            if event_slug:
                self.stdout.write(f"Event filter: {event_slug}")
            self.stdout.write(f"Total logs to process: {total_count}")
            if archive_path:
                self.stdout.write(f"Archive to: {archive_path}")
            else:
                self.stdout.write(self.style.WARNING("No archive path specified - logs will be deleted permanently!"))
            self.stdout.write("")

            if not dry_run and not skip_confirmation:
                confirm = input("Do you want to proceed? [y/N]: ")
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.WARNING("Operation cancelled"))
                    return

            # Setup archive if specified
            archive_file = None
            if archive_path and not dry_run:
                archive_dir = Path(archive_path)
                archive_dir.mkdir(parents=True, exist_ok=True)

                timestamp = now().strftime("%Y%m%d_%H%M%S")
                filename = f"activitylog_archive_{timestamp}"
                if event_slug:
                    filename += f"_{event_slug}"
                filename += ".jsonl.gz"

                archive_file_path = archive_dir / filename
                self.stdout.write(f"Creating archive: {archive_file_path}")
                archive_file = gzip.open(archive_file_path, "wt", encoding="utf-8")

            # Process logs
            deleted_count = 0
            archived_count = 0
            processed = 0

            try:
                # Process in batches
                while processed < total_count:
                    # Get batch of IDs to avoid holding large queryset in memory
                    batch_ids = list(
                        queryset.values_list("id", flat=True)[processed:processed + batch_size]
                    )

                    if not batch_ids:
                        break

                    # Fetch full objects for this batch
                    batch = ActivityLog.objects.filter(id__in=batch_ids).select_related(
                        "person", "content_type", "event"
                    )

                    # Archive if requested
                    if archive_file:
                        for log in batch:
                            log_data = {
                                "id": log.id,
                                "timestamp": log.timestamp.isoformat(),
                                "event": log.event.slug if log.event else None,
                                "person": {
                                    "code": log.person.code,
                                    "name": log.person.name,
                                    "email": log.person.email,
                                } if log.person else None,
                                "content_type": {
                                    "app_label": log.content_type.app_label,
                                    "model": log.content_type.model,
                                } if log.content_type else None,
                                "object_id": log.object_id,
                                "action_type": log.action_type,
                                "data": log.json_data,
                                "is_orga_action": log.is_orga_action,
                            }
                            archive_file.write(json.dumps(log_data) + "\n")
                            archived_count += 1

                    # Delete if not dry run
                    if not dry_run:
                        with transaction.atomic():
                            deleted = ActivityLog.objects.filter(id__in=batch_ids).delete()
                            deleted_count += deleted[0]

                    processed += len(batch_ids)

                    # Progress indicator
                    self.stdout.write(
                        f"Processed {processed}/{total_count} logs "
                        f"({archived_count} archived, {deleted_count} deleted)"
                    )

            finally:
                if archive_file:
                    archive_file.close()
                    self.stdout.write(f"Archive saved to: {archive_file_path}")

            # Write metadata file if archived
            if archive_path and not dry_run:
                metadata = {
                    "created_at": now().isoformat(),
                    "cutoff_date": cutoff_date.isoformat(),
                    "event_slug": event_slug,
                    "total_logs": archived_count,
                    "batch_size": batch_size,
                }
                metadata_path = archive_file_path.with_suffix(".json")
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                self.stdout.write(f"Metadata saved to: {metadata_path}")

            # Final statistics
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=== Operation Summary ==="))
            self.stdout.write(f"Total logs processed: {processed}")
            if archive_file:
                self.stdout.write(f"Logs archived: {archived_count}")
            self.stdout.write(f"Logs deleted: {deleted_count}")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No actual changes were made"))
            else:
                self.stdout.write(self.style.SUCCESS("Operation completed successfully"))
