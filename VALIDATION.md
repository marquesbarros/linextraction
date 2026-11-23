# Validação científica e reprodutibilidade

Este documento distingue verificações executadas, evidência de reprodução e experimentos propostos. O código auditado é o do commit [`65d6080`](https://github.com/marquesbarros/linextraction/tree/65d608053e6057afe12201e75165ae50b5b2197f). As fórmulas e os parâmetros da implementação estão em [METHOD.md](METHOD.md), e as fontes em [REFERENCES.md](REFERENCES.md).

## Validação já realizada

### Testes de aquisição e verificações internas

Em 23 de novembro de 2026, foram compiladas as 13 células de código de cada notebook, e os cinco testes de aquisição passaram localmente com Python 3.14, NumPy 2.5.2, Rasterio 1.5.1 e pytest. Os testes usam GeoTIFFs sintéticos. Nas rotas remotas, substituem a obtenção dos mosaicos ou a resposta HTTP. [Testes versionados](tests/test_linextraction_dem.py)

| Teste existente | Escopo da verificação |
| --- | --- |
| `test_copernicus_url_hemispheres` | Formação de nomes de geocélula para dois pares de hemisférios |
| `test_copernicus_clip_across_two_tiles` | União de dois mosaicos sintéticos contíguos, recorte longitudinal, CRS, número de bandas, presença de NoData, valores nos extremos e tag da fonte |
| `test_opentopography_needs_key_before_network` | Rejeição sem chave configurada para AW3D30 |
| `test_opentopography_validates_tiff_and_keeps_key_out_of_errors` | Aceitação de resposta GeoTIFF simulada, rejeição de texto inválido, ausência da chave fictícia na mensagem de erro verificada e existência do arquivo válido após a falha |
| `test_invalid_region_and_model` | Rejeição de limites invertidos e de um identificador de fonte inválido |

A célula 18 de cada notebook verifica o CRS do Shapefile, a unicidade de `id`, o intervalo axial de `strike`, duas coordenadas por segmento e a concordância dos atributos CSV e Shapefile. A construção das rosetas verifica a conservação da contagem e do comprimento nas classes e a normalização dos percentuais. Esses controles avaliam integridade de dados e aritmética de saída. A suíte versionada concentra-se na aquisição e deixa em aberto testes de inclinação, Hough, regressão, posição e orientação contra feições de geometria conhecida. [Notebooks PT e EN](Extracao_de_lineamentos_SRTM.ipynb) · [Notebook em inglês](SRTM_Lineament_Extraction.ipynb)

Na verificação da interface local atual, uma resposta ANADEM simulada em EPSG:4674 foi preservada e reprojetada para UTM nos dois notebooks. Foram verificadas as saídas SVG e PNG com cinco iluminações e segmentos sintéticos, incluindo painéis com duas linhas. Em ambos os notebooks, as oito prévias JPEG embutidas apresentaram os mesmos pixels para os dois formatos de exportação. Os SVGs dos painéis preservaram a geometria vetorial e as imagens raster dos relevos sombreados.

### Aquisição Copernicus em um recorte real

Na revisão de 23 de novembro de 2026, o adaptador `download_alternative_dem("copernicus", ...)` leu um COG do bucket público na AWS para o retângulo `(-46.65, -46.64, -20.30, -20.29)` em ordem oeste, leste, sul, norte e graus WGS84. O mosaico acessado foi `Copernicus_DSM_COG_10_S21_00_W047_00_DEM`. A saída tinha CRS EPSG:4326, uma banda de 36 × 36 células a 1″, 1.296 valores válidos e tag `elevation_model=COP30`. Foi uma verificação pontual da aquisição, com o adaptador executado separadamente do notebook e GeoTIFF temporário. A verificação de entrega real pelo OpenTopography, inclusive a referência horizontal da resposta ANADEM, permanece pendente. [Adaptador](linextraction_dem.py) · [Catálogo Copernicus e distribuição](REFERENCES.md#copernicus-handbook)

### Caso de referência na Serra da Canastra

As saídas incorporadas aos notebooks datam de 19 de novembro de 2026, da execução de referência do commit [`6f42994`](https://github.com/marquesbarros/linextraction/tree/6f42994c50771bbe0f2ea6de9735b95a032e08ea) com SRTM, quatro iluminações, comprimento mínimo de 600 m e sensibilidade muito alta. Os resultados reais incluem sobreposições por iluminação, mapa sobre a média dos hillshades e comparações direcionais. A revisão conferiu os arquivos locais correspondentes às execuções em inglês e português. Ambos os CSVs têm o mesmo SHA‑256, e cada Shapefile contém 480 segmentos de dois vértices com atributos que conferem com o CSV correspondente dentro da precisão de leitura. A saída incorporada precede a introdução do seletor de MDE. O código atual preserva a rota de aquisição padrão. [Produtos reais no notebook executado](Extracao_de_lineamentos_SRTM.ipynb)

| Azimute/elevação em ° | Segmentos | Soma de `comp_m` em m |
| --- | ---: | ---: |
| 45/45 | 120 | 458.773,699 |
| 135/45 | 120 | 392.268,209 |
| 225/45 | 120 | 464.890,376 |
| 315/45 | 120 | 422.451,401 |

O GeoTIFF de entrada inspecionado tem 1.477 colunas, 901 linhas, CRS EPSG:4326 e espaçamento de 1″. O hillshade inspecionado tem 1.462 colunas, 952 linhas, CRS EPSG:32723 e espaçamento de 29,500906 m. Os hashes permitem identificar esses artefatos específicos.

| Artefato nas duas execuções | SHA‑256 |
| --- | --- |
| `srtm/srtm.tif` | `41dd09e143705a79addd8ee0b7611b311c736f00c480ae7f5565b5b2a89a1e6e` |
| `lineamentos.csv` | `ef4208763c68cea1b45cf089dfc0c598b1913390a0d0519eb3eeac956fd0d9e9` |

As quatro iluminações atingiram o teto de 120 segmentos por iluminação. A igualdade das contagens documenta saturação neste caso. A detectabilidade por azimute deve ser estimada com uma referência externa. Os totais de comprimento somam registros, incluindo possíveis reaparições de feições. A repetição entre versões do notebook é evidência de consistência computacional no mesmo recorte com o mesmo insumo e configuração. A exatidão geométrica e a interpretação estrutural exigem dados de referência externos. [Método e limites](METHOD.md#10-interpretação-geológica-e-limites-de-inferência) · [Šilhavý et al. (2016)](REFERENCES.md#silhavy-2016)

## Reprodução

1. Obter a revisão auditada do repositório, escolher um notebook e manter o diretório raiz como diretório de trabalho do kernel. As fontes alternativas usam o módulo Python da raiz. Salvar uma cópia parametrizada do notebook e registrar o identificador Git e os parâmetros da célula 3. [Notebook PT](Extracao_de_lineamentos_SRTM.ipynb) · [Notebook EN](SRTM_Lineament_Extraction.ipynb)
2. Preparar Python 3.14.5 e GMT 6.6.0, com as bibliotecas nativas acessíveis ao kernel. O exemplo registra PyGMT 0.19.0 e GDAL 3.12.4, reportado pelo Rasterio. Registrar o sistema operacional, as versões efetivas de GDAL e PROJ, o GMT, a arquitetura e as dependências resolvidas. Os notebooks fornecem o comando de instalação e fixam as dependências diretas abaixo.
3. Registrar a fonte de elevação, limites, pares de iluminação, modo de sensibilidade e comprimento mínimo. A aquisição SRTM usa o GMT, o Copernicus usa leitura COG e as rotas AW3D30 e ANADEM usam a chave OpenTopography. Nas execuções interativas atuais, ela pode ser informada em campo oculto na aquisição. Para reprodução automatizada, configure `OPENTOPOGRAPHY_API_KEY` no ambiente. Registrar data, versão do produto ou mosaicos e URL sem credenciais, conforme disponíveis. Arquivar o GeoTIFF de entrada e seu hash SHA‑256 para identificar os dados efetivamente processados. Retenção e redistribuição devem observar as condições do produto. [Produtos e API](REFERENCES.md#gmt-srtm) · [Copernicus](REFERENCES.md#copernicus-handbook) · [AW3D30](REFERENCES.md#tadono-2016) · [ANADEM](REFERENCES.md#laipelt-2024)
4. Executar todas as células em ordem. Guardar a saída da aquisição com CRS, dimensões, espaçamento e hash. Preservar a estrutura da pasta gerada, inclusive máscaras raster e arquivos auxiliares do Shapefile. Usar `az_luz` e `alt_luz` para recuperar a origem dos segmentos. Em uma repetição com dados arquivados, conferir que o GeoTIFF adquirido coincide com o arquivo registrado. A entrada configurável do notebook atual é a aquisição por provedor. Uma repetição baseada em arquivo arquivado exigiria um procedimento experimental separado. [Rastreabilidade dos produtos](METHOD.md#9-produtos-rastreabilidade-e-adaptação-metodológica)
5. Para verificar repetibilidade, comparar hashes dos insumos e atributos e geometrias usando CRS e tolerâncias declarados. Uma diferença em bytes no GeoTIFF pode provir de metadados ou compressão. Para diagnosticar, comparar afim, CRS, máscara e array de alturas ou intensidades. Registrar cada repetição como execução própria, com parâmetros, versões, hash do insumo e local do resultado.

| Componente | Versão de referência |
| --- | --- |
| Python, GMT e GDAL do Rasterio | 3.14.5, 6.6.0 e 3.12.4 |
| NumPy, SciPy e scikit-image | 2.5.2, 1.18.1 e 0.26.0 |
| Rasterio, PyGMT e pyproj | 1.5.1, 0.19.0 e 3.7.2 |
| GeoPandas, pyogrio e Shapely | 1.1.4, 0.13.0 e 2.1.2 |
| Matplotlib, pandas, Pillow e ipykernel | 3.11.1, 3.0.5, 12.3.0 e 7.4.0 |

A semente da PPHT é fixada em zero no código. Isso controla o componente pseudoaleatório em condições equivalentes. As bibliotecas, o recorte efetivo, as revisões dos produtos e as regras de interpolação também fazem parte das condições de reprodução. O projeto informa as versões diretas nos notebooks. Um manifesto separado de ambiente resolvido, objetos remotos e hashes por execução completaria a proveniência necessária a um artigo. [Código da PPHT](REFERENCES.md#scikit-image-026) · [Rastreabilidade](METHOD.md#9-produtos-rastreabilidade-e-adaptação-metodológica)

## Validação ainda necessária

Os itens abaixo são um protocolo proposto. Os valores de exemplo ilustram níveis de experimentação e devem ser fixados antes de consultar o conjunto de avaliação final. Cada análise deve especificar o domínio comum, a unidade observacional e a variável medida. O protocolo diferencia concordância cartográfica com traçados e sustentação geológica das hipóteses de origem. [Goodchild e Hunter (1997)](REFERENCES.md#goodchild-hunter-1997) · [Masoud e Koike (2011)](REFERENCES.md#masoud-koike-2011)

### 1. Referência manual, evidência geológica e desenho amostral

- Selecionar áreas independentes com contrastes de relevo, cobertura do solo, litologia, densidade de drenagem e intensidade de interferência antrópica. Usar blocos de calibração e avaliação separados espacialmente. Fixar parâmetros de comparação nos blocos de calibração e manter sítios de avaliação para estimar transferência. Incluir condições com emendas e vazios. [Grohmann (2018)](REFERENCES.md#grohmann-2018) · [Roberts et al. (2017)](REFERENCES.md#roberts-2017)
- Para avaliar detecção topográfica, obter ao menos duas interpretações manuais independentes e cegas aos candidatos automáticos. Padronizar escala de visualização, comprimento mínimo, regra de segmentação, máscaras e legenda. Manter as interpretações originais, registrar a concordância entre intérpretes e produzir consenso ou adjudicação com categoria de incerteza. Analisar separadamente a referência interpretada sob condições visuais equivalentes e a referência enriquecida com múltiplas vistas e insumos. Isso explicita a diferença entre concordância sob o mesmo produto e mudança de evidência. [Smith e Clark (2005)](REFERENCES.md#smith-clark-2005) · [Šilhavý et al. (2016)](REFERENCES.md#silhavy-2016)
- Para avaliar interpretação estrutural, comparar com mapas geológicos e estruturais independentes de escala compatível. Quando disponíveis, usar observações de campo de falhas, fraturas, contatos e atitudes, além de geofísica ou imagens ópticas independentes. Registrar a proveniência, a escala, a data e a incerteza de localização das referências. Classificar correspondências como sustentadas, ambíguas, erosivas, antrópicas ou sem informação suficiente. Reservar a classe sem informação para regiões pouco observadas. A coincidência espacial pode sustentar uma hipótese, junto com evidências sobre a natureza da feição. [O’Leary et al. (1976)](REFERENCES.md#oleary-1976) · [Masoud e Koike (2011)](REFERENCES.md#masoud-koike-2011) · [Ângelo da Silva Neto et al. (2022)](REFERENCES.md#silva-neto-2022)

### 2. Concordância, posição e orientação

Comparar geometrias em um CRS métrico comum. Uma regra proposta exige diferença axial de até $\epsilon_\phi$ e cobertura mútua mínima a uma distância $\tau$, definidos a partir do espaçamento efetivo e da incerteza da cartografia. Como análise de sensibilidade, podem-se testar $\tau$ de um, dois e quatro espaçamentos da grade UTM e tolerâncias angulares como 5°, 10° e 20°. Esses valores pertencem ao protocolo de avaliação e devem ser discutidos diante da escala do mapa. [Goodchild e Hunter (1997)](REFERENCES.md#goodchild-hunter-1997) · [Mardia e Jupp (2000)](REFERENCES.md#mardia-jupp-2000)

Para candidatos $D$ e referências $R$, tome $\mathcal L$ como comprimento de linha em metros e $B_\tau$ como união dos buffers de raio $\tau$ m. A cobertura em comprimento pode ser descrita por

$$
P_\ell(\tau)=\frac{\mathcal L(D\cap B_\tau(R))}{\mathcal L(D)},\qquad
R_\ell(\tau)=\frac{\mathcal L(R\cap B_\tau(D))}{\mathcal L(R)}.
$$

Calcular as frações em ambas as direções, usando o domínio comum e explicando se o comprimento do denominador representa registros ou a união das linhas. A cobertura baseada em buffers deriva da avaliação posicional de linhas. A escolha de usá-la de modo simétrico junto a limiares angulares faz parte deste protocolo. Um denominador zero deve ser registrado como métrica indefinida. [Goodchild e Hunter (1997)](REFERENCES.md#goodchild-hunter-1997)

Para métricas por objeto, construir pares elegíveis e usar correspondência um a um de cardinalidade máxima, com desempate pela qualidade da sobreposição e distância. Sejam $TP$ os pares aceitos, $FP$ os candidatos sem par e $FN$ as referências sem par. Registrar a precisão $TP/(TP+FP)$ e a revocação $TP/(TP+FN)$ para um universo de referência com cobertura conhecida, além de $F_1=2PR/(P+R)$, com $P$ e $R$ proporções adimensionais. Registrar também a cobertura por comprimento e correspondências um-para-muitos e muitos-para-um em análise separada, pois a reta detectada e a trajetória interpretada podem usar segmentações diferentes. Áreas sem referência adequada devem ser identificadas ou excluídas da avaliação de omissão e comissão, de acordo com uma regra prévia. [Goodchild e Hunter (1997)](REFERENCES.md#goodchild-hunter-1997) · [Šilhavý et al. (2016)](REFERENCES.md#silhavy-2016)

Para pares correspondentes, amostrar ambos os traços a passo fixo em metros e relatar a mediana e o percentil 95 das distâncias ao traço oposto, por direção, comprimento e tipo de feição. Para orientações $\phi_D,\phi_R\in[0,180^\circ)$, usar

$$
e_\phi=\min\bigl(|\phi_D-\phi_R|,\ 180^\circ-|\phi_D-\phi_R|\bigr).
$$

$e_\phi$ está em graus e varia de 0° a 90°. Reportar distribuição, mediana e percentil 95. Ao estimar uma média axial, representar a orientação como $(\cos 2\phi,\sin 2\phi)$ com ângulos em radianos, calcular a resultante e dividir seu ângulo por dois, acompanhando a resultante com sua concentração e examinando multimodalidade. Essa estatística é uma análise proposta, distinta do histograma implementado. [Mardia e Jupp (2000)](REFERENCES.md#mardia-jupp-2000)

### 3. Iluminação, fontes e parâmetros

| Fator | Experimento proposto | Resultado a registrar |
| --- | --- | --- |
| Azimute e elevação da luz | Totalizar e comparar separadamente as quatro luzes padrão e pares opostos. Em teste ampliado, controlar simetricamente azimute e elevações como 25°, 45° e 65°, com o mesmo MDE. | Proporção de referências detectadas por orientação e diferença axial entre traço e azimute de luz, posição, extensão, recorrência entre configurações e saturação do teto. Comparar distribuições de contagem e de comprimento. |
| Fonte de elevação | Testar aquisição completa das quatro fontes na cobertura comum. Usar as grades nativas em um braço e, em outro braço experimental, comparar referências verticais e padronizar extensão, grade e máscara em preparação externa. | Registrar versões e máscaras, exatidão vertical frente a pontos independentes, contraste, posições, orientações e detecções correspondentes. Quantificar separadamente o efeito da grade. |
| Sensibilidade e comprimento | Comparar os quatro perfis, variar $L_{\min}$ em torno de 600 m e analisar separadamente a ativação da busca complementar. Se houver uma análise experimental instrumentada, isolar quantis, proeminência, teto, cobertura, espaçamento efetivo, condições de sobreposição e tolerância angular e de distância. | Curvas de precisão e revocação e distribuição de comprimento, posição e orientação. Informar a proporção de iluminações saturadas. Decompor contribuições da busca principal e da complementar. |
| Discretização angular | Recalcular externamente as estatísticas em classes de, por exemplo, 2,5°, 5° e 10°, com um deslocamento de meia classe. Manter os mesmos segmentos. | Estabilidade de máximos, mudança da distribuição e variabilidade por bloco, em contagem e comprimento. |
| Repetibilidade | Reexecutar com os mesmos insumos e ambiente. Em seguida variar separadamente ambiente e distribuição dos dados, mantendo os parâmetros explícitos. | Hashes, igualdade de atributos e geometrias, diferenças de posição e orientação e logs das versões. Em experimento separado, testar a sensibilidade a sementes alternativas sem alterar a implementação documentada. |

A padronização altimétrica deve considerar a referência de alturas e a distinção entre MDS e MDT. Para pontos independentes, por exemplo GNSS ou LiDAR com referenciais compatíveis e resolução adequada, reportar o viés, a mediana do erro absoluto e a raiz do erro quadrático médio de resíduos $e_i=Z_{\mathrm{MDE},i}-Z_{\mathrm{ref},i}$, em metros, por declividade e cobertura. Comparar COP30 e ANADEM como produtos relacionados, já que o segundo deriva do primeiro. Testar limites de mosaico, NoData, regiões além da cobertura e discrepância de CRS na resposta do OpenTopography. [Grohmann (2018)](REFERENCES.md#grohmann-2018) · [Laipelt et al. (2024)](REFERENCES.md#laipelt-2024) · [Florinsky (1998)](REFERENCES.md#florinsky-1998)

### 4. Dependência, recorrência e comparação direcional

Preservar os resultados brutos por iluminação. Em análise externa, agrupar possíveis recorrências com um critério espacial e angular preestabelecido, revisado com amostras manuais, e relatar a multiplicidade de cada grupo. Comparar as rosetas por vista, o conjunto bruto combinado e a versão agrupada. Quando houver agrupamento, definir a geometria representativa, como tratar fragmentações e como atribuir o comprimento sem dupla contagem. Comparar também com a referência manual e um método publicado ou uma linha de base especificada. [Masoud e Koike (2011)](REFERENCES.md#masoud-koike-2011) · [Šilhavý et al. (2016)](REFERENCES.md#silhavy-2016)

Uma medida descritiva proposta de distância entre dois histogramas normalizados nas mesmas classes é $D_{\mathrm{TV}}=\tfrac12\sum_j |p_j-q_j|$. $p_j,q_j$ são proporções em $[0,1]$ e somam um em cada distribuição. $D_{\mathrm{TV}}$ varia entre zero e um. Calcular separadamente para contagem e comprimento e relatar a diferença ao alterar a origem das classes. Para incerteza e generalização, usar reamostragem em blocos espaciais, conservando dentro de cada bloco detecções recorrentes e suas relações. Definir tamanho de bloco e partição antes da avaliação, considerando dependência espacial e cobertura das referências. Tratar as iluminações do mesmo MDE como medições relacionadas. [Mardia e Jupp (2000)](REFERENCES.md#mardia-jupp-2000) · [Roberts et al. (2017)](REFERENCES.md#roberts-2017)

## Maturidade científica

**Estado atual.** O LinExtraction é um fluxo computacional auditável para gerar candidatos a lineamentos topográficos. Dispõe de dois notebooks executados no caso de referência, verificações internas de integridade, cinco testes offline do adaptador e uma demonstração pontual de aquisição real de Copernicus. A Canastra é um exemplo de execução com saída consistente e tetos saturados. O desempenho posicional, a estabilidade entre áreas e MDEs e a correspondência geológica ainda carecem de quantificação.

**Evidência necessária para publicação.** Uma avaliação do método precisa de testes sintéticos das etapas de detecção, repetição documentada nas quatro fontes, referências manuais independentes e comparação em áreas de avaliação reservadas. Para alegações sobre falhas ou fraturas, exige-se validação estrutural independente em escala compatível. O artigo deve apresentar métricas de concordância e incerteza, efeitos da iluminação, da fragmentação e da recorrência, sensibilidade aos limiares e à grade, e uma linha de base para qualquer alegação de desempenho relativo. O insumo, a configuração e os resultados verificáveis devem acompanhar a análise. [Goodchild e Hunter (1997)](REFERENCES.md#goodchild-hunter-1997) · [Šilhavý et al. (2016)](REFERENCES.md#silhavy-2016) · [Roberts et al. (2017)](REFERENCES.md#roberts-2017)
