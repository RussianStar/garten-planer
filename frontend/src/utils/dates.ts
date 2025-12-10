export function parseISO(value: string): Date {
  return new Date(value);
}

export function differenceInCalendarDays(b: Date, a: Date): number {
  const msPerDay = 1000 * 60 * 60 * 24;
  const diff = b.getTime() - a.getTime();
  return Math.round(diff / msPerDay);
}
