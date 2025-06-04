import os
import re
import itertools
import pandas as pd

from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.element import NavigableString
from concurrent.futures import ProcessPoolExecutor, as_completed
import concurrent.futures
ITEMS = {
    'item1': 'Item 1',
    'item1a': 'Item 1A',
    'item1b': 'Item 1B',
    'item2': 'Item 2',
    'item7': 'Item 7',
    'item7a': 'Item 7A',
    'item8': 'Item 8',
}

# Each part should have as few items as possible, but it is essential to ensure that at least two items are present
# According to statistics, the current segmentation is the best practice
PARTS = {
    'part1.1': ['item1', 'item1a', 'item1b'],
    'part1.2': ['item2'],
    'part2.2': ['item7', 'item7a', 'item8'],
}

SYMBOL_TERMINATORS = ['.', ' .', ' :', ':', '-', ' -', '—', ' —', '\t']
NON_SYMBOL_TERMINATORS = [' ']
MAX_WORKERS = 8


def get_part_by_item(item_key):
    for part_key, items in PARTS.items():
        if item_key in items:
            return part_key
    return None


def get_previous_part_key(part_key):
    part_keys = list(PARTS.keys())
    current_index = part_keys.index(part_key)
    if current_index - 1 >= 0:
        return part_keys[current_index - 1]
    else:
        return None


def get_next_part_key(part_key):
    part_keys = list(PARTS.keys())
    current_index = part_keys.index(part_key)
    if current_index + 1 < len(part_keys):
        return part_keys[current_index + 1]
    else:
        return None


def get_previous_item_key(item_key):
    item_keys = list(ITEMS.keys())
    current_index = item_keys.index(item_key)
    if current_index - 1 >= 0:
        return item_keys[current_index - 1]
    else:
        return None


def get_next_item_key(item_key):
    item_keys = list(ITEMS.keys())
    current_index = item_keys.index(item_key)
    if current_index + 1 < len(item_keys):
        return item_keys[current_index + 1]
    else:
        return None


def check_same_tags(tag1, tag2):
    while tag1 and tag2:
        if tag1 != tag2:
            return False
        tag1 = tag1.parent
        tag2 = tag2.parent
    return tag1 is None and tag2 is None


def search_tags(html_tag, item_value, results, depth=1, max_content_length=500):
    # Check if the tag contains the item_value as the beginning of any direct text node
    for content in html_tag.contents:
        if isinstance(content, NavigableString):
            text_content = content.strip().lower()
            terminators = SYMBOL_TERMINATORS + NON_SYMBOL_TERMINATORS
            possible_starts = [item_value.lower() + terminator for terminator in terminators]
            # Without space
            possible_starts += [item_value.lower().replace(' ', '') + terminator for terminator in terminators]
            if len(text_content) <= max_content_length and (
                any(text_content.startswith(start) for start in possible_starts) or
                text_content == item_value.lower() or text_content == item_value.lower().replace(' ', '')
            ):
                results.append((html_tag, depth))
                break  # Once found, no need to add the same tag again
        else:
            search_tags(content, item_value, results, depth + 1, max_content_length)
    return None


def filter_tags(html_tag):
    for content in html_tag.contents:
        if isinstance(content, NavigableString):
            text_content = content.strip().lower()
            terminators = SYMBOL_TERMINATORS + NON_SYMBOL_TERMINATORS
            if any(text_content.endswith(terminator) for terminator in terminators):
                return True
    return False


def find_common_ancestor(item_tags):
    # Check for invalid input, either an empty list of tags or tags without parents
    if len(item_tags) == 0 or len(item_tags[0]) == 0:
        raise ValueError('Invalid item tags')
    # Create a list of sets, each containing all ancestors of each item_tag
    ancestor_lists = [set(item_tag.parents) for item_tag, _ in item_tags]
    # Find the intersection of all sets to get common ancestors for all provided tags
    common_ancestors = set.intersection(*ancestor_lists)
    # Find the closest common ancestor
    closest_common_ancestor = None
    max_depth = float('-inf')
    base_node = item_tags[0][0].find_parent('body')
    if base_node is None:
        raise ValueError('Invalid body tag')
    # Iterate through each common ancestor to find the one closest to the item_tags
    for ancestor in common_ancestors:
        # Calculate the depth of the ancestor by comparing its distance from the 'body' tag
        depth = len(list(ancestor.parents)) - len(list(base_node.parents))
        if depth > max_depth:
            closest_common_ancestor = ancestor
            max_depth = depth
    return closest_common_ancestor, max_depth + 1  # Adjust the calculated depth


