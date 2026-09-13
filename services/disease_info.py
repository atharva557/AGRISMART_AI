"""
services/disease_info.py

Static, curated knowledge base for the shared class list (Section 4.1 of the
problem statement). This is the SINGLE SOURCE OF TRUTH the Farmer Assistant
(Bonus E) is grounded against — the LLM/template layer is never allowed to
invent facts that aren't here. Extend this dict if your organizers publish a
different / longer final class list; keep the label strings identical to
whatever `predict.py` returns so lookups never miss.

Each entry:
    description         : one-line, farmer-facing description of the disease
    symptoms             : short list of visible symptoms
    favorable_conditions  : what makes the disease spread/appear
    precautions          : actionable, low-cost steps a farmer can take now
    severity             : "low" | "moderate" | "high" (rough triage signal)
"""

from typing import Dict, Any

DISEASE_KB: Dict[str, Dict[str, Any]] = {
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "description": "A fungal disease causing dark concentric 'target-board' spots on older leaves.",
        "symptoms": ["Brown/black concentric ring spots on lower leaves", "Yellowing around spots", "Leaf drop starting from the bottom"],
        "favorable_conditions": ["Warm, humid weather", "Overhead irrigation", "Dense planting / poor airflow"],
        "precautions": [
            "Remove and destroy affected leaves immediately.",
            "Avoid overhead watering; water at the base early in the day.",
            "Apply a recommended fungicide (e.g. copper-based or chlorothalonil) if spread continues.",
            "Rotate with a non-solanaceous crop next season.",
        ],
        "severity": "moderate",
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "description": "A fast-spreading fungal-like (oomycete) disease that can destroy a crop within days in cool, wet weather.",
        "symptoms": ["Irregular water-soaked patches on leaves", "White fuzzy growth on leaf undersides in humid conditions", "Rapid blackening of stems and fruit"],
        "favorable_conditions": ["Cool nights, warm humid days", "Prolonged leaf wetness", "Poor field drainage"],
        "precautions": [
            "Remove and destroy infected plants immediately — do not compost them.",
            "Apply a protectant fungicide as soon as symptoms are seen; this disease spreads very fast.",
            "Improve drainage and spacing to reduce leaf wetness duration.",
            "Avoid working in the field when foliage is wet, to prevent spreading spores.",
        ],
        "severity": "high",
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "description": "A fungal disease common in humid, poorly ventilated conditions (greenhouses especially).",
        "symptoms": ["Pale green/yellow patches on upper leaf surface", "Olive-green to grey mold on the underside"],
        "favorable_conditions": ["High humidity (>85%)", "Poor ventilation", "Leaf wetness"],
        "precautions": [
            "Improve ventilation and reduce humidity around plants.",
            "Space plants to improve airflow; prune dense foliage.",
            "Remove infected leaves and avoid overhead watering.",
        ],
        "severity": "moderate",
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "description": "A bacterial disease producing small, dark, greasy-looking spots on leaves and fruit.",
        "symptoms": ["Small dark water-soaked spots with yellow halo", "Spots on fruit are raised and scab-like"],
        "favorable_conditions": ["Warm, wet, humid weather", "Overhead irrigation", "Contaminated seed/tools"],
        "precautions": [
            "Use certified disease-free seed/seedlings next season.",
            "Avoid working with wet plants; disinfect tools between plants.",
            "Apply copper-based bactericide early if pressure is high.",
        ],
        "severity": "moderate",
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "description": "A fungal disease causing target-spot lesions, mainly on older leaves.",
        "symptoms": ["Dark concentric-ring spots on lower/older leaves", "Yellowing and premature leaf drop"],
        "favorable_conditions": ["Warm temperatures", "Alternating wet/dry periods", "Plant stress or low nitrogen"],
        "precautions": [
            "Remove and destroy heavily infected foliage.",
            "Maintain balanced fertilization — nitrogen-stressed plants are more susceptible.",
            "Apply a labelled fungicide if the disease is spreading past a few leaves.",
        ],
        "severity": "moderate",
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "description": "The same aggressive disease responsible for historic potato famines — spreads extremely fast in cool wet weather.",
        "symptoms": ["Dark water-soaked lesions on leaves", "White mold ring on the underside in humid mornings", "Rapid collapse of foliage"],
        "favorable_conditions": ["Cool, wet weather", "High humidity", "Infected seed tubers"],
        "precautions": [
            "Destroy infected plants and any nearby volunteer plants immediately.",
            "Apply a protectant fungicide preventively if the forecast is cool and wet.",
            "Never plant tubers showing any sign of blight.",
        ],
        "severity": "high",
    },
    "Corn___Common_rust": {
        "crop": "Corn (Maize)",
        "description": "A fungal disease producing reddish-brown pustules on leaves.",
        "symptoms": ["Small reddish-brown raised pustules on both leaf surfaces", "Pustules turn dark brown/black as they mature"],
        "favorable_conditions": ["Cool temperatures (16–25°C)", "High humidity or dew", "Extended leaf wetness"],
        "precautions": [
            "Plant rust-resistant hybrids where available.",
            "Fungicide is rarely needed unless infection is severe and the crop is young.",
            "Monitor regularly during cool, humid weeks.",
        ],
        "severity": "low",
    },
    "Corn___Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "description": "A fungal disease producing rectangular grey-tan lesions that can merge and kill leaf tissue.",
        "symptoms": ["Rectangular, grey to tan lesions bound by leaf veins", "Lesions merge in severe cases, killing large leaf areas"],
        "favorable_conditions": ["Warm, humid weather", "Continuous corn cropping (no rotation)", "Reduced tillage leaving infected residue"],
        "precautions": [
            "Rotate with a non-host crop.",
            "Manage crop residue (tillage) to reduce carryover spores.",
            "Use resistant hybrids; apply fungicide if disease appears before tasseling on a susceptible variety.",
        ],
        "severity": "moderate",
    },
    "Apple___Apple_scab": {
        "crop": "Apple",
        "description": "A fungal disease causing olive-green to black scabby lesions on leaves and fruit.",
        "symptoms": ["Olive-green velvety spots on leaves", "Dark scabby, corky lesions on fruit"],
        "favorable_conditions": ["Cool, wet spring weather", "Extended leaf wetness after rain"],
        "precautions": [
            "Rake and destroy fallen leaves in autumn to reduce overwintering spores.",
            "Apply protectant fungicide from bud break through wet spring weather.",
            "Prune to improve airflow and speed leaf drying.",
        ],
        "severity": "moderate",
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "description": "A fungal disease causing leaf spots, fruit rot, and cankers on branches.",
        "symptoms": ["Purple-bordered leaf spots ('frog-eye')", "Rotting fruit with concentric rings", "Sunken bark cankers"],
        "favorable_conditions": ["Warm, wet weather", "Dead wood/cankers left in the orchard", "Wounded or stressed trees"],
        "precautions": [
            "Prune out and destroy cankered/dead wood.",
            "Remove mummified fruit from the tree and ground.",
            "Apply fungicide during bloom and early fruit development if pressure is high.",
        ],
        "severity": "moderate",
    },
    "Grape___Black_rot": {
        "crop": "Grape",
        "description": "A fungal disease causing leaf spots and shriveled, mummified berries.",
        "symptoms": ["Small tan spots with dark borders on leaves", "Berries shrivel into hard black mummies"],
        "favorable_conditions": ["Warm, wet weather during early season", "Overwintering mummies/canes left in vineyard"],
        "precautions": [
            "Remove mummified berries and infected canes during dormant pruning.",
            "Improve canopy airflow (leaf pulling) to speed drying.",
            "Apply fungicide from bud break through berry set if disease has occurred before.",
        ],
        "severity": "moderate",
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "description": "A bacterial disease causing dark, water-soaked spots on leaves and raised scabs on fruit.",
        "symptoms": ["Small dark water-soaked leaf spots with yellow halo", "Raised, rough scabby spots on fruit"],
        "favorable_conditions": ["Warm, wet, humid weather", "Overhead irrigation or wind-driven rain", "Contaminated seed"],
        "precautions": [
            "Use certified disease-free seed/transplants.",
            "Avoid overhead irrigation; do not work fields when leaves are wet.",
            "Apply copper-based bactericide early if pressure is high.",
        ],
        "severity": "moderate",
    },
}

