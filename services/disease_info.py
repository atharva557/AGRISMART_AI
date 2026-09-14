"""
services/disease_info.py

Static, curated knowledge base for the 38 crop pathology classes.
This is the SINGLE SOURCE OF TRUTH the Farmer Assistant (Bonus E) and
diagnostic endpoints are grounded against.
"""

from typing import Dict, Any

DISEASE_KB: Dict[str, Dict[str, Any]] = {
    # ── Apple ────────────────────────────────────────────────────────
    "Apple___Apple_scab": {
        "crop": "Apple",
        "description": "A fungal disease caused by Venturia inaequalis producing olive-green to black scabby lesions on leaves and fruit.",
        "symptoms": ["Olive-green to dark velvety spots on leaves", "Distorted, puckered foliage", "Dark scabby lesions on fruit surface"],
        "favorable_conditions": ["Cool, wet spring weather (15–24°C)", "Prolonged leaf wetness after rain"],
        "precautions": [
            "Rake, chop, or destroy fallen leaves in autumn to eliminate overwintering fungal spores.",
            "Apply protectant fungicides (captan, mancozeb, or sulfur) from green tip stage through petal fall.",
            "Prune tree canopy during dormancy to maximize air circulation and accelerate drying.",
        ],
        "severity": "moderate",
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "description": "A fungal pathogen (Botryosphaeria obtusa) causing frog-eye leaf spots, limb cankers, and fruit rot.",
        "symptoms": ["Small purple spots on leaves that enlarge with tan centers ('frog-eye')", "Rotting fruit with dark concentric rings", "Sunken, reddish-brown bark cankers"],
        "favorable_conditions": ["Warm, humid conditions (20–28°C)", "Dead wood or cankers remaining in the orchard", "Wounded fruit or branches"],
        "precautions": [
            "Prune out and destroy cankered limbs, dead wood, and fire-blight strikes.",
            "Remove and discard all mummified apples clinging to branches or on the ground.",
            "Apply labelled fungicides beginning at petal fall and continuing during early fruit development.",
        ],
        "severity": "moderate",
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "description": "A heteroecious rust fungus (Gymnosporangium juniperi-virginianae) requiring Eastern red cedar or juniper alternate hosts.",
        "symptoms": ["Bright yellow-orange or reddish spots on upper leaf surfaces", "Small tube-like fungal projections (aecia) on leaf undersides", "Premature defoliation in severe cases"],
        "favorable_conditions": ["Warm, wet spring weather", "Presence of nearby juniper or red cedar trees within 1–2 miles"],
        "precautions": [
            "Remove nearby eastern red cedar and juniper trees within orchard vicinity if feasible.",
            "Plant rust-resistant apple cultivars (e.g., Enterprise, Freedom, Liberty).",
            "Apply preventive rust-labelled fungicides (e.g., myclobutanil) between pink bud and petal fall.",
        ],
        "severity": "low",
    },

    # ── Cherry ───────────────────────────────────────────────────────
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "description": "A fungal disease caused by Podosphaera clandestina affecting leaves, green shoots, and young fruit.",
        "symptoms": ["White, powdery fungal patches on leaf undersides and tips", "Upward leaf curling and distortion", "Stunted terminal shoot growth"],
        "favorable_conditions": ["High relative humidity with warm temperatures (15–27°C)", "Shaded, dense canopies with limited air movement"],
        "precautions": [
            "Prune dense canopy water sprouts to improve air movement and light penetration.",
            "Apply registered fungicides or horticultural oils at petal fall and during early fruit sizing.",
            "Avoid excessive late-season nitrogen fertilization which stimulates vulnerable young flush.",
        ],
        "severity": "moderate",
    },

    # ── Corn (Maize) ─────────────────────────────────────────────────
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "description": "A prevalent fungal foliar disease caused by Cercospora zeae-maydis causing rectangular tan lesions bounded by veins.",
        "symptoms": ["Rectangular, narrow grey-to-tan lesions strictly parallel with leaf veins", "Lesions merge under high pressure causing extensive foliar blight", "Premature stalk lodging"],
        "favorable_conditions": ["Warm, humid conditions (>25°C with >90% RH)", "Continuous corn monoculture with zero or reduced tillage leaving residue"],
        "precautions": [
            "Rotate fields with non-host crops (soybeans, legumes) for at least one season.",
            "Utilize certified hybrid corn varieties with strong gray leaf spot resistance ratings.",
            "Consider foliar fungicide application between tasseling (VT) and silking (R1) if economic threshold is reached.",
        ],
        "severity": "moderate",
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "description": "A fungal disease caused by Puccinia sorghi producing small, elevated reddish-brown pustules on both leaf surfaces.",
        "symptoms": ["Small, oval to elongate cinnamon-brown pustules on upper and lower leaf surfaces", "Pustules rupture epidermal tissue releasing powdery spores", "Pustules turn dark brownish-black late season"],
        "favorable_conditions": ["Moderate temperatures (16–25°C)", "High relative humidity (>95%) and extended nocturnal dew periods"],
        "precautions": [
            "Plant corn hybrids containing specific Rp gene resistance.",
            "Fungicide intervention is rarely warranted on commercial dent corn unless infection occurs before tasseling.",
            "Monitor fields early in vegetative development during unusually cool, damp seasons.",
        ],
        "severity": "low",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "description": "A damaging fungal foliar disease caused by Setosphaeria turcica producing long, elliptical 'cigar-shaped' grey-green lesions.",
        "symptoms": ["Long (2.5–15 cm) elliptical, cigar-shaped grey-green to tan lesions", "Lesions start on lower leaves and progress upward", "Dark sporulation visible on lesions during damp mornings"],
        "favorable_conditions": ["Moderate temperatures (18–27°C)", "Extended wet foliage periods (6–18 hours of rain or heavy dew)"],
        "precautions": [
            "Select resistant corn hybrids with polygenic and race-specific Ht gene resistance.",
            "Incorporate crop residue with conservation tillage to accelerate decomposition of infected debris.",
            "Apply approved strobilurin/triazole fungicide mixtures if lesions appear on the ear leaf before blister stage (R2).",
        ],
        "severity": "high",
    },

    # ── Grape ────────────────────────────────────────────────────────
    "Grape___Black_rot": {
        "crop": "Grape",
        "description": "A destructive fungal pathogen (Guignardia bidwellii) attacking all green vine tissues, turning berries into hard black mummies.",
        "symptoms": ["Small circular reddish-brown leaf spots with tiny black fruiting bodies", "Sunken purple lesions on shoots", "Berries turn brown, then shrivel into hard, black, wrinkled mummies"],
        "favorable_conditions": ["Warm, humid conditions (21–32°C)", "Rainfall events with 6+ hours of continuous canopy wetness"],
        "precautions": [
            "Thoroughly remove and destroy all mummified berries from vines and the vineyard floor during dormant pruning.",
            "Perform canopy management (shoot thinning, leaf pulling) around fruit clusters to speed drying.",
            "Apply protectant fungicides starting from 1-inch shoot growth through 4–5 weeks post-bloom.",
        ],
        "severity": "high",
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "description": "A complex fungal trunk disease involving Phaeomoniella and Fomitiporia causing distinctive 'tiger-stripe' leaf necrosis and berry measles.",
        "symptoms": ["Interveinal yellow/red discoloration progressing to necrotic 'tiger-stripe' patterns on leaves", "Small dark purple spots ('measles') on berry skins", "Sudden vine apoplexy (wilting and collapse) during hot dry spells"],
        "favorable_conditions": ["Vine stress following hot periods", "Mature vineyards (>8–10 years old)", "Pruning wounds exposed to rain and fungal spores"],
        "precautions": [
            "Protect pruning wounds immediately with sealants, paints, or biocontrol agents (e.g., Trichoderma).",
            "Delay pruning until late dormant season when wound healing is most rapid.",
            "Mark symptomatic vines and prune them last to avoid spreading wood pathogens with shears.",
        ],
        "severity": "high",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "description": "A late-season fungal foliar infection caused by Pseudocercospora cladosporioides causing irregular brown necrotic leaf blotches.",
        "symptoms": ["Irregularly shaped dark brown spots with defined halos on older leaves", "Premature yellowing and leaf senescence starting near cane bases", "Reduced sugar accumulation in fruit due to foliar loss"],
        "favorable_conditions": ["Warm, humid post-harvest or late summer conditions", "High canopy density and poor air circulation"],
        "precautions": [
            "Maintain balanced canopy aeration via selective post-bloom leaf removal.",
            "Apply copper-based or dithiocarbamate fungicides if early defoliation threatens vine reserves.",
            "Maintain vine vigor without excessive late nitrogen fertilizer.",
        ],
        "severity": "moderate",
    },

    # ── Citrus / Orange ──────────────────────────────────────────────
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange / Citrus",
        "description": "Huanglongbing (HLB / Citrus Greening), a fatal bacterial infection (Candidatus Liberibacter asiaticus) vectored by the Asian Citrus Psyllid.",
        "symptoms": ["Asymmetric, blotchy yellow mottling across leaf veins", "Yellow shoot flushes ('yellow dragon')", "Small, lopsided fruit with bitter, sour flavor and aborted seeds", "Severe dieback and tree decline"],
        "favorable_conditions": ["Active populations of Asian citrus psyllid (Diaphorina citri)", "Warm subtropical climates (20–30°C)"],
        "precautions": [
            "Aggressively manage Asian Citrus Psyllid populations using registered insecticides and biocontrols.",
            "Plant only certified disease-free citrus nursery stock in clean, protected screenhouses.",
            "Remove and destroy PCR-confirmed HLB-infected trees immediately to reduce inoculum reservoirs.",
            "Provide foliar micronutrient sprays (zinc, manganese, iron) to support root and canopy health.",
        ],
        "severity": "high",
    },

    # ── Peach ────────────────────────────────────────────────────────
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "description": "A bacterial pathogen (Xanthomonas arboricola pv. pruni) causing angular leaf lesions, 'shot-hole' perforation, and sunken fruit spots.",
        "symptoms": ["Small, water-soaked angular leaf spots that turn purple-black", "Infected leaf tissue drops out leaving a 'shot-hole' appearance", "Deep pitting, cracking, and gummy exudate on fruit"],
        "favorable_conditions": ["Warm, wet, windy weather", "Light sandy soils subject to blowing sand abrasion"],
        "precautions": [
            "Plant bacterial spot-tolerant or resistant peach cultivars.",
            "Apply copper bactericides during dormancy and low-rate copper/oxytetracycline sprays from shuck split to harvest.",
            "Avoid excessive pruning and excess nitrogen that produces overly succulent shoot growth.",
        ],
        "severity": "moderate",
    },

    # ── Bell Pepper ──────────────────────────────────────────────────
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "description": "A serious bacterial foliar and fruit disease caused by Xanthomonas campestris pv. vesicatoria.",
        "symptoms": ["Small, water-soaked circular to irregular dark brown leaf lesions", "Yellow halos surrounding leaf spots", "Raised, rough, blister-like or scabby spots on green pepper fruit", "Extensive defoliation"],
        "favorable_conditions": ["Warm temperatures (24–30°C) with high relative humidity", "Overhead sprinkler irrigation or wind-driven driving rains"],
        "precautions": [
            "Use certified disease-free, hot-water treated seeds and healthy transplants.",
            "Avoid overhead irrigation; adopt drip irrigation to keep foliage completely dry.",
            "Rotate pepper fields with non-solanaceous crops for a minimum of 2–3 years.",
            "Apply copper + mancozeb bactericidal sprays early before disease pressure peaks.",
        ],
        "severity": "moderate",
    },

    # ── Potato ───────────────────────────────────────────────────────
    "Potato___Early_blight": {
        "crop": "Potato",
        "description": "A common fungal disease caused by Alternaria solani producing concentric dark 'target' spots primarily on older foliage.",
        "symptoms": ["Brown to black concentric-ring spots on mature, lower leaves", "Yellow chlorotic halo around lesions", "Premature leaf senescence and reduced tuber bulk"],
        "favorable_conditions": ["Warm temperatures (24–29°C)", "Alternating cycles of wet and dry weather", "Nitrogen deficiency or crop stress"],
        "precautions": [
            "Ensure optimal, balanced crop fertility — nitrogen-stressed potato plants succumb much faster.",
            "Utilize drip irrigation rather than overhead sprinklers to limit leaf wetness.",
            "Apply protective fungicides (chlorothalonil, mancozeb) starting around row closure.",
            "Allow proper vine kill and skin set before mechanical harvesting to protect tubers.",
        ],
        "severity": "moderate",
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "description": "A catastrophic oomycete pathogen (Phytophthora infestans) that can defoliate entire fields and rot tubers in storage within days.",
        "symptoms": ["Large, irregular water-soaked pale-to-dark green lesions on leaves", "White cottony/moldy spore growth on the underside of lesions in humid mornings", "Rapid blackening and collapse of stems", "Dry, granular brown rot inside tubers"],
        "favorable_conditions": ["Cool nights (10–15°C) followed by moderate, humid days (15–21°C)", "Relative humidity >90% and frequent rains or heavy fogs"],
        "precautions": [
            "Never plant seed tubers with any evidence of discoloration or rot; use certified seed only.",
            "Scout fields continuously and destroy localized infection foci immediately.",
            "Apply preventive protectant fungicides; switch to translaminar/systemic chemistry when pressure spikes.",
            "Kill vines completely at least 2 weeks prior to harvest to prevent tuber contact with live spores.",
        ],
        "severity": "high",
    },

    # ── Squash ───────────────────────────────────────────────────────
    "Squash___Powdery_mildew": {
        "crop": "Squash / Cucurbits",
        "description": "A widespread fungal pathogen (Podosphaera xanthii) covering cucurbit foliage in powdery white talc-like patches.",
        "symptoms": ["White, powdery fungal spots on upper and lower leaf surfaces and petioles", "Leaves turn yellow, brown, and become dry and brittle", "Sunburn on fruit due to canopy loss"],
        "favorable_conditions": ["Warm, dry climates (20–27°C) with high relative humidity at night", "Shaded, crowded vine canopies"],
        "precautions": [
            "Plant powdery mildew-tolerant or resistant hybrid squash varieties.",
            "Ensure wide crop spacing for maximum sunlight penetration and airflow.",
            "Apply potassium bicarbonate, neem oil, sulfur, or registered synthetic fungicides at first sign of white spots.",
        ],
        "severity": "moderate",
    },

    # ── Strawberry ───────────────────────────────────────────────────
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "description": "A fungal disease caused by Diplocarpon earlianum causing numerous small purple spots that coalesce into scorched leaves.",
        "symptoms": ["Numerous small, irregular purple-to-dark brown spots on upper leaf surfaces", "Tissue between spots turns purple then brown, giving a 'scorched' look", "Curling of leaf margins upward and premature leaf death"],
        "favorable_conditions": ["Warm temperatures (18–25°C)", "Extended periods of leaf wetness from rain or overhead watering"],
        "precautions": [
            "Plant resistant strawberry cultivars where available.",
            "Use drip irrigation instead of overhead sprinklers.",
            "Renovate strawberry beds after harvest by mowing and removing old diseased leaf litter.",
            "Apply protectant fungicides during early spring emergence if leaf scorch was severe previously.",
        ],
        "severity": "moderate",
    },

    # ── Tomato ───────────────────────────────────────────────────────
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "description": "A bacterial pathogen (Xanthomonas spp.) producing small dark spots with yellow halos and raised fruit scabs.",
        "symptoms": ["Small, greasy dark water-soaked spots on leaves with yellow halos", "Raised, scabby, rough spots on green fruit", "Severe blighting and leaf drop in wet weather"],
        "favorable_conditions": ["Warm, wet, humid weather (24–30°C)", "Overhead irrigation, splashing rain, contaminated tools"],
        "precautions": [
            "Use certified disease-free seeds and transplants.",
            "Avoid handling plants or cultivating fields when foliage is wet.",
            "Disinfect stakes, tools, and harvest bins between seasons.",
            "Apply preventative copper-based bactericides combined with mancozeb.",
        ],
        "severity": "moderate",
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "description": "A fungal disease caused by Alternaria linariae producing dark concentric 'target-board' spots on foliage.",
        "symptoms": ["Brown to black concentric ring spots on lower leaves", "Yellow chlorosis surrounding lesions", "Leaf drop starting from base and moving upward", "Dark leathery sunken spots at stem end of fruit"],
        "favorable_conditions": ["Warm, humid weather (24–29°C)", "Overhead irrigation and dense planting"],
        "precautions": [
            "Remove and destroy affected lower foliage immediately.",
            "Water at the soil base early in the day; avoid wetting foliage.",
            "Mulch heavily around tomato plants to prevent soil-borne spores from splashing onto leaves.",
            "Apply copper fungicides or chlorothalonil when initial symptoms appear.",
        ],
        "severity": "moderate",
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "description": "A devastating oomycete disease (Phytophthora infestans) that rapidly blackens foliage, stems, and rot fruit.",
        "symptoms": ["Large irregular water-soaked pale green lesions", "White downy fungal growth on leaf undersides in humid mornings", "Rapid blackening of stems and brown, greasy rot on green fruit"],
        "favorable_conditions": ["Cool, wet, humid conditions (15–22°C with >90% RH)", "Prolonged leaf wetness"],
        "precautions": [
            "Remove and destroy infected plants immediately — do not compost them.",
            "Apply protective fungicide (chlorothalonil, copper, or systemic chemistry) preventatively.",
            "Space plants widely and train onto stakes/cages to promote rapid foliage drying.",
        ],
        "severity": "high",
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "description": "A fungal foliar disease caused by Passalora fulva common in humid environments and high tunnels.",
        "symptoms": ["Pale green to yellow diffuse spots on upper leaf surfaces", "Olive-green to velvety brown mold growth on the corresponding leaf undersides", "Leaves curl, wither, and drop prematurely"],
        "favorable_conditions": ["High relative humidity (>85%) with moderate temperatures (21–24°C)", "Poor greenhouse or hoop-house ventilation"],
        "precautions": [
            "Maximize ventilation and air circulation in tunnels and greenhouses using fans.",
            "Prune lower sucker growth and maintain wide plant spacing.",
            "Keep foliage dry by utilizing drip irrigation exclusively.",
        ],
        "severity": "moderate",
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "description": "A destructive fungal foliar disease (Septoria lycopersici) causing numerous small circular spots with tiny dark pycnidia.",
        "symptoms": ["Numerous small (2–3 mm) circular spots with dark brown margins and grey/tan centers", "Tiny black specks (pycnidia) visible inside centers of spots", "Progressive leaf yellowing and severe upward defoliation"],
        "favorable_conditions": ["Warm temperatures (20–25°C)", "Extended wet periods from rain or overhead watering"],
        "precautions": [
            "Mulch around plants to create a physical barrier against spore splash from soil.",
            "Prune bottom 12 inches of foliage once plants are established.",
            "Apply protective fungicides (chlorothalonil, copper) starting at first fruit set.",
            "Rotate away from solanaceous crops for a minimum of 2 years.",
        ],
        "severity": "moderate",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "description": "Infestation by Two-Spotted Spider Mites (Tetranychus urticae) piercing leaf cells and sucking plant juices.",
        "symptoms": ["Fine yellow or white stippling on upper leaf surfaces", "Fine webbing on leaf undersides and stem junctions", "Leaves turn bronze, dry out, and drop under heavy infestation"],
        "favorable_conditions": ["Hot, dry, dusty conditions (>30°C)", "Drought stress and dusty field borders"],
        "precautions": [
            "Avoid plant water stress by maintaining consistent soil moisture.",
            "Release predatory mites (e.g., Phytoseiulus persimilis) in high tunnels.",
            "Apply insecticidal soaps, horticultural oils, or specific miticides targeting undersides of foliage.",
            "Wash dust off field perimeter paths to discourage mite migration.",
        ],
        "severity": "moderate",
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "description": "A fungal pathogen (Corynespora cassiicola) causing target-like lesions on foliage and sunken concentric lesions on fruit.",
        "symptoms": ["Small pinpoint brown lesions expanding into large circular spots with concentric rings", "Spots have a prominent yellow chlorotic halo", "Sunken, brown circular target lesions on tomato fruit"],
        "favorable_conditions": ["Warm, humid tropical and subtropical weather (20–28°C)", "High moisture and dense, unpruned canopies"],
        "precautions": [
            "Ensure good row spacing and trellis plants for optimal air circulation.",
            "Avoid overhead irrigation to keep foliage dry.",
            "Apply protective fungicides (chlorothalonil, mancozeb, or azoxystrobin) according to local recommendations.",
        ],
        "severity": "moderate",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "description": "A destructive Begomovirus (TYLCV) transmitted by the Silverleaf Whitefly (Bemisia tabaci) causing stunted, curled foliage.",
        "symptoms": ["Severe upward curling and cupping of leaf margins", "Prominent interveinal yellowing (chlorosis)", "Severe plant stunting with bushy, upright habit", "Flower drop and virtually no fruit set on early-infected plants"],
        "favorable_conditions": ["High populations of whiteflies (Bemisia tabaci)", "Hot, arid to sub-humid seasons"],
        "precautions": [
            "Plant certified TYLCV-resistant tomato hybrids (e.g., cultivars with Ty-1 or Ty-3 resistance genes).",
            "Protect young nursery plants using fine insect-proof mesh netting (50-mesh).",
            "Manage whitefly populations using yellow sticky traps, systemic insecticides (imidacloprid), or biocontrols.",
            "Rogue out and destroy infected symptomatic plants immediately to prevent vector spread.",
        ],
        "severity": "high",
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "description": "A highly infectious Tobamovirus (ToMV) causing mottled foliar mosaic, leaf distortion, and internal fruit browning.",
        "symptoms": ["Light and dark green mosaic or mottled patterns on leaves", "Leaf distortion, blistering, or 'shoestring' narrowing", "Stunted overall plant growth", "Internal brown necrosis in fruit walls"],
        "favorable_conditions": ["Mechanical transmission through worker hands, tools, grafting, or contaminated seeds", "High temperatures"],
        "precautions": [
            "Plant ToMV-resistant tomato varieties (look for 'T' or 'ToMV' label).",
            "Wash hands with soap/milk solution and sanitize pruning shears with 10% bleach between plants.",
            "Do not use tobacco products near tomato plants (tobacco can carry related tobamoviruses).",
            "Immediately remove and destroy confirmed infected plants.",
        ],
        "severity": "high",
    },
}

