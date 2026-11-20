# PAI-Web publication DOI metadata audit — 2026-11-21

Scope: PR #165, 68 unique DOI-linked publications in `data/publications.json` (49) and `data/publications-archive.json` (19). This is an **incremental evidence log**, **not** a claim that all 68 records have been fully verified against live IEEE Xplore metadata.

## Publication states and evidence for three new DOIs

| DOI | Title/authors | Publication / volume-issue / pages | Evidence | Action/status |
| --- | --- | --- | --- | --- |
| `10.1109/TWC.2026.3747782` | Periodically Anchored Gradient Tracking for Over-the-Air Decentralized Federated Learning with Finite-Time Consensus; Hexin Feng, Rui Wang, Erwu Liu, Wei Ni, Abbas Jamalipour | IEEE Transactions on Wireless Communications, **vol. 25, pp. 25874–25890, 2026**; IEEE Xplore lists **27 October 2026** as Date of Publication. No issue number shown in supplied metadata. | **IEEE Xplore Metadata screenshot supplied by the project owner (IMG_3547.png)**; https://doi.org/10.1109/TWC.2026.3747782 | Updated canonical JSON and both language pages with confirmed volume/pages; do not infer issue number. |
| `10.1109/MIOT.2026.3707892` | Task-Oriented Framework for Communication-Efficient Federated Learning: From Isolated Optimization to Holistic Synergy; Fan Pan, Yan Liu, Erwu Liu, Arumugam Nallanathan | IEEE Internet of Things Magazine; Queen Mary institutional record shows online-first `PP (99), 1–6`, **not evidence of a finalized issue assignment** | https://www.seresearch.qmul.ac.uk/cncs/publications/2026/ ; https://doi.org/10.1109/MIOT.2026.3707892 | Preserve year, journal and authors. Leave final volume/issue/pages blank pending IEEE Xplore detail; provisional 1–6 not automatically substituted for final pagination. |
| `10.1109/ICCWorkshops63917.2026.11586270` | Full Domain Resource Programming in Wideband MIMO Systems: A Step Towards 6G; Xuanrui Li, Zhongxiang Wei, Junyuan Wang, Wen Ji, Erwu Liu | Proc. IEEE ICC Workshops, 2026, pp. 1–6 | https://dblp.org/rec/conf/icc/LiWWJL26 ; https://doi.org/10.1109/ICCWorkshops63917.2026.11586270 | Conference year and page range corroborated; retained. |

## Corrected publisher-primary record

- `10.1109/TVT.2026.3721188`: **IEEE Trans. Veh. Technol., vol. 75, no. 11, pp. 28950–28955, Nov. 2026**. IEEE Xplore Metadata screenshot provided by the project owner. **Not Early Access**. This primary-source confirmation overrides older search snippets. Original DOI: https://doi.org/10.1109/TVT.2026.3721188.

## Other spot-checks this round

- `10.1109/TCCN.2026.3676012`: nine listed authors including fourth author **Rui Wang**, vol. 12, pp. 6955–6969, 2026, corroborated by https://dblp.org/rec/journals/tccn/JiangLNWHXGNJ26 and https://ro.ecu.edu.au/ecuworks2022-2026/8042/.
- `10.1109/TWC.2025.3625223`: formal vol. 25, pp. 6491–6506, 2026, corroborated by https://biubiuhaha.github.io/yuanzhang.github.io/ and https://www.scilit.com/publications/91a2ae8c8610b9cbad42bf5874920b57.

## Required audit discipline

1. DOI path year may refer to online publication/registration and is **not** authoritative for the finalized volume year.
2. For IEEE journals, prefer the publisher's live **Metadata** panel for `Volume`, `Issue`, `Page(s)`, and publication status. If unavailable, corroborate through institutional records and retain an explicit pending state, not invented numbers.
3. For IEEE conference proceedings, verify the proceedings name and page range; distinguish ICCC from ICCC Workshops.
4. Before merging, run `python tools/render_publications.py --check`, `python tools/validate.py`, website static checks and bilingual browser regression. No validation is claimed as passed merely because this file exists.
5. The other DOI records have not all been independently reopened against live IEEE publisher Metadata **in this pass**. Continue systematic DOI-by-DOI auditing; record exact source URLs and corrections here before declaring the 68-record publisher audit complete.
