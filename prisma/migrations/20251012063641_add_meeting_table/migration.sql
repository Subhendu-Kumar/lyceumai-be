-- CreateEnum
CREATE TYPE "MeetingStatus" AS ENUM ('ONGOING', 'CANCELED', 'SCHEDULED', 'COMPLETED');

-- CreateTable
CREATE TABLE "ClassMeetings" (
    "id" TEXT NOT NULL,
    "meetId" TEXT NOT NULL,
    "meetStatus" "MeetingStatus" NOT NULL DEFAULT 'SCHEDULED',
    "classroomId" TEXT NOT NULL,
    "MeetingTime" TIMESTAMP(3) NOT NULL,
    "CreatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ClassMeetings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ClassMeetings_meetId_key" ON "ClassMeetings"("meetId");

-- AddForeignKey
ALTER TABLE "ClassMeetings" ADD CONSTRAINT "ClassMeetings_classroomId_fkey" FOREIGN KEY ("classroomId") REFERENCES "Classroom"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