# Aliases for variations in naming conventions
ALIASES: Dict[str, str] = {
    "Corn___Common_rust": "Corn_(maize)___Common_rust_",
    "Corn___Common_rust_": "Corn_(maize)___Common_rust_",
    "Corn___Gray_leaf_spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn___Northern_Leaf_Blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___Common_rust": "Corn_(maize)___Common_rust_",
    "Cherry___Powdery_mildew": "Cherry_(including_sour)___Powdery_mildew",
    "Orange___Citrus_greening": "Orange___Haunglongbing_(Citrus_greening)",
    "Pepper_bell___Bacterial_spot": "Pepper,_bell___Bacterial_spot",
}

# Generic entry used whenever the model predicts a "healthy" class
HEALTHY_INFO: Dict[str, Any] = {
    "description": "No disease detected — the leaf appears healthy with normal tissue structure.",
    "symptoms": ["Normal green coloration", "Uniform leaf surface without necrotic lesions, mildew, or spots"],
    "favorable_conditions": ["Balanced soil nutrition", "Proper irrigation management", "Optimal airflow and sunlight"],
    "precautions": [
        "Continue routine field scouting, especially after rain or humid weather.",
        "Maintain standard balanced irrigation and soil nutrient management.",
        "Ensure good spacing to keep foliage aerated.",
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
        return {
            "crop": "Unknown",
            "description": "No prediction available.",
            "symptoms": [],
            "favorable_conditions": [],
            "precautions": [],
            "severity": "unknown",
        }

    # Resolve aliases if needed
    canonical_label = ALIASES.get(label, label)

    if "healthy" in canonical_label.lower():
        info = dict(HEALTHY_INFO)
        raw_crop = canonical_label.split("___")[0].replace("_", " ") if "___" in canonical_label else canonical_label
        raw_crop = raw_crop.replace("(maize)", "Corn").replace("(including sour)", "Cherry").replace(",", "").strip()
        info["crop"] = raw_crop
        return info

    if canonical_label in DISEASE_KB:
        return DISEASE_KB[canonical_label]

    # Unknown class fallback
    raw_crop = canonical_label.split("___")[0].replace("_", " ") if "___" in canonical_label else "Unknown"
    return {
        "crop": raw_crop,
        "description": f"No curated information available yet for '{canonical_label}'.",
        "symptoms": [],
        "favorable_conditions": [],
        "precautions": ["Consult a local agricultural extension officer for guidance on this specific condition."],
        "severity": "unknown",
    }
