# Inspeção técnica do ENADE 2023

## Origem e formato

- Fonte declarada no manual: Portal de Dados Abertos do INEP, área de microdados.
- Página oficial específica do dataset: <https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enade>.
- O portal do INEP lista os “Microdados do Enade 2023” como atualizados em 24/04/2025 (consulta em 21/08/2026).
- Modalidade: tabular.
- Formato: 32 arquivos TXT delimitados por ponto e vírgula, documentação PDF e dicionário XLSX/ODS.
- Tamanho descompactado neste projeto: aproximadamente 315 MB.
- Edição: ENADE 2023; manual atualizado em 11/04/2025.

O pacote não inclui um arquivo de licença convencional. O uso está fundamentado na disponibilização pública pelo INEP, na Lei do Sinaes citada pelo manual e nas salvaguardas da LGPD descritas pelo órgão. Antes de redistribuir dados derivados, deve-se conferir os termos atuais do portal oficial.

## Auditoria observada

- 406.294 linhas em cada arquivo de dados.
- 9.812 códigos de curso.
- 346.557 registros com `NT_GER` não nulo.
- 9.380 cursos com resultado válido; o manual exclui cursos com apenas um resultado válido.
- Nota individual `NT_GER`: média 48,284; mediana 47,9; faixa observada 0-99.
- Média de `NT_GER` por curso: média 46,328; mediana 46,047; faixa observada 17,45-80,85.
- Após exigir pelo menos 10 resultados válidos: 7.723 cursos para modelagem.
- Split: 6.178 cursos no treino e 1.545 no teste.

## Regra de importação do manual

- Separador `;`.
- Primeira linha como cabeçalho.
- Decimal `.`.
- `.` como faltante numérico e campo vazio como faltante textual.
- Vetores de respostas devem ser lidos como texto quando utilizados.

## Restrção estrutural obrigatória

Os arquivos foram deliberadamente ordenados por variáveis diferentes para dificultar reidentificação. Linhas de arquivos distintos **não representam a mesma pessoa**, mesmo quando têm a mesma posição. `CO_CURSO` também não identifica estudantes.

Assim, este projeto agrega cada arquivo separadamente por `CO_CURSO` e só depois une as tabelas agregadas. Qualquer junção linha a linha seria tecnicamente falsa e contrária à proteção descrita pelo INEP.

## Duplicados

Repetições exatas nos arquivos brutos não podem ser tratadas como estudantes duplicados: a anonimização removeu um identificador individual, e pessoas distintas podem ter os mesmos valores. Essas linhas são mantidas. A tabela de modelagem possui uma linha por curso; nela, `CO_CURSO` é validado como único e não houve duplicata.
