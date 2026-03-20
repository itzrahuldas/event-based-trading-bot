"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Activity, FileText, BarChart2, Shield } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Trades', href: '/trades', icon: Activity },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Prices', href: '/prices', icon: BarChart2 },
];

export function Sidebar() {
    const pathname = usePathname();
    const [status, setStatus] = React.useState<"online" | "offline">("offline");

    React.useEffect(() => {
        const checkHealth = async () => {
            const res = await import('@/lib/api').then(m => m.fetchHealth());
            setStatus(res.status === "online" ? "online" : "offline");
        };

        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-64 bg-slate-900 border-r border-slate-800 h-screen flex flex-col p-4">
            <div className="text-xl font-bold text-blue-500 mb-8 flex items-center gap-2">
                <Shield className="w-6 h-6" />
                <span>TradingBot v4</span>
            </div>

            <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={clsx(
                                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                                isActive ? "bg-blue-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"
                            )}
                        >
                            <item.icon className="w-5 h-5" />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="mt-auto pt-4 border-t border-slate-800">
                <div className="flex items-center gap-2 px-2">
                    <div className={clsx("w-2.5 h-2.5 rounded-full animate-pulse",
                        status === "online" ? "bg-green-500" : "bg-red-500"
                    )} />
                    <span className="text-xs text-slate-400 font-mono uppercase">
                        System: {status}
                    </span>
                </div>
            </div>
        </div>
    );
}
