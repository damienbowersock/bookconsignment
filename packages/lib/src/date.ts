import { DateTime } from 'luxon';

export const toTenantZone = (date: DateTime, timezone: string): DateTime => {
  return date.setZone(timezone, { keepLocalTime: false });
};

export const periodRange = (periodStart: string, periodEnd: string, timezone: string) => {
  const start = DateTime.fromISO(periodStart, { zone: timezone });
  const end = DateTime.fromISO(periodEnd, { zone: timezone });

  if (!start.isValid || !end.isValid) {
    throw new Error('Invalid period range');
  }

  return { start, end };
};

export const startOfDay = (date: Date, timezone: string): DateTime => {
  return DateTime.fromJSDate(date, { zone: timezone }).startOf('day');
};
