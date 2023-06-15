import argparse

from pathlib import Path
from shadows import ShadowFigureSiteGenerator

parser = argparse.ArgumentParser(
    description="Builds EAL Shadow Figures site",
)

parser.add_argument('csvfile', default="shadowfigures.csv")
parser.add_argument('sitedir', default="site")

# # data = Path("shadowfigures_test.csv")
# data = Path('shadowfigures.csv')
# site_dir = Path("site")

# site_gen: ShadowFigureSiteGenerator = ShadowFigureSiteGenerator(data)
# site_gen.generate(site_dir)
args = parser.parse_args()
print(args)

site_generator = ShadowFigureSiteGenerator(Path(args.csvfile))
site_generator.generate(site_dir=Path(args.sitedir))
