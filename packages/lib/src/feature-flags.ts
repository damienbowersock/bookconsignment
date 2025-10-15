export type FeatureFlag =
  | 'pos.square'
  | 'pos.clover'
  | 'pos.lightspeed'
  | 'mobile.barcode_scanning'
  | 'reports.advanced'
  | 'stripe.connect';

export type FeatureFlagState = Record<FeatureFlag, boolean>;

export const defaultFlags: FeatureFlagState = {
  'pos.square': true,
  'pos.clover': false,
  'pos.lightspeed': false,
  'mobile.barcode_scanning': false,
  'reports.advanced': true,
  'stripe.connect': true
};

export const isFlagEnabled = (flags: FeatureFlagState, flag: FeatureFlag): boolean =>
  flags[flag] ?? false;
