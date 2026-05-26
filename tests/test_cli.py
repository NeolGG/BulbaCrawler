from pokecrawler.cli import build_parser


class TestBuildParser:
    def test_defaults(self):
        args = build_parser().parse_args([])
        assert args.limit is None
        assert args.start_url is None
        assert args.output == "output"
        assert args.no_images is False
        assert args.concurrency == 5
        assert args.pokemon is None

    def test_all_flags_together(self):
        args = build_parser().parse_args(
            [
                "--limit",
                "5",
                "--concurrency",
                "3",
                "--output",
                "out",
                "--no-images",
                "--start-url",
                "https://example.com",
            ]
        )
        assert args.limit == 5
        assert args.concurrency == 3
        assert args.output == "out"
        assert args.no_images is True
        assert args.start_url == "https://example.com"

    def test_pokemon_single(self):
        args = build_parser().parse_args(["--pokemon", "Bulbasaur"])
        assert args.pokemon == ["Bulbasaur"]

    def test_pokemon_multiple(self):
        args = build_parser().parse_args(
            ["--pokemon", "Bulbasaur", "Eevee", "Gyarados"]
        )
        assert args.pokemon == ["Bulbasaur", "Eevee", "Gyarados"]
