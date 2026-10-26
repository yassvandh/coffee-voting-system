from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db, get_all_coffees, vote_for_coffee

app = Flask(__name__)
CORS(app, origins="*")

# ─── Initialize DB on startup ─────────────────────────────────────────────────
init_db()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/api/coffees", methods=["GET"])
def list_coffees():
    """Return all coffee varieties with their current vote counts."""
    try:
        coffees = get_all_coffees()
        return jsonify({"success": True, "coffees": coffees}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/coffees/<int:coffee_id>/vote", methods=["POST"])
def cast_vote(coffee_id):
    """Register one vote for the specified coffee."""
    try:
        updated = vote_for_coffee(coffee_id)

        if updated is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Coffee with id {coffee_id} not found.",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Vote recorded successfully",
                    "coffee_id": updated["id"],
                    "vote_count": updated["vote_count"],
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ─── Health check ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
