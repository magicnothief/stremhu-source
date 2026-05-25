import { MigrationInterface, QueryRunner } from 'typeorm';

export class InitSchema1762598798738 implements MigrationInterface {
  name = 'InitSchema1762598798738';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(
      `CREATE TABLE "users" ("id" varchar PRIMARY KEY NOT NULL, "username" varchar NOT NULL, "password_hash" text, "stremio_token" varchar NOT NULL, "user_role" varchar CHECK( "user_role" IN ('admin','user') ) NOT NULL, "torrent_resolutions" text NOT NULL DEFAULT ('["2160P","1080P","720P","576P","540P","480P"]'), "torrent_languages" text NOT NULL DEFAULT ('["hu","en"]'), "torrent_seed" integer, CONSTRAINT "UQ_fe0bb3f6520ee0469504521e710" UNIQUE ("username"))`,
    );
    await queryRunner.query(
      `CREATE INDEX "IDX_37a561a6cfd07ed41e9f2d09d6" ON "users" ("stremio_token") `,
    );
    await queryRunner.query(
      `CREATE TABLE "sessions" ("sid" text PRIMARY KEY NOT NULL, "data" text NOT NULL, "expires" integer NOT NULL)`,
    );
    await queryRunner.query(
      `CREATE INDEX "IDX_b7b5a67d8378ee0fce99a4a191" ON "sessions" ("expires") `,
    );
    await queryRunner.query(
      `CREATE TABLE "settings" ("id" text PRIMARY KEY NOT NULL, "enebled_local_ip" boolean NOT NULL DEFAULT (0), "endpoint" text NOT NULL, "upload_limit" integer NOT NULL DEFAULT (-1), "hit_and_run" boolean NOT NULL DEFAULT (1), "cache_retention" text)`,
    );
    await queryRunner.query(
      `CREATE TABLE "web_torrent_runs" ("tracker" varchar CHECK( "tracker" IN ('ncore') ) NOT NULL, "torrent_id" varchar NOT NULL, "info_hash" varchar NOT NULL, "imdb_id" varchar NOT NULL, "uploaded" integer NOT NULL DEFAULT (0), CONSTRAINT "unique_web_torrent_run_tracker_torrent" UNIQUE ("tracker", "torrent_id"), PRIMARY KEY ("tracker", "torrent_id", "info_hash"))`,
    );
    await queryRunner.query(
      `CREATE TABLE "tracker_credentials" ("tracker" varchar CHECK( "tracker" IN ('ncore') ) PRIMARY KEY NOT NULL, "username" text NOT NULL, "password" text NOT NULL)`,
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP TABLE "tracker_credentials"`);
    await queryRunner.query(`DROP TABLE "web_torrent_runs"`);
    await queryRunner.query(`DROP TABLE "settings"`);
    await queryRunner.query(`DROP INDEX "IDX_b7b5a67d8378ee0fce99a4a191"`);
    await queryRunner.query(`DROP TABLE "sessions"`);
    await queryRunner.query(`DROP INDEX "IDX_37a561a6cfd07ed41e9f2d09d6"`);
    await queryRunner.query(`DROP TABLE "users"`);
  }
}
