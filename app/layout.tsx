import type { Metadata, Viewport } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

const poppins = Poppins({ subsets: ["latin"], weight: ["100", "200", "400", "700", '900'] });

export const viewport: Viewport = {
  themeColor: '#120012',
  colorScheme: 'dark',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${poppins.className}`}>
        {children}
      </body>
    </html>
  );
}


export const metadata: Metadata = {
  title: {
    default: 'Alibek Aitbekov ✷ MLOps / ML Engineer Portfolio',
    template: '%s - Alibek Aitbekov',
  },
  description:
    'MLOps and Machine Learning Engineer portfolio. Showcase of ML projects, MLOps experience, and expertise in PyTorch, Transformers, Web3, and Kubernetes.',
  applicationName: 'Alibek Aitbekov - MLOps / ML Engineer Portfolio',
  authors: [
    {
      name: 'Alibek Aitbekov',
      url: 'https://ait-prog.github.io/mysite/',
    },
  ],
  generator: 'Next.js',
  referrer: 'origin',
  creator: 'Alibek Aitbekov',
  publisher: 'Alibek Aitbekov',
};

