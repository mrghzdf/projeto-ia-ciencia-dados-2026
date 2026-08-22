# Dicionário das principais colunas

As descrições de origem foram conferidas no dicionário XLSX oficial incluído no ZIP.

## Variáveis de origem

| Coluna               | Papel                            | Descrição/categorias principais                                                                   |
| -------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------- |
| `CO_CURSO`           | Chave de agregação               | Código do curso no ENADE; não identifica estudante                                                |
| `CO_IES`             | Identificador excluído do modelo | Código da IES no e-MEC                                                                            |
| `CO_CATEGAD`         | Preditora categórica             | Categoria administrativa: pública federal/estadual/municipal, privada, especial etc.              |
| `CO_ORGACAD`         | Preditora categórica             | Universidade, centro universitário, faculdade, instituto federal etc.                             |
| `CO_GRUPO`           | Preditora categórica             | Área de enquadramento do curso no ENADE                                                           |
| `CO_MODALIDADE`      | Preditora categórica             | `0` EaD; `1` presencial                                                                           |
| `CO_UF_CURSO`        | Preditora categórica             | Código IBGE da UF                                                                                 |
| `CO_REGIAO_CURSO`    | Preditora categórica             | `1` Norte, `2` Nordeste, `3` Sudeste, `4` Sul, `5` Centro-Oeste                                   |
| `ANO_FIM_EM`         | Engenharia de atributo           | Ano de conclusão do ensino médio informado pelo estudante; contém erros documentados              |
| `ANO_IN_GRAD`        | Engenharia de atributo           | Ano de ingresso na graduação informado pelo estudante; contém erros documentados                  |
| `CO_TURNO_GRADUACAO` | Engenharia de atributo           | `1` matutino, `2` vespertino, `3` integral, `4` noturno                                           |
| `TP_SEXO`            | Engenharia de atributo           | `M`, `F` ou `9` indefinido                                                                        |
| `NU_IDADE`           | Engenharia de atributo           | Idade em 26/11/2023, faixa oficial 17-89                                                          |
| `QE_I08`             | Engenharia de atributo           | Faixa de renda familiar                                                                           |
| `QE_I10`             | Engenharia de atributo           | Situação de trabalho                                                                              |
| `QE_I15`             | Engenharia de atributo           | Ingresso por ação afirmativa/inclusão social                                                      |
| `QE_I17`             | Engenharia de atributo           | Tipo de escola do ensino médio                                                                    |
| `QE_I21`             | Engenharia de atributo           | Familiar com ensino superior                                                                      |
| `QE_I22`             | Engenharia de atributo           | Livros extraclasse lidos no ano                                                                   |
| `QE_I23`             | Engenharia de atributo           | Horas semanais de estudo fora das aulas                                                           |
| `QE_I25`             | Engenharia de atributo           | Motivo de escolha do curso                                                                        |
| `QE_I26`             | Engenharia de atributo           | Motivo de escolha da IES                                                                          |
| `QE_I27`--`QE_I68`   | Engenharia de atributo           | Itens Likert sobre processo formativo; `1`--`6` válidos, `7` não sabe, `8` não se aplica          |
| `TP_PRES`            | Filtro do desfecho               | `555` presente com resultado válido; demais códigos documentam ausência/dispensa/desconsideração  |
| `NT_GER`             | Desfecho original                | Nota bruta 0-100: 25% formação geral e 75% componente específico; máximo observado/documentado 99 |

## Variáveis engenheiradas no nível de curso

| Padrão/coluna                 | Significado                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `N_INSCRITOS`                 | Quantidade de linhas/inscrições do curso no arquivo 1                         |
| `NT_GER_MEDIA_CURSO`          | Média de `NT_GER` entre presenças válidas; desfecho contínuo                  |
| `N_RESULTADOS_VALIDOS`        | Suporte amostral da média; usado como filtro, não como preditor               |
| `TARGET_ACIMA_MEDIANA_TREINO` | Alvo binário derivado exclusivamente pelo limiar do treino                    |
| `IDADE_*`                     | Média, mediana, desvio e quartis de idade por curso                           |
| `PROP_SEXO_*`                 | Proporção de cada categoria de sexo por curso                                 |
| `PROP_TURNO_*`                | Proporção de estudantes por turno no curso                                    |
| `PROP_QE_*`                   | Proporção de cada resposta, calculada dentro do arquivo da questão e do curso |
| `TX_RESPOSTA_QE_*`            | Cobertura de resposta da questão no curso                                     |
| `AVALIACAO_PROCESSO_MEDIA`    | Média descritiva dos itens Likert válidos `QE_I27`--`QE_I68` por curso        |
| `TX_ANO_*_INVALIDO`           | Proporção de anos informados fora de 1950-2023, convertidos em nulos          |

## Colunas deliberadamente excluídas dos preditores

- Identificadores `CO_CURSO`, `CO_IES` e `CO_MUNIC_CURSO`, para evitar memorização e alta cardinalidade.
- Todas as notas parciais, gabaritos, vetores de respostas da prova e situações de itens do arquivo 3, pois determinam diretamente `NT_GER`.
- `N_RESULTADOS_VALIDOS` e `TX_PRESENCA_VALIDA`, mantidos apenas para auditoria/EDA.
