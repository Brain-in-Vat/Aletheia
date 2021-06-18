from aletheia.mechanism_engine.qf.clr import  run_clr_calcs
class QuadraticFunding(object):
    
    def __init__(self, threshold=25, total_pot=5000):
        self.grants = {
        }
        self.threshold = threshold
        self.total_pot = total_pot
    

    def grant(self, project_id, user_id, contribution_amount):
        tmp = self.grants.get(project_id)
        if not tmp:
            self.grants[project_id] = {
                'id': project_id,
                'contributions': []
            }
        tmp = self.grants[project_id]
        tmp['contributions'].append({user_id: contribution_amount})
       
       
    def clr_calcs(self):
        grants = list(self.grants.values())
        return run_clr_calcs(grants, self.threshold, self.total_pot)