def calculate_distance_between_tags(html_tags):
    char_counts = []
    for i in range(len(html_tags) - 1):
        tag1, tag2 = html_tags[i], html_tags[i + 1]
        # Find the closest common ancestor for each pair of tags
        common_ancestor, _ = find_common_ancestor((tag1, tag2))
        if common_ancestor is None:
            raise ValueError(f'Invalid ancestor for {tag1} and {tag2}')
        # Extract all text between these two tags within the common ancestor
        found_first = False
        char_count = 0
        # Iterate through descendants of the common ancestor to find the tags and count chars
        for desc in common_ancestor.descendants:
            if isinstance(desc, Tag) and check_same_tags(desc, tag1[0]):
                found_first = True
            elif isinstance(desc, Tag) and check_same_tags(desc, tag2[0]):
                break
            elif found_first and isinstance(desc, str):
                char_count += len(desc)
        char_counts.append(char_count)
    return char_counts


def find_key_index(html_content, toc_tags_position, item_key, start_position=0):
    item_value = ITEMS[item_key].lower()
    item_value_no_space = item_value.replace(' ', '')
    # First, try matching SYMBOL_TERMINATORS
    terminator_pattern = r'(' + '|'.join(re.escape(terminator) for terminator in SYMBOL_TERMINATORS) + r')'
    pattern = re.compile(
        r'>\s*(' + re.escape(item_value) + r'|' + re.escape(item_value_no_space) + r')' + terminator_pattern)
    matches = list(pattern.finditer(html_content.lower(), pos=start_position))
    if len(matches) < 2:
        # Try matching NON_SYMBOL_TERMINATORS
        terminator_pattern = r'(' + '|'.join(re.escape(terminator) for terminator in NON_SYMBOL_TERMINATORS) + r')'
        pattern = re.compile(
            r'>\s*(' + re.escape(item_value) + r'|' + re.escape(item_value_no_space) + r')' + terminator_pattern)
        matches += list(pattern.finditer(html_content.lower(), pos=start_position))
    if len(matches) < 2:
        # Try matching item_value with a negative lookahead to ensure no letters or digits follow
        pattern = re.compile(
            r'>\s*(' + re.escape(item_value) + r'|' + re.escape(item_value_no_space) + r')(?![a-zA-Z0-9])')
        matches += list(pattern.finditer(html_content.lower(), pos=start_position))
    # Sort matches by their start positions
    matches = sorted(matches, key=lambda m: m.start())
    if matches:
        if toc_tags_position and start_position == 0 and len(matches) > 1:
            return matches[1].start() + matches[1].group().find(item_value)
        else:
            return matches[0].start() + matches[0].group().find(item_value)
    return -1

