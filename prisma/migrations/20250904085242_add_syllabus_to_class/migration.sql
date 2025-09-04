/*
  Warnings:

  - Added the required column `syllabusUrl` to the `Classroom` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Classroom" ADD COLUMN     "syllabusUrl" TEXT NOT NULL;
