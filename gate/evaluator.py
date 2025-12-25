"""
Prompt evaluation using UQLM uncertainty quantification.
"""
from uqlm import BlackBoxUQ
from langchain.chat_models import ChatOpenAI
import os


# Initialize LLM for generating candidate responses
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Initialize UQLM uncertainty quantifier
uq = BlackBoxUQ(
    llm=llm,
    scorers=["semantic_negentropy"],
    use_best=True,
)


async def evaluate_prompt(prompt: str, num_samples: int) -> float:
    """
    Evaluate prompt stability by generating multiple responses
    and measuring their agreement using UQLM.
    
    Args:
        prompt: The prompt to evaluate
        num_samples: Number of responses to generate
        
    Returns:
        float: Confidence score between 0 and 1
               Higher scores indicate more stable/consistent outputs
        
    Raises:
        Exception: If UQLM evaluation fails
        
    Example:
        >>> confidence = await evaluate_prompt("What is 2+2?", 5)
        >>> print(confidence)
        0.95  # High confidence - consistent outputs
    """
    try:
        # Generate multiple responses and score agreement
        results = await uq.generate_and_score(
            prompts=[prompt],
            num_responses=num_samples,
        )

        # Extract confidence score from results
        df = results.to_df()
        confidence = float(df["confidence_score"].iloc[0])
        
        return confidence
        
    except Exception as e:
        raise Exception(f"UQLM evaluation failed: {str(e)}")