# Generic entry used whenever the model predicts a "healthy" class for any crop,
# or a crop/class not explicitly listed above (keeps the assistant grounded —
# it will say "no data for this class" rather than invent something).
HEALTHY_INFO = {
    "description": "No disease detected — the leaf appears healthy.",
    "symptoms": [],
    "favorable_conditions": [],
    "precautions": [
        "Continue regular monitoring, especially after rain or high-humidity spells.",
        "Maintain balanced irrigation and fertilization.",
    ],
    "severity": "none",
}


def get_disease_info(label: str) -> Dict[str, Any]:
    """
    Look up grounded facts for a predicted class label.
    Falls back to a clearly-marked 'unknown' entry rather than fabricating
    information — the assistant layer must respect this and say so.
    """
    if label is None:
        return {"description": "No prediction available.", "symptoms": [], "favorable_conditions": [], "precautions": [], "severity": "unknown"}

    if "healthy" in label.lower():
        info = dict(HEALTHY_INFO)
        info["crop"] = label.split("___")[0].replace("_", " ") if "___" in label else label
        return info

    if label in DISEASE_KB:
        return DISEASE_KB[label]

    # Unknown class — be honest instead of hallucinating.
    return {
        "crop": label.split("___")[0].replace("_", " ") if "___" in label else "Unknown",
        "description": f"No curated information available yet for '{label}'.",
        "symptoms": [],
        "favorable_conditions": [],
        "precautions": ["Consult a local agricultural extension officer for guidance on this specific class."],
        "severity": "unknown",
    }
