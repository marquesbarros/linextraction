# linextraction

Extração de candidatos a lineamentos topográficos em relevos sombreados do SRTM. Um único [notebook Jupyter](Extracao_de_lineamentos_SRTM.ipynb) baixa o modelo de elevação para a área escolhida, gera os hillshades, detecta segmentos retilíneos por iluminação e exporta os dados vetoriais e as figuras.

## Como executar

1. Instale o GMT e disponibilize sua biblioteca para o PyGMT. O ambiente usado no exemplo foi **Python 3.14.5** com **GMT 6.6.0**. [Instalação do GMT e PyGMT](https://www.pygmt.org/v0.19.0/install.html)
2. Abra o notebook no Jupyter ou em um editor compatível e instale, no ambiente do kernel, as dependências com as versões listadas na primeira seção.
3. Na célula de parâmetros, defina `NOME_AREA`, `CANTO_1` e `CANTO_2`. Cole os dois cantos opostos da área em **WGS84 (EPSG:4326)**, na ordem **`(latitude, longitude)`**, com ponto decimal. [Como copiar coordenadas no Google Maps](https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=pt-BR)
4. Edite `ILUMINACOES`. Cada par `(azimute, elevação do Sol)` gera um hillshade e uma análise independente. Os ângulos estão em graus, com o azimute medido a partir do norte da grade UTM e a elevação medida acima do horizonte.
5. Execute as células em ordem, com a pasta do notebook como diretório de trabalho do kernel. Na primeira execução, o GMT baixa os dados de elevação. O notebook exibe a tabela de conferência, os painéis por iluminação e as figuras combinadas.

O exemplo da **Serra da Canastra (MG)** usa os cantos `(-20.36, -46.72)` e `(-20.11, -46.31)`, quatro iluminações e um comprimento mínimo de 600 m. A execução de referência encontrou 480 segmentos, 120 por iluminação no ajuste padrão de sensibilidade muito alta.

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
        ├── hillshade_az*_alt*.png
        ├── comparacao_rosetas.png
        └── roseta_combinada.png
```

O SRTM é exportado em WGS84. Os hillshades e as geometrias usam a zona UTM local. Cada nova execução com o mesmo nome recebe um sufixo como `_02`. Os painéis de comparação mantêm a ordem das iluminações, com até quatro imagens por linha.

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

O mapa combinado coloca todos os segmentos em vermelho sobre a média dos hillshades. A roseta combinada conta todos os segmentos exportados em classes axiais de 15°. Uma feição detectada sob mais de uma iluminação pode contribuir várias vezes. A interpretação estrutural dos candidatos requer evidências geológicas independentes.

## Licença

[BSD 3-Clause](LICENSE).
