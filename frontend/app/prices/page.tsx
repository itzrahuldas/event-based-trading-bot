"use client";
import React, { useEffect, useState } from 'react';
import { BarChart2, Clock } from 'lucide-react';

interface Price {
    ticker: string;
    time: string;
    close: number;
}

export default function PricesPage() {
    const [prices, setPrices] = useState<Price[]>([]);

    useEffect(() => {
        fetch('http://localhost:8000/prices/latest')
            .then(res => res.json())
            .then(setPrices)
            .catch(() => setPrices([]));
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Latest Prices</h1>

            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                <div className="p-6 border-b border-slate-800">
                    <div className="flex items-center gap-3">
                        <BarChart2 className="w-6 h-6 text-blue-500" />
                        <h2 className="text-lg font-semibold">Market Data</h2>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-950/50 text-slate-400">
                            <tr>
                                <th className="p-4">Ticker</th>
                                <th className="p-4">Close Price</th>
                                <th className="p-4">
                                    <div className="flex items-center gap-2">
                                        <Clock className="w-4 h-4" />
                                        Time
                                    </div>
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {prices.map((price, idx) => (
                                <tr key={idx} className="hover:bg-slate-800/50">
                                    <td className="p-4 font-bold text-blue-400">{price.ticker}</td>
                                    <td className="p-4">₹{price.close.toFixed(2)}</td>
                                    <td className="p-4 text-slate-500">{price.time}</td>
                                </tr>
                            ))}
                            {prices.length === 0 && (
                                <tr>
                                    <td colSpan={3} className="p-8 text-center text-slate-500">
                                        No price data available.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
