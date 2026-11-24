# Compartilhamento de segredos de Shamir

Projeto didático em Python para estudar **reconstrução e sigilo em corpos primos
`Z_p` e anéis modulares `Z_m` com módulo composto**. A aplicação distribui um
segredo inteiro entre `n` participantes e permite recuperá-lo com `k` fragmentos.
Os experimentos investigam quais propriedades se preservam quando mudamos a
estrutura algébrica e as coordenadas dos participantes.

O objetivo é responder a três perguntas diferentes:

1. **A fórmula de Lagrange pode ser calculada?** Os denominadores têm inverso?
2. **Os fragmentos determinam o segredo?** Quantos polinômios e termos constantes
   continuam compatíveis com os pontos observados?
3. **Há sigilo com menos de `k` fragmentos?** A distribuição conjunta das
   observações é a mesma para todos os segredos?

Uma resposta positiva ou negativa à primeira pergunta não resolve as outras.

## Executar

É necessário Python 3.10 ou superior. A aplicação usa apenas a biblioteca padrão:

```bash
python3 main.py
```

Para instalar a biblioteca e as dependências de desenvolvimento em um ambiente isolado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest -q
```

Os comandos abaixo devem ser executados a partir da raiz do repositório. Para
rodar exemplos e experimentos sem instalar o pacote, use `PYTHONPATH=src` e `-m`,
como mostrado adiante. Após a instalação editável, `PYTHONPATH=src` é dispensável.

## Entendendo a matemática

### O esquema em um corpo primo

Escolhemos um primo `p` e parâmetros `1 <= k <= n < p`. O segredo é um inteiro
`0 <= s < p`. Construímos

```text
f(x) = s + a₁x + ... + aₖ₋₁x^(k−1)  em Z_p.
```

Os coeficientes `a₁, ..., aₖ₋₁` são sorteados de maneira uniforme e independente
por `secrets.randbelow(p)`, **incluindo zero**. Portanto, o grau é **no máximo**
`k - 1`; forçar o último coeficiente a ser não nulo mudaria a distribuição.
Cada participante recebe `(x, f(x))`, com `x` em `1, ..., n`. Não usamos `x = 0`,
pois `f(0)` é o próprio segredo.

Quaisquer `k` pontos distintos permitem interpolar e recuperar `f(0)`. Com menos
de `k` fragmentos, o sigilo vem da igualdade das distribuições observáveis para
todos os segredos. O programa recusar uma chamada com poucos fragmentos é apenas
uma validação da API; **isso sozinho não demonstra sigilo**.

### Por que um módulo composto pode causar problemas?

Em aritmética modular, dividir por `a` significa multiplicar por seu inverso:
um `b` tal que `a·b ≡ 1 (mod m)`. Esse inverso existe exatamente quando
`mdc(a, m) = 1`. Chamamos esses elementos de **unidades**.

- Em `Z_17`, todo elemento não nulo é unidade: por exemplo, `3⁻¹ = 6`.
- Em `Z_12`, apenas `1, 5, 7, 11` são unidades. O número `3` não tem inverso.
- Em `Z_12`, `3·4 = 0`, apesar de ambos serem não nulos: são **divisores de zero**.

A fórmula de Lagrange exige inversos de produtos de diferenças `x_j - x_i`.
Em um corpo, coordenadas distintas garantem essas divisões. Em um anel composto,
uma diferença não nula pode não ser unidade. Além disso, as coordenadas escolhidas
podem comprometer o sigilo.

| Fenômeno | Exemplo implementado | O que aprendemos |
| --- | --- | --- |
| Denominador sem inverso | `Z_12`, pontos `1, 2, 4`, grau até 2 | A fórmula direta falha; há 6 polinômios e segredos possíveis `0, 4, 8`. |
| Polinômio ambíguo, segredo único | `Z_12`, pontos `1, 2, 3`, grau até 2 | A fórmula falha, mas os 2 polinômios compatíveis têm segredo `8`. |
| Mesmo conjunto de fragmentos, segredos diferentes | `Z_12`, coordenadas ímpares | Polinômios com termos constantes `8` e `2` podem coincidir nesses pontos. |
| Vazamento abaixo do limiar | `Z_12`, um fragmento em `x = 6`, `k = 3` | O fragmento revela `s mod 6`, reduzindo 12 candidatos a 2. |
| Reconstrução sem sigilo | `Z_15`, pontos `1, 2, 3`, `k = 3` | Lagrange funciona, mas o fragmento em `x = 3` revela `s mod 3`. |
| Anel composto com pontos adequados | `Z_25`, pontos `1, 2, 3, 4`, `k = 3` | Qualquer trio reconstrói e todo subconjunto menor preserva o sigilo. |

As contagens da tabela usam `f(x) = 8 + 5x + 2x²`, exceto o exemplo de vazamento,
que usa `f(x) = 5 + 7x + 3x²`.

### A fórmula falhou: o segredo necessariamente é ambíguo?

Não. Em `Z_12`, os fragmentos `(1, 3), (2, 2), (3, 5)` admitem os polinômios
`8 + 5x + 2x²` e `8 + 11x + 8x²`. A fórmula direta de Lagrange tenta inverter `2`,
o que é impossível, mas o termo constante é `8` nos dois casos.

Para qualquer polinômio de grau até 2, vale a identidade sem divisão:

```text
f(0) = 3f(1) − 3f(2) + f(3)
     = 3·3 − 3·2 + 5
     = 8 mod 12.
