import csv
import os
from typing import List, Dict, Any

from prettytable import PrettyTable

from src.student_info import StudentInfo

# todo in the future: fix bug in forms.html -- missing art title

class ReflectionsJudge:
    def __init__(self, judge_name: str, expertise_in_category: str):
        self.judge_name = judge_name.lower().strip()
        self.expertise_in_category = expertise_in_category.lower().strip()
        self.is_expert = self.expertise_in_category != ""

    def __hash__(self):
        return hash(self.judge_name)

    def __eq__(self, other: "ReflectionsJudge"):
        return self.judge_name == other.judge_name

    def __repr__(self):
        return f"{self.judge_name} {('(' + self.expertise_in_category + ')' if self.expertise_in_category else '').strip()}"

class ReflectionsJudgeScore:
    def __init__(self, judge: ReflectionsJudge, csv_entry_dict: Dict[str, Any]):
        self.judge = judge
        self.interpretation: int = int(csv_entry_dict['interpretation'].lower().strip())
        self.interpretation_comments = csv_entry_dict['interpretation_comments']
        self.creativity: int = int( csv_entry_dict['creativity'].lower().strip())
        self.creativity_comments = csv_entry_dict['creativity_comments']
        self.technique: int = int( csv_entry_dict['technique'].lower().strip())
        self.technique_comments = csv_entry_dict['technique_comments']
        self.other_comments = csv_entry_dict['other_comments']
        self.is_coi: bool = csv_entry_dict['coi'].lower().strip() == "yes"
        self.confidence = csv_entry_dict['confidence']  # Sort of confident, Not confident, Very confident
        self.entry_category = csv_entry_dict['entry_category']
        self.unweighted_score = self.compute_total_score()
        # self.weighted_score = self.compute_weighted_score()
        self.weighted_score_v2 = self.compute_weighted_score_v2()
        self.weighted_by_confidence_score = self.compute_weighted_by_confidence_score()

    def compute_total_score(self):
        return self.interpretation + self.creativity + self.technique

    def compute_weighted_by_confidence_score(self):
        wt = 0.0
        if self.confidence == "Sort of confident":
            wt = 0.66
        elif self.confidence == "Very confident":
            wt = 1.0
        elif self.confidence == "Not confident":
            wt = 0.33
        return wt * self.unweighted_score

    def compute_weighted_score_v2(self):
        wt = 0.0
        if self.confidence == "Sort of confident":
            wt = 0.66
        elif self.confidence == "Very confident":
            wt = 1.0
        elif self.confidence == "Not confident":
            wt = 0.33

        if self.judge.expertise_in_category.lower() != self.entry_category.lower():
            wt = 0.5 * wt
        return wt * self.unweighted_score

    # def compute_weighted_score(self):
    #     wt = 0.0
    #     if self.confidence == "Sort of confident":
    #         wt = 0.66
    #     elif self.confidence == "Very confident":
    #         wt = 1.0
    #     elif self.confidence == "Not confident":
    #         wt = 0.33
    #
    #     if self.judge.expertise_in_category == self.entry_category:
    #         wt = 2.0 * wt
    #     return wt * self.unweighted_score

    def __repr__(self):
        confidence_red_alert = f"{self.confidence}" if self.confidence!="Very confident" else ""
        return f"{self.judge.judge_name}: {self.unweighted_score} {confidence_red_alert}"

class ReflectionsEntry:
    def __init__(self,
                 entry_id,
                 student_info: StudentInfo,
                 judges_scores: List[ReflectionsJudgeScore],
                 entry_file_types,
                 entry_urls,
                 entry_category,
                 entry_statement
                 ):
        self.entry_id = entry_id
        self.student_info = student_info
        self.judges_scores: List[ReflectionsJudgeScore] = []
        for j in judges_scores:
            self.add_judge_score(j)
        self.judges_score_dict: Dict[str, ReflectionsJudgeScore] = {x.judge.judge_name:x.unweighted_score for x in judges_scores}
        self.urls = entry_urls
        self.file_types = entry_file_types
        self.category = entry_category
        self.statement = entry_statement

    def add_judge_score(self, judge_score: ReflectionsJudgeScore):
        # do not allow repeated entries, remove the previous entry for this judge, and add the new entry.
        duplicate_indices = []
        for idx, x in enumerate(self.judges_scores):
            if x.judge == judge_score.judge:
                duplicate_indices.append(idx)
        for idx in duplicate_indices:
            self.judges_scores.pop(idx)
        self.judges_scores.append(judge_score)
        self.judges_score_dict[judge_score.judge.judge_name] = judge_score

    def __hash__(self):
        return hash(self.entry_id)

    def __eq__(self, other: "ReflectionsEntry"):
        return self.entry_id == other.entry_id


