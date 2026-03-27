// SignalR connection hook — connects to the C# gateway MarketHub.
// Handles MarketDataUpdated, RegimeChanged, and RefreshProgress events.

"use client";

import { useEffect, useRef } from "react";
import { HubConnectionBuilder, HubConnection } from "@microsoft/signalr";

const HUB_URL = (process.env.NEXT_PUBLIC_API_URL || "") + "/hubs/market";

export function useSignalR(
    onMarketDataUpdated?: () => void,
    onRegimeChanged?: () => void,
    onRefreshProgress?: (message: string) => void
) {
    const connectionRef = useRef<HubConnection | null>(null);

    useEffect(() => {
        const connection = new HubConnectionBuilder()
            .withUrl(HUB_URL)
            .withAutomaticReconnect()
            .build();

        connection.on("MarketDataUpdated", () => {
            onMarketDataUpdated?.();
        });

        connection.on("RegimeChanged", () => {
            onRegimeChanged?.();
        });

        connection.on("RefreshProgress", (message: string) => {
            onRefreshProgress?.(message);
        });

        connection.start().catch(console.error);
        connectionRef.current = connection;

        return () => {
            connection.stop();
        };
    }, []);

    return connectionRef;
}