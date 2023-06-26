# Tight and Compact Model of the SAA-based Joint Chance-constrained OPF 🚀

## Goals 🖼️

The aim of this repository is to provide the details of the power systems data set and code used in paper [[1]](https://arxiv.org/abs/2205.03370). This article has been developed by some members of the [OASYS group](https://sites.google.com/view/groupoasys/home) thanks to the funding of project [Flexanalytics](https://groupoasysflexanalytics.readthedocs.io/en/latest/). We suggest that you visit the related links to know more about our research 😉

## Contents 🌌

This repository includes the main data of the work in [[1]](https://arxiv.org/abs/2205.03370). This data is sourced and extracted from [a Library of IEEE PES Power Grid Benchmarks](https://github.com/power-grid-lib/pglib-opf).

In the following links you can download the data related to generators, lines and loads of the different power systems used in this work, where each file has extension of ".csv" format.
  * [IEEE-RTS-24](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/IEEE-RTS-24)
  * [IEEE-57](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/IEEE-57)
  * [IEEE-RTS-73](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/IEEE-RTS-73)
  * [IEEE-118](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/IEEE-118)
  * [IEEE-300](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/IEEE-300)

Also, the repository includes Python scripts that encompass the codes for the OPF model, generating the valid inequalities for the line-flow constraints, and implementing the iterative coefficient algorithm.
  * [OPF](https://github.com/groupoasys/TC_SAA_JCC-OPF/blob/main/MIP_JCC-OPF.py)
  * [Valid Inequalities](https://github.com/groupoasys/TC_SAA_JCC-OPF/blob/main/Valid_Analysis.py)
  * [Iterative Coefficient Algorithm](https://github.com/groupoasys/TC_SAA_JCC-OPF/blob/main/tightening_screening.py)

Finally, the repository provides the data generated for each experiment in pickle format.
  * [Scenarios](https://drive.google.com/file/d/1mFTjQylx8EBrowXj5fln4pUGClRaJp-C/view?usp=sharing): This file comprises scenarios of forecast errors, derived from samples drawn from a multivariate normal distribution. It consists of 10 distinct sets of randomly generated samples. The pickle file contains a nested dictionary with two keys: the first key represents the system ('24', '57', '73', '118', and '300'), while the second key corresponds to the index from the sets of randomly generated samples (ranging from 0 to 9). Each value within the nested dictionary is a data frame with dimensions of 'number of scenarios' by 'number of nodes'.
  * [Valid_Inequalities](https://github.com/groupoasys/TC_SAA_JCC-OPF/tree/main/Data/Valid_Inequalities): The valid inequalities for the line-flow constraints were generated after running the [Valid_Analysis.py](https://github.com/groupoasys/TC_SAA_JCC-OPF/blob/main/Valid_Analysis.py) script. Each pickle file represents a nested dictionary with three keys: the first key corresponds to the index of the randomly generated sample set (ranging from 0 to 9), the second key refers to the type of line-flow constraint (either the lower-bound constraint denoted as 'min' or the upper-bound constraint denoted as 'max'), and the third key corresponds to the index of the line (ranging from 0 to 'number of lines'-1). Each value within the nested dictionary is a data frame containing the slope and intercept of each valid inequality, according to Corollary 2.5 of [[1]](https://arxiv.org/abs/2205.03370).

## References 📚
[1] Á. Porras, C. Domínguez, J. M. Morales and S. Pineda "Tight and Compact Sample Average Approximation for Joint Chance-constrained Problems with Applications to Optimal Power Flow," INFORMS Journal on Computing, 2023.

## How to cite the repository and the paper? 📝

If you want to cite [this repository](https://github.com/groupoasys/TC_SAA_JCC-OPF), please use the following bib entries:


* Repository:
```
@article{TCSAAJCCOPF2023,
author = {OASYS},
journal = {GitHub repository (https://github.com/groupoasys/TC{\_}SAA{\_}JCC-OPF)},
title = {{Data and Code for a Tight and Compact Model of the {SAA}-based Joint Chance-constrained {OPF}}},
url = {https://github.com/groupoasys/TC_SAA_JCC-OPF},
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
