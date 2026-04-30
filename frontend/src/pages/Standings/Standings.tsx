import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import "./Standings.css";
import { useAuth } from "../../context/AuthContext";

type Profile = {
  id: string;
  society_name: string;
  realized_pnl: number;
  initial_capital: number;
  competition_score: number;
  return_score: number;
  risk_score: number;
  consistency_score: number;
  activity_score: number;
};

const HARDCODED_STANDINGS: Profile[] = [
  {
    id: "1",
    society_name: "International University of Monaco Finance Society",
    competition_score: 82,
    return_score: 91,
    risk_score: 73,
    consistency_score: 72,
    activity_score: 73,
    realized_pnl: 13580.21,
    initial_capital: 100000,
  },
  {
    id: "2",
    society_name: "Irish Student Managed Fund",
    competition_score: 70,
    return_score: 76,
    risk_score: 63,
    consistency_score: 64,
    activity_score: 65,
    realized_pnl: 8776.71,
    initial_capital: 100000,
  },
  {
    id: "3",
    society_name: "Marshall Finance Group",
    competition_score: 63,
    return_score: 64,
    risk_score: 69,
    consistency_score: 46,
    activity_score: 72,
    realized_pnl: 4565.23,
    initial_capital: 100000,
  },
  {
    id: "4",
    society_name: "University of Birmingham Investment & Finance Society",
    competition_score: 56,
    return_score: 53,
    risk_score: 50,
    consistency_score: 72,
    activity_score: 58,
    realized_pnl: 1117.11,
    initial_capital: 100000,
  },
  {
    id: "5",
    society_name: "University of Southampton Trading & Investment Society",
    competition_score: 51,
    return_score: 55,
    risk_score: 28,
    consistency_score: 67,
    activity_score: 65,
    realized_pnl: 1611.94,
    initial_capital: 100000,
  },
  {
    id: "6",
    society_name: "Warwick Trading Society",
    competition_score: 50,
    return_score: 52,
    risk_score: 35,
    consistency_score: 57,
    activity_score: 65,
    realized_pnl: 731.52,
    initial_capital: 100000,
  },
  {
    id: "7",
    society_name: "ESSCA Finance Society",
    competition_score: 49,
    return_score: 48,
    risk_score: 43,
    consistency_score: 61,
    activity_score: 54,
    realized_pnl: -308.2,
    initial_capital: 100000,
  },
  {
    id: "8",
    society_name: "University College Cork Student Managed Fund",
    competition_score: 44,
    return_score: 47,
    risk_score: 46,
    consistency_score: 46,
    activity_score: 24,
    realized_pnl: -463.0,
    initial_capital: 100000,
  },
  {
    id: "9",
    society_name: "National College of Ireland (NCI)",
    competition_score: 44,
    return_score: 49,
    risk_score: 24,
    consistency_score: 47,
    activity_score: 68,
    realized_pnl: -199.75,
    initial_capital: 100000,
  },
  {
    id: "10",
    society_name: "University of Galway Student Managed Fund",
    competition_score: 40,
    return_score: 34,
    risk_score: 30,
    consistency_score: 56,
    activity_score: 69,
    realized_pnl: -2585.04,
    initial_capital: 100000,
  },
];

