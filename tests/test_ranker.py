import unittest
from datetime import date

from app import create_app
from app.features import (education_level, estimate_experience_years,
                          extract_email, required_years)
from app.scorer import rank_resumes
from app.skills import extract_skills

JD = ("Machine Learning Engineer, 2+ years experience, Bachelor's degree. "
      "Python, pandas, scikit-learn, TensorFlow, NLP, Flask, Docker, Git.")

STRONG = ("Asha Rao\nasha@example.com\nML engineer, 4 years. Python, pandas, scikit-learn, "
          "TensorFlow, NLP, Flask, Docker, Git.\nB.Tech Computer Science\nEngineer (2021 - Present)")
WEAK = "Ravi Kumar\nravi@example.com\nFresher. Knows HTML and CSS. Diploma in electronics."


class SkillTests(unittest.TestCase):
    def test_word_boundaries(self):
        self.assertIn("javascript", extract_skills("I write JavaScript daily"))
        self.assertNotIn("java", extract_skills("I write JavaScript daily"))

    def test_symbols_and_aliases(self):
        found = extract_skills("C++, C#, Node.js, sklearn and k8s")
        for s in ("c++", "c#", "node.js", "scikit-learn", "kubernetes"):
            self.assertIn(s, found)


class FeatureTests(unittest.TestCase):
    def test_experience_from_ranges_merges_overlap(self):
        text = "A (2018 - 2020)\nB (2019 - 2022)"
        self.assertEqual(estimate_experience_years(text, today=date(2025, 1, 1)), 4.0)

    def test_present_and_explicit_years(self):
        self.assertEqual(estimate_experience_years("Dev (Jan 2022 - Present)", date(2026, 1, 1)), 4.0)
        self.assertEqual(estimate_experience_years("7+ years in backend", date(2026, 1, 1)), 7.0)

    def test_required_years_and_education(self):
        self.assertEqual(required_years("Need 3+ years of Python"), 3.0)
        self.assertEqual(education_level("M.Tech in AI"), 3)
        self.assertEqual(education_level("B.E. in CS"), 2)
        self.assertEqual(education_level("nothing here"), 0)

    def test_email(self):
        self.assertEqual(extract_email("mail me: a.b@x.io please"), "a.b@x.io")


class RankingTests(unittest.TestCase):
    def test_strong_beats_weak_and_ranks_are_sequential(self):
        out = rank_resumes(JD, {"strong.txt": STRONG, "weak.txt": WEAK})
        self.assertEqual([c.filename for c in out], ["strong.txt", "weak.txt"])
        self.assertEqual([c.rank for c in out], [1, 2])
        self.assertGreater(out[0].score, out[1].score)
        self.assertTrue(0 <= out[1].score <= out[0].score <= 100)

    def test_missing_skills_are_reported(self):
        out = rank_resumes(JD, {"weak.txt": WEAK})[0]
        self.assertIn("python", out.missing_skills)

    def test_empty_input(self):
        self.assertEqual(rank_resumes(JD, {}), [])


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def _post(self, url):
        import io
        return self.client.post(url, data={
            "job_description": JD,
            "resumes": [(io.BytesIO(STRONG.encode()), "strong.txt"),
                        (io.BytesIO(WEAK.encode()), "weak.txt"),
                        (io.BytesIO(b"x"), "bad.exe")],
        }, content_type="multipart/form-data")

    def test_pages(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").json["status"], "ok")

    def test_api(self):
        r = self._post("/api/rank")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["candidates"][0]["filename"], "strong.txt")
        self.assertTrue(any("bad.exe" in w for w in r.json["warnings"]))

    def test_ui_and_downloads(self):
        r = self._post("/rank")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        rid = html.split("/download/")[1].split(".pdf")[0]
        self.assertTrue(self.client.get(f"/download/{rid}.csv").data.startswith(b"\xef\xbb\xbfRank"))
        self.assertTrue(self.client.get(f"/download/{rid}.pdf").data.startswith(b"%PDF"))
        self.assertEqual(self.client.get("/download/nope.pdf").status_code, 404)

    def test_validation_errors(self):
        r = self.client.post("/rank", data={"job_description": "short"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
