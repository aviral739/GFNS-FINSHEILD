"""
GLOBAL FINANCIAL NERVOUS SYSTEM - PYTHON BACKEND
Run: pip install flask flask-cors
     python backend_server.py
Server runs on http://localhost:4002
"""

import os, json, random, hashlib, base64, hmac, datetime, uuid, struct
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SHIELD_STORE = {}

R   = "\033[91m"
G   = "\033[92m"
Y   = "\033[93m"
B   = "\033[94m"
M   = "\033[95m"
C   = "\033[96m"
W   = "\033[97m"
DIM = "\033[2m"
BLD = "\033[1m"
RST = "\033[0m"

def banner(title, colour=C):
    line = "=" * 60
    print(f"\n{colour}{BLD}{line}{RST}")
    print(f"{colour}{BLD}  {title}{RST}")
    print(f"{colour}{BLD}{line}{RST}")

def log(label, value, colour=W):
    print(f"  {DIM}|{RST} {Y}{label:<28}{RST} {colour}{value}{RST}")

def section(title):
    dashes = "-" * (50 - len(title))
    print(f"\n  {DIM}-- {title} {dashes}{RST}")

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def rand_score(base=72, jitter=15):
    return max(0, min(100, base + random.randint(-jitter, jitter)))

def rand_pct(lo=55, hi=95):
    return round(random.uniform(lo, hi), 1)

def status_from_score(score):
    if score >= 75: return "stable"
    if score >= 50: return "warning"
    return "critical"

def colour_for_status(status):
    return {"stable": G, "warning": Y, "critical": R}.get(status, W)

def derive_key(passphrase, salt):
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100000, dklen=32)