export default function Standings() {
  const { session } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const sortProfiles = useCallback((profileList: Profile[]) => {
    return [...profileList].sort((a, b) => {
      const scoreA = a.competition_score || 0;
      const scoreB = b.competition_score || 0;

      if (scoreB !== scoreA) {
        return scoreB - scoreA;
      }

      return (b.realized_pnl || 0) - (a.realized_pnl || 0);
    });
  }, []);

  const fetchStandings = useCallback(async () => {
    if (profiles.length === 0) {
      setLoading(true);
    }
    setError(null);

    // Simulate fetch with hardcoded data
    setTimeout(() => {
      const sortedProfiles = sortProfiles(HARDCODED_STANDINGS);
      setProfiles(sortedProfiles);

      if (profiles.length === 0) {
        setLoading(false);
      }
    }, 100);
  }, [profiles.length, sortProfiles]);

  // Initial fetch
  useEffect(() => {
    fetchStandings();
  }, []);

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-UK", {
      style: "currency",
      currency: "EUR",
    }).format(value);

  const formatPercent = (value: number) =>
    `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;

  const calculateReturn = (profile: Profile) => {
    const initial = profile.initial_capital || 100000;
    if (initial === 0) return 0;
    // For hardcoded data without total_equity, base it on realized_pnl
    return (profile.realized_pnl / initial) * 100;
  };

  return (
    <div className="standings-container">
      <div className="standings-header">
        <h1>EuroPitch Portfolio Round Leaderboard</h1>
        <p className="subtitle">
          Track your society's performance against other societies
        </p>
      </div>

      {loading ? (
        <div className="loading">Loading leaderboard...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : profiles.length === 0 ? (
        <div className="empty-state">
          <p>No teams have joined yet. Be the first!</p>
        </div>
      ) : (
        <>
          {/* CLEAN PODIUM - Just medals, names, and scores */}
          {profiles.length >= 3 && (
            <div className="podium">
              <div className="podium-place second">
                <div className="podium-medal"></div>
                <h3 className="podium-society">{profiles[1].society_name}</h3>
                <div className="podium-score">
                  {profiles[1].competition_score || 0} pts
                </div>
              </div>

              <div className="podium-place first">
                <div className="podium-medal"></div>
                <h3 className="podium-society">{profiles[0].society_name}</h3>
                <div className="podium-score">
                  {profiles[0].competition_score || 0} pts
                </div>
              </div>

              <div className="podium-place third">
                <div className="podium-medal"></div>
                <h3 className="podium-society">{profiles[2].society_name}</h3>
                <div className="podium-score">
                  {profiles[2].competition_score || 0} pts
                </div>
              </div>
            </div>
          )}

          <div className="score-breakdown-legend">
            <h3>Score Breakdown</h3>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-weight">50%</span>
                <span className="legend-label">Return Score</span>
              </div>
              <div className="legend-item">
                <span className="legend-weight">25%</span>
                <span className="legend-label">Risk Score</span>
              </div>
              <div className="legend-item">
                <span className="legend-weight">15%</span>
                <span className="legend-label">Consistency Score</span>
              </div>
              <div className="legend-item">
                <span className="legend-weight">10%</span>
                <span className="legend-label">Activity Score</span>
              </div>
            </div>
          </div>

          <div className="standings-table-container">
            <table className="standings-table">
              <thead>
                <tr>
                  <th className="rank-col">Rank</th>
                  <th className="society-col">Society</th>

                  <th>P&L</th>
                  <th>Return %</th>
                  <th className="subscore-col">Return</th>
                  <th className="subscore-col">Risk</th>
                  <th className="subscore-col">Consistency</th>
                  <th className="subscore-col">Activity</th>
                  <th className="score-col">Competition Score</th>
                </tr>
              </thead>
              <tbody>
                {profiles.map((profile, index) => {
                  const returnPercent = calculateReturn(profile);
                  const isCurrentUser = session?.user?.id === profile.id;

                  return (
                    <tr
                      key={profile.id}
                      className={isCurrentUser ? "current-user" : ""}
                    >
                      <td className="rank-col">
                        <span
                          className={`rank-badge rank-${Math.min(index + 1, 4)}`}
                        >
                          {index === 0 && "🥇"}
                          {index === 1 && "🥈"}
                          {index === 2 && "🥉"}
                          {index > 2 && `#${index + 1}`}
                        </span>
                      </td>
                      <td className="society-col">
                        <strong>
                          {profile.society_name || "Unknown Society"}
                        </strong>
                      </td>

                      <td
                        className={
                          profile.realized_pnl >= 0 ? "positive" : "negative"
                        }
                      >
                        {formatCurrency(profile.realized_pnl || 0)}
                      </td>
                      <td
                        className={returnPercent >= 0 ? "positive" : "negative"}
                      >
                        {formatPercent(returnPercent)}
                      </td>
                      <td className="subscore-col">
                        {profile.return_score || 0}
                      </td>
                      <td className="subscore-col">
                        {profile.risk_score || 0}
                      </td>
                      <td className="subscore-col">
                        {profile.consistency_score || 0}
                      </td>
                      <td className="subscore-col">
                        {profile.activity_score || 0}
                      </td>
                      <td className="score-col">
                        <strong className="total-score">
                          {profile.competition_score || 0}
                        </strong>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="standings-footer">
            <p className="tiebreaker-note">
              In case of tied scores, P&L is used as tiebreaker
            </p>
            <p className="refresh-note">⟳ Realtime Live updates</p>
          </div>
        </>
      )}
    </div>
  );
}
