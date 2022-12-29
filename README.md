# Anki scripts
A group of scripts to make cards and prep decks for [Anki](https://apps.ankiweb.net/).
These are fairly tailored to my uses for med school, so they might not be all that helpful unless you're a student at [LCOM](https://med.uvm.edu/).

## Files
This is a manifest of the files included in this repo.
### `drug_list.py`
This formats given drug lists in a way that Anki can import.

My drug cards have the following fields:
- Drug name
- Class
- Mechanism
- Unique pharmacokinetics
- Major or unique adverse effects
- Major or unique indications

These get used in the following card types:
- Name to class
- Name to mechanism
- Name to pharmacokinetics
- Name to adverse effects
- Name to indications
- Indications to name

Templates for these card types can be generated using the `make_all_cards()`
function.
