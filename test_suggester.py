import unittest
from datetime import time as Time

from suggester import suggest_tasks, validate, assign_times, fallback_items


def minutes(t):
    return t.hour * 60 + t.minute


def no_overlap(sugs, busy=()):
    ivs = list(busy) + [(minutes(s.start_time), s.duration) for s in sugs]
    ivs.sort()
    return all(a[0] + a[1] <= b[0] for a, b in zip(ivs, ivs[1:]))


def bad_llm(name, species):
    raise RuntimeError("down")


class TestFallback(unittest.TestCase):
    def test_cat_gets_litter_and_no_walk(self):
        sugs, source = suggest_tasks("Jiji", "cat", llm=bad_llm)
        titles = [s.title for s in sugs]
        self.assertEqual(source, "fallback")
        self.assertEqual(titles, ["Feed Jiji", "Scoop Litter Box", "Play with Jiji"])

    def test_dog_gets_walk_and_no_litter(self):
        sugs, _ = suggest_tasks("Max", "dog", llm=bad_llm)
        titles = [s.title for s in sugs]
        self.assertIn("Walk Max", titles)
        self.assertFalse(any("litter" in t.lower() for t in titles))

    def test_other_species(self):
        sugs, _ = suggest_tasks("Kiwi", "other", llm=bad_llm)
        self.assertTrue(2 <= len(sugs) <= 3)


class TestValidation(unittest.TestCase):
    def good(self, title="Feed Max"):
        return {"title": title, "duration": 10, "priority": "high", "preferred_time": "08:00"}

    def test_drops_litter_for_dog(self):
        out = validate([self.good(), self.good("Scoop Litter Box")], "dog")
        self.assertEqual([o[0] for o in out], ["Feed Max"])

    def test_drops_bad_schema(self):
        bad = [
            {"title": "x", "duration": 0, "priority": "high", "preferred_time": "08:00"},
            {"title": "x", "duration": 10, "priority": "urgent", "preferred_time": "08:00"},
            {"title": "x", "duration": 10, "priority": "low", "preferred_time": "noon"},
            {"title": "x"},
            "garbage",
        ]
        self.assertEqual(validate(bad, "cat"), [])

    def test_dedupes_and_caps_at_three(self):
        raw = [self.good("A"), self.good("a"), self.good("B"), self.good("C"), self.good("D")]
        self.assertEqual([o[0] for o in validate(raw, "cat")], ["A", "B", "C"])

    def test_non_list_is_empty(self):
        self.assertEqual(validate({"title": "x"}, "cat"), [])


class TestLLMPath(unittest.TestCase):
    def test_valid_llm_output_used(self):
        raw = [
            {"title": "Feed Jiji", "duration": 10, "priority": "high", "preferred_time": "08:00"},
            {"title": "Play with Jiji", "duration": 15, "priority": "med", "preferred_time": "18:00"},
        ]
        sugs, source = suggest_tasks("Jiji", "cat", llm=lambda n, s: raw)
        self.assertEqual(source, "ai")
        self.assertEqual(len(sugs), 2)

    def test_too_few_valid_falls_back(self):
        raw = [{"title": "Scoop Litter Box", "duration": 10, "priority": "med", "preferred_time": "08:00"}]
        sugs, source = suggest_tasks("Max", "dog", llm=lambda n, s: raw)
        self.assertEqual(source, "fallback")
        self.assertIn("Walk Max", [s.title for s in sugs])


class TestTimes(unittest.TestCase):
    def test_avoids_existing_task(self):
        busy = [(8 * 60, 30)]  # 08:00-08:30
        sugs, _ = suggest_tasks("Max", "dog", busy, llm=bad_llm)
        self.assertTrue(no_overlap(sugs, busy))
        self.assertEqual(len(sugs), 3)

    def test_suggestions_do_not_overlap_each_other(self):
        items = [("A", 60, "low", Time(9, 0)), ("B", 60, "low", Time(9, 0)), ("C", 60, "low", Time(9, 0))]
        sugs = assign_times(items, [])
        self.assertEqual(len(sugs), 3)
        self.assertTrue(no_overlap(sugs))

    def test_fully_booked_day_places_nothing(self):
        sugs = assign_times(fallback_items("Max", "dog"), [(6 * 60, 16 * 60)])
        self.assertEqual(sugs, [])


if __name__ == "__main__":
    unittest.main()
