import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { Inter, Montserrat } from 'next/font/google';

// Load fonts
const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const montserrat = Montserrat({ subsets: ['latin'], variable: '--font-montserrat' });

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>eCFR Analyzer</title>
        <meta name="description" content="Analyze and visualize Federal Regulations data" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={`${inter.variable} ${montserrat.variable} font-sans min-h-screen bg-background`}>
        <Component {...pageProps} />
      </main>
    </>
  );
}
