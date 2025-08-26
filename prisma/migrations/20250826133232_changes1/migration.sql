/*
  Warnings:

  - Added the required column `role` to the `Enrollment` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Enrollment" ADD COLUMN     "role" "Role" NOT NULL;
