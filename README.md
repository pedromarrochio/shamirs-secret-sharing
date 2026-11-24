# Compartilhamento de segredos de Shamir

Implementação em Python do esquema de compartilhamento de segredos de Shamir,
com foco nas propriedades de álgebra abstrata que permitem reconstruir um
segredo por interpolação de Lagrange.

O fluxo implementado usa o corpo dos inteiros módulo um primo, `Z_p`. Um segredo
inteiro é dividido em `n` fragmentos, dos quais pelo menos `k` são necessários
para recuperá-lo. Os exemplos simulam a distribuição local a participantes.

## Funcionalidades atuais

- Operações em `Z_p`: soma, subtração, multiplicação, divisão e inverso modular.
- Validação de primalidade do módulo.
- Geração de polinômios com coeficientes aleatórios usando `secrets`.
- Distribuição e reconstrução de segredos com `ShamirScheme` e `SecretManager`.
- Representação de participantes e fragmentos imutáveis.
- Serialização de fragmentos no formato textual `p:x:y`.
- Interface de terminal com menu central (`main.py`): configuração, distribuição,
  reconstrução, exemplo guiado e experimentos.
- Experimentos sobre falhas em anéis com módulo composto: inverso inexistente, ambiguidade e vazamento de informação com menos de `k` fragmentos.
- Testes de operações algébricas, validações, integração e propriedades de segurança.

Para o esquema padrão, os parâmetros devem satisfazer `1 <= k <= n < p`, e o segredo deve ser um inteiro no intervalo `0 <= secret < p`. Cada fragmento é um ponto `(x, f(x))`, com coordenadas de distribuição `x = 1, ..., n`. O termo
constante do polinômio é o segredo; os demais coeficientes são sorteados.

## Preparação

Use Python 3.10 ou superior. Execute os comandos abaixo a partir da raiz do
repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pytest
```

O código de execução usa a biblioteca padrão do Python. `pytest` é necessário
para os testes. O `pyproject.toml` configura a descoberta dos testes e o caminho
`src` e a raiz (para os testes dos experimentos); os exemplos e experimentos usam `PYTHONPATH=src` explicitamente.

## Organização

| Pasta | Responsabilidade |
| --- | --- |
| `src/shamir/algebra/` | Interfaces algébricas, corpo primo, anel modular e polinômios. |
| `src/shamir/randomness/` | Interface de amostragem e sorteio de coeficientes no corpo primo. |
| `src/shamir/cryptography/` | Esquema de Shamir, fragmentos, regras do domínio e interpolação de Lagrange. |
| `src/shamir/application/` | Coordenação da distribuição e recuperação por `SecretManager`, e representação de participantes. |
| `src/shamir/serialization/` | Conversão entre fragmentos e texto. |
| `src/shamir/interface/` | Menu de terminal, que só lê entradas e mostra resultados do núcleo. |
| `main.py` | Ponto de entrada da aplicação. |
| `examples/` | Demonstrações executáveis do fluxo de uso. |
| `experiments/` | Experimentos matemáticos e espaços reservados para análises futuras. |
| `tests/` | Verificações automatizadas com pytest. |

## Aplicação principal

```bash
python3 main.py
```

Abre um menu no terminal, sem dependências além da biblioteca padrão:

| Opção | O que faz |
| --- | --- |
| 1. Configurar esquema | Pede o primo `p`, o limiar `k`, o número de participantes `n` e, opcionalmente, os nomes. Valores inválidos são recusados com a explicação. |
| 2. Distribuir um segredo | Gera os fragmentos e entrega um a cada participante, no formato `p:x:y`. Pode mostrar o polinômio sorteado. |
| 3. Reconstruir o segredo | Escolhe os participantes presentes ou recebe fragmentos digitados em texto; mostra os coeficientes de Lagrange e o cálculo de `f(0)`. Recusa menos de `k` fragmentos e abscissas repetidas. |
| 4. Ver participantes | Mostra a configuração e o fragmento de cada participante. |
| 5. Exemplo guiado | Passo a passo com `f(x) = 8 + 5x + 2x²` em `Z_17`: geração, Lagrange e por que dois fragmentos são compatíveis com qualquer um dos 17 segredos. |
| 6. Experimentos | Submenu com os experimentos sobre anéis `Z_m` compostos (descritos abaixo). |

## Demonstrações com saída no terminal

Os scripts abaixo também podem ser executados separadamente; cada um tem sua
própria função `main()`.

### Distribuição e interpolação

```bash
PYTHONPATH=src python3 examples/basic_example.py
```

Usa o segredo `8` em `Z_17`, com limiar de três entre cinco participantes.
Exibe os cinco fragmentos, seleciona as coordenadas `1`, `2` e `4`, mostra os
coeficientes de Lagrange e o cálculo de `f(0)`. Também demonstra a recusa de uma
tentativa com apenas dois fragmentos.

### Recuperação com participantes

```bash
PYTHONPATH=src python3 examples/distributed_recovery.py
```

Usa o segredo `123` em `Z_257`, com limiar de três entre cinco participantes.
Simula a entrega em texto a Alice, Bruno, Carla, Diego e Eva. Alice, Carla e Eva
apresentam seus fragmentos para reconstrução, mesmo com os demais ausentes.
Ao final, demonstra a recusa de fragmentos com coordenadas duplicadas.

Os fragmentos dos dois exemplos podem mudar a cada execução devido ao sorteio
dos coeficientes. A entrega é simulada em memória, sem comunicação de rede ou
persistência em arquivos.

### Por que o módulo primo importa

```bash
PYTHONPATH=src python3 experiments/missing_inverse.py
```

Compara o mesmo polinômio em `Z_17` e `Z_12`: a interpolação funciona no primeiro
caso e encontra um denominador sem inverso no segundo. Também imprime uma tabela
com a proporção de conjuntos de três pontos cujas diferenças permitem calcular
os coeficientes de Lagrange em diferentes módulos, e demonstra dois polinômios
em `Z_12` com fragmentos iguais em coordenadas ímpares e segredos diferentes.

### Vazamento de informação em anel composto

```bash
PYTHONPATH=src python3 experiments/composite_leakage.py
```

Mostra que, em `Z_m` composto, um único fragmento (menos que `k`) já revela
parte do segredo. Como `f(x) - s = x(a_1 + a_2 x + ...)` é múltiplo de `x`,
vale `f(x) ≡ s (mod mdc(x, m))`. Em `Z_12`, o fragmento em `x = 6` reduz os
12 segredos possíveis a 2; em `Z_13`, o mesmo fragmento é compatível com todos.

O anel de inteiros módulo `m`, `Z_m`, é corpo somente quando `m` é primo. Existem
corpos finitos de ordem composta, como `GF(4)`, mas eles não são `Z_4` e não estão
implementados neste projeto.

## Uso como biblioteca

Com `src` disponível no caminho de importação:

```python
from shamir.algebra.finite_field import FiniteField
from shamir.application.secret_manager import SecretManager
from shamir.cryptography.shamir import ShamirScheme
from shamir.randomness.finite_sampler import FiniteFieldSampler
from shamir.serialization.share_text import ShareTextSerializer

