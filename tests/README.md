Usage: calc_reward_lv2 / calc_reward_lv3

- Both tools enumerate counts for 3 agents with each agent picking in [1..V].
- lv2 matches the formula in `rewards/CE_reward.py` and marks `S>2V` as TERMINATE.
- lv3 uses entropy-based balance (normalized) multiplied by 2.8.

Additionally, an alternative lv3 based on MSD (variance) is provided in
`tests/calc_reward_lv3_msd`. Formula:
  - N = num agents, t = V/N
  - msd = (1/N) * sum (s_i - t)^2
  - msd_max = (1/N) * V^2 * (1 - 1/N)
  - lv3 = 4 * max(0, 1 - msd/(msd_max+eps)) - 2

Run (single V)
- lv2 print all: `python LLM_Collab_Module_Completion/tests/calc_reward_lv2/main.py -V 3 --print-all`
- lv3 print all: `python LLM_Collab_Module_Completion/tests/calc_reward_lv3/main.py -V 3 --print-all`
- lv3 (MSD) print all: `python LLM_Collab_Module_Completion/tests/calc_reward_lv3_msd/main.py -V 3 --print-all`

CSV export
- Export V=3..8:
  - lv2: `python LLM_Collab_Module_Completion/tests/calc_reward_lv2/main.py --csv LLM_Collab_Module_Completion/tests/calc_reward_lv2/lv2_V3-8.csv --export-range`
  - lv3: `python LLM_Collab_Module_Completion/tests/calc_reward_lv3/main.py --csv LLM_Collab_Module_Completion/tests/calc_reward_lv3/lv3_V3-8.csv --export-range`
  - lv3 (MSD): `python LLM_Collab_Module_Completion/tests/calc_reward_lv3_msd/main.py --csv LLM_Collab_Module_Completion/tests/calc_reward_lv3_msd/lv3_msd_V3-8.csv --export-range`
- Export single V:
  - lv2: `python LLM_Collab_Module_Completion/tests/calc_reward_lv2/main.py -V 5 --csv LLM_Collab_Module_Completion/tests/calc_reward_lv2/lv2_V5.csv`
  - lv3: `python LLM_Collab_Module_Completion/tests/calc_reward_lv3/main.py -V 5 --csv LLM_Collab_Module_Completion/tests/calc_reward_lv3/lv3_V5.csv`
  - lv3 (MSD): `python LLM_Collab_Module_Completion/tests/calc_reward_lv3_msd/main.py -V 5 --csv LLM_Collab_Module_Completion/tests/calc_reward_lv3_msd/lv3_msd_V5.csv`

Sorting behavior
- lv2 `--print-all`: sort by lv2 desc, then S asc, then (s1,s2,s3); TERMINATE last.
- lv2 summary: sort by lv2 desc; all-terminate S last.
- lv3 `--print-all`: sort by lv3 desc, then S asc, then (s1,s2,s3).
- lv3 summary: sort by lv3_max desc, then S asc.
- lv3 (MSD) `--print-all`: sort by lv3 desc, then S asc, then (s1,s2,s3).
- lv3 (MSD) summary: sort by lv3_max desc, then S asc.

CSV columns
- lv2: `V,s1,s2,s3,S,lv2,terminate` (terminate=1 iff `S>2V`, `lv2` empty)
- lv3: `V,s1,s2,s3,S,lv3`
- lv3 (MSD): `V,s1,s2,s3,S,lv3_msd`
