from pathlib import Path
import json
from ap4 import BrewStateMachine, ProcessSnapshot, BrewState, build_ap5_payload, build_ap6_dashboard_payload
from ap4.recipe import BrewRecipe

out = Path(__file__).parent/'data'
out.mkdir(exist_ok=True)
fsm = BrewStateMachine(recipe=BrewRecipe(nachguss_min_duration_s=2,mashing_duration_s=2,transfer_to_k3_duration_s=2,lautering_duration_s=2,boiling_duration_s=2,transfer_to_k4_duration_s=2,fermentation_duration_s=2))
# Normal state example
for snap, dt in [
    (ProcessSnapshot(start_requested=True),1),
    (ProcessSnapshot(start_requested=True,k1_temperature_c=78,k1_level_l=20),1),
    (ProcessSnapshot(k1_temperature_c=78,k1_level_l=20,v3_open=True,durchfluss_k1_k2_l_min=1.2,k2_level_l=18,k2_temperature_c=65),3),
]:
    fsm.update(snap, dt)
normal_context = fsm.get_context_for_anomaly()
(out/'AP4_to_AP5_payload_normal.json').write_text(json.dumps(build_ap5_payload(normal_context), indent=2, ensure_ascii=False), encoding='utf-8')
(out/'AP4_to_AP6_payload_normal.json').write_text(json.dumps(build_ap6_dashboard_payload(normal_context), indent=2, ensure_ascii=False), encoding='utf-8')
# Fault example
fsm2 = BrewStateMachine()
fsm2.state = BrewState.BOILING
fsm2.update(ProcessSnapshot(k2_temperature_c=110,k2_level_l=18), 1)
fault_context = fsm2.get_context_for_anomaly()
(out/'AP4_to_AP5_payload_fault.json').write_text(json.dumps(build_ap5_payload(fault_context), indent=2, ensure_ascii=False), encoding='utf-8')
(out/'AP4_to_AP6_payload_fault.json').write_text(json.dumps(build_ap6_dashboard_payload(fault_context), indent=2, ensure_ascii=False), encoding='utf-8')