class ReflectionsResult:
    def __init__(self, entry: ReflectionsEntry, ignore_coi: bool, min_num_judges_per_entry:int, all_judges: List[ReflectionsJudge]):
        # retain the last judge scoring entry from csv only
        self.judges_yet_to_complete = []
        self.entry = entry
        self.judges_scores = entry.judges_scores
        self.ignore_coi = ignore_coi
        self.min_num_judges_per_entry = min_num_judges_per_entry
        self.scoring_complete: bool = self.access_if_scoring_is_complete(all_judges)
        self.num_judges = len(self.judges_scores)
        self.weighted_avg_score = self.get_weighted_sum_of_scores()/self.num_judges
        self.unweighted_avg_score = self.get_unweighted_sum_of_scores()/self.num_judges
        self.weighted_by_confidence_avg_score = self.get_weighted_by_confidence_sum_of_scores()/self.num_judges
        # self.max_formula_score = self.get_max_formula_sum_of_scores()
        self.max_formula_v2_score = self.get_max_formula_v2_avg_of_scores()
        self.max_formula_v3_score = self.get_max_formula_v3_avg_of_scores()

    def access_if_scoring_is_complete(self, all_judges: List[ReflectionsJudge]):
        # Atleast one expert judge has scored. Make sure the judge has not marked it as a COI if we care about COIs.
        expert_looked_at_it = any([judge_score.judge.is_expert and (self.ignore_coi or not judge_score.is_coi) for judge_score in self.judges_scores])
        if not expert_looked_at_it:
            expected_expert = [j for j in all_judges if j.expertise_in_category.lower() == self.entry.category.lower()]
            self.judges_yet_to_complete.extend(expected_expert or ["need_expert"])
        sufficient_judges = len(self.judges_scores) >= self.min_num_judges_per_entry
        if not sufficient_judges:
            # get more general judges
            num_short = self.min_num_judges_per_entry - len(self.judges_scores)
            remind_these_general_judges = [x for x in all_judges if x.expertise_in_category=="" and x.judge_name not in self.entry.judges_score_dict]
            # not sure which of the list of general judges who didn't evaluate to remind so list everything.
            self.judges_yet_to_complete.extend(remind_these_general_judges or ["need_general"])
        return expert_looked_at_it and sufficient_judges

    # def get_max_formula_sum_of_scores(self):
    #     non_expert_scores = [judge_score for judge_score in self.judges_scores if not judge_score.judge.is_expert]
    #     expert_scores = [judge_score for judge_score in self.judges_scores if judge_score.judge.is_expert]
    #     total_relevant_judges = len(expert_scores) + 1  # only 1 non-expert is considered
    #     return (max([x.weighted_score for x in non_expert_scores]) + sum([x.weighted_score for x in expert_scores]))/ total_relevant_judges

    def get_max_formula_v2_avg_of_scores(self):
        non_expert_scores = [judge_score for judge_score in self.judges_scores if not judge_score.judge.is_expert]
        expert_scores = [judge_score for judge_score in self.judges_scores if judge_score.judge.is_expert]
        total_relevant_judges = len(expert_scores) + 1  # only 1 non-expert is considered
        return (max([x.weighted_score_v2 for x in non_expert_scores]) + sum([x.weighted_score_v2 for x in expert_scores]))/total_relevant_judges

    # accounts for missing non-expert reviews or low-confidence only non-expert review and high confidence expert review
    def get_max_formula_v3_avg_of_scores(self, HIGH_CONF_THRESHOLD=84):
        non_expert_scores = [judge_score for judge_score in self.judges_scores if not judge_score.judge.is_expert]
        expert_scores = [judge_score for judge_score in self.judges_scores if judge_score.judge.is_expert]
        has_singleton_not_confidenct_non_expert = False
        has_very_high_confidence_expert = sum([x.weighted_score_v2 for x in expert_scores])/len(expert_scores) >= HIGH_CONF_THRESHOLD if len(expert_scores)>=1 else False
        if len(non_expert_scores) == 1 and non_expert_scores[0].confidence!="Very confident":
            has_singleton_not_confidenct_non_expert = True
        if not has_singleton_not_confidenct_non_expert and len(expert_scores)>= 1:  # this is the usual case.
            total_relevant_judges = len(expert_scores) + 1  # only 1 non-expert is considered
            return (max([x.weighted_score_v2 for x in non_expert_scores]) + sum([x.weighted_score_v2 for x in expert_scores]))/total_relevant_judges
        elif has_singleton_not_confidenct_non_expert and len(expert_scores) >= 1 and has_very_high_confidence_expert:  # this is the exception case that must account for missing non-expert or their low confidence. Focus on the expert's score
            total_relevant_judges = len(expert_scores) + 0  # 0 non-expert is considered
            return sum([x.weighted_score_v2 for x in expert_scores])/total_relevant_judges
        elif has_singleton_not_confidenct_non_expert and len(expert_scores) >= 1 and not has_very_high_confidence_expert:  # this is the exception case that must account for missing non-expert or their low confidence. AND cannot focus on the expert's score
            total_relevant_judges = len(expert_scores) + 1  # only 1 non-expert is considered
            return (max([x.weighted_score_v2 for x in non_expert_scores]) + sum([x.weighted_score_v2 for x in expert_scores]))/total_relevant_judges
        elif has_singleton_not_confidenct_non_expert and len(expert_scores) == 0:
            # no expert score and not enough high confident non-expert scores
            print(f"Score max formula v3: Entry {self.entry.entry_id} requires atleast one expert to review!! For now considering non-expert's low confidence score: ({self.judges_scores})")
            return max([x.weighted_score_v2 for x in non_expert_scores])/1
        else:
            print(f"Score max formula v3: Entry {self.entry.entry_id} is in an unusual spot in v3:  ({self.judges_scores})")

    def get_weighted_sum_of_scores(self):
        return sum([x.weighted_score_v2 for x in self.judges_scores])

    def get_unweighted_sum_of_scores(self):
        return sum([x.unweighted_score for x in self.judges_scores])

    def get_weighted_by_confidence_sum_of_scores(self):
        return sum([x.weighted_by_confidence_score for x in self.judges_scores])

    def __repr__(self):
        return f"scoring complete = {self.scoring_complete}, weighted score = {self.weighted_avg_score}, unweighted_score={self.unweighted_avg_score}, dict of scores = {self.judges_scores}"

    @classmethod
    def mk_pretty_table(cls, result_list: List["ReflectionsResult"]) -> PrettyTable:
        p = PrettyTable()
        p.field_names = ["entry id", "evaluation completed", "category", "remind these judges", "list of scores", "student name", "points_weighted_by_confidence", "points_weighted_by_expertise_and_confidence", "points_unweighted", "points_max_formula","points_max_formula_addresses_singleton_non_expert", "grade", "student info", "entry statement", "entry info urls", "entry email"]
        for result in result_list:
            remind_judges = result.judges_yet_to_complete
            p.add_row([result.entry.entry_id, result.scoring_complete, result.entry.category, remind_judges or "", result.entry.judges_scores, result.entry.student_info.get_formal_abbreviated_name(), result.weighted_by_confidence_avg_score, result.weighted_avg_score, result.unweighted_avg_score, result.max_formula_v2_score,result.max_formula_v3_score, result.entry.student_info.grade, result.entry.student_info.__repr__(), result.entry.statement, result.entry.urls.replace("\n",", "), result.entry.student_info.email])
        p.reversesort = True
        p.sortby = "points_max_formula_addresses_singleton_non_expert"
        p.sort_key = lambda x: float(x[0])
        p.align['student info'] = 'l'
        p.align['remind these judges'] = 'l'
        p.align['list of scores'] = 'l'
        p.align['student name'] = 'l'
        p.float_format = "4.2"
        return p

