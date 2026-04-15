import { Prisma } from '@prisma/client';

export function isPrismaMissingTableError(error: unknown): boolean {
  return error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2021';
}

export function getPrismaErrorMessage(error: unknown): string {
  if (isPrismaMissingTableError(error)) {
    return 'The database schema is not available yet. Run your Prisma migrations or seed step against the deployed database.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Unexpected database error.';
}
