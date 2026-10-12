import json
from pathlib import Path

import Levenshtein
from rapidfuzz import process

file_path = Path("university_domains_list/world_universities_and_domains.json").resolve()


class SearchUniversity:
    def __init__(self):
        with open(file_path, 'r') as g:
            universities_list = json.load(g)
        self.university_list = universities_list
        self.names = [u.get("name", "") for u in universities_list]

    def search_university(self, search_string):
        """
        Searches for the most likely university based on the provided name.
        """
        result = process.extractOne(
            query=search_string,
            choices=self.names,
            scorer=Levenshtein.distance,
            score_cutoff=50
        )
        return self.university_list[result[2]]
