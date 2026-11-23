"""Aquisição complementar de MDEs para o LinExtraction.

Os rasters são devolvidos como GeoTIFF em EPSG:4326, compatíveis com
reproject_to_utm dos notebooks. O caminho original do SRTM/GMT não muda.
"""

from contextlib import ExitStack
from math import ceil, floor, isfinite
from os import environ, replace
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from rasterio.merge import merge

OPENTOPOGRAPHY_ENDPOINT = "https://portal.opentopography.org/API/globaldem"
COPERNICUS_BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"
MODELS = {"copernicus": "COP30", "alos": "AW3D30", "anadem": "ANADEM"}


def _bounds(region):
    """Transforma a região GMT (oeste, leste, sul, norte) em limites raster."""
    west, east, south, north = map(float, region)
    if not (all(map(isfinite, (west, east, south, north)))
            and -180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("Limites inválidos: informe (oeste, leste, sul, norte) em WGS84.")
    return west, south, east, north


def _copernicus_tile_url(lon: int, lat: int) -> str:
    ns = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}"
    ew = f"{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
    name = f"Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM"
    return f"{COPERNICUS_BUCKET}/{name}/{name}.tif"


def download_copernicus(region, destination):
    """Recorta GLO-30 diretamente dos COGs públicos AWS, sem API key."""
    west, south, east, north = _bounds(region)
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    urls = [
        _copernicus_tile_url(lon, lat)
        for lat in range(floor(south), ceil(north))
        for lon in range(floor(west), ceil(east))
    ]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with ExitStack() as stack:
            sources = []
            for url in urls:
                try:
                    source = stack.enter_context(rasterio.open(url))
                except rasterio.errors.RasterioIOError as exc:
                    raise RuntimeError(
                        "Não foi possível abrir um mosaico COP30 da AWS. "
                        "Verifique conexão, cobertura e suporte HTTP do GDAL. "
                        f"Mosaico: {url}"
                    ) from exc
                if source.crs is None or source.crs.to_epsg() != 4326:
                    raise ValueError(f"Mosaico COP30 com CRS inesperado: {url}")
                sources.append(source)
            image, transform = merge(
                sources, bounds=(west, south, east, north),
                res=(1 / 3600, 1 / 3600), dtype="float32", nodata=np.nan,
            )
    elevation = image[0]
    if min(elevation.shape) < 2 or not np.isfinite(elevation).any():
        raise ValueError("O recorte do Copernicus não possui elevação válida.")
    with rasterio.open(
        dest, "w", driver="GTiff", count=1, height=elevation.shape[0],
        width=elevation.shape[1], dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=np.nan, compress="lzw",
    ) as dataset:
        dataset.write(elevation, 1)
        dataset.update_tags(elevation_model="COP30", provider="Copernicus DEM GLO-30 / AWS")
    return dest


def download_opentopography(region, destination, *, demtype, api_key=None):
    """Baixa AW3D30 ou ANADEM por recorte WGS84 no OpenTopography."""
    if demtype not in {"AW3D30", "ANADEM"}:
        raise ValueError("Modelo não suportado pelo adaptador OpenTopography.")
    west, south, east, north = _bounds(region)
    key = api_key if api_key is not None else environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not key or not key.strip():
        raise ValueError(
            "Para AW3D30/ANADEM, defina OPENTOPOGRAPHY_API_KEY no ambiente. "
            "Chave gratuita: https://www.opentopography.org/developers"
        )
    params = dict(demtype=demtype, south=south, north=north, west=west, east=east,
                  outputFormat="GTiff", API_Key=key.strip())
    request = Request(
        OPENTOPOGRAPHY_ENDPOINT + "?" + urlencode(params),
        headers={"User-Agent": "LinExtraction/1.0"},
    )
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        try:
            with urlopen(request, timeout=180) as response:
                with NamedTemporaryFile(
                    mode="wb", suffix=".tif", prefix=".mde-", dir=dest.parent,
                    delete=False,
                ) as handle:
                    temp = Path(handle.name)
                    copyfileobj(response, handle)
        except HTTPError as exc:
            raise RuntimeError(f"OpenTopography retornou HTTP {exc.code} para {demtype}.") from exc
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Falha de conexão ao obter {demtype} no OpenTopography.") from exc

        try:
            with rasterio.open(temp) as src:
                if src.crs is None or src.crs.to_epsg() != 4326:
                    raise ValueError(f"O retorno de {demtype} não está em EPSG:4326.")
                if min(src.width, src.height) < 2 or not src.read(1, masked=True).count():
                    raise ValueError(f"O retorno de {demtype} não possui elevação válida.")
        except rasterio.errors.RasterioIOError as exc:
            raise RuntimeError(
                f"OpenTopography não devolveu GeoTIFF válido para {demtype}. "
                "Confira a chave, as cotas e a área solicitada."
            ) from exc
        replace(temp, dest)
        temp = None
        return dest
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def download_alternative_dem(model, region, destination):
    """Seleciona apenas modelos complementares; SRTM permanece no GMT."""
    model = model.strip().lower()
    if model == "copernicus":
        return download_copernicus(region, destination)
    if model in ("alos", "anadem"):
        return download_opentopography(region, destination, demtype=MODELS[model])
    raise ValueError("Modelo de elevação desconhecido. Use srtm, copernicus, alos ou anadem.")
