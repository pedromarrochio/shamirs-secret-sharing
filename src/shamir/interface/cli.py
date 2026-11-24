"""Interface de terminal do esquema de Shamir.

A interface apenas lê dados do usuário e mostra resultados; toda a matemática
fica nas classes do núcleo. As funções de entrada e saída podem ser
substituídas, o que permite testar a interface simulando o que é digitado.

Execute pela raiz do repositório com `python3 main.py`.
"""

from ..algebra.finite_field import FiniteField
from ..algebra.polynomial import Polynomial
from ..application.participant import Participant
from ..application.secret_manager import SecretManager
from ..cryptography.reconstruction import lagrange_coefficients
from ..cryptography.shamir import ShamirScheme
from ..randomness.finite_sampler import FiniteFieldSampler
from ..randomness.sampler import CoefficientSampler
from ..serialization.share_text import ShareTextSerializer


class FixedSampler(CoefficientSampler):
    """Devolve coeficientes pré-definidos, para exemplos reprodutíveis."""

    def __init__(self, values):
        self._values = iter(values)

    def sample(self):
        return next(self._values)


def interpolating_polynomial(points, field) -> Polynomial:
    """Polinômio de grau < len(points) que passa pelos pontos dados.

    Soma y_j * L_j(x), expandindo cada base de Lagrange
    L_j(x) = prod_{m != j} (x - x_m) / (x_j - x_m) em coeficientes.
    """
    xs = [x for x, _ in points]
    result = [field.zero()] * len(points)
    for j, (xj, yj) in enumerate(points):
        basis = [field.one()]
        denominator = field.one()
        for m, xm in enumerate(xs):
            if m == j:
                continue
            expanded = [field.zero()] * (len(basis) + 1)
            for i, c in enumerate(basis):
                expanded[i] = field.add(expanded[i], field.multiply(c, field.negate(xm)))
                expanded[i + 1] = field.add(expanded[i + 1], c)
            basis = expanded
            denominator = field.multiply(denominator, field.subtract(xj, xm))
        factor = field.divide(yj, denominator)
        for i, c in enumerate(basis):
            result[i] = field.add(result[i], field.multiply(c, factor))
    return Polynomial(result, field)