```

Logo, falha da fórmula, unicidade do polinômio e unicidade do segredo precisam
ser analisadas separadamente. A tabela de frações do experimento original mede
**denominadores invertíveis**, e não todos os métodos possíveis de recuperação.

### Como um único fragmento pode vazar informação?

Para `k >= 2`, escrevemos `f(x) - s = x(a₁ + a₂x + ...)`. Com `d = mdc(x, m)`,
segue que `f(x) ≡ s (mod d)`. Assim, um fragmento `(x, y)` revela `s mod d`.
Os segredos compatíveis são exatamente os que satisfazem `s ≡ y (mod d)`:
como `a₁` é livre, essa condição também é suficiente. Há `m / d` candidatos.

Em `Z_12`, `(6, 11)` deixa apenas `5` e `11` como candidatos. Em `Z_13`, a mesma
coordenada é invertível e uma observação isolada é compatível com todos os
segredos. Para estudar vários fragmentos, o núcleo compara suas distribuições
**conjuntas**, em vez de olhar apenas para cada participante isoladamente.

### Quando um anel composto funciona?

Uma condição suficiente para esta construção é que todos os pontos e todas as
diferenças entre pontos sejam unidades. Equivalentemente, as diferenças entre
quaisquer dois elementos de `{0, x₁, ..., xₙ}` devem ser invertíveis. Incluir `0`
é essencial: só verificar diferenças entre participantes não garante sigilo.

Em `Z_25`, os pontos `1, 2, 3, 4` e suas diferenças não são múltiplos de `5`.
O experimento verifica a recuperação com todos os quatro trios e compara as
distribuições para todos os 25 segredos, em cada subconjunto de tamanho 0, 1 e 2.

Portanto, o módulo primo oferece uma garantia automática para pontos distintos;
um anel composto exige analisar as condições dos pontos. `Z_25` não é o corpo
`GF(25)`: corpos de extensão e números reais estão fora do escopo deste projeto.

## Interface de terminal

O menu principal mantém o fluxo de configuração, distribuição e recuperação:

| Opção | Função |
| --- | --- |
| 1. Configurar esquema | Escolhe `p`, `k`, `n` e nomes. Os padrões se adaptam a corpos pequenos. Digite `voltar` para trocar `p` ou `cancelar` para preservar o estado e retornar ao menu. |
| 2. Distribuir um segredo | Gera fragmentos no formato `p:x:y`, com opção de mostrar o polinômio. |
| 3. Reconstruir o segredo | Seleciona participantes ou recebe fragmentos digitados; exibe os coeficientes de Lagrange e o cálculo de `f(0)`. |
| 4. Ver participantes e fragmentos | Mostra o estado atual. |
| 5. Exemplo guiado | Mantém o exemplo `8 + 5x + 2x²` em `Z_17`, com pausas, inverso modular e os 17 segredos compatíveis com dois fragmentos. |
| 6. Experimentos | Abre as comparações abaixo, sem modificar a distribuição atual. |

O esquema operacional das opções 1 a 4 continua restrito a corpos primos. Os
anéis compostos são estudados em experimentos explícitos, com as condições de
cada demonstração visíveis.

| Submenu de experimentos | Conteúdo |
| --- | --- |
| 1 | Mesmo polinômio e pontos em `Z_17` e `Z_12`: denominador sem inverso. |
| 2 | Fração de conjuntos cujos denominadores de Lagrange são invertíveis. |
| 3 | Polinômios com os mesmos fragmentos e segredos diferentes em `Z_12`. |
| 4 | Vazamento com um fragmento e tabela por coordenada. |
| 5 | Lagrange falha, mas o segredo é único: recuperação sem divisão em `Z_12`. |
| 6 | `Z_25` com pontos adequados: reconstrução e sigilo no esquema 3 de 4. |
| 7 | Tabela comparando fórmula, número de polinômios e segredos possíveis. |
| 8 | Análise exata do limiar em `Z_5`, para todos os subconjuntos dos quatro participantes. |
| 9 | Medianas dos tempos de distribuição e recuperação em corpos primos. |
| 10 | Fragmentos adulterados ou misturados podem produzir um resultado incorreto sem detecção. |
| 11 | Explorador: digite módulo, limiar e fragmentos para contar polinômios e segredos compatíveis. |

O explorador admite `2 <= m <= 25` e `1 <= k <= 3`. Uma linha vazia encerra a
entrada de fragmentos. Sem fragmentos, todos os segredos são candidatos; dados
incompatíveis com o grau admitido podem não ter nenhum polinômio compatível.
As rotinas de enumeração também impõem um orçamento de trabalho para entradas
maiores usadas pela biblioteca.

## Roteiro sugerido para a apresentação

1. Execute a opção principal **5** para apresentar o esquema e justificar o sigilo.
2. No submenu **6**, execute **1**, **3** e **4**: mostre inversos, ambiguidade e vazamento.
3. Execute **5**: questione a conclusão de que falhar em Lagrange torna o segredo indeterminado.
4. Execute **6**: mostre que um anel composto pode preservar as propriedades com pontos adequados.
5. Use **7** para comparar as conclusões. As opções **8**, **10** e **11** ajudam a responder perguntas.

## Exemplos e experimentos separados

Todos são executáveis; não há experimentos reservados sem implementação:

```bash
PYTHONPATH=src python3 -m examples.basic_example
PYTHONPATH=src python3 -m examples.distributed_recovery
PYTHONPATH=src python3 -m experiments.missing_inverse
PYTHONPATH=src python3 -m experiments.composite_leakage
PYTHONPATH=src python3 -m experiments.ring_comparison
PYTHONPATH=src python3 -m experiments.threshold_analysis
PYTHONPATH=src python3 -m experiments.performance
```

Os exemplos básicos usam coeficientes aleatórios, portanto seus fragmentos
mudam entre execuções. As comparações algébricas usam coeficientes fixos e
espaços pequenos para permitir reprodução e enumeração exata.

O experimento de desempenho usa medianas de 15 execuções: exclui a construção
do corpo e seu teste de primalidade, inclui o sorteio na distribuição e usa
exatamente `k` fragmentos na recuperação. Os tempos dependem da máquina e não
medem segurança. A avaliação por Horner usa `O(nk)` operações algébricas e a
interpolação direta usa `O(k²)`, além do custo dos inversos e da aritmética inteira.

## Organização e uso como biblioteca

| Caminho | Responsabilidade |
| --- | --- |
| `src/shamir/algebra/` | Corpo primo, anel modular, contratos de aritmética e polinômios. |
| `src/shamir/randomness/` | Amostragem uniforme de coeficientes no corpo primo. |
| `src/shamir/cryptography/` | Esquema padrão, fragmentos, interpolação e análise exata para experimentos. |
| `src/shamir/application/` | Participantes e entrega local de fragmentos. |
| `src/shamir/serialization/` | Conversão de fragmentos para texto e vice-versa. |
| `src/shamir/interface/` | Menu, leitura de entradas e apresentação das demonstrações. |
| `examples/` | Fluxos de distribuição e recuperação. |
| `experiments/` | Comparações matemáticas, análise do limiar e desempenho. |
| `tests/` | Testes algébricos, regressões, distribuições, experimentos e interface. |
| `.github/workflows/tests.yml` | Execução automática de testes e demonstrações em Python 3.10, 3.12 e 3.13. |

`ShamirScheme` concentra geração, validação e recuperação; não há intermediário
que apenas repasse suas chamadas. A interpolação completa fica no núcleo,
junto da interpolação em um ponto. `PolynomialArithmetic` declara todas as
operações necessárias à avaliação e formatação, inclusive `one()`.

```python
from shamir.algebra.finite_field import FiniteField
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler
from shamir.serialization.share_text import ShareTextSerializer

