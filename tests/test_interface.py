"""Testes da interface de terminal, simulando o que o usuário digita."""

from unittest.mock import Mock

from shamir.interface.cli import ShamirCLI


def run_cli(inputs, sampler_values=None):
    """Executa o menu com as entradas dadas e devolve tudo o que foi impresso.

    Com `sampler_values`, os coeficientes sorteados são substituídos por
    valores fixos, para que os fragmentos sejam previsíveis.
    """
    answers = iter(inputs)
    output = []

    def fake_input(prompt):
        output.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError   # fim das entradas simuladas

    kwargs = {}
    if sampler_values is not None:
        kwargs["sampler_factory"] = lambda field: Mock(
            **{"sample.side_effect": list(sampler_values)}
        )
    cli = ShamirCLI(fake_input, output.append, **kwargs)
    cli.run()
    return "\n".join(output), cli


CONFIG_17 = ["1", "17", "3", "5", "Alice, Bruno, Carla, Diego, Eva"]


def test_exit_option():
    text, _ = run_cli(["0"])
    assert "Até logo!" in text


def test_end_of_input_closes_gracefully():
    text, _ = run_cli([])
    assert "Encerrando." in text


def test_invalid_option():
    text, _ = run_cli(["9", "0"])
    assert "Opção inválida." in text


def test_actions_require_configuration():
    text, _ = run_cli(["2", "3", "4", "0"])
    assert text.count("Configure o esquema primeiro") == 3


def test_configuration_rejects_invalid_values():
    # 15 não é primo; k = 6 > n = 5; n = 17 não cabe em Z_17
    inputs = ["1", "15", "17", "6", "5", "3", "17", "3", "5", "", "0"]
    text, cli = run_cli(inputs)
    assert "15 não é primo" in text
    assert "O limiar não pode passar" in text
    assert "n precisa ser menor que p" in text
    assert cli.field.p == 17
    assert [p.name for p in cli.participants][0] == "Participante 1"


def test_default_configuration():
    text, cli = run_cli(["1", "", "", "", "", "0"])
    assert "Z_257, limiar 3 de 5" in text
    assert cli.scheme.threshold == 3 and cli.scheme.participants == 5


def test_wrong_number_of_names():
    text, cli = run_cli(["1", "17", "3", "5", "Ana, Bia", "A, B, C, D, E", "0"])
    assert "exatamente 5 nomes" in text
    assert cli.participants[4].name == "E"


def test_distribute_and_reconstruct_with_participants():
    inputs = CONFIG_17 + ["2", "8", "s", "3", "1", "1 2 4", "0"]
    text, cli = run_cli(inputs, sampler_values=[5, 2])
    assert "f(x) = 8 + 5x + 2x²" in text
    assert "Alice: 17:1:15" in text
    assert "Coeficientes de Lagrange L_j(0): [14, 15, 6]" in text
    assert "Segredo recuperado: 8" in text
    assert all(p.has_share for p in cli.participants)


