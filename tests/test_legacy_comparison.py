"""Check the legacy ETC response parser without network requests."""

import pytest

from checks.plot_snr_vs_legacy import LegacyFilterParser, collect, parse_legacy_snr


def test_legacy_psf_response():
    # Parse the actual response format captured from the legacy r-band ETC.
    assert parse_legacy_snr("PSF SNR:   87.40<br>\n: 4715.22 : 22491.63 :\n") == 87.4


@pytest.mark.parametrize("response", [
    "", "<html>Internal server error</html>", "SNR: 87.40",
    "PSF SNR: nan<br>", "PSF SNR: 0.00<br>", "PSF SNR: 1e999<br>",
])
def test_invalid_legacy_response_is_not_a_measurement(response):
    # Reject errors, aperture responses and invalid numbers rather than plotting them.
    with pytest.raises(ValueError):
        parse_legacy_snr(response)


def test_filter_parser_uses_only_the_filter_select():
    # Discover case-sensitive filter IDs without confusing other form options.
    parser = LegacyFilterParser()
    parser.feed('<select id="compval"><option value="snr">SNR</select>'
                '<select id="ifilter"><option value="r">r<option value="HaOFF">Ha off</select>')
    assert parser.filters == ["r", "HaOFF"]


def test_cached_run_cannot_overwrite_its_source(tmp_path):
    # Refuse a destination that could replace the previous run's measurements.
    source = tmp_path / "measurements.json"
    source.write_text("original measurements")
    with pytest.raises(ValueError, match="separate output directory"):
        collect("http://localhost:8010/api", tmp_path, 0, "pristine", source)
    assert source.read_text() == "original measurements"
