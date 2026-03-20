"use client";
import React, { useEffect, useState } from 'react';
import { fetchLatestReport, fetchWeeklyReport, generateReport } from '@/lib/api';
import { FileText, TrendingUp, DollarSign, Percent, AlertTriangle, RefreshCw, Calendar, Activity } from 'lucide-react';
import { clsx } from 'clsx';

export default function ReportsPage() {
    const [report, setReport] = useState<any>(null);
    const [mode, setMode] = useState<string>("PAPER");
    const [timeRange, setTimeRange] = useState<"DAILY" | "WEEKLY">("DAILY");
    const [loading, setLoading] = useState(false);

    // Fetch on mount and when mode/timeRange changes
    useEffect(() => {
        loadReport();
    }, [mode, timeRange]);

    const loadReport = async () => {
        setLoading(true);
        try {
            const data = timeRange === "DAILY"
                ? await fetchLatestReport(mode)
                : await fetchWeeklyReport(mode);
            setReport(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        if (!report?.date) return;
        setLoading(true);
        try {
            await generateReport(report.date, mode);
            await loadReport();
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    // Helper to format currency
    const fmtMoney = (val: number) => `₹ ${val?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || '0.00'}`;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Performance Reports</h1>
                    <p className="text-slate-400 text-sm mt-1">
                        View your trading performance metrics
                    </p>
                </div>

                <div className="flex gap-4">
                    {/* Time Range Toggle */}
                    <div className="bg-slate-900 p-1 rounded-lg border border-slate-700 flex">
                        <button
                            onClick={() => setTimeRange("DAILY")}
                            className={clsx(
                                "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                                timeRange === "DAILY" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-white"
                            )}
                        >
                            Daily
                        </button>
                        <button
                            onClick={() => setTimeRange("WEEKLY")}
                            className={clsx(
                                "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                                timeRange === "WEEKLY" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-white"
                            )}
                        >
                            Weekly
                        </button>
                    </div>

                    {/* Mode Toggle */}
                    <button
                        onClick={() => setMode("PAPER")}
                        className={clsx(
                            "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                            mode === "PAPER" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white"
                        )}
                    >
                        PAPER
                    </button>
                    <button
                        onClick={() => setMode("LIVE")}
                        className={clsx(
                            "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                            mode === "LIVE" ? "bg-red-600 text-white" : "text-slate-400 hover:text-white"
                        )}
                    >
                        LIVE
                    </button>
                </div>
            </div>


            {/* Main Report Card */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 relative">
                {loading && (
                    <div className="absolute inset-0 bg-slate-900/50 flex items-center justify-center z-10 backdrop-blur-sm rounded-xl">
                        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
                    </div>
                )}

                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <FileText className="w-6 h-6 text-blue-500" />
                        <div>
                            <h2 className="text-xl font-semibold">
                                {report?.date ? `Report: ${report.date}` : "Latest Report"}
                            </h2>
                            <p className="text-slate-400 text-sm">{mode} Mode</p>
                        </div>
                    </div>

                    {report?.metrics && (
                        <button
                            onClick={handleGenerate}
                            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded text-sm text-blue-400 transition-colors"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Regenerate
                        </button>
                    )}
                </div>

                {report?.metrics ? (
                    <div className="space-y-6">
                        {/* High Level Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                            {/* Total Trades */}
                            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                <div className="flex items-center gap-3 mb-2">
                                    <TrendingUp className="w-5 h-5 text-blue-500" />
                                    <span className="text-sm text-slate-400">Total Trades</span>
                                </div>
                                <p className="text-2xl font-bold">{report.metrics.total_trades}</p>
                            </div>

                            {/* Net PnL */}
                            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                <div className="flex items-center gap-3 mb-2">
                                    <DollarSign className={clsx("w-5 h-5", report.metrics.net_pnl >= 0 ? "text-green-500" : "text-red-500")} />
                                    <span className="text-sm text-slate-400">Net P&L</span>
                                </div>
                                <p className={clsx("text-2xl font-bold", report.metrics.net_pnl >= 0 ? "text-green-400" : "text-red-400")}>
                                    {fmtMoney(report.metrics.net_pnl)}
                                </p>
                            </div>

                            {/* Win Rate */}
                            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                <div className="flex items-center gap-3 mb-2">
                                    <Percent className="w-5 h-5 text-purple-500" />
                                    <span className="text-sm text-slate-400">Win Rate</span>
                                </div>
                                <p className="text-2xl font-bold">{report.metrics.win_rate}%</p>
                            </div>

                            {/* Max Drawdown */}
                            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                <div className="flex items-center gap-3 mb-2">
                                    <Activity className="w-5 h-5 text-orange-500" />
                                    <span className="text-sm text-slate-400">Max Drawdown</span>
                                </div>
                                <p className="text-2xl font-bold text-orange-400">
                                    - {fmtMoney(Math.abs(report.metrics.max_drawdown))}
                                </p>
                            </div>
                        </div>

                        {/* Best/Worst */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
                            <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded text-sm">
                                <span className="text-slate-400">Best Trade</span>
                                <div className="flex gap-4">
                                    <span className="font-mono text-white">{report.metrics.best_ticker || "-"}</span>
                                    <span className="text-green-400">{fmtMoney(report.metrics.best_pnl)}</span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded text-sm">
                                <span className="text-slate-400">Worst Trade</span>
                                <div className="flex gap-4">
                                    <span className="font-mono text-white">{report.metrics.worst_ticker || "-"}</span>
                                    <span className="text-red-400">{fmtMoney(report.metrics.worst_pnl)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-800 mb-4">
                            <AlertTriangle className="w-6 h-6 text-amber-500" />
                        </div>
                        <h3 className="text-lg font-medium text-white mb-2">No Report Available</h3>
                        <p className="text-slate-400 max-w-sm mx-auto mb-6">
                            No trading activity found for today in {mode} mode.
                        </p>
                    </div>
                )}
            </div>
        </div >
    );
}
