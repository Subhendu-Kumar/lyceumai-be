/*
  Warnings:

  - You are about to drop the column `recordingUrl` on the `MeetingData` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[sessionId]` on the table `MeetingData` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `meetingCompletionTime` to the `MeetingData` table without a default value. This is not possible if the table is not empty.
  - Added the required column `sessionId` to the `MeetingData` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "MeetingData" DROP COLUMN "recordingUrl",
ADD COLUMN     "meetingCompletionTime" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "sessionId" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "MeetingData_sessionId_key" ON "MeetingData"("sessionId");
