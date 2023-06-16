# Tight and Compact Model of the SAA-based Joint Chance-constrained OPF 🚀

## Goals 🖼️

The aim of this repository is to provide the details of the power systems data set and code used in paper [[1]](https://arxiv.org/abs/2205.03370). This article have been developed by some members of the [OASYS group](https://sites.google.com/view/groupoasys/home) thanks to the funding of the project [Flexanalytics](https://groupoasysflexanalytics.readthedocs.io/en/latest/). We suggest you to visit the related links to know more our research 😉

## Contents 🌌

This repository includes the main code and data of the work in [[1]](https://arxiv.org/abs/2205.03370). The data is extracted from a [repository of power grids](https://github.com/power-grid-lib/pglib-opf).

In the next links, you can find data related to generators, lines and loads of the different power systems used in this work, where each file is in ".csv" format.

  * [IEEE-RTS-24](https://drive.google.com/drive/folders/1bO0Zn1_U4spsLt_2FPnbdsLW4C78i_ZO?usp=sharing)
  * [IEEE-57](https://drive.google.com/drive/folders/1kO8rQRfdZKqfCArPLtQZNoMAiXTiBOrs?usp=sharing)
  * [IEEE-RTS-73](https://drive.google.com/drive/folders/1DVXbJ0h5zM5-bKg2UncwBBIW5-ftdd1R?usp=sharing)
  * [IEEE-118](https://drive.google.com/drive/folders/11X14_FxIf98eQvsDFQ0xjymZpXgR9SPy?usp=sharing)
  * [IEEE-300](https://drive.google.com/drive/folders/1fDDxe76KOYHGac9IoY9s4j5O7U-RGuvT?usp=sharing)


  * [Scenarios](https://drive.google.com/file/d/1mFTjQylx8EBrowXj5fln4pUGClRaJp-C/view?usp=sharing)
  * [Valid_Inequalities](https://drive.google.com/drive/folders/1UGhFqqvzIf7sk4MEgeJ1--cOvYBULubg?usp=sharing)

The codes of the OPF model, of generating the valid inequalities and of the iterative coefficient algorithm are provided in the following Python scripts:
  * [OPF]()
  * [Valid Inequalities](https://github.com/groupoasys/TC_SAA_JCC-OPF/blob/main/Valid_Analysis.py)
  * [Iterative Coefficient Algorithm]()

## References 📚
[1] Á. Porras, C. Domínguez, J. M. Morales and S. Pineda "Tight and Compact Sample Average Approximation of Joint Chance-cosntrained Problems with Applications to Optimal Power Flow," 2023.

## How to cite the repository and the paper? 📝

If you want to cite [this repository](https://github.com/groupoasys/TC_SAA_JCC-OPF), please use the following bib entries:


* Repository:
```
@article{TCSAAJCCOPF2023,
author = {OASYS},
journal = {GitHub repository (https://github.com/groupoasys/TC{\_}SAA{\_}JCC-OPF)},
title = {{Data and Code for the {SAA}-based Joint Chance-constrained {OPF}}},
url = {https://github.com/groupoasys/TC{\_}SAA{\_}JCC-OPF},
year = {2023}
}
```

## Do you want to contribute? 👨🏾‍🔬
 
 Please, do it ☺ Any feedback is welcome 🤩 so feel free to ask or comment anything you want via a Pull Request in this repo.
 If you need extra help, you can ask Álvaro Porras (alvaroporras19@gmail.com).

 ## Contributors 👑
 
 * [OASYS group](http://oasys.uma.es) -  groupoasys@gmail.com
 
 ## Developed by 👨🏾‍💻
 * [Álvaro Porras](https://www.researchgate.net/profile/Alvaro-Porras-Cabrera) - alvaroporras19@gmail.com

 ## License 📝
 
    Copyright 2021 Optimization and Analytics for Sustainable energY Systems (OASYS)

    Licensed under the GNU General Public License, Version 3 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.gnu.org/licenses/gpl-3.0.en.html

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
