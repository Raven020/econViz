// Dashboard page — SSR with data, hydrates with SWR for live updates.

import { fetchDashboardSSR, fetchRegimeSSR, fetchMacroSSR } from "../lib/serverFetch";
import DashboardClient from "../components/DashboardClient";

export default async function DashboardPage() {
  const [instruments, regime, macro] = await Promise.all([
    fetchDashboardSSR(),
    fetchRegimeSSR(),
    fetchMacroSSR(),
  ]);

  return (
    <DashboardClient
      initialInstruments={instruments ?? []}
      initialRegime={regime}
      initialMacro={macro ?? []}
    />
  );
}