class ShamirCLI:
    """Menu de terminal para configurar, distribuir e reconstruir segredos."""

    DEFAULT_P, DEFAULT_K, DEFAULT_N = 257, 3, 5

    def __init__(self, input_func=input, output_func=print,
                 sampler_factory=FiniteFieldSampler):
        self._input = input_func
        self._out = output_func
        self._sampler_factory = sampler_factory
        self.field = None
        self.scheme = None
        self.manager = None
        self.participants: list[Participant] = []

    # ------------------------------------------------------------------
    # Laço principal
    # ------------------------------------------------------------------

    def run(self) -> None:
        actions = {
            "1": self.configure,
            "2": self.distribute,
            "3": self.reconstruct,
            "4": self.show_status,
            "5": self.guided_example,
            "6": self.experiments_menu,
        }
        self._out("Compartilhamento de segredos de Shamir")
        try:
            while True:
                self._show_main_menu()
                choice = self._ask("Escolha uma opção: ")
                if choice == "0":
                    self._out("Até logo!")
                    return
                action = actions.get(choice)
                if action is None:
                    self._out("Opção inválida.")
                    continue
                self._out("")
                action()
        except (EOFError, KeyboardInterrupt):
            self._out("\nEncerrando.")

    def _show_main_menu(self) -> None:
        if self.scheme is None:
            status = "esquema não configurado"
        else:
            status = (f"Z_{self.field.p}, limiar {self.scheme.threshold} "
                      f"de {self.scheme.participants}")
        self._out("")
        self._out(f"=== Menu principal ({status}) ===")
        self._out("1. Configurar esquema (p, k, n)")
        self._out("2. Distribuir um segredo")
        self._out("3. Reconstruir o segredo")
        self._out("4. Ver participantes e fragmentos")
        self._out("5. Exemplo guiado (segredo 8 em Z_17, 3 de 5)")
        self._out("6. Experimentos: por que o módulo precisa ser primo")
        self._out("0. Sair")

    # ------------------------------------------------------------------
    # Entrada
    # ------------------------------------------------------------------

    def _ask(self, prompt: str) -> str:
        return self._input(prompt).strip()

    def _ask_int(self, prompt: str, default: int | None = None) -> int:
        suffix = f" [{default}]" if default is not None else ""
        while True:
            text = self._ask(f"{prompt}{suffix}: ")
            if not text and default is not None:
                return default
            try:
                return int(text)
            except ValueError:
                self._out(f"  '{text}' não é um número inteiro. Tente novamente.")

    def _ask_yes_no(self, prompt: str, default: bool = False) -> bool:
        options = "S/n" if default else "s/N"
        while True:
            text = self._ask(f"{prompt} ({options}): ").lower()
            if not text:
                return default
            if text in ("s", "sim"):
                return True
            if text in ("n", "nao", "não"):
                return False
            self._out("  Responda com 's' ou 'n'.")

    def _pause(self) -> None:
        self._ask("(Enter para continuar) ")

    def _require_scheme(self) -> bool:
        if self.scheme is None:
            self._out("Configure o esquema primeiro (opção 1).")
            return False
        return True

    def _has_distribution(self) -> bool:
        return bool(self.participants) and all(p.has_share for p in self.participants)

    # ------------------------------------------------------------------
    # 1. Configuração
    # ------------------------------------------------------------------

    def configure(self) -> None:
        self._out("--- Configuração do esquema ---")
        if self._has_distribution() and not self._ask_yes_no(
                "Reconfigurar descarta os fragmentos atuais. Continuar?"):
            return

        while True:
            p = self._ask_int("Primo p (ordem do corpo Z_p)", self.DEFAULT_P)
            try:
                field = FiniteField(p)
                break
            except (TypeError, ValueError) as error:
                self._out(f"  {error}")

        while True:
            k = self._ask_int("Limiar k (fragmentos necessários)", self.DEFAULT_K)
            n = self._ask_int("Número de participantes n", self.DEFAULT_N)
            try:
                scheme = ShamirScheme(field, k, n, self._sampler_factory(field))
                break
            except (TypeError, ValueError) as error:
                self._out(f"  {error}")

        names = self._ask_names(n)
        self.field = field
        self.scheme = scheme
        self.manager = SecretManager(scheme)
        self.participants = [Participant(i, name) for i, name in enumerate(names, start=1)]
        self._out(f"Esquema configurado: Z_{p}, limiar {k} de {n}.")
        self._out("Participantes: " + ", ".join(p.name for p in self.participants))

    def _ask_names(self, n: int) -> list[str]:
        while True:
            text = self._ask(
                f"Nomes dos {n} participantes, separados por vírgula "
                "(Enter para nomes padrão): "
            )
            if not text:
                return [""] * n   # Participant usa "Participante i" quando vazio
            names = [name.strip() for name in text.split(",")]
            if len(names) != n or any(not name for name in names):
                self._out(f"  Informe exatamente {n} nomes não vazios.")
                continue
            return names

    # ------------------------------------------------------------------
    # 2. Distribuição
    # ------------------------------------------------------------------

    def distribute(self) -> None:
        if not self._require_scheme():
            return
        self._out("--- Distribuição do segredo ---")
        if self._has_distribution():
            if not self._ask_yes_no("Já existe um segredo distribuído. Substituir?"):
                return
        while True:
            secret = self._ask_int(f"Segredo (inteiro de 0 a {self.field.p - 1})")
            try:
                self.scheme.validate_secret(secret)
                break
            except (TypeError, ValueError) as error:
                self._out(f"  {error}")

        show_polynomial = self._ask_yes_no("Mostrar o polinômio sorteado?")
        polynomial, shares = self.scheme.split_with_polynomial(secret)

        if show_polynomial:
            self._out(f"\nPolinômio sorteado (grau ≤ {self.scheme.threshold - 1}):")
            self._out(f"  f(x) = {polynomial}  em Z_{self.field.p}")
            self._out(f"  O segredo é o termo constante: f(0) = {polynomial.evaluate(0)}")

        # Participantes novos: cada um só pode receber um fragmento.
        self.participants = [Participant(p.participant_id, p.name) for p in self.participants]
        self._out("\nFragmentos entregues (formato p:x:y):")
        for participant, share in zip(self.participants, shares):
            participant.receive_share(share)
            text = ShareTextSerializer.serialize(share)
            detail = f"   f({share.x}) = {share.y}" if show_polynomial else ""
            self._out(f"  {participant.name}: {text}{detail}")
        self._out(f"\nQuaisquer {self.scheme.threshold} participantes podem recuperar o segredo.")

    # ------------------------------------------------------------------
    # 3. Reconstrução
    # ------------------------------------------------------------------

    def reconstruct(self) -> None:
        if not self._require_scheme():
            return
        self._out("--- Reconstrução do segredo ---")
        self._out("1. Escolher participantes que apresentam o fragmento")
        self._out("2. Digitar fragmentos em texto (p:x:y)")
        choice = self._ask("Escolha: ")
        if choice == "1":
            shares = self._shares_from_participants()
        elif choice == "2":
            shares = self._shares_from_text()
        else:
            self._out("Opção inválida.")
            return
        if shares is not None:
            self._recover(shares)

    def _shares_from_participants(self):
        if not self._has_distribution():
            self._out("Nenhum segredo foi distribuído ainda (opção 2).")
            return None
        for p in self.participants:
            self._out(f"  {p.participant_id}. {p.name}")
        while True:
            text = self._ask("Números dos participantes presentes (ex.: 1 3 5): ")
            try:
                indices = [int(part) for part in text.replace(",", " ").split()]
            except ValueError:
                self._out("  Use apenas números separados por espaço.")
                continue
            if not indices:
                self._out("  Informe pelo menos um participante.")
                continue
            if any(not 1 <= i <= len(self.participants) for i in indices):
                self._out(f"  Os números vão de 1 a {len(self.participants)}.")
                continue
            break
        chosen = [self.participants[i - 1] for i in indices]
        for p in chosen:
            text = ShareTextSerializer.serialize(p.present_share())
            self._out(f"  {p.name} apresenta {text}")
        return [p.present_share() for p in chosen]

    def _shares_from_text(self):
        self._out("Digite um fragmento por linha; linha vazia para terminar.")
        shares = []
        while True:
            text = self._ask(f"Fragmento {len(shares) + 1}: ")
            if not text:
                break
            try:
                shares.append(ShareTextSerializer.deserialize(text))
            except (TypeError, ValueError) as error:
                self._out(f"  Ignorado: {error}")
        return shares

    def _recover(self, shares) -> None:
        try:
            secret = self.manager.recover_secret(shares)
        except (TypeError, ValueError) as error:
            self._out(f"Reconstrução recusada: {error}")
            return
        p = self.field.p
        xs = [share.x for share in shares]
        coefficients = lagrange_coefficients(xs, 0, self.field)
        self._out(f"\nAbscissas usadas: {xs}")
        self._out(f"Coeficientes de Lagrange L_j(0): {coefficients}")
        expression = " + ".join(
            f"{share.y}·{c}" for share, c in zip(shares, coefficients)
        )
        self._out(f"f(0) = ({expression}) mod {p} = {secret}")
        self._out(f"Segredo recuperado: {secret}")

    # ------------------------------------------------------------------
    # 4. Estado
    # ------------------------------------------------------------------

    def show_status(self) -> None:
        if not self._require_scheme():
            return
        self._out("--- Estado atual ---")
        self._out(f"Corpo: Z_{self.field.p}")
        self._out(f"Limiar: {self.scheme.threshold} de {self.scheme.participants}")
        if not self._has_distribution():
            self._out("Nenhum segredo distribuído.")
        for participant in self.participants:
            self._out(f"  {participant}")

    # ------------------------------------------------------------------
    # 5. Exemplo guiado
    # ------------------------------------------------------------------

    def guided_example(self) -> None:
        """Reproduz o exemplo feito à mão: f(x) = 8 + 5x + 2x² em Z_17."""
        field = FiniteField(17)
        scheme = ShamirScheme(field, 3, 5, FixedSampler([5, 2]))
        secret = 8

        self._out("--- Exemplo guiado: segredo 8, limiar 3 de 5, em Z_17 ---")
        self._out("Passo 1. O distribuidor escolhe um polinômio de grau 2 = k - 1")
        self._out("com termo constante igual ao segredo. Os outros coeficientes")
        self._out("seriam sorteados; aqui foram fixados em 5 e 2 para o exemplo.")
        polynomial, shares = scheme.split_with_polynomial(secret)
        self._out(f"  f(x) = {polynomial}")
        self._pause()

        self._out("Passo 2. Cada participante i recebe o ponto (i, f(i)) mod 17:")
        for share in shares:
            raw = sum(c * share.x ** i for i, c in enumerate(polynomial.coefficients))
            self._out(f"  f({share.x}) = {raw} ≡ {share.y} (mod 17)")
        self._pause()

        selected = [shares[0], shares[1], shares[3]]
        xs = [s.x for s in selected]
        self._out(f"Passo 3. Os participantes {xs} se reúnem. Coeficientes de Lagrange:")
        self._out("  L_j(0) = prod_{m≠j} (0 - x_m) / (x_j - x_m)  em Z_17")
        coefficients = lagrange_coefficients(xs, 0, field)
        for xj, c in zip(xs, coefficients):
            others = [xm for xm in xs if xm != xj]
            num = " · ".join(f"(0 - {xm})" for xm in others)
            den = " · ".join(f"({xj} - {xm})" for xm in others)
            self._out(f"  L({xj}) = {num} / {den} ≡ {c}")
        expression = " + ".join(f"{s.y}·{c}" for s, c in zip(selected, coefficients))
        total = sum(s.y * c for s, c in zip(selected, coefficients))
        recovered = scheme.reconstruct(selected)
        self._out(f"  f(0) = {expression} = {total} ≡ {recovered} (mod 17)")
        self._pause()

        known = shares[:2]
        self._out("Passo 4. E com só 2 fragmentos? Tentativa de reconstrução:")
        try:
            scheme.reconstruct(known)
        except ValueError as error:
            self._out(f"  Recusada: {error}")
        self._out("Mais que isso: os pontos "
                  f"({known[0].x}, {known[0].y}) e ({known[1].x}, {known[1].y}) "
                  "são compatíveis com QUALQUER segredo.")
        self._out("Para cada s em Z_17 existe exatamente um polinômio de grau ≤ 2")
        self._out("passando por (0, s) e por esses dois pontos:")
        for s in range(field.p):
            points = [(0, s)] + [(share.x, share.y) for share in known]
            candidate = interpolating_polynomial(points, field)
            marker = "   <- segredo verdadeiro" if s == secret else ""
            self._out(f"  s = {s:>2}: f(x) = {candidate}{marker}")
        self._out("Por isso k - 1 fragmentos não revelam nada sobre o segredo.")

    # ------------------------------------------------------------------
    # 6. Experimentos
    # ------------------------------------------------------------------

    def experiments_menu(self) -> None:
        # Os experimentos ficam na pasta experiments/, fora do pacote.
        # main.py coloca a raiz do repositório no caminho de importação.
        from experiments import composite_leakage, missing_inverse

        actions = {
            "1": lambda: self._experiment_missing_inverse(missing_inverse),
            "2": lambda: self._experiment_fraction(missing_inverse),
            "3": lambda: self._experiment_ambiguity(missing_inverse),
            "4": lambda: self._experiment_leakage(composite_leakage),
        }
        while True:
            self._out("")
            self._out("--- Experimentos: corpos Z_p versus anéis Z_m compostos ---")
            self._out("1. Inverso inexistente: mesma interpolação em Z_17 e Z_12")
            self._out("2. Quantos conjuntos de pontos permitem reconstruir, por módulo")
            self._out("3. Ambiguidade: mesmos fragmentos, segredos diferentes (Z_12)")
            self._out("4. Vazamento: um único fragmento revela parte do segredo (Z_12)")
            self._out("0. Voltar")
            choice = self._ask("Escolha: ")
            if choice == "0":
                return
            action = actions.get(choice)
            if action is None:
                self._out("Opção inválida.")
                continue
            self._out("")
            action()
            self._pause()

    def _experiment_missing_inverse(self, module) -> None:
        from ..algebra.integer_mod_ring import IntegerModRing

        coefficients, points = [8, 5, 2], [1, 2, 4]
        self._out("f(x) = 8 + 5x + 2x², fragmentos nos pontos x = 1, 2, 4")
        for ring, name, modulus in ((FiniteField(17), "Z_17", 17),
                                    (IntegerModRing(12), "Z_12", 12)):
            r = module.reconstruction_attempt(ring, coefficients, points)
            self._out(f"\n{name}: fragmentos {r['shares']}")
            if r["success"]:
                self._out(f"  L's = {r['lambdas']} -> segredo recuperado = {r['recovered']}")
            else:
                self._out(f"  FALHOU: o denominador {r['element']} não tem inverso "
                          f"(mdc({r['element']}, {modulus}) = {r['gcd']})")
        self._out("\nEm Z_p todo elemento não nulo tem inverso; em Z_12, só 1, 5, 7 e 11.")

    def _experiment_fraction(self, module) -> None:
        from ..algebra.finite_field import is_prime

        self._out("Conjuntos de 3 abscissas em {1, ..., m-1} cujos denominadores")
        self._out("de Lagrange são todos invertíveis em Z_m:\n")
        self._out(f"{'m':>4} {'tipo':>9} {'funcionam':>10} {'total':>6} {'fração':>8}")
        for m in (12, 13, 15, 16, 17, 21, 25, 29, 35):
            ok, total = module.reconstructible_fraction(m, 3)
            kind = "primo" if is_prime(m) else "composto"
            self._out(f"{m:>4} {kind:>9} {ok:>10} {total:>6} {ok / total:>8.1%}")

    def _experiment_ambiguity(self, module) -> None:
        a = module.ambiguity_example()
        self._out("f(x) = 8 + 5x + 2x²  e  g(x) = f(x) + 6(x + 1), em Z_12")
        self._out(f"pontos x:      {a['points']}")
        self._out(f"f(x) mod 12:   {a['f_values']}   segredo f(0) = {a['f_secret']}")
        self._out(f"g(x) mod 12:   {a['g_values']}   segredo g(0) = {a['g_secret']}")
        self._out("Para x ímpar, 6(x + 1) é múltiplo de 12: os fragmentos coincidem,")
        self._out("mas os segredos não. Em Z_12 os fragmentos não determinam o segredo.")

    def _experiment_leakage(self, module) -> None:
        module.print_prime_vs_composite(self._out)
        self._out("")
        module.print_leakage_table(self._out)