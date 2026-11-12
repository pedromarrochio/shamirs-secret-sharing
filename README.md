# shamirs-secret-sharing
An implementation of Shamir's Secret Sharing with a focus on its abstract algebra properties.

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