def find_best_item_combination(html_content, debug=False, is_save=False):

    soup = BeautifulSoup(html_content, 'html.parser')
    # Step 1
    # Dictionary to store results for each item
    item_results = {}
    for item_key, item_value in ITEMS.items():
        results = []
        # Find and store tags related to each item in the HTML
        search_tags(soup.body, item_value, results)
        item_results[item_key] = results
    if debug:
        print('Item Results:', item_results)
    # Step 2
    toc_tags_position = True  # True is at the beginning / False is at the end
    non_empty_item_results = {key: value for key, value in item_results.items() if len(value) > 0}
    if non_empty_item_results:
        # Check combinations and collect invalid tags
        # Strategy: The table of contents can only appear at the beginning and the end,
        # no need to check all combinations
        items_with_more_than_one_tags = sum(1 for tags in non_empty_item_results.values() if len(tags) > 1)
        items_with_more_than_one_tags_ratio = items_with_more_than_one_tags / len(non_empty_item_results)
        # Sometimes there will be human errors (some items are missing in the table of contents) in the report,
        # set an error tolerance
        threshold = 0.5
        if items_with_more_than_one_tags_ratio > threshold:
            # Strategy: Only need to check the first 3 tags
            first_tags = [tags[0] for tags in non_empty_item_results.values()][:3]
            # last_tags = [tags[-1] for tags in non_empty_item_results.values()][:3]
            # Assumption: If calculate_distance_between_tags takes too long to execute,
            # it indicates that it is not a table of contents
            timeout = 60
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(calculate_distance_between_tags, first_tags)
                try:
                    first_tags_distances = future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    first_tags_distances = []
            avg_distance_first = (sum(first_tags_distances) / len(first_tags_distances)) if first_tags_distances else float('inf')
            if debug:
                print('First Tags Distances:', first_tags_distances)
            max_content_length = 1000  # Max table of contents gap
            if avg_distance_first <= max_content_length:
                toc_tags_position = True
            else:
                toc_tags_position = False
            if debug:
                print('Table of Contents Position:', 'Begin' if toc_tags_position else 'End')
            filtered_results = {}
            # Keep max 2 tags for each key
            # The more tags saved per key, the higher the cutting accuracy, but this will slow down the cutting speed
            num_of_tags = 2
            for key, tags in item_results.items():
                if len(tags) > 0:
                    if toc_tags_position:
                        filtered_results[key] = tags[1:1+num_of_tags]
                    else:
                        if len(tags) > 2:
                            filtered_results[key] = tags[:num_of_tags]
                        else:
                            filtered_results[key] = tags[:-1]
                else:
                    filtered_results[key] = []
            # Update item results directly
            item_results = filtered_results
    if debug:
        print('Filtered Item Results:', item_results)
    # Step 3
    # Dictionary to store parts' information
    part_ancestors = {}
    part_depths = {}
    part_best_combinations = {}
    for part_key, part_items in PARTS.items():
        # Filter out items with no results
        non_empty_item_results = {k: item_results[k] for k in part_items if len(item_results[k]) > 0}
        # Find the best combination
        max_ancestor_depth = -1
        best_combination_indices = []
        common_ancestor = None
        if non_empty_item_results:
            for combination in itertools.product(*non_empty_item_results.values()):
                common_ancestor, ancestor_depth = find_common_ancestor(combination)
                # Check if this common ancestor is deeper than the previously found ancestors
                if common_ancestor and ancestor_depth > max_ancestor_depth:
                    max_ancestor_depth = ancestor_depth
                    # Store the indices of the best combination
                    # where the best combination is defined by deepest common ancestor
                    best_combination_indices = [non_empty_item_results[key].index(html_tag) for key, html_tag in
                                                zip(non_empty_item_results.keys(), combination)]
        # Dictionary to store item combination
        item_combination = {}
        for key in non_empty_item_results:
            index = list(non_empty_item_results.keys()).index(key)
            if len(best_combination_indices) > 0:
                selected_index = best_combination_indices[index]
                # Store the best combination's corresponding HTML tag for each key
                item_combination[key] = item_results[key][selected_index]
            else:
                raise ValueError('Invalid best combination indices')
        part_ancestors[part_key] = common_ancestor
        part_depths[part_key] = max_ancestor_depth + 1  # item depth
        part_best_combinations[part_key] = item_combination

    return part_best_combinations, part_depths, part_ancestors, html_content, toc_tags_position