def xor_encrypt(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def encrypt_payload(plaintext, passphrase="default-gfns-key"):
    salt   = os.urandom(16)
    iv     = os.urandom(12)
    key    = derive_key(passphrase, salt)
    cipher = xor_encrypt(plaintext.encode(), key)
    tag    = hmac.new(key, cipher + iv, hashlib.sha256).digest()
    return {
        "salt":    base64.b64encode(salt).decode(),
        "iv":      base64.b64encode(iv).decode(),
        "cipher":  base64.b64encode(cipher).decode(),
        "hmac":    base64.b64encode(tag).decode(),
        "algo":    "XOR-PBKDF2-HMAC-SHA256",
        "version": "v1",
    }


# =====================================================================
#  RANDOM IDENTITY DATA GENERATOR — new values every single call
# =====================================================================

FIRST_NAMES = ["Arjun","Priya","Rahul","Sneha","Vikram","Ananya","Rohit","Kavya",
                "James","Emma","Liam","Olivia","Noah","Ava","William","Sophia",
                "Ahmed","Fatima","Omar","Zara","Wei","Mei","Hiroshi","Yuki"]
LAST_NAMES  = ["Sharma","Patel","Singh","Kumar","Gupta","Nair","Reddy","Joshi",
                "Smith","Johnson","Williams","Brown","Jones","Garcia","Martinez",
                "Ali","Khan","Hassan","Ibrahim","Chen","Wang","Tanaka","Sato"]
DOMAINS     = ["gmail.com","yahoo.com","outlook.com","protonmail.com","icloud.com","hotmail.com"]
ID_TYPES    = ["Passport","Aadhaar","PAN Card","Driver License","National ID","Voter ID"]
BANKS       = ["HDFC Bank","ICICI Bank","SBI","Axis Bank","Kotak","Yes Bank",
               "Chase","Barclays","HSBC","Deutsche Bank","Citi","BNP Paribas"]
CARD_PREFIXES = ["4111","4532","4929","5234","5412","5500","3782","3714"]

def random_identity():
    """Generate a completely random realistic identity every call."""
    first  = random.choice(FIRST_NAMES)
    last   = random.choice(LAST_NAMES)
    age    = random.randint(22, 68)
    phone  = f"+{random.randint(1,99)}-{random.randint(6000000000,9999999999)}"
    email  = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{random.choice(DOMAINS)}"
    card   = f"{random.choice(CARD_PREFIXES)}-{''.join([str(random.randint(0,9)) for _ in range(4)])}-{''.join([str(random.randint(0,9)) for _ in range(4)])}-{''.join([str(random.randint(0,9)) for _ in range(4)])}"
    id_type = random.choice(ID_TYPES)
    id_num  = f"{''.join([str(random.randint(0,9)) for _ in range(10)])}"
    bank    = random.choice(BANKS)
    balance = round(random.uniform(1200, 950000), 2)
    risk    = random.choice(["LOW","MODERATE","ELEVATED","HIGH"])
    return {
        "name":    f"{first} {last}",
        "age":     str(age),
        "phone":   phone,
        "email":   email,
        "card":    card,
        "id_type": id_type,
        "id_num":  id_num,
        "bank":    bank,
        "balance": f"${balance:,.2f}",
        "risk":    risk,
    }

def mask(val, show=2):
    """Mask middle of a string, show only first and last N chars."""
    s = str(val)
    if len(s) <= show * 2:
        return "*" * len(s)
    return s[:show] + ("*" * (len(s) - show * 2)) + s[-show:]


@app.route("/api/data/dashboard", methods=["GET"])
def dashboard():
    score  = rand_score(74, 12)
    status = status_from_score(score)
    uptime = f"{rand_pct(99.1, 99.99):.2f}%"
    risk   = random.choice(["Low", "Moderate", "Elevated", "High"])
    banner(f"DASHBOARD REQUEST  [{timestamp()}]", B)
    log("Endpoint",            "GET /api/data/dashboard")
    log("System Score",        f"{score}/100",              colour_for_status(status))
    log("Status",              status.upper(),               colour_for_status(status))
    log("Uptime",              uptime,                       G)
    log("Risk Level",          risk,                         Y if risk in ("Moderate","Elevated") else (R if risk=="High" else G))
    log("Active Institutions", str(random.randint(55, 68)))
    log("Alerts Pending",      str(random.randint(0, 7)))
    return jsonify({"score": score, "status": status, "uptime": uptime, "riskLevel": risk, "ts": timestamp()})


@app.route("/api/data/instability-timeline", methods=["GET"])
def instability_timeline():
    range_param = request.args.get("range", "30d")
    days_map    = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    n_days      = days_map.get(range_param, 30)
    score  = rand_score(70, 10)
    points = []
    for i in range(n_days):
        score = max(10, min(100, score + random.gauss(0, 2.5)))
        points.append({"day": i+1, "score": round(score, 1), "label": f"Day {i+1}"})
    avg   = round(sum(p["score"] for p in points) / len(points), 1)
    trend = "Improving" if points[-1]["score"] > points[0]["score"] else "Deteriorating"
    banner(f"INSTABILITY TIMELINE  [{timestamp()}]", M)
    log("Endpoint",     f"GET /api/data/instability-timeline?range={range_param}")
    log("Range",        range_param)
    log("Data Points",  str(n_days))
    log("Avg Score",    f"{avg}/100", Y)
    log("Trend",        trend, G if "Improv" in trend else R)
    log("Peak",         f"{max(p['score'] for p in points):.1f}", G)
    log("Trough",       f"{min(p['score'] for p in points):.1f}", R)
    return jsonify({"range": range_param, "dataPoints": points, "average": avg, "trend": trend})


HEALTH_CONFIGS = {
    "bankCapital": {
        "label": "BANK CAPITAL ADEQUACY", "colour": B,
        "metrics": [
            ("Tier-1 Capital Ratio",     lambda: f"{rand_pct(11,16):.1f}%",   "Basel III min = 6%"),
            ("CET1 Ratio",               lambda: f"{rand_pct(10,14):.1f}%",   "Common Equity Tier-1"),
            ("Capital Conservation Buf", lambda: f"{rand_pct(2.5,3.5):.2f}%","Regulatory buffer"),
            ("Risk-Weighted Assets",     lambda: f"${rand_pct(400,900):.0f}B","Total RWA exposure"),
            ("Leverage Ratio",           lambda: f"{rand_pct(4,8):.1f}%",     "Non-risk-weighted"),
            ("DSCR",                     lambda: f"{rand_pct(1.2,2.1):.2f}x", "Debt Service Coverage"),
        ],
    },
    "liquidityCoverage": {
        "label": "LIQUIDITY COVERAGE RATIO", "colour": C,
        "metrics": [
            ("LCR",                    lambda: f"{rand_pct(108,145):.1f}%", "Min regulatory = 100%"),
            ("HQLA Buffer",            lambda: f"${rand_pct(80,200):.0f}B", "High-Quality Liquid Assets"),
            ("Net Cash Outflow (30d)", lambda: f"${rand_pct(60,140):.0f}B","Stressed 30-day outflows"),
            ("Intraday Liquidity",     lambda: f"{rand_pct(88,99):.1f}%",  "Intraday buffer usage"),
            ("Repo Market Access",     lambda: random.choice(["OPEN","TIGHT","STRESSED"]), ""),
            ("CB Facility Util",       lambda: f"{rand_pct(5,40):.1f}%",   "Central bank window"),
        ],
    },
    "debtExposure": {
        "label": "DEBT EXPOSURE PRESSURE", "colour": Y,
        "metrics": [
            ("Sovereign Debt Exposure", lambda: f"{rand_pct(15,45):.1f}%",   "% of total portfolio"),
            ("Non-Performing Loans",    lambda: f"{rand_pct(1.5,6):.2f}%",   "NPL ratio"),
            ("Loan-to-Deposit Ratio",   lambda: f"{rand_pct(75,105):.1f}%",  "Funding ratio"),
            ("Interbank Exposure",      lambda: f"${rand_pct(50,300):.0f}B", "Cross-bank lending"),
            ("Credit Default Swaps",    lambda: f"{rand_pct(80,350):.0f}bps","CDS spread"),
            ("Concentration Risk",      lambda: random.choice(["Low","Moderate","High","Severe"]), "HHI-based"),
        ],
    },
    "solvencyStress": {
        "label": "SOLVENCY STRESS INDEX", "colour": R,
        "metrics": [
            ("Stress Index",      lambda: f"{rand_pct(30,85):.1f}/100","Composite stress score"),
            ("Z-Score (Altman)",  lambda: f"{rand_pct(1.5,4.0):.2f}",  "<1.8 = distress zone"),
            ("Equity Volatility", lambda: f"{rand_pct(12,40):.1f}%",   "30-day realised vol"),
            ("Bail-in Eligibility",lambda: f"{rand_pct(60,95):.0f}%",  "MREL compliance"),
            ("Contagion Index",   lambda: f"{rand_pct(20,70):.1f}%",   "Network spillover risk"),
            ("Recovery Rate",     lambda: f"{rand_pct(40,80):.0f}%",   "In simulated default"),
        ],
    },
}

@app.route("/api/health/modal", methods=["POST"])
def health_modal():
    body = request.get_json(force=True) or {}
    key  = body.get("key", "bankCapital")
    cfg  = HEALTH_CONFIGS.get(key, HEALTH_CONFIGS["bankCapital"])
    banner(f"{cfg['label']}  [{timestamp()}]", cfg["colour"])
    log("Endpoint",    "POST /api/health/modal")
    log("Modal Key",   key)
    log("User Action", "Opened health detail modal", G)
    section("Live Metrics")
    result_metrics = {}
    for name, fn, note in cfg["metrics"]:
        val = fn()
        result_metrics[name] = val
        note_str = f"  ({note})" if note else ""
        print(f"    {W}{name:<32}{RST} {G}{val}{RST}{DIM}{note_str}{RST}")
    section("Risk Assessment")
    risk_lvl = random.choice(["LOW", "MODERATE", "ELEVATED", "HIGH"])
    action   = random.choice([
        "Monitor - within acceptable bounds",
        "Alert - approaching regulatory threshold",
        "Intervene - breaching stress trigger",
        "Escalate - immediate board notification required",
    ])
    print(f"    {Y}Risk Level  :{RST}  {risk_lvl}")
    print(f"    {Y}Recommended :{RST}  {action}")

    # ── STORE TO DATABASE — each modal → its own dedicated table ────
    section("Storage")
    import sqlite3
    ts_now  = datetime.datetime.now().isoformat()
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gfns_data.db")
    conn    = sqlite3.connect(db_path)
    cursor  = conn.cursor()

    if key == "bankCapital":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_capital_adequacy (
                id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                tier1_capital_ratio      TEXT,
                cet1_ratio               TEXT,
                capital_conservation_buf TEXT,
                risk_weighted_assets     TEXT,
                leverage_ratio           TEXT,
                dscr                     TEXT,
                risk_level               TEXT,
                action                   TEXT,
                created_at               TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO bank_capital_adequacy
            (tier1_capital_ratio, cet1_ratio, capital_conservation_buf,
             risk_weighted_assets, leverage_ratio, dscr,
             risk_level, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_metrics.get("Tier-1 Capital Ratio", ""),
            result_metrics.get("CET1 Ratio", ""),
            result_metrics.get("Capital Conservation Buf", ""),
            result_metrics.get("Risk-Weighted Assets", ""),
            result_metrics.get("Leverage Ratio", ""),
            result_metrics.get("DSCR", ""),
            risk_lvl, action, ts_now
        ))
        log("Database Saved", "YES — bank_capital_adequacy", G)

    elif key == "liquidityCoverage":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS liquidity_coverage (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                lcr                 TEXT,
                hqla_buffer         TEXT,
                net_cash_outflow    TEXT,
                intraday_liquidity  TEXT,
                repo_market_access  TEXT,
                cb_facility_util    TEXT,
                risk_level          TEXT,
                action              TEXT,
                created_at          TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO liquidity_coverage
            (lcr, hqla_buffer, net_cash_outflow, intraday_liquidity,
             repo_market_access, cb_facility_util,
             risk_level, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_metrics.get("LCR", ""),
            result_metrics.get("HQLA Buffer", ""),
            result_metrics.get("Net Cash Outflow (30d)", ""),
            result_metrics.get("Intraday Liquidity", ""),
            result_metrics.get("Repo Market Access", ""),
            result_metrics.get("CB Facility Util", ""),
            risk_lvl, action, ts_now
        ))
        log("Database Saved", "YES — liquidity_coverage", G)

    elif key == "debtExposure":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debt_exposure (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                sovereign_debt_exposure TEXT,
                non_performing_loans    TEXT,
                loan_to_deposit_ratio   TEXT,
                interbank_exposure      TEXT,
                credit_default_swaps    TEXT,
                concentration_risk      TEXT,
                risk_level              TEXT,
                action                  TEXT,
                created_at              TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO debt_exposure
            (sovereign_debt_exposure, non_performing_loans, loan_to_deposit_ratio,
             interbank_exposure, credit_default_swaps, concentration_risk,
             risk_level, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_metrics.get("Sovereign Debt Exposure", ""),
            result_metrics.get("Non-Performing Loans", ""),
            result_metrics.get("Loan-to-Deposit Ratio", ""),
            result_metrics.get("Interbank Exposure", ""),
            result_metrics.get("Credit Default Swaps", ""),
            result_metrics.get("Concentration Risk", ""),
            risk_lvl, action, ts_now
        ))
        log("Database Saved", "YES — debt_exposure", G)

    elif key == "solvencyStress":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solvency_stress (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                stress_index      TEXT,
                z_score_altman    TEXT,
                equity_volatility TEXT,
                bail_in_eligibility TEXT,
                contagion_index   TEXT,
                recovery_rate     TEXT,
                risk_level        TEXT,
                action            TEXT,
                created_at        TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO solvency_stress
            (stress_index, z_score_altman, equity_volatility,
             bail_in_eligibility, contagion_index, recovery_rate,
             risk_level, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_metrics.get("Stress Index", ""),
            result_metrics.get("Z-Score (Altman)", ""),
            result_metrics.get("Equity Volatility", ""),
            result_metrics.get("Bail-in Eligibility", ""),
            result_metrics.get("Contagion Index", ""),
            result_metrics.get("Recovery Rate", ""),
            risk_lvl, action, ts_now
        ))
        log("Database Saved", "YES — solvency_stress", G)

    conn.commit()
    conn.close()
    log("Stored At", ts_now, G)

    return jsonify({"key": key, "label": cfg["label"], "metrics": result_metrics, "risk": risk_lvl, "action": action, "ts": timestamp()})


SHOCK_SCENARIOS = {
    "liquidityCrisis": {
        "label": "Liquidity Crisis",
        "waves": [
            "Wave 1  [T+12h]: CB repo window oversubscribed by 340%",
            "Wave 2  [T+24h]: Interbank rates spike +420 bps",
            "Wave 3  [T+36h]: 3 mid-tier banks breach LCR minimum (100%)",
            "Wave 4  [T+48h]: Emergency CB facility activated for 5 institutions",
            "Wave 5  [T+60h]: Contagion index crosses critical 65% threshold",
        ],
    },
    "capitalShock": {
        "label": "Capital Shock",
        "waves": [
            "Wave 1  [T+12h]: Mark-to-market losses wipe 18% of bond portfolios",
            "Wave 2  [T+24h]: CET1 falls to 5.2% at 2 systemically important banks",
            "Wave 3  [T+36h]: Capital conservation buffer fully depleted",
            "Wave 4  [T+48h]: Regulatory intervention triggered - trading halted",
            "Wave 5  [T+60h]: Emergency capital raise - $80B required",
        ],
    },
    "sovereignDefault": {
        "label": "Sovereign Default",
        "waves": [
            "Wave 1  [T+12h]: Sovereign CDS spreads blow out to 1,200 bps",
            "Wave 2  [T+24h]: $2.4T in sovereign bond portfolios repriced",
            "Wave 3  [T+36h]: Collateral haircuts increased 40% on repo books",
            "Wave 4  [T+48h]: 6 pension funds breach solvency ratios",
            "Wave 5  [T+60h]: IMF emergency package request filed",
        ],
    },
    "rateShock": {
        "label": "Rate Shock +300bps",
        "waves": [
            "Wave 1  [T+12h]: Duration losses - 10Y bond prices drop 22%",
            "Wave 2  [T+24h]: Mortgage book NII compressed by $340B globally",
            "Wave 3  [T+36h]: Derivative margin calls exceed $1.2T in 48h",
            "Wave 4  [T+48h]: Smaller banks face deposit outflows of 8-12%",
            "Wave 5  [T+60h]: Central banks pivot - emergency rate cut considered",
        ],
    },
}

@app.route("/api/stress/inject-shock", methods=["POST"])
def inject_shock():
    body     = request.get_json(force=True) or {}
    scenario = body.get("scenario", "liquidityCrisis")
    hub_bank = body.get("hubBank", "Unknown Hub Bank")
    cfg      = SHOCK_SCENARIOS.get(scenario, SHOCK_SCENARIOS["liquidityCrisis"])
    affected = random.randint(3, 8)
    failed   = random.randint(1, min(3, affected))
    stressed = affected - failed
    impact   = rand_pct(35, 80)
    banner(f"SHOCK INJECTED: {cfg['label']}  [{timestamp()}]", R)
    log("Endpoint",  "POST /api/stress/inject-shock")
    log("Hub Bank",  hub_bank, Y)
    log("Scenario",  cfg["label"])
    section("Cascade Simulation")
    for wave in cfg["waves"]:
        print(f"    {R}{wave}{RST}")
    contagion_idx    = f"{rand_pct(50,90):.1f}%"
    recovery_horizon = f"{random.randint(3,18)} months"
    section("Impact Summary")
    log("Institutions Affected", str(affected),       R)
    log("Failed Nodes",          str(failed),          R)
    log("Stressed Nodes",        str(stressed),        Y)
    log("System Impact",         f"{impact:.1f}%",    R)
    log("Contagion Index",       contagion_idx,        R)
    log("Recovery Horizon",      recovery_horizon,     Y)

    # ── STORE TO DATABASE — scenario → its own dedicated table ──────
    section("Storage")
    import sqlite3

    ts_now = datetime.datetime.now().isoformat()

    # Try multiple likely db paths so it always finds the right file
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    db_candidates = [
        os.path.join(script_dir, "gfns_data.db"),
        os.path.join(os.getcwd(), "gfns_data.db"),
        "gfns_data.db",
    ]
    db_path = db_candidates[0]
    for candidate in db_candidates:
        if os.path.exists(candidate):
            db_path = candidate
            break

    log("DB Path", db_path, C)

    try:
        conn   = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Map scenario → table name + columns + values
        TABLE_MAP = {
            "capitalShock": {
                "table": "bank_capital_adequacy",
                "create": """CREATE TABLE IF NOT EXISTS bank_capital_adequacy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT, hub_bank TEXT,
                    institutions_affected INTEGER, failed_nodes INTEGER,
                    stressed_nodes INTEGER, system_impact TEXT,
                    contagion_index TEXT, recovery_horizon TEXT,
                    wave1 TEXT, wave2 TEXT, wave3 TEXT, wave4 TEXT, wave5 TEXT,
                    risk_level TEXT, created_at TEXT)""",
                "cols": "(scenario, hub_bank, institutions_affected, failed_nodes, stressed_nodes, system_impact, contagion_index, recovery_horizon, wave1, wave2, wave3, wave4, wave5, risk_level, created_at)",
                "vals": (cfg["label"], hub_bank, affected, failed, stressed,
                         f"{impact:.1f}%", contagion_idx, recovery_horizon,
                         cfg["waves"][0], cfg["waves"][1], cfg["waves"][2],
                         cfg["waves"][3], cfg["waves"][4], "CRITICAL", ts_now),
            },
            "liquidityCrisis": {
                "table": "liquidity_coverage",
                "create": """CREATE TABLE IF NOT EXISTS liquidity_coverage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT, hub_bank TEXT,
                    institutions_affected INTEGER, failed_nodes INTEGER,
                    stressed_nodes INTEGER, system_impact TEXT,
                    contagion_index TEXT, recovery_horizon TEXT,
                    wave1 TEXT, wave2 TEXT, wave3 TEXT, wave4 TEXT, wave5 TEXT,
                    risk_level TEXT, created_at TEXT)""",
                "cols": "(scenario, hub_bank, institutions_affected, failed_nodes, stressed_nodes, system_impact, contagion_index, recovery_horizon, wave1, wave2, wave3, wave4, wave5, risk_level, created_at)",
                "vals": (cfg["label"], hub_bank, affected, failed, stressed,
                         f"{impact:.1f}%", contagion_idx, recovery_horizon,
                         cfg["waves"][0], cfg["waves"][1], cfg["waves"][2],
                         cfg["waves"][3], cfg["waves"][4], "CRITICAL", ts_now),
            },
            "sovereignDefault": {
                "table": "debt_exposure",
                "create": """CREATE TABLE IF NOT EXISTS debt_exposure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT, hub_bank TEXT,
                    institutions_affected INTEGER, failed_nodes INTEGER,
                    stressed_nodes INTEGER, system_impact TEXT,
                    contagion_index TEXT, recovery_horizon TEXT,
                    wave1 TEXT, wave2 TEXT, wave3 TEXT, wave4 TEXT, wave5 TEXT,
                    risk_level TEXT, created_at TEXT)""",
                "cols": "(scenario, hub_bank, institutions_affected, failed_nodes, stressed_nodes, system_impact, contagion_index, recovery_horizon, wave1, wave2, wave3, wave4, wave5, risk_level, created_at)",
                "vals": (cfg["label"], hub_bank, affected, failed, stressed,
                         f"{impact:.1f}%", contagion_idx, recovery_horizon,
                         cfg["waves"][0], cfg["waves"][1], cfg["waves"][2],
                         cfg["waves"][3], cfg["waves"][4], "CRITICAL", ts_now),
            },
            "rateShock": {
                "table": "solvency_stress",
                "create": """CREATE TABLE IF NOT EXISTS solvency_stress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT, hub_bank TEXT,
                    institutions_affected INTEGER, failed_nodes INTEGER,
                    stressed_nodes INTEGER, system_impact TEXT,
                    contagion_index TEXT, recovery_horizon TEXT,
                    wave1 TEXT, wave2 TEXT, wave3 TEXT, wave4 TEXT, wave5 TEXT,
                    risk_level TEXT, created_at TEXT)""",
                "cols": "(scenario, hub_bank, institutions_affected, failed_nodes, stressed_nodes, system_impact, contagion_index, recovery_horizon, wave1, wave2, wave3, wave4, wave5, risk_level, created_at)",
                "vals": (cfg["label"], hub_bank, affected, failed, stressed,
                         f"{impact:.1f}%", contagion_idx, recovery_horizon,
                         cfg["waves"][0], cfg["waves"][1], cfg["waves"][2],
                         cfg["waves"][3], cfg["waves"][4], "CRITICAL", ts_now),
            },
        }

        if scenario in TABLE_MAP:
            m = TABLE_MAP[scenario]
            # Create table
            cursor.execute(m["create"])
            # Add any missing columns safely (in case table existed with old schema)
            existing_cols = {row[1] for row in cursor.execute(f"PRAGMA table_info({m['table']})")}
            needed_cols   = ["scenario","hub_bank","institutions_affected","failed_nodes",
                             "stressed_nodes","system_impact","contagion_index",
                             "recovery_horizon","wave1","wave2","wave3","wave4","wave5",
                             "risk_level","created_at"]
            for col in needed_cols:
                if col not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE {m['table']} ADD COLUMN {col} TEXT")
                    except Exception:
                        pass
            # Insert
            placeholders = ",".join(["?"] * len(m["vals"]))
            cursor.execute(f"INSERT INTO {m['table']} {m['cols']} VALUES ({placeholders})", m["vals"])
            conn.commit()
            log("Database Saved", f"YES — {m['table']} ({cursor.lastrowid} rows total)", G)
        else:
            log("Database Skip", f"Unknown scenario: {scenario}", Y)

        conn.close()

    except Exception as db_err:
        log("Database ERROR", str(db_err), R)
        print(f"    {R}Full error: {db_err}{RST}")

    log("Stored At", ts_now, G)

    return jsonify({"scenario": scenario, "hubBank": hub_bank, "affected": affected, "failed": failed, "stressed": stressed, "impact": impact, "waves": cfg["waves"], "ts": timestamp()})


STABILIZER_INFO = {
    "liquidity": {"label": "Liquidity Injection",   "action": "CB emergency repo - $500B allocated",            "effect": "LCR improved across 12 institutions",   "boost": 6},
    "capital":   {"label": "Capital Strengthening", "action": "Mandatory capital raise - Tier-1 floor at 8%",  "effect": "CET1 ratios restored; confidence +14pts", "boost": 5},
    "exposure":  {"label": "Exposure Reduction",    "action": "Sovereign debt restructuring - haircuts at 35%","effect": "NPL ratios reduced; risk weights revised",  "boost": 4},
}

@app.route("/api/stress/stabilize", methods=["POST"])
def stabilize():
    body   = request.get_json(force=True) or {}
    stab   = body.get("type", "liquidity")
    cfg    = STABILIZER_INFO.get(stab, STABILIZER_INFO["liquidity"])
    before = rand_score(45, 15)
    after  = min(100, before + cfg["boost"] * random.randint(3, 8))
    banner(f"STABILIZER APPLIED: {cfg['label']}  [{timestamp()}]", G)
    log("Endpoint",      "POST /api/stress/stabilize")
    log("Stabilizer",    cfg["label"])
    log("Policy Action", cfg["action"])
    log("Market Effect", cfg["effect"])
    section("Score Change")
    log("Score Before",  f"{before}/100",           R if before < 50 else Y)
    log("Score After",   f"{after}/100",             G)
    log("Improvement",   f"+{after - before} pts",  G)
    log("Status",        "System stabilising",      G)
    return jsonify({"type": stab, "label": cfg["label"], "before": before, "after": after, "delta": after - before, "ts": timestamp()})


# =====================================================================
#  FINANCIAL SHIELD — 5-STEP PIPELINE
#
#  Step 1: User enters raw data in frontend
#  Step 2: Encode raw data → convert each char to 8-bit binary
#          (raw data is now hidden, only bits exist)
#  Step 3: Encrypt the ENCODED (binary) data — NOT the raw data
#  Step 4: Decrypt the encrypted encoded data → get binary back
#  Step 5: Decode binary → identify the person (reconstruct fields)
#
#  Raw data is NEVER stored or transmitted anywhere directly.
# =====================================================================

# ── STEP 2 HELPER: Encode raw field value → binary string ─────────
def encode_to_bits(text):
    """Convert each character to 8-bit binary. e.g. 'A' → '01000001'"""
    return " ".join(format(ord(c), "08b") for c in str(text))

# ── STEP 2 HELPER: Decode binary string → original text ───────────
def decode_from_bits(bit_str):
    """Convert 8-bit binary groups back to characters."""
    bits = bit_str.replace("\n", " ").strip().split()
    chars = []
    for b in bits:
        b = b.strip()
        if len(b) == 8:
            try:
                chars.append(chr(int(b, 2)))
            except ValueError:
                pass
    return "".join(chars)

# ── STEP 3 HELPER: Encrypt encoded (binary) data ──────────────────
def encrypt_encoded(encoded_str, passphrase="gfns-shield-key"):
    """XOR + PBKDF2 encrypt the binary-encoded string."""
    salt   = os.urandom(16)
    key    = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100000, dklen=32)
    data   = encoded_str.encode("utf-8")
    cipher = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    tag    = hmac.new(key, cipher, hashlib.sha256).digest()
    return {
        "salt":   base64.b64encode(salt).decode(),
        "cipher": base64.b64encode(cipher).decode(),
        "hmac":   base64.b64encode(tag).decode(),
    }

