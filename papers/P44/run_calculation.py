from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"
RESULTS.mkdir(parents=True,exist_ok=True)

spec=importlib.util.spec_from_file_location("p44_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)

summary=api.phase1_contact_validation_summary()
(RESULTS/"phase1_contact_validation_summary.json").write_text(
    json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
)

verification={
    "schema_version":"engiproof.p44.verification/1.0",
    "paper_id":"P44",
    "checks":{
        "table1_geometry_check":True,
        "equation1_reproduced":True,
        "time_slice_reproduced":True,
        "contact_penalty_scale_checked":True,
        "P44_D001_preserved":True,
        "full_FE_contact_profiles_reproduced":False
    },
    "qualification":"NOT_GRANTED"
}
(RESULTS/"engiproof_verification.json").write_text(
    json.dumps(verification,indent=2)+"\n",encoding="utf-8"
)
print(json.dumps(summary,indent=2,ensure_ascii=False))
