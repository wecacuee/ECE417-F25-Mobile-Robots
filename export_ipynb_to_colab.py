import os
import os.path as osp
import nbformat

def main(notebookpath, mathaliasesnotebook, exportpath):
    with (open(notebookpath) as nbfp,
          open(mathaliasesnotebook) as mafp,
          open(exportpath, 'w') as exfp):
        nb = nbformat.read(nbfp, 4)
        ma = nbformat.read(mafp, 4)
        #print(nb['cells'][0])
        nb['cells'][0] = ma['cells'][0]
        print(f"Writing to '{exportpath}'")
        nbformat.write(nb, exfp)

def ensuredirs(path):
    os.makedirs(osp.dirname(path), exist_ok=True)
    return path

def colab_filepath_create(nfilepath):
    root, ext = osp.splitext(osp.basename(nbfilepath))
    return osp.join(osp.dirname(sys.argv[1]), "exports",
                    f"{root} Colab{ext}")

if __name__ == '__main__':
    import sys
    nbfilepath = sys.argv[1]
    colab_filepath = colab_filepath_create(nbfilepath)
    mathaliasesnotebook = osp.join(
            osp.dirname(__file__ or "."),
            "templates/math-aliases.ipynb")
    main(sys.argv[1], 
         mathaliasesnotebook,
         ensuredirs(colab_filepath))

