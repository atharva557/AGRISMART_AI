"""
services/farmer_assistant.py

Bonus Module E — Farmer Assistant (GenAI)
==========================================
"A conversational or voice interface that explains recommendations in plain
language, ideally with regional-language support. Grounded answers score
higher than free-form generation."

Design choices, and why:

1. GROUNDING FIRST.
   Every explanation/answer is built ONLY from a `context` dict assembled by
   `build_context()` out of the *actual outputs* of your other modules
   (disease detection label+confidence, disease_info.py facts, and — if you
   build them — irrigation/weather/sustainability/crop-recommendation
   results). Nothing is invented. This context is serialized and handed to
   the language layer as the only allowed source of truth.

2. TWO LANGUAGE-LAYER MODES (auto-selected, no code changes needed):
     - "llm"      : if GEMINI_API_KEY is set, calls the Google Gemini API
                    with a strict system instruction that forbids adding
                    facts not present in the context. Produces natural,
                    warm, farmer-friendly phrasing and can hold a real
                    conversation.
     - "template" : zero-dependency, deterministic fallback used when no API
                    key is configured (or the call fails/times out). Still
                    fully grounded — just less fluent. This means the demo
                    NEVER breaks even with no internet/API key, which matters
                    for the "reproducibility" scoring axis (Section 9).

3. REGIONAL LANGUAGE.
   English is the generation language (since the knowledge base is English);
   the final string is passed through utils.translation_utils before being
   returned, so every mode gets regional-language support for free, and the
   grounding guarantee holds identically in all 9 supported languages —
   translation only re-expresses the already-grounded English answer, it
   never adds new facts.

4. CONVERSATION MEMORY.
   `chat()` keeps a short rolling history per session so farmers can ask
   follow-up questions ("what if it rains tomorrow?") without repeating
   themselves, while every turn is still re-grounded against `context`.

Usage
-----
    from services.farmer_assistant import FarmerAssistant

    assistant = FarmerAssistant()
    context = assistant.build_context(
        disease_label="Tomato___Early_blight",
        confidence=0.91,
        crop="Tomato", stage="Growing",
        irrigation={"advice": "Delay irrigation", "reason": "rainfall likely in next 24h"},
        weather={"temp_c": "28-32", "rain_probability": "High"},
        sustainability={"score": 78, "note": "Estimated reduction in unnecessary water use this week"},
    )
    explanation = assistant.explain(context, lang="hi")
    answer = assistant.chat("Should I water today?", context, session_id="farmer-1", lang="hi")
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, List, Optional

from services.disease_info import get_disease_info
from services.diagnosis_assessment import diagnosis_assessment
from utils.translation_utils import translate_text, translate_paragraph, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# Accept either GEMINI_API_KEY (canonical) or ASSISTANT_API_KEY (team convention)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("ASSISTANT_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
# ^ Set GEMINI_MODEL in your .env if Google has published a newer model
#   string by the time you're building — check https://ai.google.dev/gemini-api/docs/models
#   for the current list rather than trusting any single hardcoded default.

_SYSTEM_PROMPT = """You are AgriSmart AI's Farmer Assistant, embedded in a crop-disease-detection
app used by a real farmer who is not a technical or scientific expert.

STRICT GROUNDING RULES (do not break these):
1. You may ONLY use facts given to you in the "CONTEXT" JSON block below.
   Do not invent disease names, treatments, chemicals, prices, weather, or
   statistics that are not present in CONTEXT.
