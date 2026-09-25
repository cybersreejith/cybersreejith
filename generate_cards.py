#!/usr/bin/env python3
"""Generate self-hosted GitHub profile cards into assets/ (no third-party image services).

Outputs: stats.svg, top-langs.svg, streak.svg, activity-graph.svg, repo-owl.svg, repo-api-security.svg
Standard library only. Uses GITHUB_TOKEN when present (set automatically in GitHub Actions).
"""
import json, os, urllib.request, urllib.parse
from html import escape

USER = os.environ.get("PROFILE_USER", "cybersreejith")
# (owner, repo, output file, display title)
FEATURED = [
    ("OWASP", "www-project-webshield-library", "repo-owl.svg", "OWL · OWASP Web Shield Library"),
    ("cybersreejith", "www-project-api-security-testing-framework", "repo-api-security.svg", "OWASP API Security Testing"),
]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TOKEN = os.environ.get("GITHUB_TOKEN")

BG, TITLE, TEXT, ICON, BORDER = "#1a1b27", "#70a5fd", "#c0caf5", "#bf91f3", "#2c5364"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
LANG_COLORS = {
    "Java": "#b07219", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "Shell": "#89e051", "Kotlin": "#A97BFF", "Go": "#00ADD8",
    "Dockerfile": "#384d54", "SCSS": "#c6538c", "Groovy": "#4298b8", "Vue": "#41b883",
}
STAR = ("M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97"
        ".719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194"
        "L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z")
FORK = ("M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878"
        "a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25"
        "v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 "
        "0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z")


def icon(path, x, y, color=ICON):
    return f'<path transform="translate({x} {y})" d="{path}" fill="{color}"/>'


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-cards"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search_count(kind, q):
    try:
        return api(f"/search/{kind}?per_page=1&q=" + urllib.parse.quote(q))["total_count"]
    except Exception as e:
        print("search failed:", kind, q, e)
        return None


def fmt(n):
    if n is None:
        return "-"
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def card(width, height, title, body):
    # Animations use fill-mode "both" so content stays visible if animation is unsupported.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
