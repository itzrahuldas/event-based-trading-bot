
"use client";
import React, { useEffect, useRef } from 'react';
import { toast } from 'sonner';

export default function RealtimeListener() {
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Connect to WS
        const wsUrl = "ws://localhost:8000/ws/stream";
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WS Connected");
        };

        ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);

                // Handle Heartbeat (ignore or debug)
                if (payload.type === "heartbeat") return;

                // Handle Trade Events
                if (payload.type === "TRADE_ENTRY" || payload.type === "TRADE_EXIT") {
                    // Extract message from data.message (string)
                    const msg = payload.data?.message || "Trade Event";
                    // Simple cleaning of markdown specific to telegram if needed, 
                    // or just display raw. Sonner supports rich text logic? 
                    // Let's strip simple markdown for cleaner toast:
                    const cleanMsg = msg.replace(/\*/g, "").replace(/`/g, "");

                    toast.success(cleanMsg, {
                        duration: 5000,
                        position: 'top-right'
                    });
                }

                // Handle Kill Switch
                if (payload.type === "KILL_SWITCH") {
                    toast.error("KILL SWITCH TRIGGERED: " + payload.data?.message);
                }

            } catch (e) {
                console.error("WS Parse Error", e);
            }
        };

        ws.onclose = () => {
            console.log("WS Closed");
            // Simple reconnect logic could go here
        };

        return () => {
            ws.close();
        };
    }, []);

    return null; // Headless component
}