def extract_item_content(html_content, item_key, item_combination, part_depth, next_part_depth, toc_tags_position, debug=False):
    if item_key not in ITEMS:
        raise ValueError('Invalid item key')
    if item_combination[item_key] is None:
        raise ValueError('Invalid item key')
    if debug:
        print('-----', item_key)
    start_tag, start_tag_depth = item_combination[item_key]
    end_tag = None
    end_tag_depth = 0
    # Loop to find the next item tag in the combination that is not None
    next_item_key = get_next_item_key(item_key)
    while next_item_key is not None:
        if item_combination.get(next_item_key) is not None:
            end_tag, end_tag_depth = item_combination[next_item_key]
            break
        next_item_key = get_next_item_key(next_item_key)
    # Find the direct parent layers of start_tag and end_tag
    if start_tag is not None:
        while start_tag_depth > part_depth:
            start_tag = start_tag.parent
            start_tag_depth -= 1
    # Get the part of the document for the starting and ending tags
    start_tag_part = get_part_by_item(item_key)
    end_tag_part = None
    if next_item_key is not None:
        end_tag_part = get_part_by_item(next_item_key)
    # Adjust the ending tag's depth
    if start_tag_part == end_tag_part:
        if end_tag is not None:
            while end_tag_depth > part_depth:
                end_tag = end_tag.parent
                end_tag_depth -= 1
    else:
        if part_depth == next_part_depth:
            if end_tag is not None:
                while end_tag_depth > part_depth:
                    end_tag = end_tag.parent
                    end_tag_depth -= 1
    # Build the content string starting from the start_tag and including siblings until end_tag
    content = ''
    if start_tag is not None:
        start_tag_index = find_key_index(html_content=html_content,
                                         toc_tags_position=toc_tags_position,
                                         item_key=item_key)
        if debug:
            print('Start Tag Index:', start_tag_index,
                  'Table of Contents Position:', 'Begin' if toc_tags_position else 'End', 'Item:', item_key)
        content += str(start_tag)
        content_tags = start_tag.find_next_siblings()
        if end_tag is None:
            content += ''.join(map(str, content_tags))
            # Handle case where there's another 'Item 1' at the end (table of contents)
            end_tag_index = find_key_index(html_content=html_content,
                                           toc_tags_position=toc_tags_position,
                                           item_key='item1',
                                           start_position=start_tag_index)
            if end_tag_index == -1:
                end_tag_index = len(html_content)
        else:
            for temp_tag in content_tags:
                if temp_tag == end_tag:
                    break
                content += str(temp_tag)
            end_tag_index = find_key_index(html_content=html_content,
                                           toc_tags_position=toc_tags_position,
                                           item_key=next_item_key,
                                           start_position=start_tag_index)
            if debug:
                print('End Tag Index:', end_tag_index, 'TOC Tags Position:', toc_tags_position, 'Item:', next_item_key)
            if end_tag_index == -1:
                end_tag_index = len(html_content)
            if debug:
                print('Start Tag Index:', start_tag_index, ', Eng Tag Index:', end_tag_index)
        direct_content = html_content[start_tag_index:end_tag_index]
        # end_tag is None means that the last item has been reached
        if end_tag is None:
            if debug:
                print('* Direct Content Length:', len(direct_content), ', Content Length:', len(content))
            content = direct_content
        # Assumption: If len(content) is too short,
        # it indicates that the content indeed contains title content only
        min_content_length = 500
        if len(content) <= min_content_length < len(direct_content):
            if debug:
                print('* Direct Content Length:', len(direct_content), ', Content Length:', len(content))
            content = direct_content
        # Assumption: len(content) and len(direct_content) are similar
        max_extra_content_length = 2000
        if abs(len(content) - len(direct_content)) > max_extra_content_length:
            if debug:
                print('* Direct Content Length:', len(direct_content), ', Content Length:', len(content))
            content = direct_content
    return content

def extract_from_html(html_content, debug=False, is_save=False):

    part_best_combinations, part_depths, part_ancestors, html_content, toc_tags_position = find_best_item_combination(
        html_content=html_content,
        debug=debug,
        is_save=is_save)
    if debug:
        print('Part Combinations:', part_best_combinations)
        print('Part Depths:', part_depths)
    item_combination = {}
    for part_combination in part_best_combinations.values():
        item_combination.update(part_combination)
    if debug:
        print('Item Combination:', item_combination)
    item_lengths = {}
    for part_key, part_combination in part_best_combinations.items():
        part_depth = part_depths[part_key]
        next_part_key = get_next_part_key(part_key)
        next_part_depth = 0
        if next_part_key is not None:
            next_part_depth = part_depths[next_part_key]
        for item_key, item_info in part_combination.items():
            item_content = extract_item_content(html_content=html_content,
                                                item_key=item_key,
                                                item_combination=item_combination,
                                                part_depth=part_depth,
                                                next_part_depth=next_part_depth,
                                                toc_tags_position=toc_tags_position,
                                                debug=debug)
            item_lengths[item_key] = item_content
    return item_lengths


def extract_items(html_content):
    item_outs = extract_from_html(html_content)
    output_dict = {}
    for key, value in item_outs.items():
        if key in ['item1', 'item1a', 'item7']:
            content = BeautifulSoup(item_outs[key], 'html.parser').text
            output_dict[key] = content
    return output_dict


if __name__ == '__main__':
    extract_items('')