from collections import Counter
from io import StringIO

from pokemon_tcg_simulate import output


class TestOutput:
    def test_avg(self):
        assert output.avg(Counter([1, 2, 3])) == 2.0
        assert output.avg(Counter()) is None

    def test_percentiles(self):
        # TODO: enough values to hit all percentiles
        assert output.percentiles(Counter([1, 2, 3])) == [3]  # only 50th percentile
        assert output.percentiles(Counter([])) == []

    def test_dump_histograms(self):
        hist = {"a": Counter([1, 2, 3]), "b": Counter([4, 5])}
        file = StringIO()
        output.dump_histograms(hist, file=file)
        file.seek(0)
        expected_output = "opened,a,b\n0,0,0\n1,1,0\n2,1,0\n3,1,0\n4,0,1\n5,0,1\n"
        assert file.getvalue() == expected_output
