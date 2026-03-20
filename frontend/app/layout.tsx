
import './globals.css';
import { Inter } from "next/font/google";
import { Toaster } from 'sonner';
import RealtimeListener from '@/components/RealtimeListener';
import { Sidebar } from '@/components/Sidebar';

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
    title: "TradingBot v4",
    description: "Event Based Trading Bot Dashboard",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${inter.className} flex h-screen overflow-hidden bg-slate-950 text-slate-100`}>
                <Sidebar />
                <main className="flex-1 overflow-y-auto p-8">
                    {children}
                </main>
                <Toaster richColors />
                <RealtimeListener />
            </body>
        </html>
    );
}
