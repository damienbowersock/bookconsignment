import { z } from 'zod';

const roundingSchema = z.enum(['HALF_UP', 'HALF_EVEN']);

export type RoundingMode = z.infer<typeof roundingSchema>;

export interface Money {
  amountCents: number;
  currency?: string;
}

export const toMoney = (amountCents: number, currency = 'USD'): Money => ({
  amountCents,
  currency
});

export const formatMoney = (
  amountCents: number,
  currency = 'USD',
  locale = 'en-US'
): string => {
  const formatter = Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  return formatter.format(amountCents / 100);
};

export const applySplit = (
  totalCents: number,
  percent: number,
  mode: RoundingMode = 'HALF_EVEN'
): number => {
  const raw = (totalCents * percent) / 100;
  return round(raw, mode);
};

export const round = (value: number, mode: RoundingMode): number => {
  switch (mode) {
    case 'HALF_UP':
      return Math.round(value);
    case 'HALF_EVEN': {
      const floor = Math.floor(value);
      const diff = value - floor;
      if (diff < 0.5) return floor;
      if (diff > 0.5) return floor + 1;
      return floor % 2 === 0 ? floor : floor + 1;
    }
    default:
      return Math.round(value);
  }
};
