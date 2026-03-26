

from service.plan_service import gather_context_and_plan

def execute_internal_reasoning_loop():
    while True:
        # gather context and plan
        plan = gather_context_and_plan()
         
