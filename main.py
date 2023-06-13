from pathlib import Path
from shadows import ShadowFigureSiteGenerator


# data = Path("shadowfigures_test.csv")
data = Path('shadowfigures.csv')
site_dir = Path("site")

site_gen: ShadowFigureSiteGenerator = ShadowFigureSiteGenerator(data)
site_gen.generate(site_dir)