def create_entries(judges_scores_fp: str, judges_expertise: Dict[str, str]) -> List[ReflectionsEntry]:
    # one student can have multiple entries, and multiple entries can be selected from one student.
    d: Dict[ReflectionsEntry, List[ReflectionsJudgeScore]] = {}

    with open(judges_scores_fp) as infile:
        for j in csv.DictReader(infile):
            student_info = StudentInfo(f_name = j['entry_student_first_name'],
                                       l_name = j['entry_student_last_name'],
                                       teacher = j['entry_student_teacher_name'],
                                       grade = j['entry_grade'],
                                       email = j['entry_parent_email_id']
                                       )
            entry = ReflectionsEntry(entry_id=j['entry_id'],
                                     entry_category=j['entry_category'],
                                     entry_file_types=j['entry_file_types'],
                                     entry_urls=j['entry_urls'],
                                     entry_statement=j['entry_statement'],
                                     student_info=student_info,
                                     judges_scores=[])
            judge_name = j['judge_name'].lower().strip()
            assert judge_name in judges_expertise, f"Judge name {judge_name} not found in {judges_expertise}"
            judge = ReflectionsJudge(judge_name=judge_name, expertise_in_category=judges_expertise[judge_name])
            if entry not in d:
                d[entry] = []
            d[entry].append(ReflectionsJudgeScore(judge=judge, csv_entry_dict=j))

    # create entries to evaluate
    entries: List[ReflectionsEntry] = []
    for entry, judge_scores in d.items():
        for j in judge_scores:
            entry.add_judge_score(j)
        entries.append(entry)
    return entries


