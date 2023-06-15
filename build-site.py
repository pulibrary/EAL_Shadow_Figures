import argparse

from pathlib import Path
from shadows import ShadowFigureSiteGenerator

parser = argparse.ArgumentParser(
    description="Builds EAL Shadow Figures site",
)

parser.add_argument('--csvfile', default="shadowfigures.csv")
parser.add_argument('--sitedir', default="site")

args = parser.parse_args()

print("Generating site...")
site_generator = ShadowFigureSiteGenerator(Path(args.csvfile))
site_generator.generate(site_dir=Path(args.sitedir))
print("Finished generating site")
