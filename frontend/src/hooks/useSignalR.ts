// SignalR connection hook — connects to the C# gateway MarketHub.
// Handles MarketDataUpdated, RegimeChanged, and RefreshProgress events.
// Uses refs to avoid stale closures and unnecessary reconnections.

"use client";

import { useEffect, useRef } from "react";
import { HubConnectionBuilder, HubConnection } from "@microsoft/signalr";

const HUB_URL = (process.env.NEXT_PUBLIC_API_URL || "") + "/hubs/market";

export function useSignalR(
    onMarketDataUpdated?: () => void,
    onRegimeChanged?: () => void,
) {
    const connectionRef = useRef<HubConnection | null>(null);
    const onMarketRef = useRef(onMarketDataUpdated);
    const onRegimeRef = useRef(onRegimeChanged);

    onMarketRef.current = onMarketDataUpdated;
    onRegimeRef.current = onRegimeChanged;

    useEffect(() => {
        const connection = new HubConnectionBuilder()
            .withUrl(HUB_URL)
            .withAutomaticReconnect()
            .build();

        connection.on("MarketDataUpdated", () => onMarketRef.current?.());
        connection.on("RegimeChanged", () => onRegimeRef.current?.());

        connection.start().catch(console.error);
        connectionRef.current = connection;

        return () => {
            connection.stop();
        };
    }, []);

    return connectionRef;
}
