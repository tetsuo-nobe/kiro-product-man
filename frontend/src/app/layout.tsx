import type { Metadata } from 'next';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: '商品管理',
  description: '商品情報管理Webアプリケーション',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
