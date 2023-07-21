# Restaurant menu OCR category extraction

This is a project I made for a coding task for SharpGrid. It is a python script that extracts the categories from a restaurant menu OCR scan data. It may not work perfectly on all menus, but it it is more correct than not.

I have also implemented something that highlights the lines that may be categories onto the pdf.

I have parallelizing the script, but the only part that takes any significant amount of time is are the requests to OpenAI, and those don't have a official way to be parallelized, so I would have to manually write the queries to the API, which would take a lot of time. The endpoint is also rate limited, so it would not be that much faster.

## How to run the project

### Prerequisites

-   Python 3.11 - Lower versions may work, but I have not tested them. You can download and install Python from [here](https://www.python.org/downloads/).
-   Poetry - You can download and install Poetry from [here](https://python-poetry.org/docs/#installation).

### Steps

git clone https://github.com/gvarph/sharpgrid-task.git
cd sharpgrid-task

1. Install the dependencies.

```bash
poetry install --only main
```

The `--only main` will omit the development dependencies such as `black`

2. Set up your environment variables.

2.1. Create a `.env` file based on the `.env.template` file.

2.2. Edit the `.env` file. The variables are explained in the `.env.template` file.

2.3 (Optional) Now you can tune the filter parameters in the `filter/__ini__.py` file. The different filters can be found in the `filter` folder, and have docstrings so hovering over them in an IDE should show you what they do. The first parameter in each of them is their weight, which is used to symbolize how important the filter is. The higher the weight, the more important the filter is. The weight should be between 0 and 1.

3. Run the script.

```bash
# You can process a single json file by using it as an argument to the script.
poetry run python src/main.py path/to/ocr/data.json
```

```bash
# You can also process multiple json files by using the directory they are in as an argument to the script.
# This will try to process all json files in the directory.
poetry run python src/main.py path/to/ocr/data/directory
```
