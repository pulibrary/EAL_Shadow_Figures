from pathlib import Path
from shadows import ShadowFigureSiteGenerator, TypePage


# data = Path("shadowfigures_test.csv")
data = Path('shadowfigures.csv')
site_dir = Path("site")
# image_page_dir = site_dir / Path("image_pages")
image_page_dir = Path("image_pages")
image_dir = Path("images")

site_gen: ShadowFigureSiteGenerator = ShadowFigureSiteGenerator(data)
for page in site_gen.type_pages:
    page.render(site_dir, image_page_dir)

for page in site_gen.image_pages:
    page.render(site_dir, image_page_dir, image_dir)
