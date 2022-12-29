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
    parser.add_argument("drug_list",
                        help="Path(s) to the drug list(s).",
                        nargs="+")
    args = parser.parse_args()
    if args.output is None:
        output = sys.stdout
    else:
        output = args.output[0]

    # Reading each drug list
    data = pd.DataFrame()
    for path in args.drug_list:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} not found.")
        data = pd.concat([data, read_list(path)])

    # Outputting
    data.to_csv(output, index=False, sep=";", header=False)


if __name__ == "__main__":
    main()
