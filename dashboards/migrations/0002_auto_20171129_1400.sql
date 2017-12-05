BEGIN;
--
-- Create model Period
--
CREATE TABLE "period" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "year" integer NOT NULL, "month" integer NOT NULL);
--
-- Create model Products
--
CREATE TABLE "products" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" varchar(10) NOT NULL);
--
-- Create model Sources
--
CREATE TABLE "sources" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "source" varchar(10) NOT NULL);
--
-- Create model Stats
--
CREATE TABLE "product_stats" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "active" integer NOT NULL, "inactive" integer NOT NULL, "period_id" integer NOT NULL REFERENCES "period" ("id"), "product_id" integer NOT NULL REFERENCES "products" ("id"), "source_id" integer NOT NULL REFERENCES "sources" ("id"));
--
-- Alter field class_code on productstats
--
ALTER TABLE "product_statistics" RENAME TO "product_statistics__old";
CREATE TABLE "product_statistics" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" varchar(10) NOT NULL, "class_state" integer NOT NULL, "month" integer NOT NULL, "year" integer NOT NULL, "count" integer NOT NULL, "created_date" datetime NOT NULL, "class_code" varchar(10) NOT NULL);
INSERT INTO "product_statistics" ("id", "product", "class_state", "month", "year", "count", "created_date", "class_code") SELECT "id", "product", "class_state", "month", "year", "count", "created_date", "class_code" FROM "product_statistics__old";
DROP TABLE "product_statistics__old";
CREATE INDEX "product_stats_period_id_a3279616" ON "product_stats" ("period_id");
CREATE INDEX "product_stats_product_id_8fd9040d" ON "product_stats" ("product_id");
CREATE INDEX "product_stats_source_id_6d88d6b6" ON "product_stats" ("source_id");
--
-- Alter field class_state on productstats
--
ALTER TABLE "product_statistics" RENAME TO "product_statistics__old";
CREATE TABLE "product_statistics" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" varchar(10) NOT NULL, "class_code" varchar(10) NOT NULL, "month" integer NOT NULL, "year" integer NOT NULL, "count" integer NOT NULL, "created_date" datetime NOT NULL, "class_state" integer NOT NULL);
INSERT INTO "product_statistics" ("id", "product", "class_code", "month", "year", "count", "created_date", "class_state") SELECT "id", "product", "class_code", "month", "year", "count", "created_date", "class_state" FROM "product_statistics__old";
DROP TABLE "product_statistics__old";
--
-- Add field sources to products
--
ALTER TABLE "products" RENAME TO "products__old";
CREATE TABLE "products" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" varchar(10) NOT NULL);
INSERT INTO "products" ("id", "product") SELECT "id", "product" FROM "products__old";
DROP TABLE "products__old";
COMMIT;