def test_polynomial_hidden_by_default():
    inputs = CONFIG_17 + ["2", "8", "", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "Polinômio sorteado" not in text
    assert "Alice: 17:1:15" in text


def test_invalid_secret_is_asked_again():
    inputs = CONFIG_17 + ["2", "abc", "17", "8", "n", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "não é um número inteiro" in text
    assert "O segredo precisa estar entre 0 e 16" in text


def test_redistribution_replaces_shares():
    inputs = CONFIG_17 + ["2", "8", "n", "2", "s", "3", "n", "0"]
    text, cli = run_cli(inputs, sampler_values=[5, 2, 0, 0])
    # segundo segredo 3 com coeficientes nulos: todos recebem y = 3
    assert all(p.share.y == 3 for p in cli.participants)


def test_reconstruction_refused_below_threshold():
    inputs = CONFIG_17 + ["2", "8", "n", "3", "1", "1 3", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "Reconstrução recusada: São necessários pelo menos 3" in text


def test_reconstruction_refuses_duplicate_participant():
    inputs = CONFIG_17 + ["2", "8", "n", "3", "1", "1 1 2", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "As abscissas precisam ser distintas" in text


def test_invalid_participant_numbers_are_asked_again():
    inputs = CONFIG_17 + ["2", "8", "n", "3", "1", "a b", "", "9", "2 3 5", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "Use apenas números" in text
    assert "Informe pelo menos um participante" in text
    assert "Os números vão de 1 a 5" in text
    assert "Segredo recuperado: 8" in text


def test_reconstruction_without_distribution():
    text, _ = run_cli(CONFIG_17 + ["3", "1", "0"])
    assert "Nenhum segredo foi distribuído" in text


def test_reconstruction_from_text():
    inputs = CONFIG_17 + ["3", "2", "17:1:15", "lixo", "17:3:7", "17:5:15", "", "0"]
    text, _ = run_cli(inputs)
    assert "Ignorado: Formato inválido" in text
    assert "Segredo recuperado: 8" in text


def test_reconstruction_from_text_with_wrong_modulus():
    inputs = CONFIG_17 + ["3", "2", "13:1:2", "13:2:3", "13:3:4", "", "0"]
    text, _ = run_cli(inputs)
    assert "módulo do fragmento difere" in text


def test_status():
    inputs = CONFIG_17 + ["4", "2", "8", "n", "4", "0"]
    text, _ = run_cli(inputs, sampler_values=[5, 2])
    assert "Nenhum segredo distribuído." in text
    assert "Alice: (1, 15) em Z_17" in text


def test_guided_example():
    text, _ = run_cli(["5", "", "", "", "0"])
    assert "f(x) = 8 + 5x + 2x²" in text
    assert "f(0) = 15·14 + 9·15 + 9·6 = 399 ≡ 8 (mod 17)" in text
    assert "Recusada: São necessários pelo menos 3" in text
    assert text.count("s = ") == 17
    assert "<- segredo verdadeiro" in text


def test_experiments_menu():
    inputs = ["6", "1", "", "2", "", "3", "", "4", "", "99", "0", "0"]
    text, _ = run_cli(inputs)
    assert "FALHOU: o denominador 3 não tem inverso" in text
    assert "100.0%" in text
    assert "segredo g(0) = 2" in text
    assert "Segredos ainda possíveis: [5, 11] (2 de 12)" in text
    assert "Opção inválida." in text


def test_small_field_has_valid_defaults():
    text, cli = run_cli(["1", "2", "", "", "", "0"])
    assert "Z_2, limiar 1 de 1" in text
    assert cli.scheme.participants == cli.scheme.threshold == 1


def test_configuration_can_change_modulus_and_cancel():
    inputs = CONFIG_17 + ["2", "8", "n", "1", "s", "13", "voltar",
                          "19", "3", "5", "cancelar", "4", "0"]
    text, cli = run_cli(inputs, sampler_values=[5, 2])
    assert "Configuração cancelada" in text
    assert cli.field.p == 17
    assert [p.share.y for p in cli.participants] == [15, 9, 7, 9, 15]


def test_configuration_back_commits_only_the_new_complete_scheme():
    text, cli = run_cli(["1", "17", "3", "voltar", "13", "2", "3", "", "0"])
    assert cli.field.p == 13
    assert cli.scheme.threshold == 2
    assert len(cli.participants) == 3


def test_new_demonstrations_preserve_current_distribution():
    inputs = CONFIG_17 + ["2", "8", "n", "6", "5", "", "6", "", "7", "",
                          "8", "", "9", "", "10", "", "0", "3", "1", "1 2 4", "0"]
    text, cli = run_cli(inputs, sampler_values=[5, 2])
    assert "Polinômios compatíveis: 2; segredos possíveis: [8]" in text
    assert "distribuições iguais para todos os 25 segredos? sim" in text
    assert "A recusa da API sozinha não prova sigilo" in text
    assert "resultado 14" in text and "resultado 15" in text
    assert "Segredo recuperado: 8" in text
    assert cli.field.p == 17


def test_explorer_distinguishes_unique_secret_from_unique_polynomial():
    text, cli = run_cli(["6", "11", "12", "3", "12:1:3", "12:2:2", "12:3:5",
                         "", "", "0", "0"])
    assert "Segredos possíveis: [8]" in text
    assert "Polinômios compatíveis: 2" in text
    assert cli.scheme is None


def test_explorer_refuses_wrong_modulus_duplicates_and_large_parameters():
    for answers, expected in (
        (["12", "3", "13:1:3", ""], "módulo de cada fragmento"),
        (["12", "3", "12:1:3", "12:1:3", ""], "abscissas precisam ser distintas"),
        (["1000", "3"], "Use m entre 2 e 25"),
    ):
        text, _ = run_cli(["6", "11", *answers, "", "0", "0"])
        assert expected in text


def test_explorer_reports_incompatible_observations():
    text, _ = run_cli(["6", "11", "5", "1", "5:1:1", "5:2:2", "", "", "0", "0"])
    assert "Nenhum polinômio de grau < k" in text
