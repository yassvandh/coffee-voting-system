import { useState, useEffect, useCallback } from "react";
import "./App.css";

const API_BASE = "http://localhost:5000/api";

/* ─── Coffee Card ─────────────────────────────────────────────────────────── */
function CoffeeCard({ coffee, onVote, rank }) {
  const [voting, setVoting] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: "success"|"error", msg }
  const [imgError, setImgError] = useState(false);

  const handleVote = async () => {
    if (voting) return;
    setVoting(true);
    setFeedback(null);

    try {
      const res = await fetch(`${API_BASE}/coffees/${coffee.id}/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Unknown error");
      }

      onVote(coffee.id, data.vote_count);
      setFeedback({ type: "success", msg: "✓ Vote recorded!" });
    } catch (err) {
      setFeedback({ type: "error", msg: `✗ ${err.message}` });
    } finally {
      setVoting(false);
      setTimeout(() => setFeedback(null), 3000);
    }
  };

  const rankColors = ["#FFD700", "#C0C0C0", "#CD7F32"];
  const showRank = rank <= 3;

  return (
    <article className={`card ${voting ? "card--voting" : ""}`} id={`coffee-card-${coffee.id}`}>
      {showRank && (
        <div className="card__rank" style={{ background: rankColors[rank - 1] }}>
          #{rank}
        </div>
      )}

      <div className="card__img-wrap">
        {imgError ? (
          <div className="card__img-fallback">
            <span>☕</span>
            <p>{coffee.name}</p>
          </div>
        ) : (
          <img
            src={coffee.image_url}
            alt={`A cup of ${coffee.name}`}
            className="card__img"
            loading="lazy"
            onError={() => setImgError(true)}
          />
        )}
        <div className="card__img-overlay" />
      </div>

      <div className="card__body">
        <h2 className="card__name">{coffee.name}</h2>
        <p className="card__desc">{coffee.description}</p>

        <div className="card__meta">
          <div className="card__votes">
            <span className="card__votes-icon">☕</span>
            <span className="card__votes-count">{coffee.vote_count}</span>
            <span className="card__votes-label">votes</span>
          </div>

          <button
            className={`btn-vote ${voting ? "btn-vote--loading" : ""}`}
            onClick={handleVote}
            disabled={voting}
            id={`vote-btn-${coffee.id}`}
            aria-label={`Vote for ${coffee.name}`}
          >
            {voting ? (
              <>
                <span className="spinner" />
                Voting…
              </>
            ) : (
              "Vote for Coffee"
            )}
          </button>
        </div>

        {feedback && (
          <div
            className={`card__feedback card__feedback--${feedback.type}`}
            role="alert"
            aria-live="polite"
          >
            {feedback.msg}
          </div>
        )}
      </div>
    </article>
  );
}

/* ─── Sort Controls ───────────────────────────────────────────────────────── */
function SortControls({ sortBy, onSortChange }) {
  return (
    <div className="sort-controls" role="group" aria-label="Sort coffees">
      <span className="sort-controls__label">Sort by:</span>
      {["popularity", "name"].map((opt) => (
        <button
          key={opt}
          className={`sort-btn ${sortBy === opt ? "sort-btn--active" : ""}`}
          onClick={() => onSortChange(opt)}
          id={`sort-${opt}`}
        >
          {opt === "popularity" ? "🏆 Popularity" : "🔤 Name"}
        </button>
      ))}
    </div>
  );
}

/* ─── Champion Banner ────────────────────────────────────────────────────── */
function ChampionBanner({ coffee }) {
  if (!coffee) return null;
  return (
    <section className="champion" aria-label="Top voted coffee">
      <div className="champion__inner">
        <span className="champion__crown">👑</span>
        <div>
          <p className="champion__label">Current Fan Favorite</p>
          <h2 className="champion__name">{coffee.name}</h2>
          <p className="champion__votes">
            {coffee.vote_count === 0
              ? "No votes yet – be the first!"
              : `${coffee.vote_count} ${coffee.vote_count === 1 ? "vote" : "votes"}`}
          </p>
        </div>
      </div>
    </section>
  );
}

/* ─── App ─────────────────────────────────────────────────────────────────── */
export default function App() {
  const [coffees, setCoffees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState("popularity");

  const fetchCoffees = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/coffees`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || "API error");
      setCoffees(data.coffees);
    } catch (err) {
      setError(`Could not load coffees: ${err.message}. Make sure the backend is running on port 5000.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCoffees();
  }, [fetchCoffees]);

  const handleVote = useCallback((coffeeId, newCount) => {
    setCoffees((prev) =>
      prev.map((c) => (c.id === coffeeId ? { ...c, vote_count: newCount } : c))
    );
  }, []);

  const sortedCoffees = [...coffees].sort((a, b) => {
    if (sortBy === "popularity") return b.vote_count - a.vote_count;
    return a.name.localeCompare(b.name);
  });

  // Champion: highest vote count (use popularity sort to find it)
  const champion = coffees.length
    ? [...coffees].sort((a, b) => b.vote_count - a.vote_count)[0]
    : null;

  return (
    <div className="app">
      {/* ── Nav ── */}
      <nav className="navbar" role="navigation" aria-label="Main navigation">
        <div className="navbar__inner">
          <a href="/" className="navbar__brand" aria-label="Coffee Rating home">
            <span className="navbar__icon">☕</span>
            <span className="navbar__title">Coffee Rating</span>
          </a>
          <span className="navbar__tagline">Community-Powered Coffee Votes</span>
        </div>
      </nav>

      {/* ── Hero ── */}
      <header className="hero" role="banner">
        <div className="hero__inner">
          <p className="hero__eyebrow">Discover &amp; Vote</p>
          <h1 className="hero__heading">Vote for Your Favorite Coffee</h1>
          <p className="hero__sub">
            Cast your vote, shape the rankings, and find your perfect brew.
          </p>
        </div>
        <div className="hero__beans" aria-hidden="true">
          {["☕", "🫘", "☕", "🫘", "☕"].map((icon, i) => (
            <span key={i} className="hero__bean" style={{ "--i": i }}>
              {icon}
            </span>
          ))}
        </div>
      </header>

      <main className="main" id="main-content">
        {/* ── Champion ── */}
        {!loading && !error && <ChampionBanner coffee={champion} />}

        {/* ── Sort ── */}
        {!loading && !error && coffees.length > 0 && (
          <SortControls sortBy={sortBy} onSortChange={setSortBy} />
        )}

        {/* ── Loading ── */}
        {loading && (
          <div className="state-loading" role="status" aria-live="polite">
            <div className="loader" />
            <p>Brewing your coffee list…</p>
          </div>
        )}

        {/* ── Error ── */}
        {!loading && error && (
          <div className="state-error" role="alert">
            <span className="state-error__icon">⚠️</span>
            <p>{error}</p>
            <button className="btn-retry" onClick={fetchCoffees} id="retry-btn">
              Try Again
            </button>
          </div>
        )}

        {/* ── Empty ── */}
        {!loading && !error && coffees.length === 0 && (
          <div className="state-empty" role="status">
            <span>☕</span>
            <p>No coffees found. Check the backend database.</p>
          </div>
        )}

        {/* ── Grid ── */}
        {!loading && !error && sortedCoffees.length > 0 && (
          <section className="grid" aria-label="Coffee varieties">
            {sortedCoffees.map((coffee, idx) => (
              <CoffeeCard
                key={coffee.id}
                coffee={coffee}
                onVote={handleVote}
                rank={
                  sortBy === "popularity"
                    ? idx + 1
                    : [...coffees]
                        .sort((a, b) => b.vote_count - a.vote_count)
                        .findIndex((c) => c.id === coffee.id) + 1
                }
              />
            ))}
          </section>
        )}
      </main>

      <footer className="footer" role="contentinfo">
        <p>
          ☕ Coffee Rating App &bull; Votes are stored permanently in SQLite &bull;{" "}
          {new Date().getFullYear()}
        </p>
      </footer>
    </div>
  );
}
