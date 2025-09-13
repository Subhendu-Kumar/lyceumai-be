-- AlterTable
ALTER TABLE "TextSubmission" ADD COLUMN     "feedback" TEXT,
ADD COLUMN     "improvements" TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN     "score" INTEGER,
ADD COLUMN     "strengths" TEXT[] DEFAULT ARRAY[]::TEXT[];

-- AlterTable
ALTER TABLE "VoiceSubmission" ALTER COLUMN "feedback" DROP NOT NULL,
ALTER COLUMN "improvements" SET DEFAULT ARRAY[]::TEXT[],
ALTER COLUMN "score" DROP NOT NULL,
ALTER COLUMN "strengths" SET DEFAULT ARRAY[]::TEXT[];
