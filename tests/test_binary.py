"""Test the Comby binary."""
import pytest

from comby import CombyBinary


@pytest.fixture()
def get_comby_binary() -> CombyBinary:
    """
    Create the Comby binary.

    """
    return CombyBinary()


def test_matches_should_return_single_match_when_pattern_contains_backslashes(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'matches' method accurately identifies patterns with backslashes in the source code.

    Verifies that the 'matches' method of a CombyBinary object can successfully find a pattern
    that includes backslash escapes in a source string exactly once.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = ' if \'charset\' in response.headers.get("Content-Type", "")\n'
    template = ":[ spaces]:[a]:[newline~[\n]]"

    result = list(get_comby_binary.matches(source, template, language=".py"))

    assert len(result) == 1


def test_matches_should_return_correct_substitution_when_backslash_escapes_present(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'matches' method correctly substitutes patterns that include backslash escapes.

    Verifies that the 'matches' method of a CombyBinary object can correctly perform a substitution
    when the source string contains backslash escapes. The substitution is considered correct if the
    result matches the expected string exactly.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = ' if \'charset\' in response.headers.get("Content-Type", "")\n'
    template = ":[ spaces]:[a]:[newline~[\n]]"
    replacement = ":[spaces]:[a]:[newline]:[spaces]break;:[newline]"
    matches = list(get_comby_binary.matches(source, template, language=".py"))
    match = matches[0]
    environment = {entry: match[entry].fragment for entry in match.environment}
    expected = ' if \'charset\' in response.headers.get("Content-Type", "")\n break;\n'

    result = get_comby_binary.substitute(replacement, environment)

    assert result == expected


def test_matches_should_return_single_match_when_pattern_exists_once(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'matches' method successfully finds patterns in the source code.

    Verifies that the 'matches' method of a CombyBinary object can identify when a specified pattern
    (template) occurs in a source string. A successful match is when the source contains the exact
    pattern described by the template exactly once.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = "print('hello world')"
    template = "print(:[1])"

    result = list(get_comby_binary.matches(source, template))

    assert len(result) == 1


def test_matches_should_return_no_matches_when_pattern_does_not_exist(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'matches' method returns no matches when the pattern does not exist in the source string.

    Verifies that the 'matches' method of a CombyBinary object accurately identifies the absence of a specified pattern
    (template) within a source string. A successful test is when the source does not contain the specified pattern,
    resulting in zero matches.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = "foo"
    template = "bar"

    result = list(get_comby_binary.matches(source, template))

    assert len(result) == 0


def test_rewrite_should_succeed_when_template_matches_once(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'rewrite' method successfully applies transformations.

    Verifies that the 'rewrite' method of a CombyBinary object can apply a specified transformation
    when the source string contains the pattern described by the template exactly once.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = "print('hello world')"
    template = "print(:[1])"
    rewrite = "println(:[1])"
    expected = "println('hello world')"

    result = get_comby_binary.rewrite(source, template, rewrite)

    assert result == expected


def test_rewrite_switch_case_to_c3po(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'rewrite' method can successfully replace a specific case in a switch statement.

    Verifies that the 'rewrite' method of a CombyBinary object can identify and replace a specified pattern
    (template) in a source string with a desired replacement pattern. The test checks for a correct rewrite
    when replacing the case label "WALL-E" with "C3PO" within a switch statement.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source: str = """
    switch (name) {
        case "WALL-E":
            System.out.println("Hey! Stop that droid!");
            break;
        default:
            System.out.println("These aren't the droids we're looking for...");
    }
    """.strip()
    template = 'case "WALL-E"'
    rewrite = 'case "C3PO"'
    expected = """
    switch (name) {
        case "C3PO":
            System.out.println("Hey! Stop that droid!");
            break;
        default:
            System.out.println("These aren't the droids we're looking for...");
    }
    """.strip()

    result = get_comby_binary.rewrite(source, template, rewrite, language=".java")

    assert result == expected


def test_rewrite_should_match_newline_at_top_of_source(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'rewrite' method matches and rewrites code at the top level of the source code.

    Verifies that the 'rewrite' method of a CombyBinary object can identify and transform a specified pattern
    (template) that occurs at the top level of a source string, where the pattern includes a newline character
    at the beginning of the source string.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    source = "\n".join(
        [
            "def foo():",
            "    print('hello world')",
            "",
        ],
    )
    template = "def :[fn_name]::[body]:[next_fn~(\n\\z)]"
    rewrite = "\n".join(
        [
            "def :[fn_name]::[body]",
            "    print('hello mars'):[next_fn]",
        ],
    )
    expected = "\n".join(
        [
            "def foo():",
            "    print('hello world')",
            "    print('hello mars')",
            "",
        ],
    )

    result = get_comby_binary.rewrite(
        source, template, rewrite, language=".py", match_newline_at_toplevel=True
    )

    assert result == expected


def test_substitute_should_replace_pattern_with_arguments(
    get_comby_binary: CombyBinary,
) -> None:
    """
    Test that the 'substitute' method replaces patterns with provided arguments.

    Verifies that the 'substitute' method of a CombyBinary object can accurately replace a specified pattern
    (template) with the arguments provided. A successful substitution is when the template is replaced by
    the arguments exactly as specified.

    :param get_comby_binary: A callable that returns a CombyBinary object.
    :type get_comby_binary: CombyBinary
    """
    template = "my name is :[1]"
    args = {"1": "very secret"}
    expected = "my name is very secret"

    result = get_comby_binary.substitute(template, args)

    assert result == expected
