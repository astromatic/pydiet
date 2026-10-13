#!/usr/bin/env python3
"""Compare live PyDIET and legacy CFHT MegaCam PSF signal-to-noise ratios.

Query all MegaCam filters advertised by the local API for a single 30-second
exposure at twelve seeings from 0.4 to 2 arcseconds, including the default 0.7.
Keep all other PyDIET settings at their API defaults, unless ``--mirror`` is
specified, and match the available legacy controls. Use ``--legacy-cache`` to
reuse previous legacy measurements. Save raw responses, request URLs, defaults, CSV measurements,
and four-column square-panel plots. Use ``--cached`` to replot without requests.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shlex
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np


SEEINGS = (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0)
LEGACY_PAGE = "https://etc.cfht.hawaii.edu/mp/"
LEGACY_API = "https://etc.cfht.hawaii.edu/cgi-bin/mp/mp.py"
LEGACY_DOCUMENTATION = "https://www.cfht.hawaii.edu/Instruments/Imaging/Megacam/dietmegacam.html"


class LegacyFilterParser(HTMLParser):
    """Read filter option values from the legacy form's ``ifilter`` select.

    Attributes
    ----------
    filters: list[str]
        Filter identifiers in the order advertised by the form.
    """

    def __init__(self) -> None:
        """Initialize an empty filter collection and HTML parser."""
        super().__init__()
        self.filters: list[str] = []
        self._in_filters = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect option values while inside the filter selector."""
        values = dict(attrs)
        if tag == "select":
            self._in_filters = values.get("id") == "ifilter"
        elif tag == "option" and self._in_filters and values.get("value"):
            self.filters.append(str(values["value"]))

    def handle_endtag(self, tag: str) -> None:
        """Stop collecting options when a select element ends."""
        if tag == "select":
            self._in_filters = False


