#!/bin/bash

# ============================================================
# SentinelLedger — Automated Database Backup Script
# Runs daily to keep your data safe
# Stores the last 7 days of backups and cleans up old ones
# ============================================================

# --- Configuration ---
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$HOME/sentinelledger_backups"
DB_NAME="sentinelledger"
DB_USER="postgres"

echo "============================================================"
echo "  SentinelLedger Daily Backup — $(date '+%d %B %Y at %H:%M')"
echo "============================================================"

# --- Create backup folder if it doesn't exist yet ---
mkdir -p $BACKUP_DIR
echo "📁 Backup folder ready at: $BACKUP_DIR"

# --- Take the backup ---
echo ""
echo "🔄 Connecting to PostgreSQL and backing up database..."
pg_dump -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/backup_$DATE.sql"

# --- Check if it worked ---
if [ $? -eq 0 ]; then
    SIZE=$(du -sh "$BACKUP_DIR/backup_$DATE.sql" | cut -f1)
    echo "✅ Backup successful! File size: $SIZE"
    echo "📄 Saved as: backup_$DATE.sql"
else
    echo "❌ Something went wrong — backup failed!"
    echo "💡 Check your PostgreSQL connection and try again."
    exit 1
fi

# --- Clean up backups older than 7 days ---
echo ""
echo "🧹 Removing backups older than 7 days..."
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
echo "✅ Old backups cleaned up — keeping last 7 days only"

# --- Done ---
echo ""
echo "============================================================"
echo "  Backup complete! Your data is safe."
echo "============================================================"