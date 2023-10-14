# 117-billion

# Usage

Just go to [https://joernstoehler.github.io/117-billion/](https://joernstoehler.github.io/117-billion/) and enjoy.

# Local Development

## View the page

I use github pages to host the page. Everything is static html pages, with a bit of css and javascript magic.

If you clone the project, you can simply open `docs/index.html` in your favorite browser.

## Sample a random human

To sample a new random human, run

```bash
python3 src/sample.py --openai-api-key=<YOUR_API_KEY>
```
Replace `YOUR_API_KEY` with your [OpenAI API key](https://platform.openai.com/account/api-keys). Alternatively, you can also set the environment variable `OPENAI_API_KEY`.

The script will create four files: 
* an html-page you can view in your browser: `docs/generated/<id>.html`.
* a json-file with statistical variables that describe the human: `docs/generated/<id>.json`.
* the generated biography: `docs/generated/<id>.md`.
* the generated portrait image: `docs/generated/<id>.png`.
* a log file: `docs/generated/<id>.log`.

### Costs

I do not make any guarantees about how expensive running the script or otherwise interacting with this project is.

From my own experience I expect that each fake-human costs $1. Costs can be broken down into
```
gpt-4: $0.005/1k tokens * 10k tokens = $0.05
dall-e 3: 
```

You can check the log file to investigate all api calls that were made.

### Dummy Run

Instead of actually executing api calls, you can also run the script with 

```bash
python3 src/sample.py --dummy
```

In this case, the script will not call the OpenAI API, but instead use a dumber program that generates an automatic response for every possible type of prompt. This is useful for testing and debugging.

The dummy program is defined in `src/dummy.py` and uses templates from `src/templates/dummy/`.

## Customize your human (For Programmers)

The script `src/sample.py` basically just calls several other scripts in sequence. You can do this manually, and specify some extra parameters.

The first step is to run `src/sample_variables.py` which creates `docs/generated/<id>.json` and returns `<id>`.

The second step is to run `src/biography.py --id=<id>` which creates the biography `docs/generated/<id>.md`.

The third step is to run `src/image.py --id=<id>` which creates the image `docs/generated/<id>.png`.

And the fourth step is to run `src/html.py --id=<id>` which creates the html file `docs/generated/<id>.html`.

### Variables

The script `src/sample_variables.py` samples several statistical variables that describe a human. Because LLMs are bad random number generators I use a trick: I let the LLM write down a probability distribution, and then let a simple python script sample from that distribution properly.

Because the full distribution over all humans ever is hard to write down, I evaluate one statistical variable after the other, thereby only requiring the marginal distribution for the next variable, conditioned on all earlier variables.

In the following you'll find instructions how to set-up and modify the list of variables for the script, both in command-line, and in python-code.

Once the script has run, internally calling the OpenAI API many times, it writes the values of all variables into a json file `docs/generated/<id>.json` and prints the `<id>`. This `<id>` and file is then used by the other scripts to create the biography, the image, and the html file.

#### Example Usage

```bash
python3 src/sample_variables.py \
    --default-var \
    --default-order \
    --var birth_date="December 24th, 1 B.C." \
    --var birth_region="Near East" \
    --var birth_subregion="Judea" \
    --var ethnic_group="Jews" \
    --var parents_socioeconomic_status="lower class" \
    --var birth_gender="male" \
    --var religion="Jewish" \
    --var socioeconomic_status="lower class" \
    --var profession="unemployed" \
    --var marital_status="single" \
    --var children="none" \
    --var death_date="April 3rd, 33 A.D." \
    --var death_cause="execution" \
    --var name="Brian"
```

#### Defining Variables

Variables are defined via command line arguments. If you define a variable several times, only the last definition will be used.

You can define a variable with constant value via the command-line argument `--var <key>=<value>`.

Instead of a fixed value, you can also assign a static distribution to a variable via `--var-table <key>=<path/to/table.csv>`. The csv-table must contain value and odds pairs. Example:

```csv
"Value", Odds
"left-handed", 1
"right-handed", 9.5
```
The first line specifying the column names is optional and will be ignored. The values ought to be quoted and may contain commas, the odds must be unquoted floats.

Instead of a static table, you can also let GPT4 write the distribution on the spot, taking into consideration the known values of earlier-evaluated variables. For this write `--var-llm <key>`.

Instead of letting the LLM write a distribution, you can also let GPT4 sample a value directly. For this write `--var-llm-direct <key>`.

Finally, you can provide a custom python function to sample the variable with `--var-python <key>=<expression>`. See the section [Custom Variable Definitions and Python Functions](#custom-variable-definitions-and-python-functions) for how to program new functions. You can also avoid editing the source files and instead do things like:

```bash
--var-python hair_color="sample_llm(model='gpt-3.5-turbo')"
--var-python gender="sample_const('male')"
--var-python favorite_band="sample_llm_direct()"
```

Internally all the other options merely delegate to `--var-python`.

You can specify the default set of variables with `--default-var` as a shortcut.

#### Evaluation Order

The order in which the variables are evaluated is determined ~~via a robust algoritm~~ - ~~by a superintelligent god~~ - by GPT-4.

You can hint that some variables ought to be evaluated in a specific order via algorithmic descriptions like `--order "<key1> before <key2>"` or natural language like `--order "please do geography first"`. 

If GPT-4 gives up, or does obvious-enough nonsense, you might get to see an error message. Otherwise, it will output a suggested ordering that is parsed and used.

May the Shoggoth have mercy on our souls.

You can provide all the default hints for the default variables with `--default-order`.

#### Custom Variable Definitions and Python Functions

With `--var-python <key>=<expression>` you can call custom python functions in order to define how a variable is sampled.

Here `expression` must be python code that evaluates to a function (named, lambda, or otherwise) with the following signature:

```python
def sample_custom(var: str, variables: OrderedDict[str, str]) -> List[Tuple[str, float]]:
    """
    :param var: The name of the variable to be sampled
    :param variables: An ordered dictionary with all previously sampled variables
    :return: A non-empty list of value-odds pairs that define a probability distribution over the possible values of the variable
    """
    ...
```

If you write such a function you might want to look at, or call, these functions in `src/variables.py`:

```python
def sample_llm(var, variables, values, model="gpt-4",
    template="templates/prompt_distribution.md"):
    # calls a LLM to define the distribution
    ...

def sample_const(value: str):
    # returns a function that always returns the certain value
    def fn(var, variables, values):
        return [(value, 1.0)]
    return fn

def sample_table(table: str):
    # returns a function that always returns the table as a distribution
    ...
    def fn(var, variables, values):
        return distribution
    return fn

def sample_llm_direct(var, variables, values, model="gpt-4", 
    # calls GPT4 to sample a value directly
    template="templates/prompt_direct.md"):
    ...
    return [(value, 1.0)]
```

# Contribution

## How to Contribute

I am new to this "collaboration" thing. Probably you could open a pull request? If you also link me a how-to-guide for how to review and merge it, that would be great.

If I tell you that I trust you not to manipulate your generated fake-humans, then you can also add them to the repo and make a pull request. The problem here is that I can't verify if your data set is a good (lol) approximation of the distribution of all humans, or if you have stealthily manipulated it.

There may be smart ways to fix this trust-issue, but I don't think they'd be cheap & fast enough for me to bother.

# Q&A

## Your statistical data is inaccurate. You erase minorities from history.

Yes and that is bad (duh!). 

I spent like 1 hour thinking about how to avoid this, and the best idea I came up with was to let the LLMs output distributions instead of also doing the random sampling. Afaict neither LLMs nor 1h!Jörn are smart enough to find e.g. better prompts that make sure that minorities, or unusual corners of human-space in general, aren't overlooked. Mayyybe writing explicit lists is a hot-patch for some minorities, at least those who are on Wikipedia. Or in recorded history at all.

Go and learn about some genocides, if you expect that you'd learn something.

## Your generated human biographies are biased / ahistorical / not very lifelike.

Yes and that is bad (duh!).

Better prompt engineering might help. I neither had the time to do lots of trial-and-error, nor the expertise to immediately see how to do it, nor an LLM that could do either.

I suspect that the RLHFing of GPT-4 biases it towards being this "helpful assistant" persona, and roleplaying as e.g. an uneducated medieval peasant doesn't work that well anymore. Maybe "gpt-3.5-turbo" or some other model might be better for some of the prompts?

## The species homo sapiens doesn't encompass everyone whose death mattered

Agreed.

If I (or you) find time, maybe I will add other members of the homo genus. And some primates.

Maybe also cataceans, proboscidea, magpies, pidgeons, and manta rays. Mayyybe wrasses.

There's a tiny chance I should add pigs. *I don't like that fact*.

If somebody wants to finally build an (automated) successor to Spore, be my guest.

## Newborn babies aren't moral patients

I didn't have time to add support for filter rules. Coding is fast, GPT-4 can do that while I get another coffee. But testing and bug-fixing? Nah, only humans can make screenshots and copy-paste them into ChatGPT!

## This project is cursed.

Sorry, I can't hear you over the *eldritch chants* that I utter in order to slightly increase the chance that our *smiley-faced Shoggoth* will actually *sort the variables in a reasonable order*. 

If you want to uncurse this project, you should solve AI interpretability, or write a good sorting algorithm. You can guess which is easier. I'll probably accept pull-requests for either.

## Are we on track to solve the technical problem of how to align smarter-than-human AI to our own preferences, such that we will not with near-certainty be wiped out by the first emerging superintelligence?

No. This art project tries to give a glimpse into the entirety that is human experience. And it is called 117 billion.