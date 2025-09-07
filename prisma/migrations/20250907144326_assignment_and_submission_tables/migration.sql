/*
  Warnings:

  - You are about to drop the column `content` on the `Submission` table. All the data in the column will be lost.
  - You are about to drop the column `fileUrl` on the `Submission` table. All the data in the column will be lost.
  - You are about to drop the column `grade` on the `Submission` table. All the data in the column will be lost.
  - Added the required column `type` to the `Assignment` table without a default value. This is not possible if the table is not empty.

*/
-- CreateEnum
CREATE TYPE "AssignmentType" AS ENUM ('TEXT', 'VOICE');

-- AlterTable
ALTER TABLE "Assignment" ADD COLUMN     "type" "AssignmentType" NOT NULL;

-- AlterTable
ALTER TABLE "Submission" DROP COLUMN "content",
DROP COLUMN "fileUrl",
DROP COLUMN "grade";

-- CreateTable
CREATE TABLE "TextSubmission" (
    "id" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "submissionId" TEXT NOT NULL,

    CONSTRAINT "TextSubmission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VoiceSubmission" (
    "id" TEXT NOT NULL,
    "fileUrl" TEXT NOT NULL,
    "submissionId" TEXT NOT NULL,

    CONSTRAINT "VoiceSubmission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VoiceFeedback" (
    "id" TEXT NOT NULL,
    "score" INTEGER NOT NULL,
    "feedback" TEXT NOT NULL,
    "strengths" TEXT[],
    "improvements" TEXT[],
    "voiceSubmissionId" TEXT NOT NULL,

    CONSTRAINT "VoiceFeedback_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "TextSubmission_submissionId_key" ON "TextSubmission"("submissionId");

-- CreateIndex
CREATE UNIQUE INDEX "VoiceSubmission_submissionId_key" ON "VoiceSubmission"("submissionId");

-- CreateIndex
CREATE UNIQUE INDEX "VoiceFeedback_voiceSubmissionId_key" ON "VoiceFeedback"("voiceSubmissionId");

-- AddForeignKey
ALTER TABLE "TextSubmission" ADD CONSTRAINT "TextSubmission_submissionId_fkey" FOREIGN KEY ("submissionId") REFERENCES "Submission"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "VoiceSubmission" ADD CONSTRAINT "VoiceSubmission_submissionId_fkey" FOREIGN KEY ("submissionId") REFERENCES "Submission"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "VoiceFeedback" ADD CONSTRAINT "VoiceFeedback_voiceSubmissionId_fkey" FOREIGN KEY ("voiceSubmissionId") REFERENCES "VoiceSubmission"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