def request_text(url: str) -> str:
    """Fetch a UTF-8 HTTP response with bounded retries for transient failures.

    Retry connection errors and HTTP 429/5xx responses up to three times, with
    one- and two-second delays. Other HTTP errors propagate immediately.
    Each attempt has a 30-second timeout.
    """
    request = Request(url, headers={"User-Agent": "pydiet-legacy-comparison/1.0"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code != 429 and exc.code < 500:
                raise
            if attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(attempt + 1)
    raise RuntimeError("HTTP retry loop completed without a response")


def parse_legacy_snr(response: str) -> float:
    r"""Read a positive, finite SNR from the legacy PSF response.

    The form reads the first colon-separated value, before any HTML markup.
    Require the PSF label so aperture results and error pages cannot silently
    enter the comparison. Raise ``ValueError`` for an unexpected response.

    Examples
    --------
    >>> parse_legacy_snr('PSF SNR:   87.40<br>\n: 4715.22 : 22491.63 :')
    87.4
    """
    match = re.match(r"\s*PSF\s+SNR\s*:\s*([0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?)\s*(?:<|:|$)", response)
    if match is None:
        raise ValueError(f"Unexpected legacy PSF response: {response[:300]!r}")
    snr = float(match.group(1))
    if not np.isfinite(snr) or snr <= 0:
        raise ValueError(f"Invalid legacy SNR: {snr}")
    return snr


def collect(
    api_url: str, output_dir: Path, delay: float,
    mirror: str | None = None, legacy_cache: Path | None = None,
) -> dict:
    """Query both calculators and save each completed pair to a JSON snapshot.

    Parameters
    ----------
    api_url: str
        PyDIET API root, normally ``http://localhost:8010/api``.
    output_dir: pathlib.Path
        Directory receiving the instrument list, OpenAPI schema, legacy form,
        and ``measurements.json`` with raw responses and exact request URLs.
    delay: float
        Pause in seconds after each request pair to limit legacy-server load.
    mirror: str, optional
        Override PyDIET's mirror condition while retaining other API defaults.
    legacy_cache: pathlib.Path, optional
        Previous ``measurements.json`` from which to reuse legacy responses.
        Each cached request URL must exactly match the required legacy inputs.
        Its directory must differ from ``output_dir`` to preserve the old run.

    Returns
    -------
    snapshot: dict
        Metadata and one row for each filter/seeing pair.

    Raises
    ------
    ValueError
        Defaults cannot be matched, a filter is absent from the legacy form,
        or a calculator returns an invalid response.
    """
    if legacy_cache is not None and legacy_cache.parent.resolve() == output_dir.resolve():
        raise ValueError("Use a separate output directory to preserve the cached run")
    cached_legacy = None
    if legacy_cache is not None:
        cached_legacy = json.loads(legacy_cache.read_text())
    output_dir.mkdir(parents=True, exist_ok=True)
    api_url = api_url.rstrip("/")
    instruments_text = request_text(api_url + "/instruments")
    schema_text = request_text(api_url.removesuffix("/api") + "/openapi.json")
    legacy_html = (legacy_cache.parent / "legacy_form.html").read_text() \
        if legacy_cache is not None else request_text(LEGACY_PAGE)
    (output_dir / "instruments.json").write_text(instruments_text)
    (output_dir / "openapi.json").write_text(schema_text)
    (output_dir / "legacy_form.html").write_text(legacy_html)
    instruments = json.loads(instruments_text)
    schema = json.loads(schema_text)
    defaults = {
        parameter["name"]: parameter["schema"]["default"]
        for parameter in schema["paths"]["/api/{instrument}"]["get"]["parameters"]
        if "default" in parameter.get("schema", {})
    }
    for name, value in {"unit": "abmag", "source": "point_source", "photometry": "model_fitting", "exposures": 1}.items():
        if defaults[name] != value:
            raise ValueError(f"Cannot match PyDIET default {name}={defaults[name]!r}")
    if defaults["sky"] not in {"dark", "grey", "bright"}:
        raise ValueError("This comparison requires a tabulated default sky setting")
    parser = LegacyFilterParser()
    parser.feed(legacy_html)
    legacy_filters = {name.casefold(): name for name in parser.filters}
    filters = instruments["megacam"]["filters"]["transmissions"]
    if mirror is not None and mirror not in instruments["megacam"]["telescope"]["transmissions"]:
        raise ValueError(f"Unknown MegaCam mirror condition: {mirror}")
    missing = set(filters).difference(legacy_filters)
    if missing:
        raise ValueError(f"Legacy form has no matching filters: {sorted(missing)}")
    snapshot = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "pydiet_api": api_url,
        "pydiet_version": schema["info"]["version"],
        "legacy_api": LEGACY_API,
        "legacy_documentation": LEGACY_DOCUMENTATION,
        "defaults": defaults,
        "settings": defaults | ({"mirror": mirror} if mirror is not None else {}),
        "mirror_override": mirror,
        "request_overrides": ["compute", "etime", "filter", "seeing"] + (["mirror"] if mirror is not None else []),
        "exposure_seconds": 30.0,
        "seeings_arcsec": SEEINGS,
        "notes": [
            "PyDIET requests override compute, etime, filter, seeing, and optionally mirror.",
            "Legacy uses pointsource, photometry=psf, fluxormag=magAB, and matched observing inputs.",
            "PyDIET retains its default solar setting and uses the specified or default mirror; legacy exposes no equivalent controls.",
            "Legacy SNR is rounded to two decimal places by its server.",
            "Filter IDs are matched case-insensitively to the live legacy form; uS/gS/rS/iS/zS are not substituted.",
        ],
        "rows": [],
    }
    legacy_rows = {row["legacy_url"]: row for row in cached_legacy["rows"]} if cached_legacy else {}
    if legacy_cache is not None:
        snapshot["legacy_cache"] = str(legacy_cache)
        snapshot["legacy_cache_sha256"] = hashlib.sha256(legacy_cache.read_bytes()).hexdigest()
        snapshot["legacy_collected_utc"] = cached_legacy["created_utc"]
    for filter_id, filter_model in filters.items():
        legacy_filter = legacy_filters[filter_id.casefold()]
        for seeing in SEEINGS:
            pydiet_parameters = {"compute": "snr", "etime": 30, "filter": filter_id, "seeing": seeing}
            if mirror is not None:
                pydiet_parameters["mirror"] = mirror
            legacy_parameters = {
                "compval": "snr", "sourcetype": "pointsource", "etime": 30,
                "snr": 0, "filter": legacy_filter, "aperture": "optimalaperture",
                "skybackground": defaults["sky"], "skyentry": 0,
                "airmass": defaults["airmass"], "trans": defaults["transparency"],
                "seeing": seeing, "compute": "compute", "magnitude": defaults["brightness"],
                "fluxormag": "magAB", "photometry": "psf",
            }
            pydiet_url = f"{api_url}/megacam?{urlencode(pydiet_parameters)}"
            legacy_url = f"{LEGACY_API}?{urlencode(legacy_parameters)}"
            if legacy_cache is not None and legacy_url not in legacy_rows:
                raise ValueError(f"Cached legacy measurement does not match required inputs: {legacy_url}")
            pydiet_text = request_text(pydiet_url)
            legacy_text = legacy_rows[legacy_url]["legacy_response"] \
                if legacy_cache is not None else request_text(legacy_url)
            predicted = json.loads(pydiet_text)
            snr = float(predicted["snr"])
            if predicted["compute"] != "snr" or predicted["etime"] != 30 or not np.isfinite(snr) or snr <= 0:
                raise ValueError(f"Invalid PyDIET response: {pydiet_text}")
            legacy_snr = parse_legacy_snr(legacy_text)
            snapshot["rows"].append({
                "filter_id": filter_id, "filter_name": filter_model["name"],
                "legacy_filter": legacy_filter, "seeing_arcsec": seeing,
                "pydiet_snr": snr, "legacy_snr": legacy_snr,
                "ratio": snr / legacy_snr,
                "pydiet_url": pydiet_url, "legacy_url": legacy_url,
                "pydiet_response": predicted, "legacy_response": legacy_text,
            })
            (output_dir / "measurements.json").write_text(json.dumps(snapshot, indent=2) + "\n")
            time.sleep(delay)
        print(f"Collected {filter_model['name']}: {len(SEEINGS)} seeing pairs", flush=True)
    return snapshot


def plot(snapshot: dict, output_dir: Path) -> None:
    """Save a square-panel SNR comparison grid and a CSV of all measurements.

    Put legacy SNR on the horizontal axis and PyDIET SNR on the vertical axis.
    Match the four-column layout, fonts, point sizes, grid and identity line
    of ``plot_predicted_vs_recorded.py``. Color points by seeing and annotate
    each panel with its median PyDIET/legacy ratio. Save PNG, SVG and PDF.

    Matplotlib is required only when this function is called; parsing and
    collecting measurements do not require it.
    """
    import matplotlib.pyplot as plt

    rows = snapshot["rows"]
    filter_ids = list(dict.fromkeys(row["filter_id"] for row in rows))
    if not filter_ids:
        raise ValueError("No measurements to plot")
    output_dir.mkdir(parents=True, exist_ok=True)
    columns = ["filter_id", "filter_name", "legacy_filter", "seeing_arcsec", "pydiet_snr", "legacy_snr", "ratio"]
    with (output_dir / "snr_comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    defaults = snapshot["defaults"]
    settings = snapshot.get("settings", defaults)
    command = ".venv/bin/python checks/plot_snr_vs_legacy.py"
    if snapshot.get("mirror_override"):
        command += " --mirror " + shlex.quote(snapshot["mirror_override"])
    if snapshot.get("legacy_cache"):
        command += " --legacy-cache " + shlex.quote(snapshot["legacy_cache"])
    command += " --output-dir " + shlex.quote(str(output_dir))
    overrides = ", ".join(f"`{name}`" for name in snapshot.get("request_overrides", ["compute", "etime", "filter", "seeing"]))
    report = [
        "# MegaCam: PyDIET versus legacy CFHT ETC", "",
        f"Collected: {snapshot['created_utc']}", "",
        f"PyDIET {snapshot['pydiet_version']}: `{snapshot['pydiet_api']}`. "
        f"Legacy calculator: {LEGACY_PAGE}", "",
        "## Matched observing inputs", "",
        "A single 30-second exposure, point source, PSF/model-fitting photometry, "
        f"AB magnitude {defaults['brightness']:g}, airmass {defaults['airmass']:g}, "
        f"{defaults['sky']} sky, transparency {defaults['transparency']:g}. "
        "The twelve seeing FWHMs (arcsec) are " + ", ".join(f"{seeing:g}" for seeing in snapshot["seeings_arcsec"]) + ".", "",
        f"PyDIET requests override {overrides}; all remaining API defaults are preserved. "
        f"Effective settings include `solar={settings['solar']}` "
        f"and `mirror={settings['mirror']}`. Legacy uses `photometry=psf`, "
        "`sourcetype=pointsource`, and `fluxormag=magAB`. Its aperture argument is "
        "the form's `optimalaperture`, which is inactive in PSF mode.", "",
        "## Results at the default 0.7 arcsec seeing", "",
        "| Filter | PyDIET SNR | Legacy SNR | PyDIET / legacy | Difference |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        if row["seeing_arcsec"] == 0.7:
            report.append(
                f"| {row['filter_name']} | {row['pydiet_snr']:.3f} | {row['legacy_snr']:.2f} | "
                f"{row['ratio']:.4f} | {100 * (row['ratio'] - 1):+.2f}% |"
            )
    report.extend([
        "", "## Reading the plot", "",
        "`snr_vs_legacy.png` (also PDF and SVG) puts legacy SNR on the horizontal "
        "axis and PyDIET SNR on the vertical axis. Both axes have the same scale "
        "within each panel. Color indicates seeing; the dashed line is equality. "
        "A ratio above one means PyDIET predicts a higher SNR. Each panel reports "
        "the median ratio over the twelve seeings.", "",
        "The seeing grid is a deliberate parameter sweep, not an observational "
        "sample or an uncertainty estimate. The legacy server reports SNR to two "
        "decimal places. Its fixed calibration and PSF assumptions need not match "
        "PyDIET's; it exposes no solar-activity or mirror-condition controls. "
        "These results compare the calculators at matched user inputs without "
        "adjusting either model to force agreement.", "",
        "## Legacy API", "",
        f"The public form's JavaScript sends GET requests to `{LEGACY_API}`. "
        "It splits the result on colons and extracts the SNR before HTML markup. "
        "The PSF response starts with `PSF SNR:`; the collector requires that label "
        "to reject aperture results or error pages. Filter IDs are read from the "
        "form and matched case-insensitively. The older `uS/gS/rS/iS/zS` filters "
        "are not substituted for `u/g/r/i/z`.", "",
        f"Scientific documentation: {LEGACY_DOCUMENTATION}", "",
        "## Files and reproduction", "",
        "- `snr_comparison.csv`: all paired SNRs and ratios.",
        "- `measurements.json`: raw responses, exact request URLs, defaults and provenance.",
        "- `instruments.json`, `openapi.json`, `legacy_form.html`: discovery snapshots.",
        "- `snr_vs_legacy.png`, `.pdf`, `.svg`: four-column comparison grid.", "",
        "From the repository root, with the local server running:", "",
        "```sh", command, "```", "",
        "To regenerate plots and this report without making requests:", "",
        "```sh", ".venv/bin/python checks/plot_snr_vs_legacy.py --cached --output-dir " + shlex.quote(str(output_dir)), "```", "",
    ])
    if snapshot.get("legacy_cache"):
        report.extend([
            "## Reused legacy measurements", "",
            f"Legacy responses were reused unchanged from `{snapshot['legacy_cache']}`, "
            f"collected at {snapshot['legacy_collected_utc']}. No new legacy queries were made. "
            "Each legacy URL was checked for an exact match to the observing inputs. "
            f"Source snapshot SHA-256: `{snapshot['legacy_cache_sha256']}`.", "",
        ])
    (output_dir / "README.md").write_text("\n".join(report))
    width, height = 4, (len(filter_ids) + 3) // 4
    fig, axes = plt.subplots(height, width, figsize=(6 * width, 6 * height), layout="compressed", squeeze=False)
    fig.suptitle(
        f"MegaCam PSF photometry · 30 s · AB {defaults['brightness']:g} · "
        f"airmass {defaults['airmass']:g} · {defaults['sky']} sky · mirror {settings['mirror']}",
        fontsize=22,
    )
    try:
        for axis, filter_id in zip(axes.flat, filter_ids):
            sample = [row for row in rows if row["filter_id"] == filter_id]
            legacy = np.array([row["legacy_snr"] for row in sample])
            predicted = np.array([row["pydiet_snr"] for row in sample])
            seeing = np.array([row["seeing_arcsec"] for row in sample])
            points = axis.scatter(legacy, predicted, c=seeing, cmap="viridis", vmin=0.4, vmax=2.0, s=90, alpha=0.85)
            limit = max(legacy.max(), predicted.max()) * 1.05
            axis.plot((0, limit), (0, limit), "k--", linewidth=1, label="1:1")
            axis.set(xlim=(0, limit), ylim=(0, limit))
            axis.set_aspect("equal", adjustable="box")
            axis.text(0.04, 0.96, sample[0]["filter_name"], transform=axis.transAxes,
                      ha="left", va="top", fontsize=20, fontweight="bold",
                      bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
            axis.text(0.04, 0.06, f"median PyDIET/legacy = {np.median(predicted / legacy):.3f}",
                      transform=axis.transAxes, fontsize=12)
            axis.set_xlabel("Legacy CFHT ETC SNR", fontsize=16)
            axis.set_ylabel("PyDIET predicted SNR", fontsize=16)
            axis.tick_params(axis="both", labelsize=14)
            axis.grid(alpha=0.25)
            axis.legend(fontsize=14, loc="lower right")
        for axis in list(axes.flat)[len(filter_ids):]:
            axis.set_visible(False)
        colorbar = fig.colorbar(points, ax=axes.ravel().tolist(), shrink=0.55, pad=0.02)
        colorbar.set_label("Seeing FWHM (arcsec)", fontsize=16)
        colorbar.ax.tick_params(labelsize=14)
        for extension in ("png", "svg", "pdf"):
            fig.savefig(output_dir / f"snr_vs_legacy.{extension}", dpi=200)
    finally:
        plt.close(fig)
    print(f"Wrote {width}x{height} grid: {len(filter_ids)} filters, {len(rows)} paired measurements", flush=True)
    print("At the default 0.7 arcsec seeing:")
    for row in rows:
        if row["seeing_arcsec"] == 0.7:
            print(f"  {row['filter_name']:10s} PyDIET {row['pydiet_snr']:8.3f}  legacy {row['legacy_snr']:8.2f}  ratio {row['ratio']:.4f}")


def main() -> int:
    """Collect live comparison data, or replot a saved snapshot, from CLI options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:8010/api")
    parser.add_argument("--output-dir", type=Path, help="output directory; mirror overrides get a separate default directory")
    parser.add_argument("--mirror", choices=("pristine", "average", "degraded"), help="override only PyDIET's mirror condition")
    parser.add_argument("--legacy-cache", type=Path, help="reuse legacy responses from a previous measurements.json")
    parser.add_argument("--delay", type=float, default=0.25, help="pause between request pairs in seconds")
    parser.add_argument("--cached", action="store_true", help="replot existing measurements.json without network access")
    args = parser.parse_args()
    if args.output_dir is None:
        suffix = "_" + args.mirror if args.mirror else ""
        args.output_dir = Path("checks/snr_legacy_comparison" + suffix)
    if not np.isfinite(args.delay) or args.delay < 0:
        parser.error("--delay must be finite and nonnegative")
    if args.cached:
        snapshot = json.loads((args.output_dir / "measurements.json").read_text())
    else:
        snapshot = collect(args.api_url, args.output_dir, args.delay, args.mirror, args.legacy_cache)
    plot(snapshot, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
