# UpdateStateList

Utility for updating the Virginia State List for taxonomy changes

## Usage

### update_state_list

Updates the Virginia State List with the latest taxonomy changes.

```bash
python -m update_state_list.update_state_list [options]
```

#### Command Line Options for update_state_list

- `--common_names_file <file>` - Path to the current state list file
- `--version` - Display the program version and exit
- `--verbose` - Enable verbose logging output

The format of this file is a csv where the first line is the definition of the columns.

```csv
comName,State Status,Sort as
```

Then each following line is a common name, the State Status, and a common name to sort on if the common name is not in the eBird Taxonomy. "State Status" and "Sort as" can both be left blank.

For example:

```csv
Brant,
Barnacle Goose,Rare (3a)
```

A good example of how Sort as is used is Fea's Petrel which is the name of the bird in the AOS taxonomy at the time this is written. But eBird has it as Desertas Petrel. So the entry looks like this:

```csv
Fea's Petrel,Accidental (2),Desertas Petrel
```

This will add Fea's petrel to the list but Desertas Petrel will be used for eBird information and taxonomic sort.

#### Example of update_state_list

```bash
python -m update_state_list.update_state_list --common_names_file data/virginiaStateListDec2025.csv
```

#### Output of update_state_list

The program will create a file with _updated in the name. In the example above, it would be called data/virginiaStateListDec2025_updated.csv

### generate_docx

Generates a Word document from the updated state list.

```bash
python -m update_state_list.generate_docx [options]
```

#### Command Line Options for generate_docx

- `--version` - Display the program version and exit
- `--verbose` - Enable verbose logging output (INFO level)
- `--official_list_csv` -  Path to the CSV file of the official list created by
                            update_state_list (required)

#### Example of generate_docx

```bash
python -m update_state_list.generate_docx --official_list_csv data/virginiaStateListDec2025_updated.csv
```

#### Output of generate_docx

The program will create a file with the same name as the input file but with a docx extension. In the example above it would be data/virginiaStateListDec2025_updated.docx

### generate_html

Generates a HTML document from the updated state list.

```bash
python -m update_state_list.generate_html [options]
```

#### Command Line Options for generate_html

- `--version` - Display the program version and exit
- `--verbose` - Enable verbose logging output (INFO level)
- `--official_list_csv` -  Path to the CSV file of the official list created by
                            update_state_list (required)

#### Example of generate_html

```bash
python -m update_state_list.generate_html --official_list_csv data/virginiaStateListDec2025_updated.csv
```

#### Output of generate_html

The program will create a file with the same name as the input file but with a html extension. In the example above it would be data/virginiaStateListDec2025_updated.html
