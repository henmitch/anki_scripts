"""Create a deck of Anki cards based on a drug list."""
import argparse
import os
import sys

import pandas as pd

FIELDS = [
    "Drug name", "Class", "Mechanism", "Unique pharmacokinetics",
    "Major or unique adverse effects", "Major or unique indications"
]

INFO_PAIRS = [(FIELDS[0], field) for field in FIELDS[1:]]
# Just adverse effects and indications
INFO_PAIRS += [(FIELDS[5], FIELDS[0])]


def read_list(path: str) -> pd.DataFrame:
    data = pd.read_excel(path)
    # Remove empty rows
    data = data.dropna(how="all")
    data = data.fillna("None")
    # Stripping leading and trailing spaces
    data = data.applymap(lambda x: x.strip())
    # Doing the same for the column names
    data.columns = data.columns.str.strip()
    # Capitalizing each field
    # (Using this instead of str.capitalize() because it doesn't lowercase the
    # rest of the string)
    data = data.applymap(lambda x: x[0].upper() + x[1:])
    return data


def read_antibiotic_list(path: str) -> pd.DataFrame:
    columns = [
        "Drug name", "Target", "Class", "MOA", "Unique toxicity", "Unique PK"
    ]
    raw = pd.read_excel(path)
    # Removing empty rows
    raw = raw.dropna(how="all")
    raw.columns = raw.columns.str.strip()
    # Renaming the empty column to "Drug name"
    raw = raw.rename(columns={"Unnamed: 2": "Drug name"})
    # ffilling the "Target" column
    raw["Target"] = raw["Target"].ffill()
    raw = raw.fillna("None")
    for column in columns:
        raw[column] = raw[column].str.strip().str.capitalize()
    # Stacking ["MSSA", "MRSA", "E. coli", "Pseudomonas", "B. fragilis",
    # "Mycoplasma"] into one column
    data = raw.set_index(columns).stack()
    data = data.str.strip()
    # Removing the "No" values
    data = data[data != "No"]
    # Making the non-standard values explicit
    data = " (" + data.str.capitalize() + ")"
    data = data.rename("Addenda")
    data = data.reset_index()
    data = data.rename(columns={"level_6": "Indication"})
    data.loc[data["Addenda"] == " (Yes)", "Addenda"] = ""
    data["Indication"] += data["Addenda"]
    data = data.drop(columns="Addenda")
    # Combining the indications into one comma-separated column
    data = data.groupby(columns).agg(", ".join).reset_index()

    # Now, we account for rows in the original dataset that have no indication
    if len(raw) > len(data):
        # We get the rows that are in the original dataset but not in the
        # processed one
        missing = raw[~raw["Drug name"].isin(data["Drug name"])]
        # We add them to the processed dataset
        data = pd.concat([data, missing])
        # And we fill the "Indication" column with "None"
        data = data.fillna("None")

    data = data[columns + ["Indication"]]

    return data


def make_all_info_card() -> tuple[str, str]:
    front = f"{{{{{FIELDS[0]}}}}}\n<br>"
    for field in FIELDS[1:]:
        front += f"\n<br>\n{field}: ?"

    back = f"{{{{{FIELDS[0]}}}}}\n<hr id=answer>\n"
    for field in FIELDS[1:]:
        back += f"{field}: {{{{{field}}}}}\n<br>\n"
    back = back[:-5]

    return front, back


def make_specific_info_card(front: str, back: str) -> tuple[str, str]:
    front_text = f"{{{{{front}}}}}\n<br>\n<br>\n{back}: ?"

    back_text = f"{{{{FrontSide}}}}\n<hr id=answer>\n{{{{{back}}}}}"
    return front_text, back_text


def make_all_cards() -> None:
    for side in make_all_info_card():
        print(side)
        print()
        input("Press enter to continue...")
        print()
    for pair in INFO_PAIRS:
        for side in make_specific_info_card(*pair):
            print(side)
            print()
            input("Press enter to continue...")
            print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o",
                        "--output",
                        help="Path to the output file. Defaults to stdout.",
                        nargs=1,
                        default=None)
    parser.add_argument("-a",
                        "--antibiotics",
                        action="store_true",
                        help="Whether the drug list is an antibiotic list.")
    parser.add_argument("drug_list",
                        help="Path(s) to the drug list(s).",
                        nargs="+")
    args = parser.parse_args()
    if args.output is None:
        output = sys.stdout
    else:
        output = args.output[0]

    if args.antibiotics:
        func = read_antibiotic_list
    else:
        func = read_list

    # Reading each drug list
    data = pd.DataFrame()
    for path in args.drug_list:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} not found.")
        data = pd.concat([data, func(path)])

    # Outputting
    data.to_csv(output, index=False, sep=";", header=False)


if __name__ == "__main__":
    main()
