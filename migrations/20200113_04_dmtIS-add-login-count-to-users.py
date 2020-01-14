"""
Add login count to users
"""

from yoyo import step

__depends__ = {'20200113_03_HYCzS-add-timestamps-to-user'}

steps = [
    step("""
        ALTER TABLE "user"
            ADD COLUMN login_count INTEGER NOT NULL DEFAULT 0;
        """)
]
