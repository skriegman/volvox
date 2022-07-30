import numpy as np
from lxml import etree

SEEDS = range(0, 10)

fit_dict = {}
for s in SEEDS:  
    try:
        root = etree.parse("output{0}.xml".format(s)).getroot()
        fitness = np.abs(float(root.findall("detail/bot_0/fitness_score")[0].text))
        fit_dict[s] = fitness

    except (IOError, IndexError):
        pass
      

sorted_ids = [k for k, v in sorted(fit_dict.items(), key=lambda item: item[1])]
sorted_fits = [v for k, v in sorted(fit_dict.items(), key=lambda item: item[1])]

worst = sorted_ids[0]
best = sorted_ids[-1]

print("Best: id", best, ", fit ", fit_dict[best], "; Worst: id ", worst, ", fit ", fit_dict[worst])