def create_report_for_judges(reflections_entries, judges_expertise, reveal_score:bool):
    names_of_judges = sorted(list(judges_expertise.keys()))
    entry_dict = {x.entry_id: x for x in reflections_entries}
    entry_ids = sorted([r.entry_id for r in reflections_entries])
    p = PrettyTable()
    p.field_names = ["entry_id", "category", *names_of_judges, "urls"]
    p.sortby = "entry_id"
    p.sort_key = lambda x: int(x[0])
    for entry_id in entry_ids:
        entry = entry_dict[entry_id]
        judges_completed = ['x' if n not in entry.judges_score_dict else (entry.judges_score_dict[n].unweighted_score if reveal_score else u'\u2713') for n in names_of_judges]
        p.add_row([entry_id, entry.category, *judges_completed, entry.urls.replace("\n",", ")])
    return p


def main(judges_scores_fp: str, judges_expertise: Dict[str, str], ignore_coi: bool, min_num_judges_per_entry:int, reveal_score_in_report: bool) -> (PrettyTable, PrettyTable):
    judges_expertise = {k.lower(): v for k, v in judges_expertise.items()}
    judges_all_objs = [ReflectionsJudge(judge_name=j_name, expertise_in_category=j_expertise) for j_name, j_expertise in judges_expertise.items()]
    assert os.path.exists(judges_scores_fp), f"Check judges scores file path: {judges_scores_fp}"
    reflections_entries = create_entries(judges_scores_fp=judges_scores_fp, judges_expertise=judges_expertise)
    entries_report: PrettyTable = create_report_for_judges(reflections_entries=reflections_entries, judges_expertise= judges_expertise, reveal_score=reveal_score_in_report)
    reflections_results = [ReflectionsResult(entry=entry, ignore_coi=ignore_coi, min_num_judges_per_entry=min_num_judges_per_entry, all_judges=judges_all_objs) for entry in reflections_entries]
    return ReflectionsResult.mk_pretty_table(reflections_results), entries_report


if __name__ == '__main__':
    # Visual Arts
    # Music composition
    # Literature
    # Film/Video
    # Photography
    sample_judges_expertise: Dict[str, str] = {
        "shweta": "Visual Arts",
        "whitney": "Music composition",
        "thom": "Literature",
        "trisha": "",
        "dhivya priya v": ""
    }
    results, report = main(judges_scores_fp="data/judges_output/scores-submission-v2-data.csv",
         judges_expertise=sample_judges_expertise,
         min_num_judges_per_entry=3,
         ignore_coi=False,
         reveal_score_in_report=False
         )
    print(results)
    print(f"\n\n{'*'*80}\n")
    print(report)
