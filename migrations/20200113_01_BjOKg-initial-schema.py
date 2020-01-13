"""
Initial schema

This was dumped from running db.create_all() and pulling the logged SQL, then adding
various IF NOT EXISTS clauses and a single fix.
"""

from yoyo import step

__depends__ = {}

steps = [
    step('''
        CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL NOT NULL, 
                email VARCHAR(255) NOT NULL, 
                login_token VARCHAR(22), 
                PRIMARY KEY (id), 
                UNIQUE (email), 
                UNIQUE (login_token)
        );

        CREATE TABLE IF NOT EXISTS endpoint (
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                id SERIAL NOT NULL, 
                token VARCHAR(22) NOT NULL, 
                user_id INTEGER NOT NULL, 
                name VARCHAR(255) NOT NULL, 
                disabled BOOLEAN NOT NULL, 
                PRIMARY KEY (id), 
                UNIQUE (token), 
                FOREIGN KEY(user_id) REFERENCES "user" (id)
        );

        CREATE INDEX IF NOT EXISTS ix_endpoint_user_id ON endpoint (user_id);

        CREATE TABLE IF NOT EXISTS message (
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                id SERIAL NOT NULL, 
                endpoint_id INTEGER NOT NULL, 
                subject TEXT NOT NULL, 
                body TEXT NOT NULL, 
                sent BOOLEAN NOT NULL, 
                reference_id VARCHAR(255), 
                reqid VARCHAR(32), 
                PRIMARY KEY (id), 
                FOREIGN KEY(endpoint_id) REFERENCES endpoint (id)
        );

        CREATE INDEX IF NOT EXISTS ix_message_endpoint_id ON message (endpoint_id);

        -- SQLAlchemy had generated this  which makes no sense
        -- This was supposed to be a compound index but SQLAlchemy did something weird here; fix it
        DROP INDEX IF EXISTS "(no name)";

        -- Here's my fix
        CREATE UNIQUE INDEX IF NOT EXISTS idx_endpoint_and_reqid ON message (endpoint_id, reqid);
    ''')
]
