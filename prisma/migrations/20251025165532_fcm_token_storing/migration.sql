-- CreateTable
CREATE TABLE "FCMToken" (
    "id" TEXT NOT NULL,
    "fcmToken" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "FCMToken_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "FCMToken_fcmToken_key" ON "FCMToken"("fcmToken");

-- CreateIndex
CREATE UNIQUE INDEX "FCMToken_userId_key" ON "FCMToken"("userId");

-- AddForeignKey
ALTER TABLE "FCMToken" ADD CONSTRAINT "FCMToken_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
