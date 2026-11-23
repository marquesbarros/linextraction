# linextraction

Extração de candidatos a lineamentos topográficos em relevos sombreados do SRTM. O notebook baixa o modelo de elevação, gera os hillshades, detecta segmentos retilíneos por iluminação e exporta os dados vetoriais e as figuras.

[Notebook em português](Extracao_de_lineamentos_SRTM.ipynb) · [English notebook](SRTM_Lineament_Extraction.ipynb)

## Como executar

1. Instale o GMT e disponibilize sua biblioteca para o PyGMT. O ambiente usado no exemplo foi **Python 3.14.5** com **GMT 6.6.0**. [Instalação do GMT e PyGMT](https://www.pygmt.org/v0.19.0/install.html)
2. Abra o notebook no Jupyter ou em um editor compatível e instale, no ambiente do kernel, as dependências com as versões listadas na primeira seção.
3. Na célula de parâmetros, defina `NOME_AREA`, `CANTO_1` e `CANTO_2`. Cole os dois cantos opostos da área em **WGS84 (EPSG:4326)**, na ordem **`(latitude, longitude)`**, com ponto decimal. [Como copiar coordenadas no Google Maps](https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=pt-BR)
4. Edite `ILUMINACOES`. Cada par `(azimute, elevação do Sol)` gera um hillshade e uma análise independente. Os ângulos estão em graus, com o azimute medido a partir do norte da grade UTM e a elevação medida acima do horizonte.
5. Execute as células em ordem, com a pasta do notebook como diretório de trabalho do kernel. Na primeira execução, o GMT baixa os dados de elevação. O notebook exibe a tabela de conferência, os painéis por iluminação e as figuras combinadas.

O exemplo da **Serra da Canastra (MG)** usa os cantos `(-20.36, -46.72)` e `(-20.11, -46.31)`, azimutes de 45°, 135°, 225° e 315° com elevação solar de 45° e um comprimento mínimo de 600 m. A execução de referência encontrou 480 segmentos, 120 por iluminação no ajuste padrão de sensibilidade muito alta.

## Fontes alternativas de elevação

O SRTM continua sendo o **padrão**. A aquisição por GMT, os parâmetros de iluminação, a reprojeção, a extração e as exportações continuam iguais. Nas células de parâmetros, selecione a fonte:

```python
MODELO_ELEVACAO = "srtm"  # Notebook português
# ELEVATION_MODEL = "srtm"  # English notebook
```

| Opção | Produto | Acesso | Autenticação |
| --- | --- | --- | --- |
| `srtm` | SRTMGL1 (30 m) | GMT, fluxo original | Não |
| `copernicus` | Copernicus GLO-30 | AWS, leitura COG remota | Não |
| `alos` | ALOS World 3D AW3D30 | OpenTopography | Chave gratuita |
| `anadem` | ANADEM (América do Sul) | OpenTopography | Chave gratuita |

Para `alos` e `anadem`, solicite a chave em https://www.opentopography.org/developers e configure **antes de abrir o Jupyter**:

```powershell
$env:OPENTOPOGRAPHY_API_KEY = "sua_chave"
```

No Linux/macOS: `export OPENTOPOGRAPHY_API_KEY="sua_chave"`.

O SRTM mantém o arquivo `srtm/srtm.tif`. Para as demais fontes, o arquivo é armazenado em `dem/<modelo>.tif`; o GeoTIFF de entrada fica em WGS84 e o notebook usa a mesma reprojeção UTM de antes. O nome da fonte e o SHA-256 do arquivo são apresentados durante a execução.

**ALOS aqui significa AW3D30**, modelo de elevação de 30 m; não corresponde à imagem radar ALOS PALSAR RTC de 12,5 m. A grade de análise do detector permanece de aproximadamente 90 m na busca principal e 60 m na complementar, mesmo quando a fonte de elevação é alterada.

Testes sem Internet, usando GeoTIFFs sintéticos: `python -m pytest -q tests/test_linextraction_dem.py`. O acesso remoto real ao AWS ou ao OpenTopography deve ser validado em uma execução com conexão.

## Arquivos gerados

```text
linextraction_resultados/
└── <NOME_AREA>/
    ├── lineamentos.csv
    ├── srtm/
    │   └── srtm.tif
    ├── hillshades/
    │   └── hillshade_az*_alt*.tif
    ├── shapefile/
    │   ├── lineamentos.shp
    │   └── arquivos auxiliares do Shapefile
    ├── sobreposicoes/
    │   ├── hillshade_az*_alt*.png
    │   ├── comparacao_iluminacoes.png
    │   └── mapa_combinado.png
    └── rosetas/
        ├── segmentos/
        └── frequencia/
```

O SRTM é exportado em WGS84. Os hillshades e as geometrias usam a zona UTM local. Cada nova execução com o mesmo nome recebe um sufixo como `_02`. Os painéis de comparação mantêm a ordem das iluminações, com até quatro imagens por linha e rótulos no formato `Az/Dip`. A cor de cada iluminação é compartilhada entre as sobreposições, as rosetas e os gráficos cartesianos.

Cada pasta de rosetas contém as figuras individuais, `comparacao_rosetas.png`, `roseta_combinada.png` e `comparacao_cartesiana.png`. Em `segmentos/`, a métrica é a contagem por classe. Em `frequencia/`, é a soma dos comprimentos em metros por classe. As rosetas mostram percentuais do total da métrica e usam uma escala radial comum por métrica. Os gráficos cartesianos mostram valores absolutos.

O CSV e o Shapefile contêm os mesmos atributos.

| Campo | Descrição |
| --- | --- |
| `id` | Identificador do segmento na execução |
| `lon_c`, `lat_c` | Longitude e latitude do ponto médio, em graus decimais WGS84 |
| `comp_m` | Comprimento geodésico entre as extremidades, em metros |
| `strike` | Orientação axial em relação ao norte verdadeiro, no intervalo [0°, 180°) |
| `az_luz`, `alt_luz` | Azimute e elevação solar do hillshade de origem, em graus |

## Método e interpretação

O SRTM de 1 segundo de arco é reprojetado para UTM antes do cálculo do sombreamento e da declividade. A detecção usa um filtro de Sato para realçar faixas escuras alongadas e a transformada de Hough probabilística para propor segmentos. O ajuste transversal aproxima os segmentos dos eixos escuros e recorta trechos com apoio insuficiente. Na sensibilidade padrão, uma busca complementar realça eixos escuros mais estreitos. [SRTMGL1 V003](https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003) · [Dados SRTM via GMT](https://www.generic-mapping-tools.org/remote-datasets/srtm-relief.html) · [Filtro de Sato](https://doi.org/10.1016/S1361-8415(98)80009-1)

O mapa combinado coloca os segmentos na cor da iluminação de origem sobre a média dos hillshades. As duas métricas usam as mesmas 36 classes axiais de 5° no intervalo de 0° a 180°. Uma feição detectada sob mais de uma iluminação pode contribuir várias vezes. A interpretação estrutural dos candidatos requer evidências geológicas independentes.

## Licença

[BSD 3-Clause](LICENSE).
