# Database Migration for Firebase Authentication

## Migration Required

A database migration is needed to add the `firebase_uid` field to the `users` table and modify the `google_id` field to be nullable.

## Changes to Database Schema

### User Table (`users`)

**New field:**
- `firebase_uid` (VARCHAR(255), UNIQUE, NULLABLE, INDEXED) - Stores the Firebase UID for each user

**Modified field:**
- `google_id` (VARCHAR(255), UNIQUE, NULLABLE, INDEXED) - Made nullable to support Firebase-only users (previously NOT NULL)

## Run Migration

```bash
# Navigate to the Django project directory
cd /home/maxsa/epita/geopo/demperm-social/src/serveur/social/api

# Create the migration file
python manage.py makemigrations db

# Apply the migration
python manage.py migrate db
```

## Expected Migration Output

The migration should create SQL similar to:

```sql
-- Add firebase_uid column
ALTER TABLE users ADD COLUMN firebase_uid VARCHAR(255) NULL;

-- Make google_id nullable
ALTER TABLE users ALTER COLUMN google_id DROP NOT NULL;

-- Add unique constraint
ALTER TABLE users ADD CONSTRAINT users_firebase_uid_key UNIQUE (firebase_uid);

-- Add index
CREATE INDEX users_firebase_uid_idx ON users (firebase_uid);
```

## Verify Migration

After running the migration, verify the changes:

```bash
python manage.py dbshell
```

Then in the PostgreSQL shell:

```sql
-- Check users table structure
\d users;

-- Should show firebase_uid column with:
--   Type: character varying(255)
--   Nullable: yes
--   Index: users_firebase_uid_key (unique)
--   Index: users_firebase_uid_idx
```

## Rollback (if needed)

To rollback the migration:

```bash
# Find the migration number
python manage.py showmigrations db

# Rollback to previous migration (replace XXXX with previous migration number)
python manage.py migrate db XXXX
```

## Data Considerations

- Existing users with `google_id` will continue to work with Google OAuth
- New users can be created with only `firebase_uid` (no `google_id`)
- Both fields are unique, so a user can have either or both (but not duplicate values)
- The `firebase_uid` will be populated when users register via Firebase authentication
