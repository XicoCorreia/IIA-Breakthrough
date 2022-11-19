from contextlib import redirect_stdout
import io
from sys import stdout
import unittest
import importlib

mod = importlib.import_module("IIA2223-proj-jog-40")
JogoBT_40 = getattr(mod, "JogoBT_40")


class TestJogoBT_40(unittest.TestCase):
    """
    Our basic test class
    """

    def setUp(self) -> None:
        self.stdout_buf = io.StringIO()

    def tearDown(self) -> None:
        redirect_stdout(stdout)

    def test_1(self):
        with redirect_stdout(self.stdout_buf):
            jj = JogoBT_40()
            jj.display(jj.initial)
            actual = self.stdout_buf.getvalue()
            expected = """-----------------
8|B B B B B B B B
7|B B B B B B B B
6|. . . . . . . .
5|. . . . . . . .
4|. . . . . . . .
3|. . . . . . . .
2|W W W W W W W W
1|W W W W W W W W
-+---------------
 |a b c d e f g h
--NEXT PLAYER: W
"""
            self.assertEqual(actual, expected)

    def test_2(self):
        with redirect_stdout(self.stdout_buf):
            jj = JogoBT_40()
            s1 = jj.initial
            print(jj.actions(s1))
            s2 = jj.result(s1, "a2-a3")
            print("Próximo a jogar: ", "W" if 1 == jj.to_move(s2) else "B")
            actual = self.stdout_buf.getvalue()
            expected = """['a2-a3', 'a2-b3', 'b2-a3', 'b2-b3', 'b2-c3', 'c2-b3', 'c2-c3', 'c2-d3', 'd2-c3', 'd2-d3', 'd2-e3', 'e2-d3', 'e2-e3', 'e2-f3', 'f2-e3', 'f2-f3', 'f2-g3', 'g2-f3', 'g2-g3', 'g2-h3', 'h2-g3', 'h2-h3']
Próximo a jogar:  B
"""
            self.assertEqual(actual, expected)

    def test_3(self):
        with redirect_stdout(self.stdout_buf):
            jj = JogoBT_40()
            s1 = jj.initial
            s2 = jj.result(s1, "g2-h3")
            jj.display(s2)
            actual = self.stdout_buf.getvalue()
            expected = """-----------------
8|B B B B B B B B
7|B B B B B B B B
6|. . . . . . . .
5|. . . . . . . .
4|. . . . . . . .
3|. . . . . . . W
2|W W W W W W . W
1|W W W W W W W W
-+---------------
 |a b c d e f g h
--NEXT PLAYER: B
"""
            self.assertEqual(actual, expected)

    def test_4(self):
        with redirect_stdout(self.stdout_buf):
            jj = JogoBT_40()
            s1 = jj.initial
            s2 = jj.executa(s1, ["g2-h3", "e7-f6"])
            jj.display(s2)
            print("Estado terminal? ", jj.terminal_test(s2))
            actual = self.stdout_buf.getvalue()
            expected = """-----------------
8|B B B B B B B B
7|B B B B . B B B
6|. . . . . B . .
5|. . . . . . . .
4|. . . . . . . .
3|. . . . . . . W
2|W W W W W W . W
1|W W W W W W W W
-+---------------
 |a b c d e f g h
--NEXT PLAYER: W
Estado terminal?  False
"""
            self.assertEqual(actual, expected)

    def test_5(self):
        with redirect_stdout(self.stdout_buf):
            jj = JogoBT_40()
            s = jj.executa(
                jj.initial,
                [
                    "f2-f3",
                    "e7-d6",
                    "d2-e3",
                    "d6-d5",
                    "b2-b3",
                    "d5-c4",
                    "a2-a3",
                    "c4-b3",
                    "e3-d4",
                    "b3-c2",
                    "e1-f2",
                    "c2-d1",
                ],
            )
            jj.display(s)
            print(jj.terminal_test(s))
            actual = self.stdout_buf.getvalue()
            expected = """-----------------
8|B B B B B B B B
7|B B B B . B B B
6|. . . . . . . .
5|. . . . . . . .
4|. . . W . . . .
3|W . . . . W . .
2|. . . . W W W W
1|W W W B . W W W
-+---------------
 |a b c d e f g h
True
"""
            self.assertEqual(actual, expected)

    def test_6(self):
        with redirect_stdout(self.stdout_buf):
            accoes = "a2-a3 a7-a6 c2-c3 a6-b5 b2-b3 b5-b4".split()
            jj = JogoBT_40()
            interessante = jj.executa(jj.initial, accoes)
            novas_accoes = jj.actions(interessante)
            outrointeressante = jj.result(interessante, novas_accoes[0])
            jj.display(interessante)
            print("Jogadas possíveis: ", novas_accoes)
            actual = self.stdout_buf.getvalue()
            expected = """-----------------
8|B B B B B B B B
7|. B B B B B B B
6|. . . . . . . .
5|. . . . . . . .
4|. B . . . . . .
3|W W W . . . . .
2|. . . W W W W W
1|W W W W W W W W
-+---------------
 |a b c d e f g h
--NEXT PLAYER: W
Jogadas possíveis:  ['a1-a2', 'a1-b2', 'a3-a4', 'a3-b4', 'b1-a2', 'b1-b2', 'b1-c2', 'b3-a4', 'b3-c4', 'c1-b2', 'c1-c2', 'c3-b4', 'c3-c4', 'c3-d4', 'd1-c2', 'd2-d3', 'd2-e3', 'e2-d3', 'e2-e3', 'e2-f3', 'f2-e3', 'f2-f3', 'f2-g3', 'g2-f3', 'g2-g3', 'g2-h3', 'h2-g3', 'h2-h3']
"""
            self.assertEqual(actual, expected)
