import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '../components/providers/providers';

const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'Consignify | Multi-tenant consignment management',
  description: 'Track inventory, settlements, and payouts for independent authors across bookstores.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-slate-950 text-slate-50 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
