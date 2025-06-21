import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Source of Creation Dashboard',
  description: 'Multi-agent AI platform with Atlantean/Egyptian motifs',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
