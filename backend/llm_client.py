"""
llm_client.py — Centralized LLM call handler for Prompt2Plan
Tries Groq API first, falls back to Hugging Face Inference API.
All pipeline modules use this instead of making direct API calls.
"""
import os
import json
import logging
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Groq client (primary)
# --------------------------------------------------------------------------- #
_groq_client = None

def _get_groq_client():
    """Lazily initialize the Groq client."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY not set — Groq calls will be skipped")
        return None

    try:
        from groq import Groq
        _groq_client = Groq(api_key=api_key)
        logger.info("Groq client initialized successfully")
        return _groq_client
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None


# --------------------------------------------------------------------------- #
#  Hugging Face client (fallback)
# --------------------------------------------------------------------------- #
_hf_client = None

def _get_hf_client():
    """Lazily initialize the HF Inference client."""
    global _hf_client
    if _hf_client is not None:
        return _hf_client

    try:
        from huggingface_hub import InferenceClient
        token = os.environ.get("HF_TOKEN", None)
        _hf_client = InferenceClient(token=token if token else None)
        logger.info("Hugging Face Inference client initialized")
        return _hf_client
    except Exception as e:
        logger.error(f"Failed to initialize HF client: {e}")
        return None


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #

GROQ_MODEL = "llama-3.3-70b-versatile"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True,
    max_retries: int = 1,
) -> str:
    """
    Call an LLM with fallback chain: Groq → Hugging Face.

    Args:
        system_prompt: The system-level instruction.
        user_prompt:   The user-level content.
        json_mode:     If True, appends "Return ONLY valid JSON" to system prompt.
        max_retries:   Number of retries per provider on failure.

    Returns:
        The LLM's response text (should be valid JSON if json_mode=True).

    Raises:
        RuntimeError if all providers fail.
    """
    if json_mode:
        system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown fences, no explanation, no extra text."

    # --- Try Groq first ---
    groq_result = await _try_groq(system_prompt, user_prompt, max_retries)
    if groq_result is not None:
        return groq_result

    # --- Fall back to Hugging Face ---
    hf_result = await _try_hf(system_prompt, user_prompt, max_retries)
    if hf_result is not None:
        return hf_result

    raise RuntimeError("All LLM providers failed. Cannot generate response.")


async def _try_groq(system_prompt: str, user_prompt: str, max_retries: int) -> str | None:
    """Attempt to call the Groq API."""
    client = _get_groq_client()
    if client is None:
        return None

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            content = response.choices[0].message.content.strip()
            # Strip markdown fences if the model wraps JSON in ```json ... ```
            content = _strip_markdown_fences(content)
            logger.info(f"Groq call succeeded (attempt {attempt + 1})")
            return content

        except Exception as e:
            logger.warning(f"Groq attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                logger.error("Groq exhausted all retries")
                return None

    return None


async def _try_hf(system_prompt: str, user_prompt: str, max_retries: int) -> str | None:
    """Attempt to call the Hugging Face Inference API."""
    client = _get_hf_client()
    if client is None:
        return None

    combined_prompt = f"[INST] {system_prompt}\n\n{user_prompt} [/INST]"

    for attempt in range(max_retries + 1):
        try:
            response = client.text_generation(
                combined_prompt,
                model=HF_MODEL,
                max_new_tokens=4096,
                temperature=0.3,
            )
            content = response.strip()
            content = _strip_markdown_fences(content)
            logger.info(f"HF call succeeded (attempt {attempt + 1})")
            return content

        except Exception as e:
            logger.warning(f"HF attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                logger.error("Hugging Face exhausted all retries")
                return None

    return None


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers that LLMs sometimes add."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (possibly with language tag)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3].strip()
    return text


def parse_json_response(text: str) -> dict | list:
    """
    Parse a JSON response from an LLM, handling common formatting issues.
    Raises ValueError if parsing fails.
    """
    text = _strip_markdown_fences(text)

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object or array in the text
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}...")