# ── STEP 4 HELPER: Decrypt → get encoded (binary) data back ───────
def decrypt_encoded(enc_obj, passphrase="gfns-shield-key"):
    """Decrypt back to the binary-encoded string."""
    salt        = base64.b64decode(enc_obj["salt"])
    cipher      = base64.b64decode(enc_obj["cipher"])
    stored_hmac = base64.b64decode(enc_obj["hmac"])
    key         = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 100000, dklen=32)
    # Verify integrity
    expected    = hmac.new(key, cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(stored_hmac, expected):
        raise ValueError("HMAC check failed — data integrity compromised")
    plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(cipher))
    return plain.decode("utf-8")

# ── STEP 5 HELPER: Parse embed token from frontend ─────────────────
def parse_embed_token(embedded_str):
    """
    Frontend embedData_shield() sends:
      "eman:01001010 01100001...  ||  ega:00110011..."
    field name is reversed (eman = name), value is space-separated 8-bit binary.
    Returns dict of {field: binary_string}
    """
    fields = {}
    if not embedded_str or not isinstance(embedded_str, str):
        return fields
    for part in embedded_str.split(" || "):
        part = part.strip()
        if ":" not in part:
            continue
        token, bin_str = part.split(":", 1)
        field_name = token.strip()[::-1]   # reverse to get original name
        fields[field_name] = bin_str.strip()
    return fields


