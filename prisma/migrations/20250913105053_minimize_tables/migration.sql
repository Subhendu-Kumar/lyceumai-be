/*
  Warnings:

  - You are about to drop the `VoiceFeedback` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `feedback` to the `VoiceSubmission` table without a default value. This is not possible if the table is not empty.
  - Added the required column `score` to the `VoiceSubmission` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "VoiceFeedback" DROP CONSTRAINT "VoiceFeedback_voiceSubmissionId_fkey";

-- AlterTable
ALTER TABLE "VoiceSubmission" ADD COLUMN     "feedback" TEXT NOT NULL,
ADD COLUMN     "improvements" TEXT[],
ADD COLUMN     "score" INTEGER NOT NULL,
ADD COLUMN     "strengths" TEXT[];

-- DropTable
DROP TABLE "VoiceFeedback";
