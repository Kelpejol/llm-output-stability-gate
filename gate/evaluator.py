from uqlm import BlackBoxUQ
from langchain.chat_models import ChatOpenAI
import os

# LLM used only to generate candidate responses
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# UQLM uncertainty quantifier
uq = BlackBoxUQ(
    llm=llm,
    scorers=["semantic_negentropy"],
    use_best=True,
)

async def evaluate_prompt(prompt: str, num_samples: int) -> float:
    """
    Generates multiple responses and returns
    a confidence score between 0 and 1.
    """
    results = await uq.generate_and_score(
        prompts=[prompt],
        num_responses=num_samples,
    )

    df = results.to_df()

    # UQLM returns one row per prompt
    confidence = float(df["confidence_score"].iloc[0])
    return confidence