@app.route("/submit", methods=["POST"])
def shield_submit():
    body        = request.get_json(force=True) or {}
    id_hash     = body.get("idHash", "")
    enc_payload = body.get("encPayload", "")   # AES-GCM encrypted embed token from frontend

    enc_str = json.dumps(enc_payload, separators=(",", ":")) if isinstance(enc_payload, dict) else str(enc_payload or "")

    banner(f"FINANCIAL SHIELD — 5-STEP PIPELINE  [{timestamp()}]", M)
    log("Endpoint",   "POST /submit")
    log("ID Hash",    (id_hash[:20] + "...") if len(id_hash) > 20 else id_hash, C)

    # ── FRAUD CHECK ─────────────────────────────────────────────────
    section("Fraud & Duplicate Check")
    is_duplicate = id_hash in SHIELD_STORE
    if is_duplicate:
        stored = SHIELD_STORE[id_hash]
        print(f"    {R}{BLD}WARNING: DUPLICATE DETECTED!{RST}")
        print(f"    {R}   Matches record stored at : {stored['ts']}{RST}")
        print(f"    {R}   Record ID : {stored['record_id']}{RST}")
        fraud_verdict = "DUPLICATE - possible identity reuse"
    else:
        print(f"    {G}OK  No duplicate found — identity hash is unique{RST}")
        fraud_verdict = "CLEAN - no prior record"
    log("Fraud Verdict", fraud_verdict, R if is_duplicate else G)

    # ────────────────────────────────────────────────────────────────
    # The frontend sends the AES-GCM encrypted embed token.
    # We extract the raw fields from the id_hash context.
    # Since we DO have the exported AES key in the payload,
    # we can decrypt → get the embed token → decode bits → identify.
    # Raw data never travels directly — only bits do.
    # ────────────────────────────────────────────────────────────────

    # Try to get the plaintext embed token via AES-GCM decryption
    embed_token  = None
    aes_note     = ""

    if isinstance(enc_payload, dict) and enc_payload.get("key"):
        try:
            from Crypto.Cipher import AES as _AES
            key_b    = base64.b64decode(enc_payload["key"])
            iv_b     = base64.b64decode(enc_payload["iv"])
            ct_b     = base64.b64decode(enc_payload["cipher"])
            aes_obj  = _AES.new(key_b, _AES.MODE_GCM, nonce=iv_b)
            embed_token = aes_obj.decrypt_and_verify(ct_b[:-16], ct_b[-16:]).decode("utf-8")
            aes_note = "AES-GCM decryption successful"
        except ImportError:
            aes_note = "pycryptodome not installed — run: pip install pycryptodome"
        except Exception as e:
            aes_note = f"AES-GCM note: {e}"

    # Parse embed token into {field: binary_string} dict
    raw_bits = parse_embed_token(embed_token) if embed_token else {}

    # ── STEP 2: SHOW ENCODING (raw → bits) ──────────────────────────
    section("STEP 2 — Encoding: Raw Data → Binary Bits")
    print(f"    {DIM}(Raw data entered by user is converted to 8-bit binary){RST}")
    print(f"    {DIM}(Raw values are NEVER stored — only their bit representation){RST}")
    if raw_bits:
        for field, bits in raw_bits.items():
            actual = decode_from_bits(bits)
            encoded_preview = encode_to_bits(actual)[:48] + "..." if len(actual) > 5 else encode_to_bits(actual)
            print(f"    {Y}  {field:<10}{RST} {W}{mask(actual):<18}{RST} → {C}{encoded_preview}{RST}")
    else:
        print(f"    {Y}  {aes_note}{RST}")
        print(f"    {DIM}  Example encoding:{RST}")
        for ex_field, ex_val in [("name","John Smith"), ("age","28"), ("email","john@x.com")]:
            preview = encode_to_bits(ex_val)[:48] + "..."
            print(f"    {Y}  {ex_field:<10}{RST} {W}{ex_val:<18}{RST} → {C}{preview}{RST}")

    # ── STEP 3: ENCRYPT THE ENCODED DATA ────────────────────────────
    section("STEP 3 — Encryption: Binary Bits → Encrypted Ciphertext")
    print(f"    {DIM}(Only the encoded/binary data is encrypted — NOT the raw values){RST}")

    if raw_bits:
        encrypted_fields = {}
        for field, bits in raw_bits.items():
            enc_obj = encrypt_encoded(bits)
            encrypted_fields[field] = enc_obj
            print(f"    {Y}  {field:<10}{RST} bits → {R}{enc_obj['cipher'][:40]}...{RST}")
        print(f"    {G}  Salt (random per call) : {list(encrypted_fields.values())[0]['salt']}{RST}")
    else:
        print(f"    {DIM}  (showing example with placeholder encoded data){RST}")
        example_bits = encode_to_bits("John Smith")
        ex_enc = encrypt_encoded(example_bits)
        print(f"    {Y}  name      {RST} bits → {R}{ex_enc['cipher'][:40]}...{RST}")
        print(f"    {Y}  salt      {RST} {G}{ex_enc['salt']}{RST}  (fresh random every call)")

    # ── STEP 4: DECRYPT → GET BINARY BACK ───────────────────────────
    section("STEP 4 — Decryption: Ciphertext → Binary Bits Restored")
    print(f"    {DIM}(Decrypting gives back the binary bits — not the raw data yet){RST}")

    if raw_bits:
        decrypted_bits = {}
        for field, bits in raw_bits.items():
            enc_obj = encrypted_fields[field]
            recovered_bits = decrypt_encoded(enc_obj)
            decrypted_bits[field] = recovered_bits
            match = "MATCH" if recovered_bits.strip() == bits.strip() else "MISMATCH"
            colour = G if match == "MATCH" else R
            print(f"    {Y}  {field:<10}{RST} → {colour}{match}{RST}  bits restored: {C}{recovered_bits[:40]}...{RST}")
    else:
        print(f"    {DIM}  (decrypt gives back binary — raw identity still hidden){RST}")
        example_bits = encode_to_bits("John Smith")
        ex_enc = encrypt_encoded(example_bits)
        recovered = decrypt_encoded(ex_enc)
        print(f"    {Y}  name      {RST} → {G}MATCH{RST}  bits: {C}{recovered[:40]}...{RST}")

    # ── STEP 5: DECODE BITS → IDENTIFY PERSON ───────────────────────
    section("STEP 5 — Identification: Binary Bits → Person Identity")
    print(f"    {DIM}(Bits are decoded back to readable values to identify the user){RST}")
    print(f"    {DIM}(This is the ONLY point where identity is reconstructed){RST}")

    if raw_bits:
        print(f"    {G}  {'Field':<10}  {'Encrypted Bits (Step 3)':<42}  Decoded Identity{RST}")
        print(f"    {DIM}  {'-'*10}  {'-'*42}  {'-'*20}{RST}")
        for field, bits in raw_bits.items():
            actual   = decode_from_bits(bits)
            enc_obj  = encrypted_fields[field]
            enc_show = enc_obj["cipher"][:38] + "..."
            print(f"    {Y}  {field:<10}{RST}  {R}{enc_show:<42}{RST}  {G}{actual}{RST}")
        print(f"    {G}{BLD}  Identity successfully reconstructed from encoded data{RST}")
    else:
        print(f"    {Y}  Install pycryptodome to decode actual user input:{RST}")
        print(f"    {Y}  run:  pip install pycryptodome{RST}")
        print(f"    {DIM}  Showing pipeline with example data:{RST}")
        for ex_field, ex_val in [("name","John Smith"), ("age","28"), ("email","john@x.com")]:
            bits    = encode_to_bits(ex_val)
            enc_obj = encrypt_encoded(bits)
            dec_b   = decrypt_encoded(enc_obj)
            decoded = decode_from_bits(dec_b)
            print(f"    {Y}  {ex_field:<10}{RST}  {R}{enc_obj['cipher'][:38]}...{RST}  {G}{decoded}{RST}")

    # ── STORE ────────────────────────────────────────────────────────
    section("Storage")

    record_id = str(uuid.uuid4())[:8].upper()
    ts_now    = datetime.datetime.now().isoformat()

    # Store in memory
    SHIELD_STORE[id_hash] = {
        "record_id": record_id,
        "ts": ts_now
    }

    # Store in SQLite database
    import sqlite3

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gfns_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS identity_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        id_hash TEXT,
        fraud_verdict TEXT,
        is_duplicate INTEGER,
        created_at TEXT
    )
    """)

    # Insert record
    cursor.execute("""
    INSERT INTO identity_sessions
    (session_id, id_hash, fraud_verdict, is_duplicate, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        record_id,
        id_hash,
        fraud_verdict,
        1 if is_duplicate else 0,
        ts_now
    ))

    conn.commit()
    conn.close()

    log("Record ID",     record_id,              G)
    log("Stored At",     ts_now,                 G)
    log("Total Records", str(len(SHIELD_STORE)), C)
    log("Database Saved", "YES — identity_sessions table", G)

    return jsonify({
        "duplicate":    is_duplicate,
        "fraudVerdict": fraud_verdict,
        "record": {
            "idHash":    id_hash,
            "record_id": record_id,
            "ts":        ts_now
        }
    })


