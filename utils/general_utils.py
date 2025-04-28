import yfinance as yf
import re
import json
import os


def clean_company_name(name):
    """Clean a company name by removing common suffixes and standardizing format."""
    # Remove commas
    name = name.replace(",", "")

    # Remove common suffixes
    suffixes = [
        "Inc.",
        "Inc",
        "Corporation",
        "Corp.",
        "Corp",
        "Co.",
        "Company",
        "Ltd.",
        "Ltd",
        "LLC",
        "Ag",
        ".com",
        "The",
        "Group",
        "Holdings",
        "Technologies",
        "Technology",
        "Pharmaceuticals",
        "Pharmaceutical",
        "Biotech",
        "Biotechnology",
        "Solutions",
        "Solution",
        "Services",
        "Service",
        "International",
        "Global",
        "Systems",
        "System",
        "Communications",
        "Communications",
        "Therapeutics",
        "Therapeutic",
        "Energy",
        "Industries",
        "Industry",
        "Bank",
        "Bancorp",
        "Bancorporation",
        "Financial",
        "Group",
        "Partners",
        "Partner",
        "Capital",
        "Investments",
        "Investment",
        "Holdings",
        "Holdings",
        "Properties",
        "Property",
        "Real Estate",
        "Resources",
        "Resource",
        "Materials",
        "Material",
        "Manufacturing",
        "Manufacturers",
        "Manufacture",
        "Pharma",
        "Pharma",
        "Pharm",
    ]
    pattern = r"\b(?:" + "|".join(re.escape(s) for s in suffixes) + r")\b\.?"
    return re.sub(pattern, "", name, flags=re.IGNORECASE).lower().strip()


def load_topic_aliases():
    """Load topic aliases from an external JSON file."""
    aliases_path = os.path.join(os.path.dirname(__file__), "..", "data", "topic_aliases.json")
    print(f"Loading topic aliases from {aliases_path}...")
    if not os.path.exists(aliases_path):
        print(f"Aliases file not found at {aliases_path}. Using empty aliases.")
        return {}
    with open(aliases_path, "r", encoding="utf-8") as f:
        return json.load(f)


TOPIC_ALIASES = load_topic_aliases()

def generate_topic_aliases(topic, is_ticker=True):  
    """Generate a list of aliases for a topic symbol including company name."""    
    aliases = [topic]
    if is_ticker:
        # Add $ sign to ticker symbol
        aliases.append(f"${topic}")       

        # try to add company name from Yahoo Finance 
        try:
            ticker = yf.Ticker(topic)
            company_name = ticker.info.get("shortName", "")
            company_name = clean_company_name(company_name)
        except Exception:
            # ...do not print or log the error...
            company_name = ""

        if company_name:
            aliases.append(company_name)

    # Add external aliases from the JSON file
    extra_aliases = TOPIC_ALIASES.get(topic.lower())
    if extra_aliases:
        aliases.extend(extra_aliases)

    return aliases
