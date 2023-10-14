import openai
import os

def sample_custom(var: str, variables: List[str], values: Dict[str, str]) -> List[Tuple[str, float]]:
    """
    :param var: The name of the variable to be sampled
    :param variables: The names of all variables, in order of first occurance
    :param values: A dictionary of all available values, keyed by variable name
    :return: A list of value and likelihood pairs
    """
    raise NotImplementedError

def sample_llm(var, variables, values, model="gpt-4"):
    with open("templates/marginal_distribution.md") as f:
        template = f.read()
    prompt = template.format(
        var=var,
        variables = "\n".join(variables),
        values = "\n".join([f"- {var}: {value}" for var, value in values.items()])
    )
    response = openai.Completion.create(
        model=model,
        prompt=prompt,

    )