@app.route("/api/system/health", methods=["GET"])
def system_health():
    cpu    = rand_pct(18, 82)
    mem    = rand_pct(35, 78)
    net    = rand_pct(12, 95)
    disk   = rand_pct(40, 70)
    api_ms = random.randint(28, 240)
    uptime = f"{random.randint(12, 999)} days {random.randint(0,23)}h"
    banner(f"SYSTEM HEALTH CHECK  [{timestamp()}]", G)
    log("Endpoint",        "GET /api/system/health")
    log("CPU Usage",       f"{cpu:.1f}%",   R if cpu > 75 else (Y if cpu > 50 else G))
    log("Memory Usage",    f"{mem:.1f}%",   R if mem > 70 else G)
    log("Network I/O",     f"{net:.1f}%",   Y if net > 80 else G)
    log("Disk Usage",      f"{disk:.1f}%",  Y if disk > 60 else G)
    log("API Latency",     f"{api_ms} ms",  R if api_ms > 200 else (Y if api_ms > 100 else G))
    log("Server Uptime",   uptime,          G)
    log("Active Sessions", str(random.randint(12, 480)), C)
    log("DB Connections",  str(random.randint(4, 40)),   C)
    overall = "HEALTHY" if cpu < 75 and mem < 70 else "DEGRADED" if cpu < 90 else "CRITICAL"
    log("Overall Status",  overall, G if overall == "HEALTHY" else (Y if overall == "DEGRADED" else R))
    return jsonify({"cpu": cpu, "memory": mem, "network": net, "disk": disk, "api_ms": api_ms, "uptime": uptime, "status": overall, "ts": timestamp()})


if __name__ == "__main__":
    print(f"\n{C}{BLD}")
    print("=" * 60)
    print("   GLOBAL FINANCIAL NERVOUS SYSTEM - BACKEND")
    print("   Flask running on http://localhost:4002")
    print("=" * 60)
    print("   GET  /api/data/dashboard")
    print("   GET  /api/data/instability-timeline")
    print("   POST /api/health/modal")
    print("   POST /api/stress/inject-shock")
    print("   POST /api/stress/stabilize")
    print("   POST /submit  <- Financial Shield (FIXED)")
    print("   GET  /api/system/health")
    print(f"{'=' * 60}{RST}\n")
    app.run(host="0.0.0.0", port=4002, debug=False)