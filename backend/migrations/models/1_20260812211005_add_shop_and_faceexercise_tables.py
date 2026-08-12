from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "benefits" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL
);
        CREATE TABLE IF NOT EXISTS "pro_tips" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "content" TEXT NOT NULL
);
        CREATE TABLE IF NOT EXISTS "products" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "price" DECIMAL(10,2) NOT NULL,
    "image_url" VARCHAR(255),
    "stripe_price_id" VARCHAR(255)
);
        CREATE TABLE IF NOT EXISTS "routines" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "icon" VARCHAR(10) NOT NULL,
    "level" VARCHAR(50) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "target" VARCHAR(100) NOT NULL,
    "steps" JSONB NOT NULL,
    "timing" VARCHAR(100) NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "benefits";
        DROP TABLE IF EXISTS "pro_tips";
        DROP TABLE IF EXISTS "products";
        DROP TABLE IF EXISTS "routines";"""
