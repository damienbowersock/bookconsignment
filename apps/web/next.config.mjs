import { createSecureHeaders } from 'next-secure-headers';

const nextConfig = {
  experimental: {
    typedRoutes: true
  },
  headers: async () => [
    {
      source: '/(.*)',
      headers: createSecureHeaders()
    }
  ],
  transpilePackages: ['@bookconsign/ui', '@bookconsign/lib', '@bookconsign/schemas', '@bookconsign/api-sdk']
};

export default nextConfig;
