# linextraction

LinExtraction extrai candidatos a lineamentos topográficos em relevos sombreados derivados de modelos digitais de elevação. O SRTM é a fonte padrão. Cada iluminação gera uma seleção independente de segmentos retilíneos, exportados com posição, comprimento geodésico e orientação axial.

[Notebook em português](Extracao_de_lineamentos_SRTM.ipynb) · [English notebook](SRTM_Lineament_Extraction.ipynb)

## Documentação científica

- [Materiais e métodos](METHOD.md) descreve o fluxo auditado, suas equações, parâmetros, adaptações e limites de interpretação.
- [Referências](REFERENCES.md) reúne os artigos, catálogos de produtos e fontes sobre a implementação.
- [Validação e reprodução](VALIDATION.md) apresenta as verificações executadas, a evidência da Serra da Canastra e o protocolo experimental ainda necessário.

## Como executar

1. Instale o GMT e disponibilize sua biblioteca para o PyGMT. O ambiente usado no exemplo foi **Python 3.14.5** com **GMT 6.6.0**. [Instalação do GMT e PyGMT](https://www.pygmt.org/v0.19.0/install.html)
2. Abra o notebook no Jupyter ou em um editor compatível e instale, no ambiente do kernel, as dependências com as versões listadas na primeira seção.
3. Na célula de parâmetros, defina `NOME_AREA`, `CANTO_1` e `CANTO_2`. Cole os dois cantos opostos da área em **WGS84 (EPSG:4326)**, na ordem **`(latitude, longitude)`**, com ponto decimal. [Como copiar coordenadas no Google Maps](https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=pt-BR)
4. Edite `ILUMINACOES`. Cada par `(azimute, elevação do Sol)` gera um hillshade e uma análise independente. Os ângulos estão em graus, com o azimute medido a partir do norte da grade UTM e a elevação medida acima do horizonte.
5. Execute as células em ordem, com a pasta do notebook como diretório de trabalho do kernel. A primeira execução pode precisar baixar os dados de elevação do provedor escolhido. O notebook exibe a tabela de conferência, os painéis por iluminação e as figuras combinadas.

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

### Onde colocar a chave OpenTopography

1. Na célula de parâmetros, selecione `alos` ou `anadem`.
2. Rode até a célula que baixa o MDE. Quando aparecer o campo oculto **Chave da API OpenTopography**, cole a chave e pressione Enter. A entrada funciona como um campo de senha.
3. A execução segue com o download. SRTM e Copernicus seguem direto para a aquisição.

Para execução automatizada, defina `OPENTOPOGRAPHY_API_KEY` no ambiente antes de iniciar o kernel. Com essa variável configurada, a execução segue direto. [Portal de chaves OpenTopography](https://www.opentopography.org/developers)

```powershell
$env:OPENTOPOGRAPHY_API_KEY = "sua_chave"
```

No Linux/macOS: `export OPENTOPOGRAPHY_API_KEY="sua_chave"`.

O SRTM mantém o arquivo `srtm/srtm.tif`. Para as demais fontes, o arquivo é armazenado em `dem/<modelo>.tif`; o GeoTIFF de entrada mantém seu CRS geográfico e o notebook usa a mesma reprojeção UTM de antes. O nome da fonte e o SHA-256 do arquivo são apresentados durante a execução. O ANADEM aceita SIRGAS 2000 (EPSG:4674) e WGS84 (EPSG:4326), com reprojeção a partir do CRS recebido.

**ALOS aqui significa AW3D30**, modelo de elevação de 30 m; não corresponde à imagem radar ALOS PALSAR RTC de 12,5 m. A grade de análise do detector permanece de aproximadamente 90 m na busca principal e 60 m na complementar, mesmo quando a fonte de elevação é alterada.

Para rodar os testes offline com GeoTIFFs sintéticos, use `python -m pytest -q tests/test_linextraction_dem.py`. A aquisição do Copernicus pela AWS foi demonstrada em um recorte piloto. A verificação de entrega real pelo OpenTopography permanece pendente. [Escopo das evidências](VALIDATION.md#validação-já-realizada)

## Arquivos gerados

Use `FORMATO_IMAGEM = "svg"` no notebook em português ou `IMAGE_FORMAT = "svg"` no notebook em inglês para exportar as figuras no formato vetorial padrão. Use `"png"` para exportá-las como imagens raster. O formato escolhido vale para as sobreposições, rosetas, gráficos e painéis. Nos SVGs das sobreposições, o hillshade permanece raster e os traços permanecem vetoriais. O notebook embute prévias raster das figuras. Os arquivos na pasta de resultados mantêm o formato escolhido.

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
    │   ├── hillshade_az*_alt*.<formato>
    │   ├── comparacao_iluminacoes.<formato>
    │   └── mapa_combinado.<formato>
    └── rosetas/
        ├── segmentos/
        └── frequencia/
```

O SRTM é exportado em WGS84. Os hillshades e as geometrias usam a zona UTM local. Cada nova execução com o mesmo nome recebe um sufixo como `_02`. Os painéis de comparação mantêm a ordem das iluminações, com até quatro imagens por linha e rótulos no formato `Az/Dip`. A cor de cada iluminação é compartilhada entre as sobreposições, as rosetas e os gráficos cartesianos.

Cada pasta de rosetas contém as figuras individuais, `comparacao_rosetas.<formato>`, `roseta_combinada.<formato>` e `comparacao_cartesiana.<formato>`. Em `segmentos/`, a métrica é a contagem por classe. Em `frequencia/`, é a soma dos comprimentos em metros por classe. As rosetas mostram percentuais do total da métrica e usam uma escala radial comum por métrica. Os gráficos cartesianos mostram valores absolutos.

O CSV e o Shapefile contêm os mesmos atributos.

| Campo | Descrição |
| --- | --- |
| `id` | Identificador do segmento na execução |
| `lon_c`, `lat_c` | Longitude e latitude do ponto médio, em graus decimais WGS84 |
| `comp_m` | Comprimento geodésico entre as extremidades, em metros |
| `strike` | Orientação axial em relação ao norte verdadeiro, no intervalo [0°, 180°) |
| `az_luz`, `alt_luz` | Azimute e elevação solar do hillshade de origem, em graus |

## Método e interpretação

O MDE é reprojetado para UTM e convertido em um hillshade lambertiano por iluminação. O realce multiescala por Hessiana, a proeminência escura e a transformada de Hough probabilística progressiva geram propostas. O ajuste transversal, os critérios de continuidade e a seleção limitam a saída a segmentos retilíneos com suporte na imagem. [Horn (1981)](REFERENCES.md#horn-1981) · [Sato et al. (1998)](REFERENCES.md#sato-1998) · [Transformada de Hough probabilística progressiva](REFERENCES.md#ppht)

O mapa combinado mantém a origem de iluminação de cada segmento sobre a média dos hillshades. As rosetas usam 36 classes axiais de 5° e representam contagens ou somas de comprimento por classe. A agregação combinada retém as ocorrências em cada iluminação. A atribuição de origem estrutural requer validação independente. [Mardia e Jupp (2000)](REFERENCES.md#mardia-jupp-2000) · [O’Leary et al. (1976)](REFERENCES.md#oleary-1976) · [Validação](VALIDATION.md)

## Licença

[BSD 3-Clause](LICENSE).
