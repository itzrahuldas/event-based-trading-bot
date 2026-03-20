"use client";
import React, { useEffect, useState } from 'react';
import { fetchTrades, Trade } from '@/lib/api';

export default function TradesPage() {
    const [trades, setTrades] = useState<Trade[]>([]);

    useEffect(() => {
        fetchTrades().then(setTrades);
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Trade History</h1>

            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-950/50 text-slate-400">
                        <tr>
                            <th className="p-4">Ticker</th>
                            <th className="p-4">Side</th>
                            <th className="p-4">Qty</th>
                            <th className="p-4">Price</th>
                            <th className="p-4">Time</th>
                            <th className="p-4">Strategy</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {trades.map(trade => (
                            <tr key={trade.id} className="hover:bg-slate-800/50">
                                <td className="p-4 font-bold">{trade.ticker}</td>
                                <td className={`p-4 font-bold ${trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                                    {trade.side}
                                </td>
                                <td className="p-4">{trade.quantity}</td>
                                <td className="p-4">₹{trade.price.toFixed(2)}</td>
                                <td className="p-4">{new Date(trade.timestamp).toLocaleString()}</td>
                                <td className="p-4">{trade.strategy || "Unknown"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
