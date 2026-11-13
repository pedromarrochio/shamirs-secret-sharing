# shamirs-secret-sharing
An implementation of Shamir's Secret Sharing with a focus on its abstract algebra properties.

## Exemplos

Execute a partir da raiz do repositório:

```bash
PYTHONPATH=src python3 examples/basic_example.py
PYTHONPATH=src python3 examples/distributed_recovery.py
```

O primeiro mostra os fragmentos, os coeficientes de Lagrange e a recuperação
do segredo, além da recusa por quantidade insuficiente de fragmentos.
O segundo simula a entrega em texto a cinco participantes e a recuperação
por três deles, incluindo a recusa de fragmentos duplicados. Os coeficientes
são sorteados em cada execução. A distribuição é local, sem comunicação de rede.

## Interfaces e serialização

`Polynomial` requer apenas as operações de `PolynomialArithmetic`: `normalize`,
`zero`, `add` e `multiply`. A interface é estrutural; não é necessário herdá-la.

`ShamirScheme` usa `PrimeFieldDomain` por padrão quando recebe `FiniteField`.
Outros domínios podem ser fornecidos pelo argumento `domain`, implementando
`validate_secret(secret)` e `validate_participants(participants)`. As validações
gerais do limiar continuam no esquema. O domínio também implementa `create_share(x, y)` e `validate_share(share)`
para construir e validar fragmentos. `split` usa coordenadas inteiras de 1 a n;
um domínio alternativo deve suportar essa representação. A reconstrução requer
pelo menos k fragmentos com coordenadas distintas e módulos compatíveis.
Fragmentos não são autenticados: misturar segredos do mesmo corpo ou adulterar
valores pode produzir um resultado incorreto sem detecção.

A conversão textual foi extraída de `Share` para `ShareTextSerializer`:

```python
from shamir.serialization.share_text import ShareTextSerializer

text = ShareTextSerializer.serialize(share)  # substitui share.to_text()
share = ShareTextSerializer.deserialize(text)  # substitui Share.from_text(text)
```

O formato de intercâmbio continua sendo `p:x:y`.
