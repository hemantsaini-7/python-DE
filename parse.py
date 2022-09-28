import pandas as pd
import xml.etree.ElementTree as Tree
import os
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile


class Parse:
    def __init__(self, path=None, url=None) -> None:
        self.path = path
        self.url = url
        self.download()

    def download(self):
        with urlopen(self.url) as response:
            with ZipFile(BytesIO(response.read())) as z:
                z.extractall(self.path)

    def parse(self) -> None:
        filepath = None
        for (dirpath, dirnames, filenames) in os.walk(path):
            for f in filenames:
                if ".xml" in f:
                    filepath = os.path.join(self.path, f)

        tree = Tree.parse(filepath)
        root = tree.getroot()
        parent = 'TermntdRcrd'
        pattern = 'FinInstrmGnlAttrbts'
        tag = 'Issr'
        children = ['Id', 'FullNm', 'ClssfctnTp', 'CmmdtyDerivInd', 'NtnlCcy']
        cols = [pattern + '.' + k for k in children]
        cols.append(tag)
        rows = list()
        for i in root.iter():
            if parent in i.tag:
                entry = [None for x in range(len(children) + 1)]
                for child in i:
                    if pattern in child.tag:
                        for c in child:
                            for k in range(len(children)):
                                if children[k] in c.tag:
                                    entry[k] = c.text
                    if tag in child.tag:
                        entry[5] = child.text
                rows.append(entry)
        df = pd.DataFrame(data=rows, columns=cols)
        df.to_csv(os.path.join(self.path, 'final_solution.csv'), index=False)


if __name__ == '__main__':
    path = os.pardir
    url = 'http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip'

    p = Parse(path=path, url=url)
    p.parse()