.t{{font:600 18px {FONT};fill:{TITLE}}} .l{{font:400 14px {FONT};fill:{TEXT}}} .v{{font:700 14px {FONT};fill:{TEXT}}}
.s{{font:400 13px {FONT};fill:{TEXT}}} .row{{animation:f .6s ease-out both}}
@keyframes f{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion){{.row{{animation:none}}}}
</style>
<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<text x="25" y="35" class="t">{escape(title)}</text>
{body}
</svg>'''


def stats_card(user, repos):
    own = [r for r in repos if not r["fork"]]
    rows = [
        (STAR, "Stars earned", sum(r["stargazers_count"] for r in own)),
        (FORK, "Public repositories", user["public_repos"]),
        (None, "Pull requests", search_count("issues", f"author:{USER} type:pr")),
        (None, "Issues opened", search_count("issues", f"author:{USER} type:issue")),
        (None, "Commits", search_count("commits", f"author:{USER}")),
        (None, "Followers", user["followers"]),
    ]
    body = []
    for i, (ic, label, val) in enumerate(rows):
        y = 70 + i * 26
        mark = icon(ic, 25, y - 13) if ic else f'<rect x="28" y="{y-10}" width="10" height="10" rx="3" fill="{ICON}"/>'
        body.append(f'<g class="row" style="animation-delay:{i*120}ms">{mark}'
                    f'<text x="50" y="{y}" class="l">{label}:</text>'
                    f'<text x="300" y="{y}" class="v" text-anchor="end">{fmt(val)}</text></g>')
    body.append(f'<g transform="translate(345 62)">'
                f'<path d="M50 0 L95 18 V55 C95 85 72 105 50 115 C28 105 5 85 5 55 V18 Z" fill="none" stroke="{TITLE}" stroke-width="4"/>'
                f'<path d="M30 58 L45 73 L72 44" fill="none" stroke="{ICON}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')
    return card(470, 230, f"{user.get('name') or USER}'s GitHub Stats", "\n".join(body))


def langs_card(repos):
    totals = {}
    for r in repos:
        if r["fork"]:
            continue
        try:
            for lang, b in api(f"/repos/{r['full_name']}/languages").items():
                totals[lang] = totals.get(lang, 0) + b
        except Exception as e:
            print("languages failed:", r["full_name"], e)
    top = sorted(totals.items(), key=lambda x: -x[1])[:8]
    if not top:
        return card(350, 130, "Most Used Languages", '<text x="25" y="75" class="s">No language data yet</text>')
    total = sum(b for _, b in top)
    bar_w, x = 300, 25.0
    body = [f'<clipPath id="m"><rect x="25" y="55" width="{bar_w}" height="8" rx="4"/></clipPath><g clip-path="url(#m)">']
    for lang, b in top:
        w = bar_w * b / total
        body.append(f'<rect x="{x:.2f}" y="55" width="{w + 0.5:.2f}" height="8" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>')
        x += w
    body.append("</g>")
    for i, (lang, b) in enumerate(top):
        cx, cy = 25 + (i % 2) * 160, 90 + (i // 2) * 24
        body.append(f'<g class="row" style="animation-delay:{i*100}ms">'
                    f'<circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>'
                    f'<text x="{cx+16}" y="{cy}" class="s">{escape(lang)} {100*b/total:.1f}%</text></g>')
    return card(350, max(90 + ((len(top) + 1) // 2) * 24 + 5, 130), "Most Used Languages", "\n".join(body))


def wrap(text, n):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + len(w) + 1 > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if len(lines) > 2:
        lines = lines[:2]; lines[1] = lines[1][: n - 1].rstrip() + "…"
    return lines


def repo_card(owner, name, title):
    r = api(f"/repos/{owner}/{name}")
    body = [f'<text x="25" y="{62 + i*18}" class="s">{escape(l)}</text>'
            for i, l in enumerate(wrap(r.get("description") or "", 55))]
    y, lang = 115, r.get("language") or ""
    if lang:
        body.append(f'<circle cx="31" cy="{y-5}" r="6" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>'
                    f'<text x="43" y="{y}" class="s">{escape(lang)}</text>')
    body.append(icon(STAR, 150, y - 13, TEXT) + f'<text x="170" y="{y}" class="s">{fmt(r["stargazers_count"])}</text>')
    body.append(icon(FORK, 215, y - 13, TEXT) + f'<text x="235" y="{y}" class="s">{fmt(r["forks_count"])}</text>')
    lic = (r.get("license") or {}).get("spdx_id")
    if lic and lic != "NOASSERTION":
        body.append(f'<text x="280" y="{y}" class="s">{escape(lic)}</text>')
    return card(420, 135, title, "\n".join(body))


def graphql(query, variables):
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN required for contribution data")
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "profile-cards",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


def contribution_days():
    q = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
           totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""
    cal = graphql(q, {"login": USER})["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return cal["totalContributions"], days


def streak_card(total, days):
    counts = [c for _, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:      # today not counted yet: start from yesterday
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1; i -= 1
    cols = [("Total Contributions", total, "Last 12 months"),
            ("Current Streak", current, "days"),
            ("Longest Streak", longest, "days")]
    body = []
    for k, (label, val, sub) in enumerate(cols):
        cx = 85 + k * 165
        ring = (f'<circle cx="{cx}" cy="85" r="38" fill="none" stroke="{ICON}" stroke-width="5"/>'
                if k == 1 else "")
        body.append(f'<g class="row" style="animation-delay:{k*150}ms">{ring}'
                    f'<text x="{cx}" y="94" text-anchor="middle" style="font:700 26px {FONT};fill:{TITLE if k != 1 else TEXT}">{fmt(val)}</text>'
                    f'<text x="{cx}" y="150" text-anchor="middle" class="l">{label}</text>'
                    f'<text x="{cx}" y="170" text-anchor="middle" class="s" opacity=".7">{sub}</text></g>')
        if k:
            body.append(f'<line x1="{cx-82}" y1="55" x2="{cx-82}" y2="170" stroke="{BORDER}"/>')
    return card(500, 195, "Contribution Streak", "\n".join(body))


def activity_card(days):
    last = days[-31:]
    W, H, L, R, T, B = 900, 300, 50, 20, 55, 45
    pw, ph = W - L - R, H - T - B
    mx = max([c for _, c in last] + [4])
    pts = [(L + i * pw / (len(last) - 1), T + ph - c * ph / mx) for i, (_, c) in enumerate(last)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    area = line + f" L{pts[-1][0]:.1f} {T+ph} L{pts[0][0]:.1f} {T+ph} Z"
    body = [f'<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{TITLE}" stop-opacity=".45"/><stop offset="1" stop-color="{TITLE}" stop-opacity="0"/>'
            f'</linearGradient></defs>']
    for k in range(5):
        y = T + ph - k * ph / 4
        body.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{BORDER}" stroke-dasharray="3 4"/>'
                    f'<text x="{L-10}" y="{y+4:.1f}" text-anchor="end" class="s">{round(mx*k/4)}</text>')
    for i, (d, _) in enumerate(last):
        if i % 5 == 0 or i == len(last) - 1:
            body.append(f'<text x="{pts[i][0]:.1f}" y="{H-18}" text-anchor="middle" class="s">{d[5:]}</text>')
    body.append(f'<path d="{area}" fill="url(#ag)"/>'
                f'<path d="{line}" fill="none" stroke="{TITLE}" stroke-width="2.5" stroke-linejoin="round"/>')
    body += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ICON}"/>' for x, y in pts]
    return card(W, H, "Contribution Activity (last 31 days)", "\n".join(body))


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    write("stats.svg", stats_card(user, repos))
    write("top-langs.svg", langs_card(repos))
    try:
        total, days = contribution_days()
        write("streak.svg", streak_card(total, days))
        write("activity-graph.svg", activity_card(days))
    except Exception as e:
        print("contribution cards skipped:", e)
    for owner, name, fname, title in FEATURED:
        try:
            write(fname, repo_card(owner, name, title))
        except Exception as e:
            print("repo card failed:", owner, name, e)


if __name__ == "__main__":
    main()
