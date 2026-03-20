"use client";
import React, { useEffect, useState } from 'react';
import { fetchHealth, fetchRuns, RunLog } from '@/lib/api';
import { Activity, Server, Clock } from 'lucide-react';

export default function Dashboard() {
    const [health, setHealth] = useState<any>(null);
    const [runs, setRuns] = useState<RunLog[]>([]);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        fetchHealth().then(setHealth);
        fetchRuns().then(setRuns);
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">System Overview</h1>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-green-500/10 text-green-500 rounded-lg">
                            <Activity className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">System Status</p>
                            <p className="text-xl font-bold">{health?.status || "Loading..."}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-blue-500/10 text-blue-500 rounded-lg">
                            <Server className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Database</p>
                            <p className="text-xl font-bold">{health?.db_ok ? "Connected" : "Unknown"}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-purple-500/10 text-purple-500 rounded-lg">
                            <Clock className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Last Pkg Update</p>
                            <p className="text-xl font-bold">{mounted ? new Date().toLocaleTimeString() : '--:--:--'}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Runs */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-lg font-semibold">Recent Activity</h2>
                </div>
                <div className="p-0">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-950/50 text-slate-400">
                            <tr>
                                <th className="p-4">Run ID</th>
                                <th className="p-4">Mode</th>
                                <th className="p-4">Start Time</th>
                                <th className="p-4">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {runs.map(run => (
                                <tr key={run.run_id} className="hover:bg-slate-800/50">
                                    <td className="p-4 font-mono text-xs text-slate-500">{run.run_id.substring(0, 8)}...</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${run.mode === 'LIVE' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                                            {run.mode}
                                        </span>
                                    </td>
                                    <td className="p-4">{new Date(run.start_time).toLocaleString()}</td>
                                    <td className="p-4">{run.status}</td>
                                </tr>
                            ))}
                            {runs.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="p-8 text-center text-slate-500">No runs found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
