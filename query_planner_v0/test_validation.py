import unittest
from query_planner_v0.generate import FIELDS, validate, ground_extraction, deny_network, parse_output

class ValidationTests(unittest.TestCase):
    def test_unstated_entity_is_removed_without_replacement(self):
        obj={k:'' for k in FIELDS}
        obj.update(topic='graph learning',dataset='InventedBench',negative_constraints=[],important_entities=['QM9','ImaginaryModel'])
        grounded,rejected=ground_extraction(obj,'Study graph learning on QM9.')
        self.assertEqual(grounded['dataset'],'')
        self.assertEqual(grounded['important_entities'],['QM9'])
        self.assertEqual(len(rejected),2)
        validate('extract',grounded,'Study graph learning on QM9.')

    def test_invalid_facet_mapping_is_not_silently_accepted(self):
        facets=[{'facet':str(i)} for i in range(5)]
        queries=[{'query':'graph learning models','facet':str(i),'covered_constraints':['method']} for i in range(5)]
        queries[2]['facet']='wrong'
        with self.assertRaises(ValueError):validate('generate',queries,'graph learning',facets)

    def test_network_lookup_is_blocked(self):
        with self.assertRaises(RuntimeError):deny_network('socket.getaddrinfo',('google.serper.dev',443))

    def test_nonverbatim_constraint_fails_direct_validation(self):
        obj={k:'' for k in FIELDS}
        obj.update(method='transformers',negative_constraints=[],important_entities=[])
        with self.assertRaises(ValueError):validate('extract',obj,'Study graph learning.')

    def test_action_suffix_is_not_executed_or_used_as_query(self):
        self.assertEqual(parse_output('[1,2]\n[Expand]unused[StopExpand]'),[1,2])
        with self.assertRaises(ValueError):parse_output('[1,2] fabricated prose')

if __name__=='__main__':unittest.main()
