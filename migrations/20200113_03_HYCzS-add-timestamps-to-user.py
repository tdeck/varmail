"""
Add timestamps to user

"""

from yoyo import step

__depends__ = {'20200113_02_lQGmT-add-signup-ips-to-users'}

steps = [
    step("""
        ALTER TABLE "user"
            ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT TO_TIMESTAMP(0),
            ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT TO_TIMESTAMP(0);
        """)
]
