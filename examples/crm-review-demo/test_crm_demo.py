import copy, sqlite3, unittest
from crm_demo import connect, seed, propose, apply, snapshot

def contacts():
    return [{'id':str(i), 'name':' Test '+str(i)+' ', 'email':'person'+str(i)+'@EXAMPLE.COM ', 'company':' Demo ', 'notes':'quote please', 'category':''} for i in range(3)]

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(':memory:'); seed(self.db, contacts()); self.plan=propose(self.db)
    def tearDown(self): self.db.close()
    def approval(self, ids): return {'plan_id':self.plan['plan_id'], 'reviewer':'demo-reviewer', 'approved_ids':ids}
    def test_only_approved_ids_change(self):
        before=snapshot(self.db); result=apply(self.db,self.plan['plan_id'],self.approval(['0']))
        self.assertEqual(result['applied'],1); self.assertEqual(snapshot(self.db)[1:],before[1:])
    def test_replay_no_extra_writes(self):
        a=self.approval(['0']); apply(self.db,self.plan['plan_id'],a)
        self.assertEqual(apply(self.db,self.plan['plan_id'],a),{'applied':0,'already_applied':1})
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM audit').fetchone()[0],1)
    def test_wrong_plan_rejected(self):
        a=self.approval(['0']); a['plan_id']='wrong'
        with self.assertRaises(ValueError): apply(self.db,self.plan['plan_id'],a)
    def test_unknown_id_rejected(self):
        with self.assertRaises(ValueError): apply(self.db,self.plan['plan_id'],self.approval(['missing']))
    def test_stale_batch_no_partial_writes(self):
        altered=contacts()[1]; altered['company']='Changed'
        import json
        self.db.execute('UPDATE contacts SET data=? WHERE id=?',(json.dumps(altered),'1'))
        before=snapshot(self.db)
        with self.assertRaises(ValueError): apply(self.db,self.plan['plan_id'],self.approval(['0','1']))
        self.assertEqual(snapshot(self.db),before); self.assertEqual(self.db.execute('SELECT COUNT(*) FROM audit').fetchone()[0],0)
    def test_audit_failure_rolls_back_update(self):
        self.db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT,'test failure'); END")
        before=snapshot(self.db)
        with self.assertRaises(sqlite3.IntegrityError): apply(self.db,self.plan['plan_id'],self.approval(['0']))
        self.assertEqual(snapshot(self.db),before)
    def test_invalid_email_and_ambiguous_category_flagged(self):
        db=connect(':memory:'); r=contacts()[0]; r['email']='invalid'; r['notes']='quote and support'
        seed(db,[r]); p=propose(db)
        self.assertEqual(len(p['issues']),2); self.assertNotIn('category',p['proposals'][0]['changes']); db.close()
    def test_duplicates_only_candidates(self):
        db=connect(':memory:'); rows=contacts(); rows[1]['email']=rows[0]['email']
        seed(db,rows); p=propose(db); self.assertEqual(p['duplicate_candidates'],[['0','1']])
        self.assertEqual(len(snapshot(db)),3); db.close()
    def test_no_approval_no_updates(self):
        before=snapshot(self.db); apply(self.db,self.plan['plan_id'],self.approval([])); self.assertEqual(snapshot(self.db),before)
    def test_deterministic_plan(self): self.assertEqual(propose(self.db),self.plan)
    def test_duplicate_input_ids_rejected(self):
        db=connect(':memory:'); rows=contacts(); rows[1]['id']=rows[0]['id']
        with self.assertRaises(ValueError): seed(db,rows)
        self.assertEqual(snapshot(db),[]); db.close()
    def test_email_local_part_case_preserved(self):
        db=connect(':memory:'); r=contacts()[0]; r['email']='Person@EXAMPLE.COM '
        seed(db,[r]); self.assertEqual(propose(db)['proposals'][0]['changes']['email'],'Person@example.com'); db.close()

if __name__=='__main__': unittest.main(verbosity=2)
