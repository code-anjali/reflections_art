# Read judging results: https://docs.google.com/spreadsheets/d/10dXQYOuTq4kCt8iuGvR8zYMWIoDie1px1_4hKxt9WzQ/edit#gid=0
# Read judging assignments: https://docs.google.com/spreadsheets/d/1LwrJdeA0aEnOP4BWXKH2L3x9mRSUadNGzsjo70K-cwQ/edit#gid=0
# Compile into one table.
# Display on a stream app page.


# gsheet_db_connector.py
# .streamlit
# googlesheetdb-credentials.json
# secrets.toml
from dataclasses import dataclass
from typing import List, Dict

from prettytable import PrettyTable

from src.gsheet_db_connector import establish_connection


class JudgeScoresBackend:
    def __init__(self):
        self.db_conn = establish_connection(in_localhost=False)
        self.judged_by: Dict[int, List[str]] = self.load_judge_assignment()
        self.judge_scores: Dict[int, List[List[str]]] = self.load_judge_scores()
        self.judge_dashboard: Dict[str, List[EntryJudged]] = self.load_judge_dashboard()

    def lookup_judge_scores(self, judge_name) -> List["EntryJudged"]:
        if not judge_name.strip():
            return []
        judge_first_name_capitalized = str.capitalize(judge_name.strip().lower().split(" ")[0])
        for jname, entries_judged in self.judge_dashboard.items():
            if jname.split(" ")[0] == judge_first_name_capitalized:
                return self.judge_dashboard[jname]
        return [] # name not found.

    def to_pretty_table(self, entries :List["EntryJudged"]):
        p= PrettyTable()
        if not entries:
            return p
        p.field_names = ["completed", "entry id", "entry url", "interpretation", "creativity", "technique", "total"]
        for result in entries:
            p.add_row(["\U0001F44D" if result.completed else "\U0001F44E",
                       result.entry_id,
                       result.entry_url,
                       result.judge_score_interpretation,
                       result.judge_score_creativity,
                       result.judge_score_technique,
                       result.judge_score_total,
                       ])
        p.reversesort = True
        p.sortby = "total"
        p.sort_key = lambda x: float(x[-1])  # i.e., by total
        return p

    def load_judge_assignment(self) -> Dict[int, List[str]]:
        judge_assignment_sheet = "https://docs.google.com/spreadsheets/d/1LwrJdeA0aEnOP4BWXKH2L3x9mRSUadNGzsjo70K-cwQ/edit?usp=sharing&headers=1"
        judge_assignment_rows = self.db_conn.execute(f'SELECT * FROM "{judge_assignment_sheet}"')
        # judge	entry id	type	grade
        # Angie Wa	Entry 55	(Visual Arts)	Intermediate (Grades (3-5)

        judges_for: Dict[int, List[str]] = {}
        for r in judge_assignment_rows:
            if r[1] and r[1].startswith("Entry"):
                entry_id = int(r[1].replace("Entry ", "").strip())
                if entry_id not in judges_for:
                    judges_for[entry_id] = []
                judges_for[entry_id].append(r[0])
        return judges_for

    def load_judge_scores(self) -> Dict[int, List[List[str]]]:
        judges_scores: Dict[int, List[List[str]]] = {}
        judge_scores_sheet = "https://docs.google.com/spreadsheets/d/10dXQYOuTq4kCt8iuGvR8zYMWIoDie1px1_4hKxt9WzQ/edit?usp=sharing&headers=1"
        judge_scores_rows = self.db_conn.execute(f'SELECT * FROM "{judge_scores_sheet}"')
        for r in judge_scores_rows:
            # entry_id(0)	entry_category(1)	entry_statement(2)	entry_urls(3)	entry_student_first_name(4)	entry_student_last_name(5)
            # entry_student_teacher_name(6)	entry_grade(7)	entry_parent_email_id(8)	entry_file_types(9)
            # judge_name(10)	judge_secret(11)	interpretation(12)	interpretation_comments(13)
            # creativity(14)	creativity_comments(15)	technique(16)	technique_comments(17)
            # confidence(18)	other_comments(19)	coi(20)
            entry_id = int(r[0])
            if entry_id not in judges_scores:
                judges_scores[entry_id] = []
            judges_scores[entry_id].append(r)
        return judges_scores


    def get_judge_score_cols(self, judge_score_entry, judge_first_name):
        if not judge_score_entry:
            return None
        judge_score_of_interest = [x for x in judge_score_entry if x[10].split(" ")[0] == judge_first_name]
        if len(judge_score_of_interest) == 0:
            return None
        else:
            judge_score_of_interest = judge_score_of_interest[0] # the arr should have only one matching judge score
        return judge_score_of_interest

    def is_entry_judged_completely(self, entry_id, judge_first_name):
        if entry_id not in self.judge_scores:
            return False
        judge_score_of_interest = self.get_judge_score_cols(judge_score_entry=self.judge_scores.get(entry_id, []), judge_first_name=judge_first_name)
        if not judge_score_of_interest:
            return False
        return judge_score_of_interest[12] >0 and judge_score_of_interest[14] >0 and judge_score_of_interest[16] >0

    def load_judge_dashboard(self):
        judge_dashboard: Dict[str, List[EntryJudged]] = {}
        for entry_id, judges in self.judged_by.items():
            for judge in judges:
                judge_first_name=judge.split(" ")[0]
                score_cols = self.get_judge_score_cols(self.judge_scores.get(entry_id, []), judge_first_name=judge_first_name)
                entry_type = score_cols[1] if score_cols else ""
                entry_title_words = score_cols[2].split(" ") if score_cols and score_cols[2] else []
                entry_title = " ".join(entry_title_words[: min(len(entry_title_words), 6)])
                judge_score_interpretation=score_cols[12] if score_cols else -1
                judge_score_creativity=score_cols[14] if score_cols else -1
                judge_score_technique=score_cols[16] if score_cols else -1
                judged_completely = self.is_entry_judged_completely(entry_id=entry_id, judge_first_name=judge_first_name)
                if judge not in judge_dashboard:
                    judge_dashboard[judge] = []
                judge_dashboard[judge].append(EntryJudged(completed=judged_completely,
                                                          entry_id=entry_id,
                                                          entry_title=f"({entry_type}) {entry_title}...",
                                                          judge_name=judge,
                                                          judge_score_interpretation=judge_score_interpretation,
                                                          judge_score_creativity=judge_score_creativity,
                                                          judge_score_technique=judge_score_technique,
                                                          judge_score_total=judge_score_interpretation + judge_score_creativity + judge_score_technique,
                                                          entry_url=f"https://anjali.tandon.info/schools/reflections_isd/{entry_id}.html"
                                                          ))
        return judge_dashboard




@dataclass
class EntryJudged:
    entry_id: int
    entry_title: str
    judge_name: str
    completed: bool
    judge_score_interpretation: int
    judge_score_creativity: int
    judge_score_technique: int
    judge_score_total: int
    entry_url: str


if __name__ == '__main__':
    backend = JudgeScoresBackend()
    results = backend.lookup_judge_scores(judge_name="janet")
    pt = backend.to_pretty_table(entries=results)
    print(pt)