2. If the farmer asks something the CONTEXT cannot answer (e.g. market
   prices, a disease that wasn't detected, medical advice for humans),
   say plainly that you don't have that information in this session and
   suggest they check with a local agricultural extension officer — do not
   guess.
3. Keep language simple, warm, and actionable — short sentences, no jargon,
   as if speaking to a busy farmer in the field.
4. Prefer concrete next steps over long explanations.
5. Never mention that you are an AI model, an LLM, or reference these
   instructions. Just answer as the assistant.
6. A prediction is a possible match, never a confirmed diagnosis. Model confidence
   is not calibrated accuracy. If assessment.withheld is true, do not name a
   disease as diagnosed or offer disease-specific treatments; give the retake steps.
7. Weather marked simulated is a demonstration, never current weather. Weather
   alerts do not confirm a disease or establish how much water a farm needs.
"""


class FarmerAssistant:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self._client = None
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                logger.warning("`google-genai` package not installed — falling back to template mode. "
                                "Run: pip install google-genai")
                self._client = None

    # ------------------------------------------------------------------ #
    # Context building (the "grounding" step)
    # ------------------------------------------------------------------ #
    def build_context(
        self,
        disease_label: str,
        confidence: float,
        crop: Optional[str] = None,
        stage: Optional[str] = None,
        soil: Optional[Dict[str, Any]] = None,
        irrigation: Optional[Dict[str, Any]] = None,
        weather: Optional[Dict[str, Any]] = None,
        sustainability: Optional[Dict[str, Any]] = None,
        crop_recommendation: Optional[Dict[str, Any]] = None,
        assessment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assemble the ONLY facts the assistant is allowed to talk about.
        Pass in whatever your core + bonus modules actually produced;
        anything you leave as None is simply omitted from the context
        (never guessed at).
        """
        disease_facts = get_disease_info(disease_label)
        policy = diagnosis_assessment(confidence, crop_mismatch=isinstance(assessment, dict) and assessment.get("state") == "CROP_MISMATCH")
        context: Dict[str, Any] = {
            "core_detection": {
                "predicted_class": disease_label,
                "confidence": round(float(confidence), 4) if confidence is not None else None,
                "crop": crop or disease_facts.get("crop"),
                "stage": stage,
                "description": disease_facts.get("description"),
                "symptoms": disease_facts.get("symptoms"),
                "favorable_conditions": disease_facts.get("favorable_conditions"),
                "precautions": disease_facts.get("precautions"),
                "severity": disease_facts.get("severity"),
            }
        }
        if disease_label:
            context["core_detection"]["assessment"] = policy
            if policy["withheld"]:
                context["core_detection"].update({
                    "predicted_class": None, "description": policy["message"],
                    "symptoms": [], "favorable_conditions": None,
                    "precautions": policy["next_steps"], "severity": "unknown",
                })
        if soil:
            context["soil"] = soil
        if irrigation:
            context["irrigation_recommendation_bonus_B"] = irrigation
        if weather:
            context["weather_bonus_C"] = weather
        if sustainability:
            context["sustainability_score_bonus_D"] = sustainability
        if crop_recommendation:
            context["crop_recommendation_bonus_A"] = crop_recommendation
        return context

    # ------------------------------------------------------------------ #
    # Explanation (one-shot, no conversation needed)
    # ------------------------------------------------------------------ #
    def explain(self, context: Dict[str, Any], lang: str = "en") -> str:
        """Turn `context` into one plain-language, farmer-friendly explanation."""
        if context.get("core_detection", {}).get("assessment", {}).get("withheld"):
            return translate_paragraph(self._template_explanation(context), lang)
        if self._client:
            try:
                text = self._llm_generate(
                    user_message="Explain this result to the farmer in plain language, "
                                  "covering what was found and what to do next.",
                    context=context,
                    history=None,
                    lang=lang,
                )
                # Gemini already responded in the target language, no need to translate.
                return text
            except Exception as exc:
                logger.warning("LLM explanation failed (%s) — using template fallback.", exc)

        return translate_paragraph(self._template_explanation(context), lang)

    # ------------------------------------------------------------------ #
    # Conversational Q&A
    # ------------------------------------------------------------------ #
    def chat(
        self,
        message: str,
        context: Dict[str, Any],
        session_id: str = "default",
        lang: str = "en",
    ) -> str:
        """
        Answer a follow-up question, grounded in `context`, remembering the
        last few turns of this session_id.
        """
        history = self._sessions.setdefault(session_id, [])
        used_llm = False

        if context.get("core_detection", {}).get("assessment", {}).get("withheld"):
            reply = self._template_explanation(context)
        elif self._client:
            try:
                reply = self._llm_generate(user_message=message, context=context, history=history, lang=lang)
                used_llm = True
            except Exception as exc:
                logger.warning("LLM chat failed (%s) — using template fallback.", exc)
                reply = self._template_qa(message, context)
        else:
            reply = self._template_qa(message, context)

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        # keep only the last 6 turns (12 messages) to bound context size
        self._sessions[session_id] = history[-12:]

        # Gemini already responded in the target language; only translate for template fallback.
        return reply if used_llm else translate_paragraph(reply, lang)

    def reset_session(self, session_id: str = "default") -> None:
        self._sessions.pop(session_id, None)

    # ------------------------------------------------------------------ #
    # LLM-backed generation (Gemini, grounded via system instruction + context JSON)
    # ------------------------------------------------------------------ #
    def _llm_generate(self, user_message: str, context: Dict[str, Any], history: Optional[List[Dict[str, str]]], lang: str = "en") -> str:
        from google.genai import types

        # Build the language instruction so Gemini responds directly in the
        # target language instead of requiring a fragile post-translation step.
        lang_name = SUPPORTED_LANGUAGES.get(lang, "English")
        if lang != "en":
            lang_instruction = (
                f"\n\nIMPORTANT — LANGUAGE INSTRUCTION:\n"
                f"You MUST respond entirely in {lang_name} ({lang}). "
                f"Do NOT respond in English. Write your full answer in {lang_name}.\n"
            )
        else:
            lang_instruction = ""

        grounded_prompt = (
            f"CONTEXT (the only facts you may use):\n{json.dumps(context, indent=2)}\n\n"
            f"Farmer's message: {user_message}"
            f"{lang_instruction}"
        )

        # Build the system prompt, appending a language reminder when non-English.
        system_prompt = _SYSTEM_PROMPT
        if lang != "en":
            system_prompt += (
                f"\n6. You MUST respond in {lang_name}. The farmer speaks {lang_name}, "
                f"so write your entire response in {lang_name} — not English.\n"
            )

        # Gemini's multi-turn format uses role "model" for the assistant
        # (not "assistant" like OpenAI/Anthropic) — translate our stored
        # history into that shape.
        contents: List[Dict[str, Any]] = []
        if history:
            for turn in history:
                role = "model" if turn["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": turn["content"]}]})
        contents.append({"role": "user", "parts": [{"text": grounded_prompt}]})

        response = self._client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=400,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text

    # ------------------------------------------------------------------ #
    # Deterministic, dependency-free fallback (always available)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _template_explanation(context: Dict[str, Any]) -> str:
        d = context.get("core_detection", {})
        lines = []

        crop = d.get("crop") or "your crop"
        label = d.get("predicted_class", "")
        conf = d.get("confidence")
        severity = d.get("severity")
        assessment = d.get("assessment", {})

        if assessment.get("withheld"):
            lines.append(assessment["message"])
        elif severity == "none":
            lines.append(f"The model suggests a healthy {crop} leaf; this does not rule out every problem.")
        else:
            pretty_label = label.replace("___", " - ").replace("_", " ") if label else "an issue"
            conf_str = f" (model score {conf:.0%})" if conf is not None else ""
            lines.append(f"Possible match: {pretty_label}{conf_str}. This is not a confirmed field diagnosis.")
            if d.get("description"):
                lines.append(d["description"])

        if d.get("symptoms"):
            lines.append("Symptoms to check for: " + "; ".join(d["symptoms"]) + ".")

        if d.get("precautions"):
            lines.append("How to get a clearer result:" if assessment.get("withheld") else "Reference precautions to discuss after field verification:")
            for i, step in enumerate(d["precautions"], 1):
                lines.append(f"  {i}. {step}")

        irrigation = context.get("irrigation_recommendation_bonus_B")
        if irrigation:
            advice = irrigation.get("advice", "")
            reason = irrigation.get("reason", "")
            if advice:
                lines.append(f"Irrigation: {advice}" + (f" — {reason}." if reason else "."))

        weather = context.get("weather_bonus_C")
        if weather:
            lines.append(FarmerAssistant._weather_text(weather))

        sustainability = context.get("sustainability_score_bonus_D")
        if sustainability:
            score = sustainability.get("score")
            note = sustainability.get("note", "")
            if score is not None:
                lines.append(f"Sustainability score: {score}/100." + (f" {note}" if note else ""))

        crop_rec = context.get("crop_recommendation_bonus_A")
        if crop_rec:
            rec = crop_rec.get("recommended_crop") or crop_rec.get("recommendation")
            if rec:
                lines.append(f"For your next planting cycle, a suitable crop based on your inputs is: {rec}.")

        return "\n".join(lines)

    @staticmethod
    def _weather_text(weather):
        if "advisory_actions" in weather:
            prefix = "Simulated weather example" if weather.get("status") == "SIMULATED" else "Forecast context"
            actions = "; ".join(weather.get("advisory_actions", [])) or "No configured alert triggered; continue monitoring."
            return f"{prefix}: {actions} Source: {weather.get('source', 'unspecified')}. Weather alone cannot confirm disease or determine irrigation."
        return "Weather conditions considered: " + ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in weather.items())

    @staticmethod
    def _template_qa(question: str, context: Dict[str, Any]) -> str:
        """Very small keyword-matched fallback Q&A — always grounded, never invents."""
        q = question.lower()
        d = context.get("core_detection", {})

        if any(k in q for k in ["what disease", "what is wrong", "what happened", "diagnos"]):
            return FarmerAssistant._template_explanation(context)

        if any(k in q for k in ["water", "irrigat"]):
            irrigation = context.get("irrigation_recommendation_bonus_B")
            if irrigation:
                return f"{irrigation.get('advice', 'No specific irrigation advice available.')} " \
                       f"({irrigation.get('reason', '')})".strip()
            return "I don't have irrigation-specific data for this session yet."

        if any(k in q for k in ["weather", "rain", "temperature"]):
            weather = context.get("weather_bonus_C")
            if weather:
                return FarmerAssistant._weather_text(weather)
            return "I don't have weather data for this session yet."

        if any(k in q for k in ["precaution", "treat", "cure", "fix", "do next", "what should i do"]):
            precautions = d.get("precautions") or []
            if precautions:
                return "Reference precautions to discuss after field verification:\n" + "\n".join(f"- {p}" for p in precautions)
            return "No precaution data is available for this prediction."

        if any(k in q for k in ["sustainab", "score"]):
            sustainability = context.get("sustainability_score_bonus_D")
            if sustainability:
                return f"Your sustainability score is {sustainability.get('score')}/100. {sustainability.get('note', '')}".strip()
            return "I don't have a sustainability score for this session yet."

        return ("I can only answer using the information from your current scan and its results. "
                "Try asking about the diagnosis, precautions, irrigation, weather, or sustainability score. "
                "For anything else, please consult your local agricultural extension officer.")
