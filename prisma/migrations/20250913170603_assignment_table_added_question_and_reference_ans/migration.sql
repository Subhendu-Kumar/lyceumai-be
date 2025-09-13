/*
  Warnings:

  - You are about to drop the column `description` on the `Assignment` table. All the data in the column will be lost.
  - Added the required column `question` to the `Assignment` table without a default value. This is not possible if the table is not empty.
  - Added the required column `referenceAns` to the `Assignment` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Assignment" DROP COLUMN "description",
ADD COLUMN     "question" TEXT NOT NULL,
ADD COLUMN     "referenceAns" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "VoiceSubmission" ADD COLUMN     "transcript" TEXT;
