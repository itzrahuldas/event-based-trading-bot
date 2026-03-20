export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface RunLog {
    run_id: string;
    mode: string;
    start_time: string;
    status: string;
}

export interface Trade {
    id: number;
    timestamp: string;
    ticker: string;
    side: "BUY" | "SELL";
    quantity: number;
    price: number;
    strategy: string;
}

export interface Report {
    date: string;
    mode: string;
    metrics: any;
}

export async function fetchHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        return await res.json();
    } catch (e) {
        return { status: "offline" };
    }
}

export async function fetchRuns(limit = 10) {
    const res = await fetch(`${API_BASE}/runs?limit=${limit}`);
    return await res.json();
}

export async function fetchTrades(limit = 50) {
    const res = await fetch(`${API_BASE}/trades?limit=${limit}`);
    return await res.json();
}

export async function fetchLatestReport(mode: string = "PAPER") {
    const res = await fetch(`${API_BASE}/reports/latest?mode=${mode}`);
    return await res.json();
}

export async function fetchWeeklyReport(mode: string = "PAPER") {
    const res = await fetch(`${API_BASE}/reports/weekly?mode=${mode}`);
    return await res.json();
}

export async function generateReport(date: string, mode: string) {
    const res = await fetch(`${API_BASE}/reports/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, mode, universe: "NIFTY_NEXT50" })
    });
    return await res.json();
}
