"""Testes locais da aquisição complementar (sem acesso à Internet)."""
import io
from pathlib import Path
from unittest.mock import patch
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import linextraction_dem as dem


def make_dem(path, value, lon, crs="EPSG:4326"):
    with rasterio.open(path, 'w', driver='GTiff', width=120, height=120, count=1,
                       dtype='float32', crs=crs, nodata=np.nan,
                       transform=from_origin(lon, -20, 1/120, 1/120)) as dst:
        dst.write(np.full((120, 120), value, dtype=np.float32), 1)


def test_copernicus_url_hemispheres():
    assert dem._copernicus_tile_url(-47, -21).endswith(
        '/Copernicus_DSM_COG_10_S21_00_W047_00_DEM.tif')
    assert dem._copernicus_tile_url(12, 7).endswith(
        '/Copernicus_DSM_COG_10_N07_00_E012_00_DEM.tif')


def test_copernicus_clip_across_two_tiles(tmp_path):
    first = tmp_path / 'a.tif'
    second = tmp_path / 'b.tif'
    make_dem(first, 100, -47)
    make_dem(second, 200, -46)
    output = tmp_path / 'dem' / 'copernicus.tif'
    with patch.object(dem, '_copernicus_tile_url', side_effect=lambda x, y: str(first if x == -47 else second)):
        dem.download_copernicus((-46.25, -45.75, -20.8, -20.2), output)
    with rasterio.open(output) as src:
        assert src.crs.to_epsg() == 4326
        assert src.count == 1
        assert src.nodata is not None
        assert np.isclose(src.bounds.left, -46.25)
        assert np.isclose(src.bounds.right, -45.75)
        values = src.read(1)
        assert values[0, 0] == 100
        assert values[0, -1] == 200
        assert src.tags()['elevation_model'] == 'COP30'


def test_opentopography_needs_key_before_network(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENTOPOGRAPHY_API_KEY', raising=False)
    with pytest.raises(ValueError, match='OPENTOPOGRAPHY_API_KEY'):
        dem.download_alternative_dem('alos', (-47, -46, -21, -20), tmp_path / 'alos.tif')


def test_opentopography_validates_tiff_and_keeps_key_out_of_errors(tmp_path):
    source = tmp_path / 'source.tif'
    make_dem(source, 150, -47)

    class FakeResponse:
        def __init__(self, content): self.stream = io.BytesIO(content)
        def read(self, n=-1): return self.stream.read(n)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    def fake_urlopen(request, timeout=None):
        assert 'demtype=AW3D30' in request.full_url
        assert 'API_Key=secret' in request.full_url
        return FakeResponse(source.read_bytes())

    output = tmp_path / 'dem' / 'alos.tif'
    with patch.object(dem, 'urlopen', side_effect=fake_urlopen):
        dem.download_opentopography((-47, -46, -21, -20), output,
                                    demtype='AW3D30', api_key='secret')
    with rasterio.open(output) as src:
        assert src.count == 1
        assert src.read(1)[0, 0] == 150

    with patch.object(dem, 'urlopen', return_value=FakeResponse(b'{"error":"bad key"}')):
        with pytest.raises(RuntimeError, match='não devolveu GeoTIFF válido') as err:
            dem.download_opentopography((-47, -46, -21, -20), output,
                                        demtype='AW3D30', api_key='secret')
    assert 'secret' not in str(err.value)
    assert output.exists()


def test_invalid_region_and_model(tmp_path):
    with pytest.raises(ValueError, match='Limites inválidos'):
        dem.download_copernicus((-46, -47, -21, -20), tmp_path / 'test.tif')
    with pytest.raises(ValueError, match='desconhecido'):
        dem.download_alternative_dem('palsar', (-47, -46, -21, -20), tmp_path / 'test.tif')

@pytest.mark.parametrize("environment_key", ["", "configured-key"])
def test_opentopography_prompt_only_when_key_is_missing(tmp_path, monkeypatch, environment_key):
    monkeypatch.setenv("OPENTOPOGRAPHY_API_KEY", environment_key)
    source = tmp_path / "source.tif"
    make_dem(source, 150, -47)
    output = tmp_path / "alos.tif"
    expected_key = environment_key or "prompt-key"

    with (
        patch.object(dem, "getpass", return_value="prompt-key") as prompt,
        patch.object(dem, "urlopen", return_value=io.BytesIO(source.read_bytes())) as request,
    ):
        dem.download_alternative_dem(
            "alos", (-47, -46, -21, -20), output, key_prompt="Paste API key: ",
        )
        assert f"API_Key={expected_key}" in request.call_args.args[0].full_url

    assert prompt.call_count == int(not environment_key)
    assert output.is_file()


@pytest.mark.parametrize(
    ("demtype", "crs", "accepted"),
    [
        ("ANADEM", "EPSG:4674", True),
        ("ANADEM", "EPSG:4326", True),
        ("ANADEM", "EPSG:3857", False),
        ("AW3D30", "EPSG:4674", False),
    ],
)
def test_opentopography_preserves_supported_crs(tmp_path, demtype, crs, accepted):
    source = tmp_path / "source.tif"
    make_dem(source, 150, -47, crs=crs)
    output = tmp_path / "output.tif"

    with patch.object(dem, "urlopen", return_value=io.BytesIO(source.read_bytes())):
        if not accepted:
            with pytest.raises(ValueError, match=crs):
                dem.download_opentopography(
                    (-47, -46, -21, -20), output, demtype=demtype, api_key="test-key",
                )
            assert not output.exists()
            return
        dem.download_opentopography(
            (-47, -46, -21, -20), output, demtype=demtype, api_key="test-key",
        )

    assert output.read_bytes() == source.read_bytes()
    with rasterio.open(output) as dataset:
        assert dataset.crs.to_string() == crs