field = FiniteField(17)
scheme = ShamirScheme(field, threshold=3, participants=5,
                      sampler=FiniteFieldSampler(field))
shares = scheme.split(8)
texts = [ShareTextSerializer.serialize(share) for share in shares[:3]]
received = [ShareTextSerializer.deserialize(text) for text in texts]
assert scheme.reconstruct(received) == 8
```

Para análise experimental, `compatible_secret_counts(m, k, points)` conta os
polinômios de grau `< k` por termo constante; `observation_distribution` enumera
as observações para um segredo; `observations_independent_of_secret` compara as
distribuições completas. Essas funções não alteram as regras do esquema padrão.

## Testes e limites

```bash
python3 -m pytest -q
```

Os testes cobrem operações algébricas, todos os subconjuntos de exemplos pequenos,
igualdade de distribuições abaixo do limiar, recuperação em `Z_25`, identidade sem
divisão em `Z_12`, validações, serialização, interface e metodologia das medições.
Há regressões para um composto que passava pelas primeiras 12 bases de Miller–Rabin
e para o limite que exige bases adicionais.

A primalidade é determinística para `p < 3317044064679887385961981`, usando as
primeiras **13** bases primas. Acima desse limite, o teste é probabilístico, com
32 bases uniformes independentes adicionais e probabilidade de aceitar um composto
limitada por `4^-32`. Aceitação nessa faixa não é uma prova de primalidade.

Os segredos são inteiros, sem conversão automática de mensagens ou arquivos. A
entrega é simulada em memória, sem rede ou persistência. Fragmentos não são
autenticados nem identificam a distribuição: valores adulterados ou fragmentos
de distribuições diferentes podem produzir um resultado incorreto sem detecção.
O experimento 10 demonstra essa limitação; o formato `p:x:y` não a resolve.

Os exemplos mostram segredos, polinômios e fragmentos para fins didáticos. A
biblioteca é um material de estudo, sem implementação de compartilhamento
verificável ou outros mecanismos de autenticidade.

## Referências

- Adi Shamir, [How to Share a Secret (1979)](https://www.cs.tau.ac.il/research/benny.chor/Shamir.html): construção e argumento de sigilo.
- Mark Abspoel et al., [An Efficient Passive-to-Active Compiler for Honest-Majority MPC over Rings, seção 5](https://ir.cwi.nl/pub/31033/31033.pdf): diferenças invertíveis e compartilhamento sobre anéis.
- Jonathan Sorenson e Jonathan Webster, [Strong Pseudoprimes to Twelve Prime Bases, Teorema 1.1](https://arxiv.org/pdf/1509.00864): limites para as bases determinísticas do teste de primalidade.