field = FiniteField(17)
scheme = ShamirScheme(
    field, threshold=3, participants=5, sampler=FiniteFieldSampler(field)
)
manager = SecretManager(scheme)

shares = manager.distribute_secret(8)
texts = [ShareTextSerializer.serialize(share) for share in shares[:3]]
received = [ShareTextSerializer.deserialize(text) for text in texts]
secret = manager.recover_secret(received)  # 8
```

`Polynomial` depende apenas das operações de `PolynomialArithmetic`: `normalize`,
`zero`, `add` e `multiply`. Essa interface é estrutural, sem necessidade de herança.

`ShamirScheme` usa `PrimeFieldDomain` por padrão para `FiniteField`. O argumento
opcional `domain` permite fornecer regras por meio de `validate_secret`,
`validate_participants`, `create_share` e `validate_share`. Domínios alternativos
precisam ser compatíveis com as coordenadas inteiras de `1` a `n`, com `Share` e
com as operações de interpolação; essa extensão não fornece outros corpos finitos.

## Testes

```bash
python3 -m pytest -q
```

A suíte verifica operações e propriedades dos corpos finitos, anéis compostos,
polinômios, interpolação, entradas inválidas, serialização e integração com
participantes. Também verifica o limiar e, por enumeração em `Z_5`, a igualdade
das distribuições de fragmentos observáveis abaixo do limiar para diferentes
segredos. A interface é testada simulando as entradas do usuário, e o
experimento de vazamento é conferido contra a fórmula `m / mdc(x, m)`. Os
testes não dependem dos módulos de números reais.

## Pendências e limites atuais

- `RealField` e `RealGaussianSampler` ainda não estão implementados.
- `experiments/performance.py`, `experiments/threshold_analysis.py` e
  `experiments/finite_vs_real.py` contêm apenas a estrutura inicial; executá-los
  ainda não produz resultados.
- Os segredos suportados pelo domínio padrão são inteiros; não há conversão
  automática de mensagens ou arquivos em segredos.
- Fragmentos não são autenticados nem associados a uma distribuição por um
  identificador. Misturar fragmentos de segredos diferentes no mesmo corpo ou
  adulterar valores pode produzir um resultado incorreto sem detecção.
- Os exemplos exibem o segredo e os fragmentos para fins de demonstração.
