"""Build the profile stats cards: contribution streak plus profile views, in one card."""
import os
import re
import sys
import urllib.request

USER = "Mkkbeydoun"
VIEWS_URL = "https://api.visitorbadge.io/api/visitors?path=github.com%2FMkkbeydoun"
BASE = (
    f"https://streak-stats.demolab.com?user={USER}&hide_border=true&background=00000000"
    "&ring=3d7bff&fire=3d7bff&currStreakLabel=3d7bff"
)
THEMES = {
    "dark": "&stroke=30363d&currStreakNum=e6edf3&sideNums=e6edf3&sideLabels=e6edf3&dates=8b949e",
    "light": "&stroke=d0d7de&currStreakNum=1f2328&sideNums=1f2328&sideLabels=1f2328&dates=656d76",
}
COLORS = {
    "dark": ("#e6edf3", "#8b949e", "#30363d"),
    "light": ("#1f2328", "#656d76", "#d0d7de"),
}
OLD_W, NEW_W = 495, 660
FONT = "font-family='\"Segoe UI\", Ubuntu, sans-serif'"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def read_int(path, default=0):
    try:
        return int(open(path).read().strip())
    except (OSError, ValueError):
        return default


def text(x, y, fill, weight, size, value, delay):
    return (
        f"<g transform='translate({x}, {y})'><text x='0' y='32' stroke-width='0' text-anchor='middle' "
        f"fill='{fill}' stroke='none' {FONT} font-weight='{weight}' font-size='{size}px' font-style='normal' "
        f"style='opacity: 0; animation: fadein 0.5s linear forwards {delay}s'>{value}</text></g>"
    )


def widen(svg, theme, views):
    num, sub, line = COLORS[theme]
    svg = svg.replace(f"viewBox='0 0 {OLD_W} 195'", f"viewBox='0 0 {NEW_W} 195'")
    svg = svg.replace(f"width='{OLD_W}px'", f"width='{NEW_W}px'")
    svg = svg.replace(f"<rect width='{OLD_W}' height='195'", f"<rect width='{NEW_W}' height='195'")
    svg = svg.replace(f"width='{OLD_W - 1}' height='194'", f"width='{NEW_W - 1}' height='194'")
    cx = OLD_W + (NEW_W - OLD_W) / 2
    column = (
        f"<g style='isolation: isolate'>"
        f"<line x1='{OLD_W}' y1='28' x2='{OLD_W}' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' "
        f"stroke='{line}' stroke-linecap='square'/>"
        + text(cx, 48, num, 700, 28, f"{views:,}", 1.5)
        + text(cx, 84, num, 400, 14, "Profile Views", 1.6)
        + text(cx, 114, sub, 400, 12, "All time", 1.7)
        + "</g>"
    )
    end = svg.rfind("</g>")
    if end < 0 or f"viewBox='0 0 {NEW_W} 195'" not in svg:
        raise SystemExit("streak card format changed; not updating")
    return svg[:end] + column + svg[end:]


def main(out):
    os.makedirs(out, exist_ok=True)
    reads = read_int("reads.txt") + 1
    views = read_int("views.txt")
    try:
        badge = get(VIEWS_URL)
        counts = [int(n.replace(",", "")) for n in re.findall(r">\s*([\d,]+)\s*<", badge)]
        if counts:
            views = max(max(counts) - reads, views)
    except Exception as e:  # keep the last known count
        print(f"views fetch failed: {e}", file=sys.stderr)
    for theme, extra in THEMES.items():
        svg = get(BASE + extra)
        open(os.path.join(out, f"stats-{theme}.svg"), "w").write(widen(svg, theme, views))
    open(os.path.join(out, "reads.txt"), "w").write(f"{reads}\n")
    open(os.path.join(out, "views.txt"), "w").write(f"{views}\n")
    print(f"views={views} reads={reads}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
