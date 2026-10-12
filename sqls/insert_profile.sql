INSERT INTO linkedin (profile_id, profile)
VALUES (:profile_id, :profile)
ON CONFLICT(profile_id) DO UPDATE SET profile = :profile