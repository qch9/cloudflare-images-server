import aiosqlite

from config import Config
from loguru import logger


async def setup_tables(db: aiosqlite.Connection):
    await db.executescript(
        '''
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS account(
            account_id TEXT PRIMARY KEY,
            account_hash TEXT NOT NULL
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS variant(
            variant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            account_id TEXT NOT NULL,
            FOREIGN KEY (account_id)
                REFERENCES account (account_id)
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS image(
            image_id TEXT PRIMARY KEY,
            name TEXT,
            uploaded_at INTEGER NOT NULL,
            require_signed_urls INTEGER NOT NULL,
            draft INTEGER NOT NULL,
            account_id TEXT NOT NULL,
            FOREIGN KEY (account_id) 
                REFERENCES account (account_id)
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS video(
            video_id TEXT PRIMARY KEY,
            name TEXT
        ) STRICT;
        '''
    )
    await db.commit()


async def setup_default_account(cfg: Config, db: aiosqlite.Connection):
    if cfg.create_default_account is False:
        return

    cursor = await db.execute('SELECT 1 FROM account WHERE account_id = ?', (cfg.default_account['account_id'],))
    if await cursor.fetchone() is None:
        await db.execute('INSERT INTO account(account_id, account_hash) VALUES (?, ?)',
                         (cfg.default_account['account_id'], cfg.default_account['account_hash']))
        await db.commit()
        logger.info(f"Created the default account: ACCOUNT_ID={cfg.default_account['account_id']}\n ACCOUNT_HASH={cfg.default_account['account_hash']}")
