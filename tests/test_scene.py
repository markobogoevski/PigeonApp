import unittest
from itertools import combinations

from app import MIN_PIGEON_DISTANCE, build_scene
from jokes import JOKES


class SceneGenerationTest(unittest.TestCase):
    def test_scene_contract(self) -> None:
        for seed in range(100):
            scene = build_scene(seed)
            pigeons = scene["pigeons"]
            self.assertGreaterEqual(scene["count"], 8)
            self.assertLessEqual(scene["count"], 12)
            self.assertEqual(scene["count"], len(pigeons))

            kissing = [p for p in pigeons if p["behavior"] == "kiss"]
            self.assertEqual(2, len(kissing))
            self.assertEqual({"male", "female"}, {p["kind"] for p in kissing})
            self.assertEqual({"left", "right"}, {p["pairRole"] for p in kissing})

            left = next(p for p in kissing if p["pairRole"] == "left")
            right = next(p for p in kissing if p["pairRole"] == "right")
            self.assertLess(left["x"], right["x"])
            self.assertGreaterEqual(right["x"] - left["x"], 24)
            self.assertEqual("right", left["facing"])
            self.assertEqual("left", right["facing"])

            joke_pigeons = [p for p in pigeons if p["isJoker"]]
            self.assertEqual(scene["count"] - 2, len(joke_pigeons))
            self.assertEqual(len(joke_pigeons), len({p["joke"] for p in joke_pigeons}))
            self.assertTrue(all(p["joke"] in JOKES for p in joke_pigeons))

            for first, second in combinations(pigeons, 2):
                distance = (
                    (first["x"] - second["x"]) ** 2
                    + (first["y"] - second["y"]) ** 2
                ) ** 0.5
                self.assertGreaterEqual(
                    distance,
                    MIN_PIGEON_DISTANCE,
                    f"{first['id']} overlaps {second['id']} in seed {seed}",
                )

    def test_joke_bank_has_at_least_100_jokes(self) -> None:
        self.assertGreaterEqual(len(JOKES), 100)


if __name__ == "__main__":
    unittest.main()
