import { NewsFeed } from "@/components/news-feed";
import { getPreferences, getSignals, getTrending, getWeeklyReport } from "@/lib/api";

const DEFAULT_EMAIL = "demo@ainewscollector.ai";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [signals, trending, preferences, weeklyReport] = await Promise.all([
    getSignals(DEFAULT_EMAIL),
    getTrending(),
    getPreferences(DEFAULT_EMAIL),
    getWeeklyReport(DEFAULT_EMAIL),
  ]);

  return <NewsFeed initialSignals={signals} trending={trending} preferences={preferences} weeklyReport={weeklyReport} />;
}
