import json


def clean_json_data(data):
    """
    Recursively removes keys with empty string, empty list, or empty dictionary values.
    For lists, removes empty string, empty list, or empty dictionary elements.
    (Note: Original comments were requested to be removed, but added this docstring for clarity on function purpose)
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            cleaned_value = clean_json_data(value)
            if cleaned_value != "" and cleaned_value != [] and cleaned_value != {}:
                cleaned_dict[key] = cleaned_value
        return cleaned_dict
    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            cleaned_item = clean_json_data(item)
            if cleaned_item != "" and cleaned_item != [] and cleaned_item != {}:
                cleaned_list.append(cleaned_item)
        return cleaned_list
    else:
        return data


def process_json_file(input_filename, output_filename):
    """
    Reads a JSON file, cleans the content, and writes to a new JSON file.
    (Note: Original comments were requested to be removed, but added this docstring for clarity)
    """
    with open(input_filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    cleaned_data = clean_json_data(json_data)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":

    import os
    from utils.logger import get_logger
    import config

    logger = get_logger()
    file_names = os.listdir(config.RES_DIR)
    for name in file_names:
        filepath = os.path.join(config.RES_DIR, name)
        logger.info(f"Processing File: {filepath}")
        process_json_file(filepath, filepath)
    pass
