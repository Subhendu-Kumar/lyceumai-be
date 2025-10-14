-- CreateTable
CREATE TABLE "MeetingData" (
    "id" TEXT NOT NULL,
    "recordingUrl" TEXT,
    "transcript" TEXT,
    "summary" TEXT,
    "classMeetingId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MeetingData_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "MeetingData" ADD CONSTRAINT "MeetingData_classMeetingId_fkey" FOREIGN KEY ("classMeetingId") REFERENCES "ClassMeetings"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
