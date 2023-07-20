import re
import openai

from env import OPEN_AI_API_KEY
from logger import get_logger

from .base import Filter

logger = get_logger("gpt_filter")


MODEL_ID = "gpt-3.5-turbo"

# limit is 4096 tokens, but we will use 3500 to be safe
TOKEN_LIMIT = 3500


class MakeAIDoTheFiltering(Filter):
    """Leverages GPT-3 to to check if a line is a category or not. This honestly doesn't work very well, but it's a cool idea.

    Args:
        conf_threshold (float, optional): The maximum treshold for a line to be considered a processed using GPT-3, reducing this value will use less tokens.
        Defaults to 1.
    """

    conf_threshold: float

    def __init__(self, weight: float, conf_threshold: float = 1):
        if OPEN_AI_API_KEY:
            openai.api_key = OPEN_AI_API_KEY
        else:
            logger.warning("OPEN_AI_API_KEY not set, GPT-3 will not work")

        self.weight = weight
        self.conf_threshold = conf_threshold

    def apply(self, lines):
        if not OPEN_AI_API_KEY:
            logger.warning(
                "OPEN_AI_API_KEY not set, the AI based filter will be skipped"
            )
            return
        logger.debug("Applying GPT-3 filter")

        re_get_probabilities = re.compile(r"\d+: \d{1,3}")

        base_prompt = """Classify restaurant menu strings as probable (100) or improbable (0) menu categories. 'Polevky', 'Wafle', 'Vino' are examples of categories, while specific items or prices aren't. Output should follow \\d+: \\d{1,3} format, with the first number being the ID and the second the category likelihood percentage.

        Example input:
        0: Soups
        1: Wafle
        2: Wafle s grilovanou slaninou
        3: 5.99,-
        4: Hot drinks
        Example output based on the above input:
        0: 99
        1: 75
        2: 15
        3: 01
        4: 95

        provide a similar output for the following all of the following lines:
        """
        id = 0
        while id < len(lines):
            prompt = base_prompt + "\n\n"

            for i in range(id, len(lines)):
                id += 1
                line = lines[i]
                # no reason to use up tokens on lines that are already filtered out
                if line.analysis.category_confidence < self.conf_threshold:
                    continue

                prompt += f"\n{i}: {line.text}"

                #  1 token is approximately 4 characters (see: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
                if len(prompt) / 4 > TOKEN_LIMIT:
                    break

            logger.info(
                f"Sending approximately {len(prompt) / 4} tokens to GPT-3, this may take a while"
            )
            response = openai.ChatCompletion.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response["choices"][0]["message"]["content"]  # type: ignore

            probabilities = re_get_probabilities.findall(content)

            for p in probabilities:
                index, probability = p.split(": ")
                index = int(index)
                probability = float(probability)
                # calculate the confidence modifier based on the probability, and scale it's effect based on the weight
                confidence_multiplier = 1 - (1 - probability) * self.weight

                old_confidence = lines[index].analysis.category_confidence
                lines[index].analysis.category_confidence *= confidence_multiplier
                new_confidence = lines[index].analysis.category_confidence

                # logger.debug(f"'{lines[index].text}'\n\t{probability=}, {self.weight=}, {confidence_multiplier=}\n\t{old_confidence}->{new_confidence}")
