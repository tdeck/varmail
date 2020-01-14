"""
Add signup IPs to users

"""

from yoyo import step

__depends__ = {'20200113_01_BjOKg-initial-schema'}

steps = [
    step('''
        ALTER TABLE "user" ADD COLUMN signup_ip VARCHAR(255);
    ''')
]
