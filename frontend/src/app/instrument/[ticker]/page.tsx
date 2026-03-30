// Drill-down page — instrument detail with price info,
// historical chart, Monte Carlo projection cones, and regime context.

"use client";

import { useParams } from "next/navigation";
import { Box, Typography, Container, Button } from "@mui/material";
import { useRouter } from "next/navigation";
import { useInstrument, useProjectionChart } from "../../../hooks/useApi";
import InstrumentDetail from "../../../components/InstrumentDetail";
import PriceChart from "../../../components/PriceChart";
import MonteCarloChart from "../../../components/MonteCarloChart";
import RegimeBanner from "../../../components/RegimeBanner";

const VALID_TICKER_RE = /^[A-Z0-9_]{1,20}$/;

export default function InstrumentPage() {
  const params = useParams();
  const ticker = decodeURIComponent(params.ticker as string);
  const router = useRouter();

  const isValidTicker = VALID_TICKER_RE.test(ticker);

  const { data: detail, error, isLoading } = useInstrument(isValidTicker ? ticker : null);
  const { data: projectionChart } = useProjectionChart(isValidTicker ? ticker : null);

  if (!isValidTicker) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography color="error">Invalid ticker: {ticker}</Typography>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography>Loading {ticker}...</Typography>
      </Container>
    );
  }

  if (error || !detail) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography color="error">Failed to load {ticker}.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Button onClick={() => router.push("/")} sx={{ mb: 2 }}>
        Back to Dashboard
      </Button>

      <InstrumentDetail data={detail} />

      {detail.regime && <RegimeBanner regime={detail.regime} />}

      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Price History
        </Typography>
        <PriceChart data={detail.history} />
      </Box>

      {projectionChart && projectionChart.length > 0 && (
        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            30-Day Monte Carlo Projections
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, maxWidth: 800 }}>
            The projection cone below is generated from 10,000 simulated price paths using a
            multivariate Monte Carlo simulation conditioned on the current market regime. The
            bands represent percentile outcomes: the <strong>50th percentile</strong> (median) is
            the most likely path, the <strong>25th and 75th</strong> percentiles define the
            probable range, and the <strong>10th and 90th</strong> percentiles represent tail
            scenarios. If the price falls below the 10th percentile, the asset is performing worse
            than 90% of simulated outcomes. Because all assets share the same correlated
            simulation, these projections are internally consistent — if equities project down in
            a risk-off regime, safe havens project accordingly.
          </Typography>
          <MonteCarloChart data={projectionChart} />
        </Box>
      )}
    </Container>
  );
}
